#!/usr/bin/env python3
"""Zero-shot inference: one model, one or both corpora, one CSV per (model, corpus).

  python3 scripts/inference/run_inference.py --model mms --corpus zenodo pangloss
  python3 scripts/inference/run_inference.py --model whisper-large-v3-turbo --corpus pangloss --limit 10   # pilot

Output: results/inference/<model>/<corpus>.csv  (utt_id, audio_path, duration_s, reference, prediction,
detected_language, n_chunks, inference_time_s, error) and <corpus>.meta.json (config, versions, GPU, timing).
Interrupted runs resume where they stopped. Delete the CSV to start over.
"""
import argparse

import backends
from common import run

MODELS = {
    "omni-llm-7b": lambda: backends.Omnilingual("omniASR_LLM_7B_v2"),
    "omni-ctc-1b": lambda: backends.Omnilingual("omniASR_CTC_1B_v2"),
    "mms": lambda: backends.MMS("facebook/mms-1b-all", "ddn"),
    "whisper-large-v3": lambda: backends.Whisper("openai/whisper-large-v3"),
    "whisper-large-v3-turbo": lambda: backends.Whisper("openai/whisper-large-v3-turbo"),
    "chirp3": lambda: backends.Chirp3(),
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True, choices=MODELS)
    ap.add_argument("--corpus", nargs="+", default=["zenodo", "pangloss"], choices=["zenodo", "pangloss"])
    ap.add_argument("--limit", type=int, help="only the first N utterances (pilot run)")
    args = ap.parse_args()
    backend = MODELS[args.model]()
    for corpus in args.corpus:
        run(backend, corpus, args.limit)
