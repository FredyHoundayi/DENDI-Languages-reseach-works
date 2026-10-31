# Évaluation zero-shot — Dendi ASR

Généré le 2026-10-31 03:36 UTC par `scripts/evaluation/evaluate.py` (commit `82301c9`). WER/CER en %, IC 95 % par bootstrap sur les énoncés (B=2000, graine 20261018). Niveau principal : **`raw`** (voir `scripts/evaluation/normalize.py`). Découpage : `split_v0` (proposition PHASE1_READINESS §3). Énoncés exclus retirés partout.

**Score officiel = `raw`** : normalisation minimale (minuscules, ponctuation retirée, espaces nettoyés, Unicode NFC, correction de l'erreur d'encodage `ℇ`→`ɛ` de Pangloss). Aucun caractère propre au Dendi n'est substitué et les tons sont conservés. Les autres niveaux sont du **diagnostic uniquement**, pour expliquer d'où viennent les erreurs : `notone` (+ tons retirés, `ɑ`→`a`), `flat` (+ autres diacritiques, `ɛ`/`ɔ`→`e`/`o`), `skel` (+ `c`/`k`, `kp`/`kw`, semi-voyelles, longueur ; volontairement trop indulgent). **CER sans espaces** : CER calculé après suppression des espaces (le découpage en mots est ignoré). **Entièrement justes** : % d'énoncés dont l'hypothèse sans espaces est identique à la référence sans espaces (pour Zenodo, % de nombres reconnus en entier).


## Zenodo — nombres (2 locuteurs)


### Sous-ensemble `all` — 656 énoncés, 2990 mots de référence

| Modèle | WER | CER | CER sans espaces | Entièrement justes | Sub | Del | Ins | WER médian / énoncé | Énoncés WER≥100 |
|---|---|---|---|---|---|---|---|---|---|
| omniASR_CTC_1B_v2 | 100.8 [99.6–102.2] | 51.1 [49.1–53.2] | 49.0 [46.8–51.1] | 1.2 [0.5–2.1] | 64.3 | 30.9 | 5.7 | 100.0 | 89.2 |
| mms-1b-all-ddn | 105.7 [103.7–107.9] | 43.0 [41.6–44.6] | 42.2 [40.8–43.5] | 0.3 [0.0–0.8] | 81.8 | 14.0 | 9.9 | 100.0 | 89.6 |
| omniASR_LLM_7B_v2 | 114.5 [111.7–117.7] | 49.9 [47.3–53.0] | 50.8 [48.2–53.9] | 0.0 [0.0–0.0] | 88.4 | 7.0 | 19.1 | 100.0 | 91.6 |
| whisper-large-v3-turbo | 127.6 [118.4–138.8] | 75.9 [66.9–86.6] | 74.5 [65.1–86.2] | 0.3 [0.0–0.8] | 75.3 | 20.6 | 31.8 | 100.0 | 92.1 |
| whisper-large-v3 | 129.1 [110.2–165.4] | 78.3 [62.1–102.6] | 75.9 [60.7–97.4] | 0.2 [0.0–0.5] | 73.9 | 22.0 | 33.2 | 100.0 | 89.6 |

### Sous-ensemble `test` — 328 énoncés, 1495 mots de référence

| Modèle | WER | CER | CER sans espaces | Entièrement justes | Sub | Del | Ins | WER médian / énoncé | Énoncés WER≥100 |
|---|---|---|---|---|---|---|---|---|---|
| omniASR_CTC_1B_v2 | 95.8 [94.1–97.3] | 35.0 [33.6–36.3] | 31.0 [29.6–32.4] | 2.4 [0.9–4.3] | 60.7 | 34.3 | 0.8 | 100.0 | 84.1 |
| whisper-large-v3 | 97.6 [95.2–100.0] | 49.9 [42.5–62.4] | 49.2 [40.6–63.8] | 0.3 [0.0–0.9] | 67.6 | 25.5 | 4.5 | 100.0 | 80.8 |
| mms-1b-all-ddn | 98.9 [97.2–100.7] | 37.3 [36.2–38.3] | 37.8 [36.8–38.7] | 0.3 [0.0–0.9] | 80.9 | 13.7 | 4.3 | 100.0 | 84.1 |
| omniASR_LLM_7B_v2 | 104.5 [102.3–106.5] | 39.6 [38.6–40.7] | 41.0 [40.0–42.1] | 0.0 [0.0–0.0] | 88.4 | 7.3 | 8.8 | 100.0 | 89.3 |
| whisper-large-v3-turbo | 114.0 [99.6–133.6] | 62.1 [50.4–79.2] | 60.7 [49.1–79.1] | 0.6 [0.0–1.5] | 72.2 | 21.0 | 20.9 | 100.0 | 86.3 |

### Sous-ensemble `train` — 328 énoncés, 1495 mots de référence

| Modèle | WER | CER | CER sans espaces | Entièrement justes | Sub | Del | Ins | WER médian / énoncé | Énoncés WER≥100 |
|---|---|---|---|---|---|---|---|---|---|
| omniASR_CTC_1B_v2 | 105.9 [104.0–108.0] | 67.3 [64.2–70.4] | 67.0 [63.8–70.1] | 0.0 [0.0–0.0] | 67.9 | 27.4 | 10.6 | 100.0 | 94.2 |
| mms-1b-all-ddn | 112.4 [109.0–116.3] | 48.8 [46.4–51.5] | 46.5 [44.3–49.0] | 0.3 [0.0–0.9] | 82.7 | 14.4 | 15.4 | 100.0 | 95.1 |
| omniASR_LLM_7B_v2 | 124.6 [119.4–130.7] | 60.2 [55.0–66.5] | 60.6 [55.5–66.9] | 0.0 [0.0–0.0] | 88.5 | 6.8 | 29.4 | 100.0 | 93.9 |
| whisper-large-v3-turbo | 141.2 [131.2–153.6] | 89.6 [77.9–105.4] | 88.2 [75.5–105.5] | 0.0 [0.0–0.0] | 78.3 | 20.1 | 42.7 | 100.0 | 97.9 |
| whisper-large-v3 | 160.6 [123.5–232.7] | 106.7 [78.4–154.7] | 102.7 [77.5–144.1] | 0.0 [0.0–0.0] | 80.1 | 18.5 | 61.9 | 100.0 | 98.5 |

#### Effet de la normalisation (`test`) — WER / CER sans espaces / entièrement justes

| Modèle | `raw` | `notone` | `flat` | `skel` |
|---|---|---|---|---|
| omniASR_CTC_1B_v2 | 95.8 / 31.0 / 2.4 | 95.6 / 29.3 / 2.4 | 93.8 / 26.2 / 3.4 | 89.9 / 18.4 / 6.1 |
| whisper-large-v3 | 97.6 / 49.2 / 0.3 | 97.6 / 48.3 / 0.3 | 95.7 / 46.2 / 0.9 | 92.9 / 33.4 / 1.5 |
| mms-1b-all-ddn | 98.9 / 37.8 / 0.3 | 79.7 / 22.5 / 4.3 | 79.7 / 21.9 / 4.3 | 73.1 / 16.6 / 7.6 |
| omniASR_LLM_7B_v2 | 104.5 / 41.0 / 0.0 | 85.5 / 26.9 / 3.4 | 85.3 / 25.8 / 3.4 | 76.7 / 18.0 / 7.9 |
| whisper-large-v3-turbo | 114.0 / 60.7 / 0.6 | 113.8 / 59.1 / 0.6 | 112.4 / 55.7 / 1.2 | 107.3 / 41.1 / 2.4 |

## Pangloss — contes 1968


### Sous-ensemble `all` — 174 énoncés, 6606 mots de référence

| Modèle | WER | CER | CER sans espaces | Entièrement justes | Sub | Del | Ins | WER médian / énoncé | Énoncés WER≥100 |
|---|---|---|---|---|---|---|---|---|---|
| mms-1b-all-ddn | 99.3 [98.6–100.1] | 64.2 [63.0–65.4] | 73.2 [71.9–74.5] | 0.0 [0.0–0.0] | 77.7 | 20.3 | 1.3 | 100.0 | 60.9 |
| omniASR_CTC_1B_v2 | 99.8 [99.6–100.0] | 63.1 [61.4–64.9] | 68.1 [66.6–69.8] | 0.0 [0.0–0.0] | 58.0 | 41.7 | 0.2 | 100.0 | 88.5 |
| omniASR_LLM_7B_v2 | 101.9 [100.5–104.0] | 63.6 [62.0–65.7] | 72.1 [70.5–74.1] | 0.0 [0.0–0.0] | 79.4 | 20.2 | 2.2 | 100.0 | 87.9 |
| whisper-large-v3 | 142.8 [128.1–160.2] | 125.4 [107.3–146.8] | 138.2 [118.1–162.1] | 0.0 [0.0–0.0] | 72.0 | 27.7 | 43.1 | 100.0 | 93.7 |
| whisper-large-v3-turbo | 230.3 [187.7–275.4] | 206.0 [162.3–255.0] | 217.4 [173.0–268.8] | 0.0 [0.0–0.0] | 78.2 | 21.6 | 130.4 | 100.0 | 95.4 |

### Sous-ensemble `test` — 147 énoncés, 5577 mots de référence

| Modèle | WER | CER | CER sans espaces | Entièrement justes | Sub | Del | Ins | WER médian / énoncé | Énoncés WER≥100 |
|---|---|---|---|---|---|---|---|---|---|
| mms-1b-all-ddn | 99.3 [98.5–100.4] | 64.0 [62.8–65.3] | 72.9 [71.5–74.4] | 0.0 [0.0–0.0] | 77.3 | 20.6 | 1.5 | 100.0 | 59.9 |
| omniASR_CTC_1B_v2 | 99.7 [99.5–100.0] | 62.7 [60.9–64.7] | 67.7 [66.1–69.4] | 0.0 [0.0–0.0] | 58.1 | 41.5 | 0.2 | 100.0 | 86.4 |
| omniASR_LLM_7B_v2 | 101.8 [100.3–104.5] | 63.2 [61.3–65.5] | 71.8 [70.0–74.0] | 0.0 [0.0–0.0] | 79.9 | 19.7 | 2.3 | 100.0 | 85.7 |
| whisper-large-v3 | 147.3 [128.6–167.1] | 131.3 [109.3–154.0] | 144.6 [120.1–169.5] | 0.0 [0.0–0.0] | 72.8 | 26.9 | 47.6 | 100.0 | 92.5 |
| whisper-large-v3-turbo | 234.3 [187.7–285.2] | 201.1 [159.7–246.1] | 209.7 [168.5–255.0] | 0.0 [0.0–0.0] | 79.1 | 20.7 | 134.5 | 100.0 | 94.6 |

### Sous-ensemble `dev` — 27 énoncés, 1029 mots de référence

| Modèle | WER | CER | CER sans espaces | Entièrement justes | Sub | Del | Ins | WER médian / énoncé | Énoncés WER≥100 |
|---|---|---|---|---|---|---|---|---|---|
| mms-1b-all-ddn | 99.0 [98.4–99.6] | 64.9 [62.4–67.6] | 74.7 [71.5–78.4] | 0.0 [0.0–0.0] | 80.0 | 19.0 | 0.1 | 100.0 | 66.7 |
| omniASR_CTC_1B_v2 | 100.0 [100.0–100.0] | 65.0 [60.9–70.1] | 70.5 [65.8–76.2] | 0.0 [0.0–0.0] | 57.5 | 42.5 | 0.0 | 100.0 | 100.0 |
| omniASR_LLM_7B_v2 | 102.1 [100.2–104.8] | 65.9 [62.3–70.0] | 73.9 [69.5–78.8] | 0.0 [0.0–0.0] | 76.9 | 23.1 | 2.1 | 100.0 | 100.0 |
| whisper-large-v3 | 118.8 [100.0–147.9] | 93.3 [68.4–130.0] | 102.6 [74.0–144.2] | 0.0 [0.0–0.0] | 67.8 | 32.2 | 18.8 | 100.0 | 100.0 |
| whisper-large-v3-turbo | 208.6 [117.7–324.5] | 233.2 [98.6–425.8] | 259.5 [108.9–485.5] | 0.0 [0.0–0.0] | 73.3 | 26.7 | 108.6 | 100.0 | 100.0 |

#### Effet de la normalisation (`test`) — WER / CER sans espaces / entièrement justes

| Modèle | `raw` | `notone` | `flat` | `skel` |
|---|---|---|---|---|
| mms-1b-all-ddn | 99.3 / 72.9 / 0.0 | 77.3 / 38.7 / 0.0 | 75.6 / 36.3 / 0.0 | 69.9 / 30.2 / 0.0 |
| omniASR_CTC_1B_v2 | 99.7 / 67.7 / 0.0 | 85.2 / 33.1 / 0.0 | 84.7 / 32.4 / 0.0 | 81.2 / 28.7 / 0.0 |
| omniASR_LLM_7B_v2 | 101.8 / 71.8 / 0.0 | 81.3 / 38.8 / 0.0 | 80.6 / 37.8 / 0.0 | 75.6 / 32.7 / 0.0 |
| whisper-large-v3 | 147.3 / 144.6 / 0.0 | 142.0 / 114.3 / 0.0 | 141.7 / 114.2 / 0.0 | 139.6 / 108.1 / 0.0 |
| whisper-large-v3-turbo | 234.3 / 209.7 / 0.0 | 230.9 / 193.6 / 0.0 | 230.8 / 194.6 / 0.0 | 230.6 / 194.1 / 0.0 |

#### Sensibilité : références avec les réponses de l'auditoire (« nam », « tô ») — `all`, `raw`

| Modèle | WER sans (principal) | WER avec | Δ |
|---|---|---|---|
| mms-1b-all-ddn | 99.3 | 98.8 | -0.4 |
| omniASR_CTC_1B_v2 | 99.8 | 99.7 | -0.1 |
| omniASR_LLM_7B_v2 | 101.9 | 101.0 | -0.8 |
| whisper-large-v3 | 142.8 | 137.1 | -5.7 |
| whisper-large-v3-turbo | 230.3 | 216.5 | -13.8 |

## Diagnostics (énoncés non exclus)

| Modèle | Corpus | Erreurs | Vides | Non-latin | Boucles | Ratio long. médian | Ratio>2 | Langues détectées (top) | RTF | s/énoncé |
|---|---|---|---|---|---|---|---|---|---|---|
| whisper-large-v3 | pangloss | 0 | 0.0 | 1.1 | 21.3 | 0.72 | 12.1 | sw:47%; sn:32%; yo:12%; en:7%; ms:1% | 0.319 | 4.33 |
| whisper-large-v3-turbo | pangloss | 0 | 0.0 | 0.0 | 30.5 | 0.84 | 17.8 | en:76%; sw:18%; id:1%; es:1%; fr:1% | 0.065 | 0.88 |
| mms-1b-all-ddn | pangloss | 0 | 0.0 | 0.0 | 4.6 | 0.82 | 0.0 | ddn:100% | 0.013 | 0.17 |
| omniASR_CTC_1B_v2 | pangloss | 0 | 0.0 | 0.0 | 4.0 | 0.61 | 0.0 | ddn_Latn:100% | 0.020 | 0.28 |
| omniASR_LLM_7B_v2 | pangloss | 0 | 0.0 | 0.0 | 12.1 | 0.82 | 0.6 | ddn_Latn:100% | 0.378 | 5.13 |
| whisper-large-v3 | zenodo | 0 | 0.0 | 17.4 | 1.2 | 1.00 | 5.5 | sw:37%; en:12%; yo:10%; pt:9%; ko:7% | 0.179 | 0.78 |
| whisper-large-v3-turbo | zenodo | 0 | 0.0 | 22.0 | 2.0 | 1.00 | 8.1 | sw:35%; en:19%; ko:9%; ht:7%; pt:6% | 0.070 | 0.31 |
| mms-1b-all-ddn | zenodo | 0 | 0.0 | 0.0 | 0.0 | 1.00 | 2.3 | ddn:100% | 0.015 | 0.07 |
| omniASR_CTC_1B_v2 | zenodo | 0 | 0.0 | 1.1 | 0.5 | 0.67 | 0.8 | ddn_Latn:100% | 0.035 | 0.15 |
| omniASR_LLM_7B_v2 | zenodo | 0 | 0.0 | 0.0 | 0.8 | 1.00 | 4.7 | ddn_Latn:100% | 0.313 | 1.37 |

## Comparaisons appariées (`raw`, WER, sous-ensemble `test`)

Différence A − B en points, IC 95 % bootstrap apparié ; ✱ = IC excluant 0.

| Corpus | A | B | Δ WER | IC 95 % | p |
|---|---|---|---|---|---|
| zenodo | whisper-large-v3 | whisper-large-v3-turbo | -16.5 ✱ | [-36.3, -1.9] | 0.011 |
| zenodo | whisper-large-v3 | mms-1b-all-ddn | -1.3 | [-4.2, 1.4] | 0.335 |
| zenodo | whisper-large-v3 | omniASR_CTC_1B_v2 | 1.8 | [-0.5, 4.3] | 0.129 |
| zenodo | whisper-large-v3 | omniASR_LLM_7B_v2 | -6.9 ✱ | [-9.8, -3.8] | 0.000 |
| zenodo | whisper-large-v3-turbo | mms-1b-all-ddn | 15.1 ✱ | [0.4, 34.9] | 0.035 |
| zenodo | whisper-large-v3-turbo | omniASR_CTC_1B_v2 | 18.3 ✱ | [4.0, 37.8] | 0.001 |
| zenodo | whisper-large-v3-turbo | omniASR_LLM_7B_v2 | 9.6 | [-5.0, 29.1] | 0.286 |
| zenodo | mms-1b-all-ddn | omniASR_CTC_1B_v2 | 3.1 ✱ | [1.1, 5.3] | 0.006 |
| zenodo | mms-1b-all-ddn | omniASR_LLM_7B_v2 | -5.6 ✱ | [-7.7, -3.4] | 0.000 |
| zenodo | omniASR_CTC_1B_v2 | omniASR_LLM_7B_v2 | -8.7 ✱ | [-11.2, -6.1] | 0.000 |
| pangloss | whisper-large-v3 | whisper-large-v3-turbo | -87.0 ✱ | [-137.4, -42.6] | 0.000 |
| pangloss | whisper-large-v3 | mms-1b-all-ddn | 47.9 ✱ | [29.3, 67.6] | 0.000 |
| pangloss | whisper-large-v3 | omniASR_CTC_1B_v2 | 47.5 ✱ | [28.9, 67.2] | 0.000 |
| pangloss | whisper-large-v3 | omniASR_LLM_7B_v2 | 45.5 ✱ | [26.2, 64.8] | 0.000 |
| pangloss | whisper-large-v3-turbo | mms-1b-all-ddn | 134.9 ✱ | [88.7, 185.7] | 0.000 |
| pangloss | whisper-large-v3-turbo | omniASR_CTC_1B_v2 | 134.5 ✱ | [87.9, 185.3] | 0.000 |
| pangloss | whisper-large-v3-turbo | omniASR_LLM_7B_v2 | 132.5 ✱ | [86.6, 182.7] | 0.000 |
| pangloss | mms-1b-all-ddn | omniASR_CTC_1B_v2 | -0.4 | [-1.2, 0.5] | 0.334 |
| pangloss | mms-1b-all-ddn | omniASR_LLM_7B_v2 | -2.5 ✱ | [-5.1, -0.8] | 0.000 |
| pangloss | omniASR_CTC_1B_v2 | omniASR_LLM_7B_v2 | -2.1 ✱ | [-4.7, -0.5] | 0.000 |

### Zenodo : nombres entièrement justes (`raw`, sous-ensemble `test`)

Différence A − B en points de % de nombres reconnus en entier.

| A | B | Δ entièrement justes | IC 95 % | p |
|---|---|---|---|---|
| whisper-large-v3 | whisper-large-v3-turbo | -0.3 | [-1.5, 0.6] | 0.792 |
| whisper-large-v3 | mms-1b-all-ddn | 0.0 | [-0.9, 0.9] | 1.000 |
| whisper-large-v3 | omniASR_CTC_1B_v2 | -2.1 ✱ | [-4.0, -0.6] | 0.013 |
| whisper-large-v3 | omniASR_LLM_7B_v2 | 0.3 | [0.0, 0.9] | 0.732 |
| whisper-large-v3-turbo | mms-1b-all-ddn | 0.3 | [-0.6, 1.5] | 0.773 |
| whisper-large-v3-turbo | omniASR_CTC_1B_v2 | -1.8 ✱ | [-3.4, -0.6] | 0.003 |
| whisper-large-v3-turbo | omniASR_LLM_7B_v2 | 0.6 | [0.0, 1.5] | 0.268 |
| mms-1b-all-ddn | omniASR_CTC_1B_v2 | -2.1 ✱ | [-4.0, -0.6] | 0.011 |
| mms-1b-all-ddn | omniASR_LLM_7B_v2 | 0.3 | [0.0, 0.9] | 0.709 |
| omniASR_CTC_1B_v2 | omniASR_LLM_7B_v2 | 2.4 ✱ | [0.9, 4.3] | 0.001 |

## Fichiers

- `summary.csv` : toutes les métriques (modèle × corpus × sous-ensemble × niveau).
- `pairwise.csv` : comparaisons appariées (WER, CER et entièrement justes, `all` et `test`).
- `ortho_sensitivity.csv` : sensibilité à l'orthographe (`notone` / `flat` / `skel`), revue du 24 octobre.
- `ortho_decomposition.csv` : effet de chaque convention ajoutée une à une, de `raw` à `skel` (diagnostic).
- `diagnostics.csv` : hallucinations, écriture, longueur, langues, efficacité.
- `per_utterance/<modèle>__<corpus>.csv` : chaque énoncé, références et hypothèses normalisées, S/D/I par niveau.
- `alignments/<modèle>__<corpus>.txt` : alignement mot à mot (`raw`) de chaque énoncé.
- `substitutions/<modèle>__<corpus>.csv` : paires référence→hypothèse les plus fréquentes.
- `eval_meta.json` : versions, graine, paramètres, empreintes des fichiers de prédiction.
