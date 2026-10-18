# Traces : runs d'inférence zero-shot du 18 octobre 2026

**Machine :** VM AGH Cloud `my_vm_aghinstance` (Lagos), flavor `gpu.32v100-xc-max`.
- Tesla V100-PCIE 32 Go, pilote NVIDIA 580.178.04
- 32 vCPU, 62 Go de RAM
- Ubuntu 24.04, Python 3.12.3

Le détail matériel est dans `hardware.txt`.

## Contenu

| Fichier | Contenu |
|---|---|
| `logs/setup.log`, `logs/apt.log` | Installation du système et des environnements |
| `logs/pilot_<modèle>.log` | Pilotes (10 énoncés par corpus) |
| `logs/full_<modèle>.log` | Runs complets |
| `logs/full_runs.log` | Code de sortie de chaque run |
| `pip-freeze-hf.txt` | Environnement `.venv-hf` (MMS, Whisper) : torch 2.14.1+cu126, transformers 5.20.1 |
| `pip-freeze-omni.txt` | Environnement `.venv-omni` : torch 2.8.0+cu128, fairseq2 0.6, omnilingual-asr au commit `81f51e2` |
| `hf-model-revisions.txt` | Révision exacte (commit Hugging Face) de MMS et des deux Whisper |
| `model-checkpoints.sha256` | SHA-256 de tous les checkpoints utilisés |
| `model-cache.txt` | Taille des caches de modèles |

## Chronologie

Toutes les heures sont en UTC.

| Heure | Étape | Résultat |
|---|---|---|
| 13:32 | Paquets système (python3-venv, libsndfile1, ffmpeg) | OK. Le miroir Ubuntu avait des fichiers datés dans le futur, contourné avec `Acquire::Check-Date=false` |
| 13:57 | Environnements `hf` et `omni` | OK. `sm_70` (V100) présent dans les deux builds de torch |
| 13:53 | Pilote Whisper large-v3 | OK |
| 14:14 – 14:21 | Whisper large-v3, puis turbo, en complet | OK, 0 erreur |
| 14:23 – 14:24 | MMS, pilote puis complet | OK, 0 erreur |
| ≈ 14:30 | Pilote Omnilingual CTC, **échec n°1** | `libcudart.so.13` introuvable : torchaudio 2.11 (build CUDA 13) installé sans contrainte de version. Corrigé avec `torchaudio==2.8.0` (cu128) |
| — | Pilote Omnilingual CTC, **échec n°2** | `pyarrow` 26 exige numpy 2, alors que fairseq2 impose numpy 1.x. Corrigé avec `pyarrow==20.0.0` |
| — | Pilote Omnilingual CTC, **échec n°3** | `ModelNotKnownError: omniASR_CTC_1B_v2` : le paquet PyPI 0.1.0 ne contient que les cartes v1. Corrigé en installant depuis GitHub au commit `81f51e2` |
| 15:37 – 15:40 | Omnilingual CTC 1B v2, pilote puis complet | OK, 0 erreur |
| 15:40 – 16:41 | Téléchargement du checkpoint LLM 7B v2 (31,2 Go) | Débit de 4 à 10 Mo/s |
| 16:41 | Pilote Omnilingual LLM 7B v2 | OK |
| 18:12 | Omnilingual LLM 7B v2 en complet | OK, 0 erreur |

Les journaux des tentatives n°1 et n°2 ont été écrasés par la suite. Seul le pilote réussi est conservé dans `logs/pilot_omni-ctc-1b.log`. Aucune prédiction des tentatives échouées n'a été gardée.

## À noter pour le papier

- **Les deux Whisper ont été lancés en fp16, et Omnilingual avec son type de données par défaut.** Le V100 n'a pas de bf16 matériel, même si `torch.cuda.is_bf16_supported()` répond True.
- **Le pic de mémoire GPU n'a pas été mesuré pendant ces runs.** Il faudra une courte mesure dédiée pour le tableau des ressources.
- **Les pilotes font partie du run complet.** Les 10 premiers énoncés de chaque CSV viennent du pilote, avec une configuration identique, et le run complet a repris à la suite.
- **Les checkpoints ne sont pas versionnés dans le dépôt**, car ils pèsent plus de 40 Go. Ils restent téléchargeables : URL dans les cartes de modèles, révisions dans `hf-model-revisions.txt`, empreintes dans `model-checkpoints.sha256`.
