#!/usr/bin/env python3
"""Score every results/inference/<model>/<corpus>.csv against the references, per corpus.

  python3 scripts/evaluation/evaluate.py            # all models found in results/inference

For each (model, corpus, subset, normalisation level): WER and CER with 95% bootstrap CIs
(utterance resampling), substitution / deletion / insertion counts and utterance-level
distribution. Also paired-bootstrap model comparisons, hallucination and script diagnostics,
efficiency, per-utterance scores, full alignments and frequent substitutions.

Subsets: zenodo = all / test (speaker F) / train (speaker M); pangloss = all / test / dev,
from split_v0 in data/manifests/eval. Utterances with an exclude_reason are always left out.
Outputs go to results/evaluation/ (see REPORT.md there).
"""
import collections
import importlib.metadata as md
import json
import re
import subprocess
import sys
import unicodedata
import zlib
from datetime import datetime, timezone
from pathlib import Path

import jiwer
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize import LEVELS, normalize_all  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
INFER = ROOT / "results" / "inference"
OUT = ROOT / "results" / "evaluation"
PRIMARY = "raw"  # official score: case, punctuation, spacing only (decision of 31 Oct 2026)
B = 2000
SEED = 20261018
BACKCHANNEL_BARS = re.compile(r"│([^│]*)│")
SUBSETS = {"zenodo": ("all", "test", "train"), "pangloss": ("all", "test", "dev")}
MODEL_ORDER = ["whisper-large-v3", "whisper-large-v3-turbo", "mms-1b-all-ddn",
               "omniASR_CTC_1B_v2", "omniASR_LLM_7B_v2", "chirp_3"]


# ---------------------------------------------------------------- per-utterance scoring
def score_pair(ref: str, hyp: str):
    w = jiwer.process_words(ref, hyp)
    c = jiwer.process_characters(ref, hyp)
    # word segmentation ignored: CER on space-free strings, and exact match of the whole utterance
    ref_ns, hyp_ns = ref.replace(" ", ""), hyp.replace(" ", "")
    cn = jiwer.process_characters(ref_ns, hyp_ns)
    return dict(n_ref_w=len(w.references[0]), n_hyp_w=len(w.hypotheses[0]),
                S=w.substitutions, D=w.deletions, I=w.insertions, H=w.hits,
                n_ref_c=len(c.references[0]),
                cS=c.substitutions, cD=c.deletions, cI=c.insertions,
                n_ref_cn=len(ref_ns), cnE=cn.substitutions + cn.deletions + cn.insertions,
                exact=ref_ns == hyp_ns), w


def non_latin(text: str) -> bool:
    return any(ch.isalpha() and "LATIN" not in unicodedata.name(ch, "") for ch in text)


def _runs(tokens, n):
    """Longest run of back-to-back repetitions for every n-gram, e.g. 'kwa kwa kwa' -> {('kwa',): 3}."""
    best = {}
    for start in range(len(tokens) - n + 1):
        g, k = tuple(tokens[start:start + n]), 1
        while tokens[start + k * n:start + (k + 1) * n] == list(g):
            k += 1
        best[g] = max(best.get(g, 0), k)
    return best


def has_loop(hyp: str, ref: str) -> bool:
    """Decoding loop: an n-gram (n=1..4) repeated >= 3 times back to back in the hypothesis,
    more times than in the reference. Dendi reduplication ('dubu dubu', 'yo ize no yo ize no')
    stays below the threshold; frequent function words spread over the sentence do not count."""
    h, r = hyp.split(), ref.split()
    for n in (1, 2, 3, 4):
        rr = _runs(r, n)
        if any(k >= 3 and k > rr.get(g, 0) for g, k in _runs(h, n).items()):
            return True
    return False


def load_references():
    allu = pd.read_csv(ROOT / "data/manifests/all_utterances.csv", keep_default_na=False)
    # Pangloss sensitivity reference: listener back-channels kept as words (bars removed)
    bc = allu.set_index("utt_id").text_raw.map(lambda t: BACKCHANNEL_BARS.sub(r" \1 ", t))
    man = {c: pd.read_csv(ROOT / f"data/manifests/eval/{c}.csv", keep_default_na=False) for c in SUBSETS}
    return man, bc


def score_file(path: Path, manifest: pd.DataFrame, bc_ref: pd.Series, corpus: str):
    pred = pd.read_csv(path, keep_default_na=False)
    d = manifest.merge(pred[["utt_id", "prediction", "detected_language", "inference_time_s", "error"]],
                       on="utt_id", how="left", validate="one_to_one")
    missing = d.prediction.isna().sum()
    d = d.fillna({"prediction": "", "detected_language": "", "inference_time_s": np.nan, "error": "missing"})
    rows, aligns, subs = [], [], collections.Counter()
    for r in d.itertuples():
        nr, nh = normalize_all(r.reference), normalize_all(r.prediction)
        row = dict(utt_id=r.utt_id, split_v0=r.split_v0, exclude_reason=r.exclude_reason,
                   duration_s=r.duration_s, detected_language=r.detected_language,
                   inference_time_s=r.inference_time_s, error=r.error,
                   reference=r.reference, prediction=r.prediction,
                   non_latin=non_latin(r.prediction), empty_after_norm=nh[PRIMARY] == "")
        for lvl in LEVELS:
            s, w = score_pair(nr[lvl], nh[lvl])
            row.update({f"{lvl}_{k}": v for k, v in s.items()})
            row[f"{lvl}_ref"], row[f"{lvl}_hyp"] = nr[lvl], nh[lvl]
            row[f"{lvl}_wer"] = (s["S"] + s["D"] + s["I"]) / s["n_ref_w"]
            row[f"{lvl}_cer"] = (s["cS"] + s["cD"] + s["cI"]) / s["n_ref_c"]
            if lvl == PRIMARY:
                aligns.append(f"### {r.utt_id}  [{r.split_v0}{', EXCLUDED' if r.exclude_reason else ''}]"
                              f"  WER={row[f'{lvl}_wer']:.2f}\n"
                              + jiwer.visualize_alignment(w, show_measures=False).split("\n", 2)[-1].strip())
                rw, hw = w.references[0], w.hypotheses[0]
                for ch in w.alignments[0]:
                    if ch.type == "substitute":
                        for a, b in zip(rw[ch.ref_start_idx:ch.ref_end_idx], hw[ch.hyp_start_idx:ch.hyp_end_idx]):
                            subs[(a, b)] += 1
        row["loop"] = has_loop(nh[PRIMARY], nr[PRIMARY])
        row["len_ratio"] = row[f"{PRIMARY}_n_hyp_w"] / row[f"{PRIMARY}_n_ref_w"]
        if corpus == "pangloss":
            s, _ = score_pair(normalize_all(bc_ref[r.utt_id])[PRIMARY], nh[PRIMARY])
            row.update({f"bc_{k}": v for k, v in s.items()})
        rows.append(row)
    return pd.DataFrame(rows), aligns, subs, int(missing)


# ---------------------------------------------------------------- aggregation
def subset_mask(df: pd.DataFrame, subset: str):
    keep = df.exclude_reason == ""
    return keep if subset == "all" else keep & (df.split_v0 == subset)


def boot_idx(corpus: str, subset: str, n: int):
    rng = np.random.default_rng(SEED + zlib.crc32(f"{corpus}/{subset}".encode()))
    return rng.integers(0, n, size=(B, n))


def rate_ci(err: np.ndarray, den: np.ndarray, idx: np.ndarray):
    point = err.sum() / den.sum()
    bs = err[idx].sum(1) / den[idx].sum(1)
    return point, *np.percentile(bs, [2.5, 97.5])


def summarize(df, corpus, subset, prefix, level_name):
    m = subset_mask(df, subset)
    s = df[m].sort_values("utt_id")
    idx = boot_idx(corpus, subset, len(s))
    p = prefix
    werr = (s[f"{p}S"] + s[f"{p}D"] + s[f"{p}I"]).to_numpy(float)
    cerr = (s[f"{p}cS"] + s[f"{p}cD"] + s[f"{p}cI"]).to_numpy(float)
    nw, nc = s[f"{p}n_ref_w"].to_numpy(float), s[f"{p}n_ref_c"].to_numpy(float)
    wer, wlo, whi = rate_ci(werr, nw, idx)
    cer, clo, chi = rate_ci(cerr, nc, idx)
    cern, cnlo, cnhi = rate_ci(s[f"{p}cnE"].to_numpy(float), s[f"{p}n_ref_cn"].to_numpy(float), idx)
    ex, exlo, exhi = rate_ci(s[f"{p}exact"].to_numpy(float), np.ones(len(s)), idx)
    uw = werr / nw
    return dict(level=level_name, n_utts=len(s), n_ref_words=int(nw.sum()), n_ref_chars=int(nc.sum()),
                WER=wer, WER_lo=wlo, WER_hi=whi, CER=cer, CER_lo=clo, CER_hi=chi,
                CER_nospace=cern, CER_nospace_lo=cnlo, CER_nospace_hi=cnhi,
                EXACT=ex, EXACT_lo=exlo, EXACT_hi=exhi,
                S=int(s[f"{p}S"].sum()), D=int(s[f"{p}D"].sum()), I=int(s[f"{p}I"].sum()), H=int(s[f"{p}H"].sum()),
                sub_rate=s[f"{p}S"].sum() / nw.sum(), del_rate=s[f"{p}D"].sum() / nw.sum(),
                ins_rate=s[f"{p}I"].sum() / nw.sum(),
                utt_WER_median=float(np.median(uw)), utt_WER_p90=float(np.percentile(uw, 90)),
                pct_utts_WER0=float((uw == 0).mean()), pct_utts_WER_ge1=float((uw >= 1).mean()))


def pairwise(scored, corpus, subset):
    out = []
    models = [m for m in MODEL_ORDER if (m, corpus) in scored] + \
             sorted(m for m, c in scored if c == corpus and m not in MODEL_ORDER)
    base = {}
    for mname in models:
        df = scored[(mname, corpus)]
        s = df[subset_mask(df, subset)].sort_values("utt_id")
        p = f"{PRIMARY}_"
        base[mname] = dict(ids=s.utt_id.to_numpy(),
                           we=(s[p + "S"] + s[p + "D"] + s[p + "I"]).to_numpy(float), nw=s[p + "n_ref_w"].to_numpy(float),
                           ce=(s[p + "cS"] + s[p + "cD"] + s[p + "cI"]).to_numpy(float), nc=s[p + "n_ref_c"].to_numpy(float),
                           ex=s[p + "exact"].to_numpy(float), one=np.ones(len(s)))
    if not base:
        return out
    n = len(next(iter(base.values()))["ids"])
    idx = boot_idx(corpus, subset, n)
    for i, a in enumerate(models):
        for b in models[i + 1:]:
            A, Bm = base[a], base[b]
            assert (A["ids"] == Bm["ids"]).all()
            for metric, e, d in (("WER", "we", "nw"), ("CER", "ce", "nc"), ("EXACT", "ex", "one")):
                da = A[e][idx].sum(1) / A[d][idx].sum(1)
                db = Bm[e][idx].sum(1) / Bm[d][idx].sum(1)
                diff = da - db
                point = A[e].sum() / A[d].sum() - Bm[e].sum() / Bm[d].sum()
                p_two = min(1.0, 2 * min((diff <= 0).mean(), (diff >= 0).mean()))
                lo, hi = np.percentile(diff, [2.5, 97.5])
                out.append(dict(corpus=corpus, subset=subset, level=PRIMARY, metric=metric, model_a=a, model_b=b,
                                diff_a_minus_b=point, ci_lo=lo, ci_hi=hi, p_bootstrap=p_two,
                                significant_95=bool(lo > 0 or hi < 0)))
    return out


def diagnostics(df, pred_csv: Path, model, corpus, missing):
    raw = pd.read_csv(pred_csv, keep_default_na=False)
    keep = df[df.exclude_reason == ""]
    langs = keep.detected_language.value_counts(normalize=True)
    return dict(model=model, corpus=corpus, n_predictions=len(raw), n_missing=missing,
                n_errors=int((raw.error != "").sum()), n_empty_raw=int((raw.prediction == "").sum()),
                pct_empty_after_norm=float(keep.empty_after_norm.mean()),
                pct_non_latin=float(keep.non_latin.mean()), pct_loops=float(keep.loop.mean()),
                len_ratio_median=float(keep.len_ratio.median()), pct_len_ratio_gt2=float((keep.len_ratio > 2).mean()),
                pct_len_ratio_lt05=float((keep.len_ratio < 0.5).mean()),
                top_languages="; ".join(f"{k}:{v:.0%}" for k, v in langs.head(5).items()),
                n_languages=int(keep.detected_language.nunique()),
                RTF=float(raw.inference_time_s.sum() / raw.duration_s.sum()),
                sec_per_utt=float(raw.inference_time_s.mean()), total_infer_min=float(raw.inference_time_s.sum() / 60))


# ---------------------------------------------------------------- report
def pct(x):
    return f"{100 * x:.1f}"


def ci(r, k):
    return f"{pct(r[k])} [{pct(r[k + '_lo'])}–{pct(r[k + '_hi'])}]"


def write_report(summary, pw, diag, meta):
    L = [f"# Évaluation zero-shot — Dendi ASR\n",
         f"Généré le {meta['generated_utc']} par `scripts/evaluation/evaluate.py` (commit `{meta['git_commit']}`). "
         f"WER/CER en %, IC 95 % par bootstrap sur les énoncés (B={B}, graine {SEED}). "
         f"Niveau principal : **`{PRIMARY}`** (voir `scripts/evaluation/normalize.py`). "
         f"Découpage : `split_v0` (proposition PHASE1_READINESS §3). Énoncés exclus retirés partout.\n",
         "**Score officiel = `raw`** : normalisation minimale (minuscules, ponctuation retirée, espaces nettoyés, "
         "Unicode NFC, correction de l'erreur d'encodage `ℇ`→`ɛ` de Pangloss). Aucun caractère propre au Dendi n'est "
         "substitué et les tons sont conservés. Les autres niveaux sont du **diagnostic uniquement**, pour expliquer "
         "d'où viennent les erreurs : `notone` (+ tons retirés, `ɑ`→`a`), `flat` (+ autres diacritiques, `ɛ`/`ɔ`→`e`/`o`), "
         "`skel` (+ `c`/`k`, `kp`/`kw`, semi-voyelles, longueur ; volontairement trop indulgent). "
         "**CER sans espaces** : CER calculé après suppression des espaces (le découpage en mots est ignoré). "
         "**Entièrement justes** : % d'énoncés dont l'hypothèse sans espaces est identique à la référence sans espaces "
         "(pour Zenodo, % de nombres reconnus en entier).\n"]
    corp_name = {"zenodo": "Zenodo — nombres (2 locuteurs)", "pangloss": "Pangloss — contes 1968"}
    for corpus in SUBSETS:
        S = summary[summary.corpus == corpus]
        if S.empty:
            continue
        L.append(f"\n## {corp_name[corpus]}\n")
        for subset in SUBSETS[corpus]:
            T = S[(S.subset == subset) & (S.level == PRIMARY)]
            if T.empty:
                continue
            n = T.iloc[0]
            L.append(f"\n### Sous-ensemble `{subset}` — {n.n_utts} énoncés, {n.n_ref_words} mots de référence\n")
            L.append("| Modèle | WER | CER | CER sans espaces | Entièrement justes | Sub | Del | Ins | WER médian / énoncé | Énoncés WER≥100 |")
            L.append("|---|---|---|---|---|---|---|---|---|---|")
            for r in T.sort_values("WER").itertuples():
                r = r._asdict()
                L.append(f"| {r['model']} | {ci(r, 'WER')} | {ci(r, 'CER')} | {ci(r, 'CER_nospace')} | {ci(r, 'EXACT')} | "
                         f"{pct(r['sub_rate'])} | {pct(r['del_rate'])} | "
                         f"{pct(r['ins_rate'])} | {pct(r['utt_WER_median'])} | {pct(r['pct_utts_WER_ge1'])} |")
        L.append(f"\n#### Effet de la normalisation (`test`) — WER / CER sans espaces / entièrement justes\n")
        L.append("| Modèle | " + " | ".join(f"`{lv}`" for lv in LEVELS) + " |")
        L.append("|---|" + "---|" * len(LEVELS))
        A = S[S.subset == "all"]
        TT = S[S.subset == "test"]
        for mname in TT[TT.level == PRIMARY].sort_values("WER").model:
            cells = []
            for lv in LEVELS:
                r = TT[(TT.model == mname) & (TT.level == lv)].iloc[0]
                cells.append(f"{pct(r.WER)} / {pct(r.CER_nospace)} / {pct(r.EXACT)}")
            L.append(f"| {mname} | " + " | ".join(cells) + " |")
        if corpus == "pangloss":
            BC = S[(S.level == f"{PRIMARY}+backchannels") & (S.subset == "all")]
            if not BC.empty:
                L.append(f"\n#### Sensibilité : références avec les réponses de l'auditoire (« nam », « tô ») — `all`, `{PRIMARY}`\n")
                L.append("| Modèle | WER sans (principal) | WER avec | Δ |\n|---|---|---|---|")
                for r in BC.itertuples():
                    base = A[(A.model == r.model) & (A.level == PRIMARY)].iloc[0].WER
                    L.append(f"| {r.model} | {pct(base)} | {pct(r.WER)} | {pct(r.WER - base)} |")
    L.append("\n## Diagnostics (énoncés non exclus)\n")
    L.append("| Modèle | Corpus | Erreurs | Vides | Non-latin | Boucles | Ratio long. médian | Ratio>2 | Langues détectées (top) | RTF | s/énoncé |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in diag.itertuples():
        L.append(f"| {r.model} | {r.corpus} | {r.n_errors} | {pct(r.pct_empty_after_norm)} | {pct(r.pct_non_latin)} | {pct(r.pct_loops)} | "
                 f"{r.len_ratio_median:.2f} | {pct(r.pct_len_ratio_gt2)} | {r.top_languages} | {r.RTF:.3f} | {r.sec_per_utt:.2f} |")
    L.append(f"\n## Comparaisons appariées (`{PRIMARY}`, WER, sous-ensemble `test`)\n")
    L.append("Différence A − B en points, IC 95 % bootstrap apparié ; ✱ = IC excluant 0.\n")
    L.append("| Corpus | A | B | Δ WER | IC 95 % | p |\n|---|---|---|---|---|---|")
    for r in pw[(pw.metric == "WER") & (pw.subset == "test")].itertuples():
        L.append(f"| {r.corpus} | {r.model_a} | {r.model_b} | {pct(r.diff_a_minus_b)}{' ✱' if r.significant_95 else ''} | "
                 f"[{pct(r.ci_lo)}, {pct(r.ci_hi)}] | {r.p_bootstrap:.3f} |")
    L.append(f"\n### Zenodo : nombres entièrement justes (`{PRIMARY}`, sous-ensemble `test`)\n")
    L.append("Différence A − B en points de % de nombres reconnus en entier.\n")
    L.append("| A | B | Δ entièrement justes | IC 95 % | p |\n|---|---|---|---|---|")
    for r in pw[(pw.metric == "EXACT") & (pw.subset == "test") & (pw.corpus == "zenodo")].itertuples():
        L.append(f"| {r.model_a} | {r.model_b} | {pct(r.diff_a_minus_b)}{' ✱' if r.significant_95 else ''} | "
                 f"[{pct(r.ci_lo)}, {pct(r.ci_hi)}] | {r.p_bootstrap:.3f} |")
    L.append("\n## Fichiers\n")
    L.append("- `summary.csv` : toutes les métriques (modèle × corpus × sous-ensemble × niveau).\n"
             "- `pairwise.csv` : comparaisons appariées (WER, CER et entièrement justes, `all` et `test`).\n"
             "- `ortho_sensitivity.csv` : sensibilité à l'orthographe (`notone` / `flat` / `skel`), revue du 24 octobre.\n"
             "- `ortho_decomposition.csv` : effet de chaque convention ajoutée une à une, de `raw` à `skel` (diagnostic).\n"
             "- `diagnostics.csv` : hallucinations, écriture, longueur, langues, efficacité.\n"
             "- `per_utterance/<modèle>__<corpus>.csv` : chaque énoncé, références et hypothèses normalisées, S/D/I par niveau.\n"
             f"- `alignments/<modèle>__<corpus>.txt` : alignement mot à mot (`{PRIMARY}`) de chaque énoncé.\n"
             "- `substitutions/<modèle>__<corpus>.csv` : paires référence→hypothèse les plus fréquentes.\n"
             "- `eval_meta.json` : versions, graine, paramètres, empreintes des fichiers de prédiction.")
    (OUT / "REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- main
def main():
    man, bc = load_references()
    for sub in ("per_utterance", "alignments", "substitutions"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    scored, summary, diag, inputs = {}, [], [], {}
    for mdir in sorted(p for p in INFER.iterdir() if p.is_dir() and not p.name.startswith("_")):
        for corpus in SUBSETS:
            f = mdir / f"{corpus}.csv"
            if not f.exists():
                continue
            print(f"scoring {mdir.name}/{corpus}")
            df, aligns, subs, missing = score_file(f, man[corpus], bc, corpus)
            scored[(mdir.name, corpus)] = df
            inputs[f"{mdir.name}/{corpus}.csv"] = subprocess.run(["sha256sum", str(f)], capture_output=True,
                                                                 text=True).stdout.split()[0]
            tag = f"{mdir.name}__{corpus}"
            df.to_csv(OUT / "per_utterance" / f"{tag}.csv", index=False)
            (OUT / "alignments" / f"{tag}.txt").write_text("\n\n".join(aligns) + "\n", encoding="utf-8")
            pd.DataFrame([dict(ref=a, hyp=b, count=n) for (a, b), n in subs.most_common(200)]) \
                .to_csv(OUT / "substitutions" / f"{tag}.csv", index=False)
            for subset in SUBSETS[corpus]:
                for lvl in LEVELS:
                    summary.append(dict(model=mdir.name, corpus=corpus, subset=subset,
                                        **summarize(df, corpus, subset, f"{lvl}_", lvl)))
                if corpus == "pangloss":
                    summary.append(dict(model=mdir.name, corpus=corpus, subset=subset,
                                        **summarize(df, corpus, subset, "bc_", f"{PRIMARY}+backchannels")))
            diag.append(diagnostics(df, f, mdir.name, corpus, missing))
    order = {m: i for i, m in enumerate(MODEL_ORDER)}
    summary = pd.DataFrame(summary).sort_values(["corpus", "subset", "level", "WER"])
    diag = pd.DataFrame(diag).sort_values(["corpus", "model"], key=lambda s: s.map(order) if s.name == "model" else s)
    pw = pd.DataFrame([r for c in SUBSETS for sub in ("all", "test") for r in pairwise(scored, c, sub)])
    summary.to_csv(OUT / "summary.csv", index=False)
    diag.to_csv(OUT / "diagnostics.csv", index=False)
    pw.to_csv(OUT / "pairwise.csv", index=False)
    git = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    meta = dict(generated_utc=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), git_commit=git,
                primary_level=PRIMARY, levels=list(LEVELS), bootstrap_samples=B, seed=SEED,
                subsets=SUBSETS, cer_definition="character edit distance over NFC code points, spaces included (jiwer default)",
                wer_definition="(S+D+I)/N over whitespace tokens of normalised text, micro-averaged over utterances",
                versions={p: md.version(p) for p in ("jiwer", "numpy", "pandas")}, python=sys.version.split()[0],
                prediction_files_sha256=inputs)
    (OUT / "eval_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(summary, pw, diag, meta)
    print(f"wrote {OUT.relative_to(ROOT)}/REPORT.md")


if __name__ == "__main__":
    main()
