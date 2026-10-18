"""Shared plumbing for zero-shot inference runs: manifests, audio, chunking, output CSVs, run metadata."""
import csv
import json
import platform
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
EVAL_MANIFESTS = ROOT / "data" / "manifests" / "eval"
RESULTS = ROOT / "results" / "inference"
SR = 16000
OUTPUT_FIELDS = ["utt_id", "audio_path", "duration_s", "reference", "prediction",
                 "detected_language", "n_chunks", "inference_time_s", "error"]


def load_manifest(corpus: str, limit: int | None = None) -> pd.DataFrame:
    df = pd.read_csv(EVAL_MANIFESTS / f"{corpus}.csv", keep_default_na=False)
    return df.head(limit) if limit else df


def load_audio(audio_path: str) -> np.ndarray:
    x, sr = sf.read(ROOT / audio_path, dtype="float32")
    assert sr == SR and x.ndim == 1, f"{audio_path}: expected 16 kHz mono, got {sr} Hz, shape {x.shape}"
    return x


def split_on_silence(x: np.ndarray, max_s: float) -> list[np.ndarray]:
    """Deterministically cut audio longer than max_s at the quietest 20 ms frame
    in the last 40% of each window, so chunks stay <= max_s and cuts fall in pauses."""
    frame, max_len = SR // 50, int(max_s * SR)
    chunks, start = [], 0
    while len(x) - start > max_len:
        lo, hi = start + int(0.6 * max_len), start + max_len
        seg = x[lo:hi]
        n = len(seg) // frame
        rms = np.sqrt((seg[: n * frame].reshape(n, frame) ** 2).mean(axis=1))
        cut = lo + int(np.argmin(rms)) * frame + frame // 2
        chunks.append(x[start:cut])
        start = cut
    chunks.append(x[start:])
    return chunks


def done_ids(out_csv: Path) -> set[str]:
    if not out_csv.exists():
        return set()
    return set(pd.read_csv(out_csv, keep_default_na=False).utt_id)


def _gpu() -> str:
    try:
        return subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "none"


def run(backend, corpus: str, limit: int | None = None):
    """Transcribe every manifest row with `backend` and append to results/inference/<model>/<corpus>.csv.

    `backend` provides: name, config (dict), versions() -> dict, and
    transcribe(audio: np.ndarray, row) -> (prediction: str, detected_language: str, n_chunks: int).
    Rows already in the CSV are skipped, so an interrupted run can be resumed.
    """
    out_dir = RESULTS / backend.name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / f"{corpus}.csv"
    rows = load_manifest(corpus, limit)
    skip = done_ids(out_csv)
    todo = rows[~rows.utt_id.isin(skip)]
    print(f"[{backend.name}/{corpus}] {len(todo)} to transcribe, {len(skip)} already done")

    started = datetime.now(timezone.utc).isoformat()
    t0 = time.perf_counter()
    new_file = not out_csv.exists()
    with open(out_csv, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, OUTPUT_FIELDS)
        if new_file:
            w.writeheader()
        for i, r in enumerate(todo.itertuples(), 1):
            pred, lang, n_chunks, err = "", "", 0, ""
            t = time.perf_counter()
            try:
                pred, lang, n_chunks = backend.transcribe(load_audio(r.audio_path), r)
            except Exception as e:  # a failed utterance is logged, never silently dropped
                err = f"{type(e).__name__}: {e}"[:500]
            w.writerow(dict(utt_id=r.utt_id, audio_path=r.audio_path, duration_s=r.duration_s,
                            reference=r.reference, prediction=" ".join(pred.split()),
                            detected_language=lang, n_chunks=n_chunks,
                            inference_time_s=round(time.perf_counter() - t, 3), error=err))
            f.flush()
            if i % 25 == 0 or i == len(todo):
                print(f"  {i}/{len(todo)}  last: {r.utt_id} -> {pred[:60]!r} {err}")

    meta = dict(model=backend.name, corpus=corpus, config=backend.config, versions=backend.versions(),
                started_utc=started, wall_time_s=round(time.perf_counter() - t0, 1),
                n_transcribed_this_run=len(todo), limit=limit,
                host=platform.node(), python=platform.python_version(), gpu=_gpu())
    meta_path = out_dir / f"{corpus}.meta.json"
    history = json.loads(meta_path.read_text()) if meta_path.exists() else []
    meta_path.write_text(json.dumps(history + [meta], indent=2, ensure_ascii=False))
    print(f"[{backend.name}/{corpus}] wrote {out_csv.relative_to(ROOT)}")
