#!/usr/bin/env python3
"""Peak GPU memory of one model, measured on the worst-case inputs of both corpora.

  python3 scripts/inference/measure_gpu_memory.py --model mms      # one model per process

Inputs: the longest utterance of each corpus plus 10 others per corpus (fixed seed), batch size 1,
same backends and settings as run_inference.py. Records, in results/resources/gpu_memory/<model>.json:
  - after_load_*: memory once the model is on the GPU
  - peak_allocated / peak_reserved: torch.cuda peak statistics during inference
  - nvidia_smi_peak: total device memory sampled every 50 ms (includes the CUDA context
    and any allocation outside torch's caching allocator) -- the figure to size a GPU with.
"""
import argparse
import json
import subprocess
import threading
import time

import torch

from common import RESULTS, load_audio, load_manifest
from run_inference import MODELS

MiB = 1024 ** 2


class SmiSampler(threading.Thread):
    def __init__(self, interval=0.05):
        super().__init__(daemon=True)
        self.interval, self.peak, self.stop = interval, 0, threading.Event()

    def run(self):
        while not self.stop.is_set():
            out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                                 capture_output=True, text=True).stdout.split()
            if out:
                self.peak = max(self.peak, int(out[0]))
            time.sleep(self.interval)


def inputs():
    rows = []
    for corpus in ("zenodo", "pangloss"):
        m = load_manifest(corpus)
        longest = m.loc[m.duration_s.idxmax()]
        rows += [(corpus, longest)] + [(corpus, r) for _, r in m.drop(longest.name).sample(10, random_state=0).iterrows()]
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=[m for m in MODELS if m != "chirp3"])
    args = ap.parse_args()
    smi = SmiSampler()
    smi.start()
    torch.cuda.reset_peak_memory_stats()
    t0 = time.perf_counter()
    backend = MODELS[args.model]()
    torch.cuda.synchronize()
    load_s = time.perf_counter() - t0
    after_alloc, after_res = torch.cuda.memory_allocated(), torch.cuda.memory_reserved()
    after_smi = smi.peak
    torch.cuda.reset_peak_memory_stats()
    per_input = []
    for corpus, r in inputs():
        torch.cuda.reset_peak_memory_stats()
        _, _, n_chunks = backend.transcribe(load_audio(r.audio_path), r)
        torch.cuda.synchronize()
        per_input.append(dict(corpus=corpus, utt_id=r.utt_id, duration_s=float(r.duration_s), n_chunks=n_chunks,
                              peak_allocated_mib=round(torch.cuda.max_memory_allocated() / MiB),
                              peak_reserved_mib=round(torch.cuda.max_memory_reserved() / MiB)))
    time.sleep(0.3)
    smi.stop.set()
    smi.join()
    res = dict(model=backend.name, cli_model=args.model, config=backend.config, versions=backend.versions(),
               gpu=torch.cuda.get_device_name(0), total_mib=round(torch.cuda.get_device_properties(0).total_memory / MiB),
               load_time_s=round(load_s, 1),
               after_load_allocated_mib=round(after_alloc / MiB), after_load_reserved_mib=round(after_res / MiB),
               after_load_nvidia_smi_mib=after_smi,
               peak_allocated_mib=max(p["peak_allocated_mib"] for p in per_input),
               peak_reserved_mib=max(p["peak_reserved_mib"] for p in per_input),
               nvidia_smi_peak_mib=smi.peak,
               worst_input=max(per_input, key=lambda p: p["peak_allocated_mib"]), per_input=per_input)
    out = RESULTS.parent / "resources" / "gpu_memory"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{backend.name}.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
    print(json.dumps({k: v for k, v in res.items() if k not in ("per_input", "config", "versions")}, indent=1))


if __name__ == "__main__":
    main()
