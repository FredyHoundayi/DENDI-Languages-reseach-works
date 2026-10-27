# Évaluation zero-shot — Dendi ASR

Généré le 2026-10-27 13:46 UTC par `scripts/evaluation/evaluate.py` (commit `da3dd12`). WER/CER en %, IC 95 % par bootstrap sur les énoncés (B=2000, graine 20261018). Niveau principal : **`notone`** (voir `scripts/evaluation/normalize.py`). Découpage : `split_v0` (proposition PHASE1_READINESS §3). Énoncés exclus retirés partout.

Niveaux : `raw` et `flat` = diagnostic ; `skel` = **test de sensibilité uniquement** (volontairement trop indulgent, borne haute de la part due à l'orthographe ; jamais une métrique principale). **CER sans espaces** : CER calculé après suppression des espaces (le découpage en mots est ignoré). **Entièrement justes** : % d'énoncés dont l'hypothèse sans espaces est identique à la référence sans espaces (pour Zenodo, % de nombres reconnus en entier).


## Zenodo — nombres (2 locuteurs)


### Sous-ensemble `all` — 656 énoncés, 2990 mots de référence

| Modèle | WER | CER | CER sans espaces | Entièrement justes | Sub | Del | Ins | WER médian / énoncé | Énoncés WER≥100 |
|---|---|---|---|---|---|---|---|---|---|
| mms-1b-all-ddn | 90.5 [88.0–93.3] | 29.8 [28.3–31.5] | 26.5 [25.1–28.0] | 3.4 [2.0–4.7] | 65.4 | 14.6 | 10.5 | 100.0 | 59.9 |
| omniASR_LLM_7B_v2 | 95.8 [92.7–99.4] | 38.0 [35.3–41.1] | 36.6 [33.9–39.8] | 1.8 [0.9–2.9] | 69.6 | 7.1 | 19.2 | 100.0 | 57.3 |
| omniASR_CTC_1B_v2 | 100.7 [99.5–102.0] | 50.4 [48.3–52.5] | 47.9 [45.7–50.1] | 1.2 [0.5–2.1] | 64.0 | 30.9 | 5.7 | 100.0 | 89.0 |
| whisper-large-v3-turbo | 127.5 [118.3–138.7] | 75.4 [66.2–86.3] | 73.7 [64.1–85.6] | 0.3 [0.0–0.8] | 75.1 | 20.6 | 31.8 | 100.0 | 92.1 |
| whisper-large-v3 | 129.1 [110.2–165.4] | 78.2 [61.8–103.0] | 75.7 [60.2–97.7] | 0.2 [0.0–0.5] | 73.9 | 22.0 | 33.2 | 100.0 | 89.6 |

### Sous-ensemble `test` — 328 énoncés, 1495 mots de référence

| Modèle | WER | CER | CER sans espaces | Entièrement justes | Sub | Del | Ins | WER médian / énoncé | Énoncés WER≥100 |
|---|---|---|---|---|---|---|---|---|---|
| mms-1b-all-ddn | 79.7 [76.9–82.5] | 24.5 [23.3–25.7] | 22.5 [21.3–23.7] | 4.3 [2.1–6.7] | 61.5 | 13.8 | 4.4 | 100.0 | 50.6 |
| omniASR_LLM_7B_v2 | 85.5 [82.6–88.4] | 27.9 [26.6–29.0] | 26.9 [25.6–28.1] | 3.4 [1.5–5.2] | 69.2 | 7.4 | 8.9 | 100.0 | 53.4 |
| omniASR_CTC_1B_v2 | 95.6 [93.9–97.1] | 33.8 [32.5–35.2] | 29.3 [27.9–30.7] | 2.4 [0.9–4.3] | 60.5 | 34.3 | 0.8 | 100.0 | 84.1 |
| whisper-large-v3 | 97.6 [95.2–100.0] | 49.3 [41.8–62.0] | 48.3 [39.5–63.2] | 0.3 [0.0–0.9] | 67.6 | 25.5 | 4.5 | 100.0 | 80.8 |
| whisper-large-v3-turbo | 113.8 [99.5–133.4] | 61.0 [49.1–78.5] | 59.1 [47.4–77.8] | 0.6 [0.0–1.5] | 71.8 | 21.1 | 20.9 | 100.0 | 86.3 |

### Sous-ensemble `train` — 328 énoncés, 1495 mots de référence

| Modèle | WER | CER | CER sans espaces | Entièrement justes | Sub | Del | Ins | WER médian / énoncé | Énoncés WER≥100 |
|---|---|---|---|---|---|---|---|---|---|
| mms-1b-all-ddn | 101.3 [97.3–105.5] | 35.1 [32.6–37.9] | 30.4 [28.1–33.0] | 2.4 [0.9–4.3] | 69.3 | 15.5 | 16.5 | 100.0 | 69.2 |
| omniASR_CTC_1B_v2 | 105.8 [103.9–107.8] | 66.9 [63.7–70.0] | 66.5 [63.3–69.8] | 0.0 [0.0–0.0] | 67.6 | 27.5 | 10.6 | 100.0 | 93.9 |
| omniASR_LLM_7B_v2 | 106.2 [100.5–112.4] | 48.1 [42.7–54.7] | 46.3 [41.0–52.8] | 0.3 [0.0–0.9] | 69.9 | 6.8 | 29.4 | 100.0 | 61.3 |
| whisper-large-v3-turbo | 141.1 [131.2–153.6] | 89.8 [77.8–105.9] | 88.3 [75.2–106.1] | 0.0 [0.0–0.0] | 78.3 | 20.1 | 42.7 | 100.0 | 97.9 |
| whisper-large-v3 | 160.6 [123.5–232.7] | 107.2 [78.4–156.3] | 103.1 [77.3–145.4] | 0.0 [0.0–0.0] | 80.1 | 18.5 | 61.9 | 100.0 | 98.5 |

#### Effet de la normalisation (`test`) — WER / CER sans espaces / entièrement justes

| Modèle | `raw` | `notone` | `flat` | `skel` |
|---|---|---|---|---|
| mms-1b-all-ddn | 98.9 / 37.8 / 0.3 | 79.7 / 22.5 / 4.3 | 79.7 / 21.9 / 4.3 | 73.1 / 16.6 / 7.6 |
| omniASR_LLM_7B_v2 | 104.5 / 41.0 / 0.0 | 85.5 / 26.9 / 3.4 | 85.3 / 25.8 / 3.4 | 76.7 / 18.0 / 7.9 |
| omniASR_CTC_1B_v2 | 95.8 / 31.0 / 2.4 | 95.6 / 29.3 / 2.4 | 93.8 / 26.2 / 3.4 | 89.9 / 18.4 / 6.1 |
| whisper-large-v3 | 97.6 / 49.2 / 0.3 | 97.6 / 48.3 / 0.3 | 95.7 / 46.2 / 0.9 | 92.9 / 33.4 / 1.5 |
| whisper-large-v3-turbo | 114.0 / 60.7 / 0.6 | 113.8 / 59.1 / 0.6 | 112.4 / 55.7 / 1.2 | 107.3 / 41.1 / 2.4 |

## Pangloss — contes 1968


### Sous-ensemble `all` — 174 énoncés, 6606 mots de référence

| Modèle | WER | CER | CER sans espaces | Entièrement justes | Sub | Del | Ins | WER médian / énoncé | Énoncés WER≥100 |
|---|---|---|---|---|---|---|---|---|---|
| mms-1b-all-ddn | 77.7 [76.0–79.4] | 38.8 [37.4–40.4] | 38.9 [37.3–40.6] | 0.0 [0.0–0.0] | 51.7 | 22.5 | 3.4 | 80.0 | 8.0 |
| omniASR_LLM_7B_v2 | 82.2 [79.8–85.0] | 39.4 [37.4–41.7] | 39.3 [37.2–41.6] | 0.0 [0.0–0.0] | 56.9 | 21.6 | 3.6 | 85.7 | 13.2 |
| omniASR_CTC_1B_v2 | 85.6 [83.7–87.3] | 37.1 [34.8–39.8] | 33.3 [30.9–36.1] | 0.0 [0.0–0.0] | 42.8 | 42.1 | 0.6 | 89.0 | 19.5 |
| whisper-large-v3 | 137.5 [122.4–155.4] | 103.5 [85.1–124.8] | 107.6 [87.1–131.6] | 0.0 [0.0–0.0] | 66.2 | 28.0 | 43.3 | 97.6 | 46.0 |
| whisper-large-v3-turbo | 226.9 [184.6–272.0] | 194.6 [151.5–242.1] | 200.9 [157.2–251.4] | 0.0 [0.0–0.0] | 74.1 | 22.0 | 130.8 | 100.0 | 62.1 |

### Sous-ensemble `test` — 147 énoncés, 5577 mots de référence

| Modèle | WER | CER | CER sans espaces | Entièrement justes | Sub | Del | Ins | WER médian / énoncé | Énoncés WER≥100 |
|---|---|---|---|---|---|---|---|---|---|
| mms-1b-all-ddn | 77.3 [75.6–79.2] | 38.6 [36.9–40.2] | 38.7 [36.9–40.5] | 0.0 [0.0–0.0] | 51.1 | 22.7 | 3.6 | 78.9 | 8.2 |
| omniASR_LLM_7B_v2 | 81.3 [78.6–84.6] | 38.8 [36.5–41.3] | 38.8 [36.4–41.2] | 0.0 [0.0–0.0] | 56.7 | 21.0 | 3.6 | 84.8 | 12.2 |
| omniASR_CTC_1B_v2 | 85.2 [83.1–87.2] | 36.8 [34.3–39.9] | 33.1 [30.5–36.1] | 0.0 [0.0–0.0] | 42.6 | 42.0 | 0.6 | 88.9 | 19.7 |
| whisper-large-v3 | 142.0 [123.1–162.2] | 109.5 [87.4–132.3] | 114.3 [90.0–139.6] | 0.0 [0.0–0.0] | 67.0 | 27.2 | 47.8 | 97.7 | 46.3 |
| whisper-large-v3-turbo | 230.9 [184.5–281.8] | 189.8 [148.4–233.9] | 193.6 [152.8–236.5] | 0.0 [0.0–0.0] | 75.0 | 21.1 | 134.9 | 100.0 | 61.9 |

### Sous-ensemble `dev` — 27 énoncés, 1029 mots de référence

| Modèle | WER | CER | CER sans espaces | Entièrement justes | Sub | Del | Ins | WER médian / énoncé | Énoncés WER≥100 |
|---|---|---|---|---|---|---|---|---|---|
| mms-1b-all-ddn | 79.6 [76.4–82.8] | 40.0 [36.7–43.7] | 39.9 [36.0–44.2] | 0.0 [0.0–0.0] | 55.3 | 21.6 | 2.7 | 80.9 | 7.4 |
| omniASR_LLM_7B_v2 | 87.0 [83.8–89.9] | 43.1 [38.3–48.3] | 42.0 [36.4–47.9] | 0.0 [0.0–0.0] | 58.4 | 24.8 | 3.8 | 88.9 | 18.5 |
| omniASR_CTC_1B_v2 | 87.7 [84.4–90.6] | 38.6 [33.4–45.0] | 34.7 [28.7–41.8] | 0.0 [0.0–0.0] | 44.0 | 43.1 | 0.6 | 90.0 | 18.5 |
| whisper-large-v3 | 113.2 [93.7–143.3] | 70.9 [44.6–109.7] | 70.7 [40.2–115.5] | 0.0 [0.0–0.0] | 61.9 | 32.4 | 19.0 | 96.3 | 44.4 |
| whisper-large-v3-turbo | 205.2 [115.1–320.8] | 220.4 [88.1–410.7] | 240.8 [93.0–461.8] | 0.0 [0.0–0.0] | 69.7 | 26.8 | 108.7 | 100.0 | 63.0 |

#### Effet de la normalisation (`test`) — WER / CER sans espaces / entièrement justes

| Modèle | `raw` | `notone` | `flat` | `skel` |
|---|---|---|---|---|
| mms-1b-all-ddn | 99.3 / 72.9 / 0.0 | 77.3 / 38.7 / 0.0 | 75.6 / 36.3 / 0.0 | 69.9 / 30.2 / 0.0 |
| omniASR_LLM_7B_v2 | 101.8 / 71.8 / 0.0 | 81.3 / 38.8 / 0.0 | 80.6 / 37.8 / 0.0 | 75.6 / 32.7 / 0.0 |
| omniASR_CTC_1B_v2 | 99.7 / 67.7 / 0.0 | 85.2 / 33.1 / 0.0 | 84.7 / 32.4 / 0.0 | 81.2 / 28.7 / 0.0 |
| whisper-large-v3 | 147.3 / 144.6 / 0.0 | 142.0 / 114.3 / 0.0 | 141.7 / 114.2 / 0.0 | 139.6 / 108.1 / 0.0 |
| whisper-large-v3-turbo | 234.3 / 209.7 / 0.0 | 230.9 / 193.6 / 0.0 | 230.8 / 194.6 / 0.0 | 230.6 / 194.1 / 0.0 |

#### Sensibilité : références avec les réponses de l'auditoire (« nam », « tô ») — `all`, `notone`

| Modèle | WER sans (principal) | WER avec | Δ |
|---|---|---|---|
| mms-1b-all-ddn | 77.7 | 78.1 | 0.5 |
| omniASR_LLM_7B_v2 | 82.2 | 82.6 | 0.4 |
| omniASR_CTC_1B_v2 | 85.6 | 86.6 | 1.0 |
| whisper-large-v3 | 137.5 | 132.0 | -5.5 |
| whisper-large-v3-turbo | 226.9 | 213.1 | -13.8 |

## Diagnostics (énoncés non exclus)

| Modèle | Corpus | Erreurs | Vides | Non-latin | Boucles | Ratio long. médian | Ratio>2 | Langues détectées (top) | RTF | s/énoncé |
|---|---|---|---|---|---|---|---|---|---|---|
| whisper-large-v3 | pangloss | 0 | 0.0 | 1.1 | 20.7 | 0.72 | 12.1 | sw:47%; sn:32%; yo:12%; en:7%; ms:1% | 0.319 | 4.33 |
| whisper-large-v3-turbo | pangloss | 0 | 0.0 | 0.0 | 30.5 | 0.84 | 17.8 | en:76%; sw:18%; id:1%; es:1%; fr:1% | 0.065 | 0.88 |
| mms-1b-all-ddn | pangloss | 0 | 0.0 | 0.0 | 3.4 | 0.82 | 0.0 | ddn:100% | 0.013 | 0.17 |
| omniASR_CTC_1B_v2 | pangloss | 0 | 0.0 | 0.0 | 2.9 | 0.61 | 0.0 | ddn_Latn:100% | 0.020 | 0.28 |
| omniASR_LLM_7B_v2 | pangloss | 0 | 0.0 | 0.0 | 9.2 | 0.82 | 0.6 | ddn_Latn:100% | 0.378 | 5.13 |
| whisper-large-v3 | zenodo | 0 | 0.0 | 17.4 | 1.2 | 1.00 | 5.5 | sw:37%; en:12%; yo:10%; pt:9%; ko:7% | 0.179 | 0.78 |
| whisper-large-v3-turbo | zenodo | 0 | 0.0 | 22.0 | 2.0 | 1.00 | 8.1 | sw:35%; en:19%; ko:9%; ht:7%; pt:6% | 0.070 | 0.31 |
| mms-1b-all-ddn | zenodo | 0 | 0.0 | 0.0 | 0.0 | 1.00 | 2.3 | ddn:100% | 0.015 | 0.07 |
| omniASR_CTC_1B_v2 | zenodo | 0 | 0.0 | 1.1 | 0.5 | 0.67 | 0.8 | ddn_Latn:100% | 0.035 | 0.15 |
| omniASR_LLM_7B_v2 | zenodo | 0 | 0.0 | 0.0 | 0.8 | 1.00 | 4.7 | ddn_Latn:100% | 0.313 | 1.37 |

## Comparaisons appariées (`notone`, WER, sous-ensemble `test`)

Différence A − B en points, IC 95 % bootstrap apparié ; ✱ = IC excluant 0.

| Corpus | A | B | Δ WER | IC 95 % | p |
|---|---|---|---|---|---|
| zenodo | whisper-large-v3 | whisper-large-v3-turbo | -16.3 ✱ | [-36.1, -1.7] | 0.012 |
| zenodo | whisper-large-v3 | mms-1b-all-ddn | 17.9 ✱ | [14.9, 20.9] | 0.000 |
| zenodo | whisper-large-v3 | omniASR_CTC_1B_v2 | 2.0 | [-0.3, 4.5] | 0.090 |
| zenodo | whisper-large-v3 | omniASR_LLM_7B_v2 | 12.1 ✱ | [8.9, 15.4] | 0.000 |
| zenodo | whisper-large-v3-turbo | mms-1b-all-ddn | 34.2 ✱ | [19.7, 53.7] | 0.000 |
| zenodo | whisper-large-v3-turbo | omniASR_CTC_1B_v2 | 18.3 ✱ | [3.9, 38.1] | 0.000 |
| zenodo | whisper-large-v3-turbo | omniASR_LLM_7B_v2 | 28.4 ✱ | [13.8, 48.2] | 0.000 |
| zenodo | mms-1b-all-ddn | omniASR_CTC_1B_v2 | -15.9 ✱ | [-18.6, -13.1] | 0.000 |
| zenodo | mms-1b-all-ddn | omniASR_LLM_7B_v2 | -5.8 ✱ | [-9.1, -2.7] | 0.000 |
| zenodo | omniASR_CTC_1B_v2 | omniASR_LLM_7B_v2 | 10.1 ✱ | [7.0, 13.1] | 0.000 |
| pangloss | whisper-large-v3 | whisper-large-v3-turbo | -88.9 ✱ | [-139.2, -44.2] | 0.000 |
| pangloss | whisper-large-v3 | mms-1b-all-ddn | 64.7 ✱ | [46.0, 84.4] | 0.000 |
| pangloss | whisper-large-v3 | omniASR_CTC_1B_v2 | 56.8 ✱ | [37.6, 77.2] | 0.000 |
| pangloss | whisper-large-v3 | omniASR_LLM_7B_v2 | 60.7 ✱ | [41.3, 80.7] | 0.000 |
| pangloss | whisper-large-v3-turbo | mms-1b-all-ddn | 153.6 ✱ | [107.4, 204.2] | 0.000 |
| pangloss | whisper-large-v3-turbo | omniASR_CTC_1B_v2 | 145.7 ✱ | [98.8, 197.1] | 0.000 |
| pangloss | whisper-large-v3-turbo | omniASR_LLM_7B_v2 | 149.6 ✱ | [104.0, 199.4] | 0.000 |
| pangloss | mms-1b-all-ddn | omniASR_CTC_1B_v2 | -7.9 ✱ | [-10.0, -5.6] | 0.000 |
| pangloss | mms-1b-all-ddn | omniASR_LLM_7B_v2 | -4.0 ✱ | [-7.4, -1.3] | 0.002 |
| pangloss | omniASR_CTC_1B_v2 | omniASR_LLM_7B_v2 | 3.9 ✱ | [0.3, 6.8] | 0.035 |

### Zenodo : nombres entièrement justes (`notone`, sous-ensemble `test`)

Différence A − B en points de % de nombres reconnus en entier.

| A | B | Δ entièrement justes | IC 95 % | p |
|---|---|---|---|---|
| whisper-large-v3 | whisper-large-v3-turbo | -0.3 | [-1.5, 0.6] | 0.792 |
| whisper-large-v3 | mms-1b-all-ddn | -4.0 ✱ | [-6.4, -1.8] | 0.000 |
| whisper-large-v3 | omniASR_CTC_1B_v2 | -2.1 ✱ | [-4.0, -0.6] | 0.013 |
| whisper-large-v3 | omniASR_LLM_7B_v2 | -3.0 ✱ | [-5.2, -1.2] | 0.001 |
| whisper-large-v3-turbo | mms-1b-all-ddn | -3.7 ✱ | [-5.8, -1.8] | 0.000 |
| whisper-large-v3-turbo | omniASR_CTC_1B_v2 | -1.8 ✱ | [-3.4, -0.6] | 0.003 |
| whisper-large-v3-turbo | omniASR_LLM_7B_v2 | -2.7 ✱ | [-4.9, -0.9] | 0.006 |
| mms-1b-all-ddn | omniASR_CTC_1B_v2 | 1.8 | [0.0, 3.7] | 0.073 |
| mms-1b-all-ddn | omniASR_LLM_7B_v2 | 0.9 | [-0.9, 2.7] | 0.395 |
| omniASR_CTC_1B_v2 | omniASR_LLM_7B_v2 | -0.9 | [-2.4, 0.3] | 0.255 |

## Fichiers

- `summary.csv` : toutes les métriques (modèle × corpus × sous-ensemble × niveau).
- `pairwise.csv` : comparaisons appariées (WER, CER et entièrement justes, `all` et `test`).
- `ortho_sensitivity.csv` : sensibilité à l'orthographe (`notone` / `flat` / `skel`), revue du 24 octobre.
- `diagnostics.csv` : hallucinations, écriture, longueur, langues, efficacité.
- `per_utterance/<modèle>__<corpus>.csv` : chaque énoncé, références et hypothèses normalisées, S/D/I par niveau.
- `alignments/<modèle>__<corpus>.txt` : alignement mot à mot (`notone`) de chaque énoncé.
- `substitutions/<modèle>__<corpus>.csv` : paires référence→hypothèse les plus fréquentes.
- `eval_meta.json` : versions, graine, paramètres, empreintes des fichiers de prédiction.
