# Dendi ASR data

Layout produced on 12 Oct 2026 by `scripts/organize_data.py` and `scripts/compute_stats.py`
(run from the project root). Audit findings are in [audit/DATA_AUDIT.md](audit/DATA_AUDIT.md).

```
data/
├── raw/                          originals, never modified (SHA256SUMS lists checksums)
│   ├── zenodo_6591186/           jami_dendi.zip (MD5 matches Zenodo) + extracted/
│   └── pangloss_dendi/           audio/*.wav (96 kHz masters), transcriptions/*.xml, sources.tsv
├── processed/                    16 kHz, mono, PCM 16-bit, one WAV per utterance
│   ├── zenodo/{female,male}/     zen_F_<n>.wav, zen_M_<prompt-file>.wav
│   └── pangloss/conte1..6/       pan_conteN_<S-id>.wav, cut from the masters on XML timestamps
├── manifests/                    zenodo, pangloss, all_utterances (.csv and .jsonl)
└── audit/                        stats.json, DATA_AUDIT.md
```

## Manifest columns

| Column | Meaning |
|---|---|
| `utt_id` | Unique utterance ID, prefixed `zen_` or `pan_` |
| `source`, `license`, `doc_id`, `segment_id` | Provenance (source record, licence, original file, original segment ID) |
| `speaker_id`, `gender`, `age` | Zenodo: from metadata. Pangloss: one placeholder per tale, gender unknown |
| `audio_path` | Processed 16 kHz file |
| `orig_audio_path`, `orig_sr`, `orig_bits`, `start_s`, `end_s` | Where the audio came from in the raw data |
| `duration_s` | Utterance duration in seconds |
| `text_raw` | Transcript exactly as distributed (Unicode NFC only) |
| `text_clean` | Pangloss: listener back-channels `│nam│`, `│tô│` removed. Zenodo: same as raw |
| `text_norm_v0` | **Provisional** normalisation: lowercase, punctuation removed, diacritics kept |
| `text_norm_v0_notone` | `text_norm_v0` with tone marks and tilde-below removed |
| `translation_fr` | French translation (Pangloss only) |
| `prompt_id` | Same normalised text within a source gives the same ID (shows shared prompts) |
| `audio_md5` | MD5 of the source audio (Zenodo) or the processed segment (Pangloss) |

`text_norm_v0` is a starting point for the normalisation policy due on 14 Oct. It is not the frozen policy.

## Licences

- Zenodo 6591186: **CC-BY-4.0**.
- Pangloss Dendi: **CC-BY-NC-SA-4.0**. Non-commercial use only, and derived data must use the same licence. Check this before releasing any data, derived transcripts or models trained on it.

## Regenerating

Audio is not stored in git (1.2 GB of originals, some files over GitHub's 100 MB limit).
Download it first. `sources.tsv`, `SHA256SUMS`, the manifests and the audit are versioned.

```bash
bash scripts/download_data.sh      # ~1.2 GB, checks SHA256 sums
python3 scripts/organize_data.py   # ~2 min, skips WAVs that already exist
python3 scripts/compute_stats.py
```
