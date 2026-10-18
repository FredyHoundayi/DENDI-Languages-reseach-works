#!/usr/bin/env python3
"""Build the per-corpus evaluation manifests used by every inference run.

Writes data/manifests/eval/{zenodo,pangloss}.csv with one row per utterance:
  utt_id, audio_path, duration_s, reference, split_v0, exclude_reason

Inference runs on ALL rows; `split_v0` and `exclude_reason` let the evaluation
report full-corpus and test-only scores from the same predictions.
`split_v0` is the proposal in data/audit/PHASE1_READINESS.md §3, not a frozen split.

Run from the project root after organize_data.py:  python3 scripts/build_eval_manifests.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "manifests" / "eval"
COLUMNS = ["utt_id", "audio_path", "duration_s", "reference", "split_v0", "exclude_reason"]

PANGLOSS_DEV_TALES = {"conte1", "conte5"}


def zenodo(df: pd.DataFrame) -> pd.DataFrame:
    z = df[df.source == "zenodo_6591186"].copy()
    z["split_v0"] = z.gender.map({"female": "test", "male": "train"})
    # Different numbers sharing one transcript (e.g. 100,000 and 100,000,000): at least one is wrong.
    dup = z.duplicated(["speaker_id", "text_norm_v0"], keep=False)
    z["exclude_reason"] = dup.map({True: "duplicate_transcript_for_different_numbers", False: ""})
    return z


def pangloss(df: pd.DataFrame) -> pd.DataFrame:
    p = df[df.source == "pangloss_dendi"].copy()
    tale = p.utt_id.str.split("_").str[1]
    p["split_v0"] = tale.map(lambda t: "dev" if t in PANGLOSS_DEV_TALES else "test")
    p["exclude_reason"] = ""
    return p


if __name__ == "__main__":
    df = pd.read_csv(ROOT / "data" / "manifests" / "all_utterances.csv", keep_default_na=False)
    df["reference"] = df.text_clean
    OUT.mkdir(parents=True, exist_ok=True)
    for name, sub in (("zenodo", zenodo(df)), ("pangloss", pangloss(df))):
        sub[COLUMNS].to_csv(OUT / f"{name}.csv", index=False)
        counts = sub.groupby(["split_v0", sub.exclude_reason != ""]).size().to_dict()
        print(f"{name}: {len(sub)} utterances {counts}")
