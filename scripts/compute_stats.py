#!/usr/bin/env python3
"""Data audit v1: statistics for each source, from the manifests and processed audio.

Run from the project root after organize_data.py:  python3 scripts/compute_stats.py
Writes data/audit/stats.json and prints a summary.
"""
import collections
import json
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "audit"


def audio_qc(path: Path):
    sr, x = wavfile.read(ROOT / path)
    x = x.astype(np.float32) / 32768.0
    frame = sr // 50  # 20 ms
    n = len(x) // frame
    rms = np.sqrt((x[: n * frame].reshape(n, frame) ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    return dict(
        peak=float(np.abs(x).max()),
        clipped_ratio=float((np.abs(x) > 0.999).mean()),
        rms_dbfs=float(20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)),
        silence_ratio=float((db < db.max() - 40).mean()) if n else 1.0,
        lead_sil_s=float(np.argmax(db > db.max() - 40) * 0.02) if n else 0.0,
    )


def describe(s: pd.Series):
    q = s.quantile([0, .1, .25, .5, .75, .9, 1]).round(2)
    return dict(min=q[0], p10=q[.1], p25=q[.25], median=q[.5], mean=round(s.mean(), 2),
                p75=q[.75], p90=q[.9], max=q[1], std=round(s.std(), 2))


def text_stats(df: pd.DataFrame):
    words = [w for t in df.text_norm_v0 for w in t.split()]
    chars = collections.Counter(c for t in df.text_norm_v0 for c in unicodedata.normalize("NFD", t) if not c.isspace())
    vocab = collections.Counter(words)
    return dict(
        n_tokens=len(words), vocab_size=len(vocab), hapax=sum(1 for v in vocab.values() if v == 1),
        vocab_size_notone=len({w for t in df.text_norm_v0_notone for w in t.split()}),
        words_per_utt=describe(df.text_norm_v0.str.split().str.len()),
        chars_per_utt=describe(df.text_norm_v0.str.replace(" ", "").str.len()),
        top_words=vocab.most_common(25),
        char_inventory={f"{c} (U+{ord(c):04X} {unicodedata.name(c, '?')})": n for c, n in chars.most_common()},
        non_ascii_utt_ratio=round(float((df.text_raw.map(lambda t: not t.isascii())).mean()), 3),
    )


def source_stats(df: pd.DataFrame):
    dur = df.duration_s
    st = dict(
        n_utterances=len(df), n_documents=df.doc_id.nunique(),
        total_hours=round(dur.sum() / 3600, 4), total_minutes=round(dur.sum() / 60, 2),
        duration_s=describe(dur),
        utts_over_30s=int((dur > 30).sum()), utts_under_1s=int((dur < 1).sum()),
        orig_sample_rates=df.orig_sr.value_counts().to_dict(),
        orig_bit_depths=df.orig_bits.value_counts().to_dict(),
        licenses=df.license.value_counts().to_dict(),
        speakers={k: dict(n_utts=len(g), minutes=round(g.duration_s.sum() / 60, 2),
                          gender=g.gender.iloc[0]) for k, g in df.groupby("speaker_id")},
        empty_transcripts=int((df.text_norm_v0.str.len() == 0).sum()),
        duplicate_audio_md5=int(df.audio_md5.duplicated(keep=False).sum()),
        duplicate_texts_utts=int(df.text_norm_v0.duplicated(keep=False).sum()),
        n_unique_prompts=df.prompt_id.nunique(),
        per_document={k: dict(n_utts=len(g), minutes=round(g.duration_s.sum() / 60, 2))
                      for k, g in df.groupby("doc_id")},
    )
    st["text"] = text_stats(df)
    qc = pd.DataFrame([audio_qc(p) for p in df.audio_path])
    st["audio_qc"] = dict(
        rms_dbfs=describe(qc.rms_dbfs), peak=describe(qc.peak), silence_ratio=describe(qc.silence_ratio),
        utts_with_clipping=int((qc.clipped_ratio > 0.001).sum()),
        utts_mostly_silent=int((qc.silence_ratio > 0.8).sum()),
        mostly_silent_ids=df.utt_id[qc.silence_ratio.values > 0.8].tolist(),
    )
    return st


if __name__ == "__main__":
    df = pd.read_csv(ROOT / "data" / "manifests" / "all_utterances.csv", keep_default_na=False)
    out = {src: source_stats(g) for src, g in df.groupby("source")}
    z, p = df[df.source == "zenodo_6591186"], df[df.source == "pangloss_dendi"]
    vz = {w for t in z.text_norm_v0_notone for w in t.split()}
    vp = {w for t in p.text_norm_v0_notone for w in t.split()}
    zf, zm = z[z.gender == "female"], z[z.gender == "male"]
    out["cross"] = dict(
        total_utterances=len(df), total_minutes=round(df.duration_s.sum() / 60, 2),
        vocab_overlap_notone=len(vz & vp), vocab_overlap_words=sorted(vz & vp),
        audio_md5_overlap=len(set(z.audio_md5) & set(p.audio_md5)),
        zenodo_prompts_shared_by_both_speakers=len(set(zf.prompt_id) & set(zm.prompt_id)),
        zenodo_female_texts_not_in_male=sorted(set(zf.text_norm_v0) - set(zm.text_norm_v0)),
        zenodo_male_texts_not_in_female=sorted(set(zm.text_norm_v0) - set(zf.text_norm_v0)),
    )
    AUDIT.mkdir(parents=True, exist_ok=True)
    (AUDIT / "stats.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
