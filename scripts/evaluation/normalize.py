"""Text normalisation for Dendi ASR scoring. Applied identically to references and hypotheses.

Four cumulative levels (see data/audit/PHASE1_READINESS.md §4 and results/evaluation/REVIEW.md):

  raw     NFC, lowercase, ℇ→ɛ (encoding error in Pangloss), every character that is not a
          letter, combining mark or digit becomes a space (punctuation, quotes, hyphens),
          spaces collapsed. Tones and all diacritics are kept. PRIMARY level (official score),
          decided 31 Oct 2026: normalisation is limited to case, punctuation and spacing;
          nothing specific to Dendi is substituted, because that would denature the language.
          The levels below are DIAGNOSTIC ONLY: they show where errors come from.
  notone  raw + tone marks removed (grave, acute, circumflex, caron, macron, double acute,
          double grave, breve, combined tone marks) + ɑ→a. Diagnostic.
          ɑ is the Bible/MMS spelling of /a/ (MMS's ddn vocabulary has 202k ɑ for 4k a);
          Dendi has no ɑ/a contrast, so the difference is orthographic, not a recognition error.
          Nasal and phonation marks (tilde above, tilde below, ...) are kept.
  flat    notone + every remaining combining mark removed + ɛ→e, ɔ→o, ɲ→ny, ɳ→n, ɟ→j.
          Orthography-insensitive upper bound: Pangloss (1968) writes e/o where modern
          Dendi spelling writes ɛ/ɔ, so `flat` separates spelling conventions from errors. Diagnostic.
  skel    flat + ay/ey/oy/uy→ai/ei/oi/ui, kp→kw, ŋm→ŋ, ch/c→k, repeated letters collapsed
          (vowel length, gemination). SENSITIVITY ONLY: deliberately too generous (it can merge
          real contrasts such as vowel length), an upper bound on the share of error due to
          spelling conventions; never the paper's main metric. Conventions taken from the
          frequent substitutions (results/evaluation/substitutions/), review of 24 Oct 2026.
"""
import re
import unicodedata

LEVELS = ("raw", "notone", "flat", "skel")
TONE_MARKS = {"̀", "́", "̂", "̌", "̄", "̋", "̏", "̆",
              *map(chr, range(0x1DC4, 0x1DCA))}
FLAT_MAP = str.maketrans({"ɛ": "e", "ɔ": "o", "ɲ": "ny", "ɳ": "n", "ɟ": "j"})


def _raw(text: str) -> str:
    t = unicodedata.normalize("NFD", text.replace("ℇ", "ɛ").lower())
    t = "".join(c if unicodedata.category(c)[0] in "LMN" else " " for c in t)
    # a combining mark left at the start of a word (after removed punctuation) has no base: drop it
    t = re.sub(r"(^|\s)[̀-ͯ᷀-᷿]+", r"\1", t)
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", t).strip())


def _notone(raw: str) -> str:
    t = unicodedata.normalize("NFD", raw)
    t = "".join(c for c in t if c not in TONE_MARKS).replace("ɑ", "a")
    return unicodedata.normalize("NFC", t)


def _flat(notone: str) -> str:
    t = unicodedata.normalize("NFD", notone)
    t = "".join(c for c in t if unicodedata.category(c)[0] != "M").translate(FLAT_MAP)
    return unicodedata.normalize("NFC", t)


def _skel(flat: str) -> str:
    t = re.sub(r"([aeiou])y", r"\1i", flat)
    t = t.replace("kp", "kw").replace("ŋm", "ŋ").replace("ch", "c").replace("c", "k")
    return re.sub(r"(.)\1+", r"\1", t)


def normalize_all(text: str) -> dict[str, str]:
    r = _raw(text)
    n = _notone(r)
    f = _flat(n)
    return {"raw": r, "notone": n, "flat": f, "skel": _skel(f)}


def normalize(text: str, level: str) -> str:
    return normalize_all(text)[level]
