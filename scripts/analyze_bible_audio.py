#!/usr/bin/env python3
"""Acoustic audit of the Bible.is Dendi New Testament audio (fileset DDNBIVN1DA, non-drama).

Reads the extracted MP3s in data/raw/bibleis_DDNBIVN1DA/ (copyrighted, never committed) and
writes only aggregate statistics: data/audit/bible_audio_chapters.csv (one row per chapter).

  python3 scripts/analyze_bible_audio.py

Per chapter: decode errors, duration, stereo redundancy (L/R correlation, side/mid energy),
bandwidth (frequency below which 99% of the energy lies), speech ratio and pauses from a
20 ms energy detector, median F0 of voiced frames (autocorrelation, 60-400 Hz) as a proxy for
the number of narrators, and similarity of the first 6 s to chapter 1 (shared jingle/intro).
"""
import re
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/raw/bibleis_DDNBIVN1DA/Dendi_ddn_BIV_NT_Non-Drama"
OUT = ROOT / "data/audit/bible_audio_chapters.csv"
SR = 16000
FRAME = SR // 50  # 20 ms


def decode(path, sr, channels):
    p = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), "-ac", str(channels),
                       "-ar", str(sr), "-f", "f32le", "-"], capture_output=True)
    x = np.frombuffer(p.stdout, dtype=np.float32)
    return (x.reshape(-1, channels) if channels > 1 else x), p.stderr.decode().strip()


def frames_db(x):
    n = len(x) // FRAME
    rms = np.sqrt((x[: n * FRAME].reshape(n, FRAME) ** 2).mean(1) + 1e-12)
    return 20 * np.log10(rms)


def runs(mask):
    """Lengths (in frames) of consecutive True runs."""
    d = np.diff(np.concatenate([[0], mask.astype(int), [0]]))
    return np.flatnonzero(d == -1) - np.flatnonzero(d == 1)


def median_f0(x):
    """Median F0 (Hz) of voiced 40 ms frames by normalised autocorrelation, on the middle 60 s."""
    mid = len(x) // 2
    seg = x[max(0, mid - 30 * SR): mid + 30 * SR]
    win = 2 * FRAME
    n = len(seg) // win
    fr = seg[: n * win].reshape(n, win)
    fr = fr - fr.mean(1, keepdims=True)
    energy = (fr ** 2).sum(1)
    keep = energy > np.percentile(energy, 50)
    fr = fr[keep]
    spec = np.fft.rfft(fr, 2 * win)
    ac = np.fft.irfft(np.abs(spec) ** 2)[:, :win]
    ac = ac / (ac[:, :1] + 1e-12)
    lo, hi = SR // 400, SR // 60
    lag = lo + ac[:, lo:hi].argmax(1)
    peak = ac[np.arange(len(ac)), lag]
    f0 = SR / lag[peak > 0.5]
    return float(np.median(f0)) if len(f0) > 20 else np.nan, float((peak > 0.5).mean())


def bandwidth(x24, sr=24000):
    seg = x24[: 60 * sr]
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
    c = np.cumsum(spec) / spec.sum()
    return float(np.searchsorted(c, 0.99) * sr / 2 / len(spec))


def intro_signature(x):
    """Log-spectrogram of the first 6 s, flattened, for chapter-to-chapter comparison."""
    seg = x[: 6 * SR]
    n = len(seg) // 512
    s = np.abs(np.fft.rfft(seg[: n * 512].reshape(n, 512) * np.hanning(512), axis=1))
    v = np.log1p(s).ravel()
    return (v - v.mean()) / (v.std() + 1e-9)


def analyze(f):
    m = re.match(r"B(\d+)___(\d+)_(.+?)_*DDNBIVN1DA$", f.stem)
    book_no, chapter, book = int(m[1]), int(m[2]), m[3].strip("_")
    x, err = decode(f, SR, 1)
    st, _ = decode(f, 24000, 2)
    l, r = st[:, 0], st[:, 1]
    mid, side = (l + r) / 2, (l - r) / 2
    db = frames_db(x)
    speech = db > db.max() - 35
    pauses = runs(~speech) * 0.02
    row = dict(
        book_no=book_no, book=book, chapter=chapter, duration_s=round(len(x) / SR, 2),
        decode_error=err[:200],
        lr_correlation=round(float(np.corrcoef(l, r)[0, 1]), 4),
        side_to_mid_db=round(float(10 * np.log10((side ** 2).mean() / ((mid ** 2).mean() + 1e-12) + 1e-12)), 1),
        bandwidth_99_hz=round(bandwidth(mid)),
        peak_dbfs=round(float(20 * np.log10(np.abs(x).max() + 1e-12)), 1),
        clipped_ratio=float((np.abs(x) > 0.999).mean()),
        speech_ratio=round(float(speech.mean()), 3),
        leading_silence_s=round(float(np.argmax(speech) * 0.02), 2),
        pauses_ge_300ms=int((pauses >= 0.3).sum()),
        pauses_ge_700ms=int((pauses >= 0.7).sum()),
        median_pause_s=round(float(np.median(pauses[pauses >= 0.3])) if (pauses >= 0.3).any() else 0, 2),
        **dict(zip(("median_f0_hz", "voiced_ratio"), median_f0(x))),
    )
    return row, intro_signature(x)


def main():
    from multiprocessing import Pool

    files = sorted(SRC.glob("*.mp3"))
    with Pool() as pool:
        results = pool.map(analyze, files, chunksize=4)
    rows, sigs = [r for r, _ in results], [s for _, s in results]
    ref = sigs[0]
    for row, s in zip(rows, sigs):
        k = min(len(ref), len(s))
        row["intro_similarity_to_ch1"] = round(float(np.dot(ref[:k], s[:k]) / k), 3)
    df = pd.DataFrame(rows).sort_values(["book_no", "chapter"])
    df.to_csv(OUT, index=False)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(df)} chapters")


if __name__ == "__main__":
    main()
