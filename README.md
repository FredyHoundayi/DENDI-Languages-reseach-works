# Dendi ASR Benchmark

A reproducible Automatic Speech Recognition benchmark for Dendi (ddn). The experimental phase runs from 12 October to 8 November 2026.

- Project charter and protocol: `Dendi ASR Benchmark Project Charter and Experimental Protocol.docx`
- Four-week roadmap: `Dendi ASR Benchmark Four-Week Research Roadmap.docx`
- Data layout, manifests and licences: [data/README.md](data/README.md)
- Data audit v1 (statistics and issues to decide on): [data/audit/DATA_AUDIT.md](data/audit/DATA_AUDIT.md)

## Setup

Requires Python 3 with `pandas`, `openpyxl`, `numpy`, `scipy`, plus `ffmpeg` and `curl`.

```bash
bash scripts/download_data.sh
python3 scripts/organize_data.py
python3 scripts/compute_stats.py
```
