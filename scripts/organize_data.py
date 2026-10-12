#!/usr/bin/env python3
"""Organise the two Dendi speech resources into a common, traceable layout.

Inputs (unchanged, never modified):
  data/raw/zenodo_6591186/   Zenodo record 6591186 (jami_dendi.zip + extraction)
  data/raw/pangloss_dendi/   Pangloss / CNRS Dendi tales (WAV masters + XML)

Outputs:
  data/processed/<source>/...wav   16 kHz, mono, PCM 16-bit, one file per utterance
  data/manifests/*.csv|jsonl       one row per utterance, with provenance

Run from the project root:  python3 scripts/organize_data.py
"""
import csv
import hashlib
import json
import re
import subprocess
import unicodedata
import wave
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
MAN = ROOT / "data" / "manifests"
TARGET_SR = 16000

ZEN = RAW / "zenodo_6591186" / "extracted" / "jami_dendi"
PAN = RAW / "pangloss_dendi"

FIELDS = [
    "utt_id", "source", "license", "doc_id", "segment_id", "speaker_id", "gender", "age",
    "dialect", "speech_style", "audio_path", "orig_audio_path", "orig_sr", "orig_bits",
    "start_s", "end_s", "duration_s", "text_raw", "text_clean", "text_norm_v0",
    "text_norm_v0_notone", "translation_fr", "prompt_id", "audio_md5",
]

# Pangloss marks listener back-channels between box-drawing bars: │nam│, │tô│
BACKCHANNEL = re.compile(r"│[^│]*│")
TONE_MARKS = {"̀", "́", "̂", "̌", "̄", "̰"}  # grave acute circ caron macron tilde-below


def norm_v0(text: str) -> str:
    """PROVISIONAL normalisation (to be validated at kickoff): NFC, lowercase,
    drop punctuation, keep letters + combining diacritics, collapse spaces."""
    t = unicodedata.normalize("NFD", text.lower())
    t = "".join(c if (unicodedata.category(c)[0] in "LM" or c.isspace()) else " " for c in t)
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", t).strip())


def strip_tones(text: str) -> str:
    t = unicodedata.normalize("NFD", text)
    return unicodedata.normalize("NFC", "".join(c for c in t if c not in TONE_MARKS))


def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def wav_info(path: Path):
    with wave.open(str(path)) as w:
        return w.getframerate(), w.getsampwidth() * 8, w.getnframes() / w.getframerate()


def ffmpeg(src: Path, dst: Path, start=None, end=None):
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y"]
    if start is not None:
        cmd += ["-ss", f"{start:.3f}", "-to", f"{end:.3f}"]
    cmd += ["-i", str(src), "-ac", "1", "-ar", str(TARGET_SR), "-sample_fmt", "s16", str(dst)]
    subprocess.run(cmd, check=True)


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def zenodo_rows():
    meta = pd.read_excel(ZEN / "Metadata" / "jami_metadata.xlsx")
    meta.columns = ["speaker_id", "gender", "age", "dialect", "txt", "wav"]
    rows = []
    for m in meta.itertuples():
        sub = "male" if m.gender.strip().lower() == "male" else "female"
        txt = ZEN / "Dataset" / sub / m.txt
        src = ZEN / "Dataset" / sub / m.wav
        assert txt.exists() and src.exists(), (txt, src)
        text = unicodedata.normalize("NFC", txt.read_text(encoding="utf-8").strip())
        stem = Path(m.txt).stem
        utt = f"zen_{sub[0].upper()}_{stem}"
        dst = PROC / "zenodo" / sub / f"{utt}.wav"
        if not dst.exists():
            ffmpeg(src, dst)
        sr, bits, dur = wav_info(src)
        rows.append(dict(
            utt_id=utt, source="zenodo_6591186", license="CC-BY-4.0", doc_id="jami_dendi",
            segment_id=stem, speaker_id=f"zen_{sub}", gender=sub, age=int(m.age),
            dialect="Dendi (Parakou, Benin)", speech_style="read, isolated numerals",
            audio_path=rel(dst), orig_audio_path=rel(src), orig_sr=sr, orig_bits=bits,
            start_s=0.0, end_s=round(dur, 3), duration_s=round(dur, 3),
            text_raw=text, text_clean=text, text_norm_v0=norm_v0(text),
            text_norm_v0_notone=strip_tones(norm_v0(text)), translation_fr="",
            audio_md5=md5(src),
        ))
    return rows


def pangloss_rows():
    src_meta = {}
    for line in (PAN / "sources.tsv").read_text(encoding="utf-8").splitlines():
        oai, title, lic, wav_url, xml_url = line.split("\t")
        src_meta[Path(xml_url).stem] = (oai, title, lic.rsplit("/", 1)[-1])
    rows = []
    for xml in sorted((PAN / "transcriptions").glob("*.xml")):
        doc = xml.stem
        oai, title, lic = src_meta[doc]
        src = PAN / "audio" / f"{doc}.wav"
        sr, bits, _ = wav_info(src)
        tale = doc.rsplit("_", 1)[-1]  # conte1..conte6
        for s in ET.parse(xml).getroot().findall("S"):
            a = s.find("AUDIO")
            start, end = float(a.get("start")), float(a.get("end"))
            raw = unicodedata.normalize("NFC", re.sub(r"\s+", " ", s.findtext("FORM", "")).strip())
            clean = re.sub(r"\s+", " ", BACKCHANNEL.sub(" ", raw)).strip()
            utt = f"pan_{tale}_{s.get('id')}"
            dst = PROC / "pangloss" / tale / f"{utt}.wav"
            if not dst.exists():
                ffmpeg(src, dst, start, end)
            rows.append(dict(
                utt_id=utt, source="pangloss_dendi", license=lic, doc_id=doc,
                segment_id=s.get("id"), speaker_id=f"pan_{tale}_narrator", gender="unknown",
                age="", dialect="Dendi (Karimama, Benin/Niger border)",
                speech_style=f"spontaneous folk tale, 1968 field recording: {title}",
                audio_path=rel(dst), orig_audio_path=rel(src), orig_sr=sr, orig_bits=bits,
                start_s=start, end_s=end, duration_s=round(end - start, 3),
                text_raw=raw, text_clean=clean, text_norm_v0=norm_v0(clean),
                text_norm_v0_notone=strip_tones(norm_v0(clean)),
                translation_fr=re.sub(r"\s+", " ", s.findtext("TRANSL", "")).strip(),
                audio_md5=md5(dst),
            ))
    return rows


def add_prompt_ids(rows):
    """Same normalised text => same prompt_id (reveals shared prompts across speakers)."""
    ids = {}
    for r in rows:
        r["prompt_id"] = ids.setdefault((r["source"], r["text_norm_v0"]), f"p{len(ids):04d}")


def write(rows, name):
    MAN.mkdir(parents=True, exist_ok=True)
    with open(MAN / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)
    with open(MAN / f"{name}.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps({k: r[k] for k in FIELDS}, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    z, p = zenodo_rows(), pangloss_rows()
    add_prompt_ids(z + p)
    write(z, "zenodo")
    write(p, "pangloss")
    write(z + p, "all_utterances")
    print(f"zenodo: {len(z)} utterances, pangloss: {len(p)} utterances")
