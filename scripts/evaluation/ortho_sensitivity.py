#!/usr/bin/env python3
"""Sensitivity of the zero-shot scores to spelling conventions (test subsets only).

Exploratory: an upper bound on how much of the error is orthography rather than recognition.
The `skel` level is deliberately too generous (it can merge real contrasts such as vowel
length) and is NOT a metric for the paper's main table.

  notone  primary level (scripts/evaluation/normalize.py)
  flat    normalize.py's flat level
  skel    normalize.py's skel level (defined there since the review was integrated)

For each level: WER, CER with spaces removed (word segmentation ignored), and the share of
utterances whose space-free hypothesis equals the space-free reference ("exact").
Writes results/evaluation/ortho_sensitivity.csv.  Run from the project root:
  python3 scripts/evaluation/ortho_sensitivity.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize import normalize  # noqa: E402
from verify_metrics import edit_distance  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MODELS = ["mms-1b-all-ddn", "omniASR_LLM_7B_v2", "omniASR_CTC_1B_v2", "whisper-large-v3", "whisper-large-v3-turbo"]
SUBSETS = {"zenodo": "test", "pangloss": "test"}


LEVELS = {name: (lambda t, name=name: normalize(t, name)) for name in ("notone", "flat", "skel")}


def main():
    rows = []
    for corpus, subset in SUBSETS.items():
        man = pd.read_csv(ROOT / f"data/manifests/eval/{corpus}.csv", keep_default_na=False)
        for model in MODELS:
            pred = pd.read_csv(ROOT / f"results/inference/{model}/{corpus}.csv", keep_default_na=False)
            d = man.merge(pred[["utt_id", "prediction"]], on="utt_id")
            d = d[(d.exclude_reason == "") & (d.split_v0 == subset)]
            row = dict(corpus=corpus, subset=subset, model=model, n_utt=len(d))
            for name, f in LEVELS.items():
                refs, hyps = d.reference.map(f), d.prediction.map(f)
                n_words = sum(len(r.split()) for r in refs)
                word_err = sum(edit_distance(r.split(), h.split()) for r, h in zip(refs, hyps))
                refs_ns, hyps_ns = refs.str.replace(" ", ""), hyps.str.replace(" ", "")
                char_err = sum(edit_distance(r, h) for r, h in zip(refs_ns, hyps_ns))
                row[f"WER_{name}"] = round(100 * word_err / n_words, 1)
                row[f"CER_nospace_{name}"] = round(100 * char_err / refs_ns.str.len().sum(), 1)
                row[f"exact_{name}"] = round(100 * (refs_ns == hyps_ns).mean(), 1)
            rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "results/evaluation/ortho_sensitivity.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
