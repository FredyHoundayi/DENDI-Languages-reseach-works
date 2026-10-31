#!/usr/bin/env python3
"""Step-by-step decomposition of the normalisation effect (test subsets only).

Starts from `raw` and adds one spelling convention at a time, so the gain of each step
shows how much of the error that convention explains. Step 2 equals normalize.py's
`notone`, step 3 `flat` and step 7 `skel` (checked utterance by utterance).

  0 raw            case, punctuation  (= raw, official score)
  1 tones          tone marks removed
  2 alpha          ɑ -> a                                        (= notone)
  3 diacritics     other marks removed, ɛ/ɔ -> e/o, ɲ -> ny ...  (= flat)
  4 semivowels     ay/ey/oy/uy -> ai/ei/oi/ui
  5 kp_kw          kp -> kw, ŋm -> ŋ
  6 c_k            ch/c -> k
  7 length         repeated letters collapsed (vowel length, gemination)  (= skel)

For each step: WER, CER, space-free CER (word segmentation ignored) and exact match.
Writes results/evaluation/ortho_decomposition.csv.  Run from the project root:
  python3 scripts/evaluation/ortho_decomposition.py
"""
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize import TONE_MARKS, _flat, _raw, normalize  # noqa: E402
from verify_metrics import edit_distance  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MODELS = ["mms-1b-all-ddn", "omniASR_LLM_7B_v2", "omniASR_CTC_1B_v2", "whisper-large-v3", "whisper-large-v3-turbo"]


def _tones_only(t):
    t = unicodedata.normalize("NFD", t)
    return unicodedata.normalize("NFC", "".join(c for c in t if c not in TONE_MARKS))


STEPS = [
    ("0_raw", _raw),
    ("1_tones", _tones_only),
    ("2_alpha", lambda t: unicodedata.normalize("NFC", t.replace("ɑ", "a"))),  # recompose ɑ̃ -> ã
    ("3_diacritics", _flat),
    ("4_semivowels", lambda t: re.sub(r"([aeiou])y", r"\1i", t)),
    ("5_kp_kw", lambda t: t.replace("kp", "kw").replace("ŋm", "ŋ")),
    ("6_c_k", lambda t: t.replace("ch", "c").replace("c", "k")),
    ("7_length", lambda t: re.sub(r"(.)\1+", r"\1", t)),
]
CHECK = {"2_alpha": "notone", "3_diacritics": "flat", "7_length": "skel"}


def chain(text):
    out, t = {}, text
    for name, f in STEPS:
        t = f(t)
        out[name] = t
    for step, level in CHECK.items():
        assert out[step] == normalize(text, level), (text, step)
    return out


def main():
    rows = []
    for corpus in ("zenodo", "pangloss"):
        man = pd.read_csv(ROOT / f"data/manifests/eval/{corpus}.csv", keep_default_na=False)
        man = man[(man.exclude_reason == "") & (man.split_v0 == "test")]
        refs = [chain(t) for t in man.reference]
        for model in MODELS:
            pred = pd.read_csv(ROOT / f"results/inference/{model}/{corpus}.csv", keep_default_na=False)
            hyp_text = man[["utt_id"]].merge(pred[["utt_id", "prediction"]], on="utt_id").prediction
            hyps = [chain(t) for t in hyp_text]
            for name, _ in STEPS:
                r = [x[name] for x in refs]
                h = [x[name] for x in hyps]
                rn, hn = [x.replace(" ", "") for x in r], [x.replace(" ", "") for x in h]
                rows.append(dict(
                    corpus=corpus, model=model, step=name, n_utt=len(r),
                    WER=round(100 * sum(edit_distance(a.split(), b.split()) for a, b in zip(r, h))
                              / sum(len(a.split()) for a in r), 1),
                    CER=round(100 * sum(edit_distance(a, b) for a, b in zip(r, h)) / sum(len(a) for a in r), 1),
                    CER_nospace=round(100 * sum(edit_distance(a, b) for a, b in zip(rn, hn)) / sum(len(a) for a in rn), 1),
                    exact=round(100 * sum(a == b for a, b in zip(rn, hn)) / len(rn), 1)))
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "results/evaluation/ortho_decomposition.csv", index=False)
    print(out.pivot_table(index=["corpus", "model"], columns="step", values="CER_nospace").to_string())


if __name__ == "__main__":
    main()
