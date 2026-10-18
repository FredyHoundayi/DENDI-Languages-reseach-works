# Inférence zero-shot (phase 1)

Chaque modèle est évalué **séparément sur chaque corpus** :
- `zenodo` : les nombres ;
- `pangloss` : les contes.

On obtient un CSV par couple (modèle, corpus) :

```
results/inference/<modèle>/<corpus>.csv
results/inference/<modèle>/<corpus>.meta.json   # config, versions, GPU, durée (un bloc par exécution)
```

| Colonne | Contenu |
|---|---|
| `utt_id` | Identifiant de l'énoncé |
| `audio_path` | Chemin du WAV 16 kHz (relatif à la racine du projet) |
| `duration_s` | Durée en secondes |
| `reference` | Transcription de référence (`text_clean` : pour Pangloss, les réponses de l'auditoire sont retirées) |
| `prediction` | Sortie brute du modèle, sans normalisation |
| `detected_language` | Langue détectée (Whisper, Chirp 3) ; `ddn` / `ddn_Latn` pour MMS et Omnilingual |
| `n_chunks` | Nombre de morceaux traités (> 1 si l'audio a été découpé) |
| `inference_time_s` | Temps d'inférence de l'énoncé |
| `error` | Message d'erreur si l'énoncé a échoué. La ligne est gardée dans tous les cas |

L'inférence porte sur **tous** les énoncés. Le découpage proposé (`split_v0`) et les exclusions (`exclude_reason`) sont dans `data/manifests/eval/*.csv`. Il suffit de les joindre sur `utt_id` au moment de l'évaluation.

## Les 6 configurations

| `--model` | Checkpoint | Environnement | Remarques |
|---|---|---|---|
| `omni-llm-7b` | `omniASR_LLM_7B_v2`, `ddn_Latn` | omnilingual | ≈ 17 Go de VRAM. Entrées limitées à 40 s : les 2 segments Pangloss trop longs sont découpés sur une pause |
| `omni-ctc-1b` | `omniASR_CTC_1B_v2`, `ddn_Latn` | omnilingual | ≈ 3 Go de VRAM. Même découpage |
| `mms` | `facebook/mms-1b-all`, adaptateur `ddn` | hf | Décodage CTC glouton |
| `whisper-large-v3` | `openai/whisper-large-v3` | hf | Langue détectée automatiquement ; décodage glouton ; long-form au-delà de 30 s |
| `whisper-large-v3-turbo` | `openai/whisper-large-v3-turbo` | hf | Mêmes paramètres |
| `chirp3` | Google `chirp_3`, `language_codes=["auto"]` | chirp | Exploratoire : le dendi n'est pas officiellement pris en charge. API payante |

## Installation sur le serveur GPU

```bash
git clone git@github.com:FredyHoundayi/DENDI-Languages-reseach-works.git && cd DENDI-Languages-reseach-works
bash scripts/download_data.sh && python3 scripts/organize_data.py && python3 scripts/build_eval_manifests.py

python3 -m venv .venv-hf   && .venv-hf/bin/pip install -r envs/requirements-hf.txt
python3 -m venv .venv-omni && .venv-omni/bin/pip install -r envs/requirements-omnilingual.txt
python3 -m venv .venv-gcp  && .venv-gcp/bin/pip install -r envs/requirements-chirp.txt   # seulement pour Chirp 3
```

## Exécution

**1. Pilote** : 10 énoncés par corpus, pour vérifier le chargement, la mémoire et les sorties.

```bash
.venv-hf/bin/python   scripts/inference/run_inference.py --model mms --limit 10
.venv-omni/bin/python scripts/inference/run_inference.py --model omni-ctc-1b --limit 10
```

Relis les CSV du pilote. Si un paramètre change ensuite, **supprime le CSV** avant le run complet, pour ne pas mélanger deux configurations.

**2. Run complet** : il reprend là où le pilote s'est arrêté.

```bash
.venv-hf/bin/python   scripts/inference/run_inference.py --model mms
.venv-hf/bin/python   scripts/inference/run_inference.py --model whisper-large-v3
.venv-hf/bin/python   scripts/inference/run_inference.py --model whisper-large-v3-turbo
.venv-omni/bin/python scripts/inference/run_inference.py --model omni-ctc-1b
.venv-omni/bin/python scripts/inference/run_inference.py --model omni-llm-7b
GOOGLE_CLOUD_PROJECT=<projet> .venv-gcp/bin/python scripts/inference/run_inference.py --model chirp3 --limit 10
```

Par défaut, les deux corpus sont traités. Pour n'en traiter qu'un : `--corpus zenodo` ou `--corpus pangloss`.

Le volume total est de 842 énoncés, soit 88 minutes d'audio par modèle. Pour Chirp 3, lance d'abord le pilote et note le coût dans `meta.json`.
