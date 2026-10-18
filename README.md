# Dendi ASR Benchmark

A reproducible Automatic Speech Recognition benchmark for Dendi (ddn). The experimental phase runs from 12 October to 8 November 2026.

## Status (18 Oct 2026)

- ✅ **Data:** both corpora are audited, organised and resampled to 16 kHz, with evaluation manifests.
- ✅ **Phase 1, zero-shot baselines:** done for 5 of the 6 models, each scored separately on each corpus. Chirp 3 is waiting for GCP credentials.
- ⏳ **Phase 2, fine-tuning:** not started.

## Where to look

| Topic | File |
|---|---|
| Protocol and roadmap | `Dendi ASR Benchmark Project Charter and Experimental Protocol.docx`, `Dendi ASR Benchmark Four-Week Research Roadmap.docx` |
| Data layout, licences, manifests | [data/README.md](data/README.md) |
| Data audit and resource survey | [data/audit/DATA_AUDIT.md](data/audit/DATA_AUDIT.md), [data/audit/RESOURCE_SURVEY.md](data/audit/RESOURCE_SURVEY.md), [data/audit/PHASE1_READINESS.md](data/audit/PHASE1_READINESS.md) |
| **Zero-shot results and analysis** | [results/evaluation/ANALYSIS.md](results/evaluation/ANALYSIS.md), [results/evaluation/REPORT.md](results/evaluation/REPORT.md) |
| Raw predictions (one CSV per model × corpus) | [results/inference/](results/inference/) |
| GPU memory at inference | [results/resources/GPU_MEMORY.md](results/resources/GPU_MEMORY.md) |
| Run traces (logs, package versions, hardware, checkpoint hashes) | [results/traces/vm_agh_2026-10-18/](results/traces/vm_agh_2026-10-18/) |
| How to run inference | [scripts/inference/README.md](scripts/inference/README.md) |

## Reproduce

Data setup needs Python 3 with `pandas`, `openpyxl`, `numpy` and `scipy`, plus `ffmpeg` and `curl`:

```bash
bash scripts/download_data.sh
python3 scripts/organize_data.py
python3 scripts/compute_stats.py
python3 scripts/build_eval_manifests.py
```

Inference runs on a GPU machine. Run `scripts/setup_vm.sh` first, then follow [scripts/inference/README.md](scripts/inference/README.md):

```bash
bash scripts/setup_vm.sh hf omni
.venv-hf/bin/python scripts/inference/run_inference.py --model mms
```

Evaluation runs on a CPU (requirements: `envs/requirements-eval.txt`):

```bash
python3 scripts/evaluation/evaluate.py        # writes results/evaluation/
python3 scripts/evaluation/verify_metrics.py  # recomputes every score without jiwer
```

Audio and source archives are not stored in git. `download_data.sh` fetches them and checks them against `data/raw/SHA256SUMS`. The Bible.is audio is copyrighted and is never committed.
