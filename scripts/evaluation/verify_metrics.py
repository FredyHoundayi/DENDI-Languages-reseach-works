#!/usr/bin/env python3
"""Independent check of the WER/CER in results/evaluation/summary.csv.

Recomputes every corpus-level score from the raw prediction CSVs with a separate
Levenshtein implementation (no jiwer) and the shared normaliser, then compares.
  python3 scripts/evaluation/verify_metrics.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize import LEVELS, normalize  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def edit_distance(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def main():
    summary = pd.read_csv(ROOT / "results/evaluation/summary.csv")
    worst = 0.0
    for (model, corpus), _ in summary.groupby(["model", "corpus"]):
        man = pd.read_csv(ROOT / f"data/manifests/eval/{corpus}.csv", keep_default_na=False)
        pred = pd.read_csv(ROOT / f"results/inference/{model}/{corpus}.csv", keep_default_na=False)
        d = man.merge(pred[["utt_id", "prediction"]], on="utt_id")
        d = d[d.exclude_reason == ""]
        for lvl in LEVELS:
            refs = d.reference.map(lambda t: normalize(t, lvl))
            hyps = d.prediction.map(lambda t: normalize(t, lvl))
            we = [edit_distance(r.split(), h.split()) for r, h in zip(refs, hyps)]
            ce = [edit_distance(r, h) for r, h in zip(refs, hyps)]
            nw, nc = refs.str.split().str.len(), refs.str.len()
            for subset in summary[(summary.corpus == corpus)].subset.unique():
                m = (d.split_v0 == subset).to_numpy() if subset != "all" else slice(None)
                wer = pd.Series(we)[m].sum() / nw.to_numpy()[m].sum()
                cer = pd.Series(ce)[m].sum() / nc.to_numpy()[m].sum()
                row = summary[(summary.model == model) & (summary.corpus == corpus) &
                              (summary.subset == subset) & (summary.level == lvl)].iloc[0]
                diff = max(abs(wer - row.WER), abs(cer - row.CER))
                worst = max(worst, diff)
                flag = "OK " if diff < 1e-9 else "DIFF"
                if flag != "OK ":
                    print(f"{flag} {model:24} {corpus:8} {subset:5} {lvl:6} WER {wer:.5f} vs {row.WER:.5f}  CER {cer:.5f} vs {row.CER:.5f}")
    print(f"max absolute difference over all model x corpus x subset x level: {worst:.2e}")
    return 0 if worst < 1e-9 else 1


if __name__ == "__main__":
    sys.exit(main())
