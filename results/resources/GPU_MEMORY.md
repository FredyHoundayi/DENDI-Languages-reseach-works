# Mémoire GPU à l'inférence

**Mesure du 18 octobre 2026** avec `scripts/inference/measure_gpu_memory.py`.
- Machine : Tesla V100-PCIE 32 Go (32 494 Mio utilisables), VM AGH.
- Mêmes backends et réglages que pour les runs d'inférence, batch de 1.
- Entrées testées : l'énoncé le plus long de chaque corpus (48,1 s pour Pangloss), plus 10 énoncés tirés au hasard par corpus (graine 0).

Le détail par entrée est dans `gpu_memory/<modèle>.json`.

| Modèle | Précision | Chargement | Mémoire après chargement | Pic alloué (torch) | Pic réservé (torch) | **Pic total (nvidia-smi)** |
|---|---|---|---|---|---|---|
| Whisper large-v3 | fp16 | 17 s | 2,9 Gio | 3,2 Gio | 3,5 Gio | **3,9 Gio** |
| Whisper large-v3-turbo | fp16 | 7 s | 1,5 Gio | 1,6 Gio | 1,8 Gio | **2,1 Gio** |
| MMS-1b-all (ddn) | fp32 | 9 s | 3,7 Gio | 4,6 Gio | 5,4 Gio | **5,7 Gio** |
| Omnilingual CTC 1B v2 | défaut du pipeline | 6 s | 1,8 Gio | 2,6 Gio | 2,9 Gio | **3,2 Gio** |
| Omnilingual LLM 7B v2 | défaut du pipeline (demi-précision) | 31 s | 14,6 Gio | 15,5 Gio | 16,6 Gio | **16,9 Gio** |

## Comment lire ces colonnes

- **Pic total (nvidia-smi)** : toute la mémoire occupée sur la carte, contexte CUDA compris (environ 0,3 à 0,5 Gio), relevée toutes les 50 ms. C'est le chiffre qui sert à dimensionner un GPU.
- **Pic alloué** : la mémoire réellement utilisée par les tenseurs.
- **Pic réservé** : la mémoire gardée en réserve par l'allocateur de PyTorch.
- Pour 4 modèles sur 5, le pic est atteint sur le conte le plus long (`pan_conte2_S6`, 48 s). Omnilingual le traite en 2 morceaux, à cause de sa limite de 40 s.

## Conclusions

- **Tous les modèles tiennent sur un GPU de 24 Go en inférence**, y compris le LLM 7B (≈ 17 Gio, ce qui confirme les ≈ 17 Gio annoncés par Meta). Une instance g5 (A10G 24 Go) suffirait.
- **Un GPU de 8 Go suffit pour Whisper turbo, Omnilingual CTC 1B et MMS.**
- **Le LLM 7B occupe 14,6 Gio une fois chargé**, soit environ 2 octets par paramètre. Il tourne donc en demi-précision sur le V100, malgré l'absence de bf16 matériel.
- **Ces chiffres valent pour l'inférence uniquement.** Le fine-tuning demande nettement plus de mémoire (gradients, états de l'optimiseur) et sera mesuré séparément en semaine 2.
