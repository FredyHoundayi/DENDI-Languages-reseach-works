# Phase 2 : adaptation des modèles au Dendi

**Proposition du 31 octobre 2026, à valider.** Ce plan fait suite à la décision de normalisation stricte et à deux études menées le même jour : une revue de littérature (30 sources vérifiées) et une étude de faisabilité technique (checkpoints et code inspectés). Les références numérotées [n] sont en fin de document.

## 1. Ce que dit la recherche

### Le pré-entraînement continu (CPT)

C'est la poursuite de l'apprentissage auto-supervisé d'un encodeur wav2vec2 sur de l'audio Dendi non transcrit. Elle fonctionne, mais sous conditions :

| Audio non transcrit | Gain observé dans la littérature |
|---|---|
| < 10 h | faible ou nul ; peut même dégrader [2, 7, 12] |
| ≈ 10 h | mesurable : −19 % de WER relatif, avec 1 h de fine-tuning [4] |
| 70–200 h, sources variées | fiable : −8 à −28 % de WER relatif [1, 3, 4] |

1. **La diversité compte autant que le volume.** De la lecture homogène seule ne suffit pas ; il faut des journaux, de la parole spontanée, plusieurs voix [4, 12]. Une langue proche peut compléter la cible (10 h + 60 h d'une langue sœur ≈ 70 h de la cible) [4]. Pour nous, ce serait le **zarma**.
2. **Le CPT sur la Bible.is serait presque inutile.** Le pré-entraînement de MMS inclut déjà l'audio du Nouveau Testament de 1 362 langues [11]. Re-pré-entraîner sur des données déjà vues n'apporte presque rien [4].
3. **Le CPT ne réglera probablement pas les tons.** Les cibles de wav2vec2 sont quantifiées, et la quantification perd l'information tonale [25, 26]. Les tons s'apprennent au fine-tuning, avec des transcriptions tonales cohérentes [27, 28].
4. **Risques connus :** l'effondrement du codebook et l'oubli catastrophique. Les parades publiées sont un learning rate faible (≈ 1e-4) et le mélange avec une autre langue (« data replay ») [1, 12, 14].

### Le pseudo-étiquetage

On transcrit automatiquement l'audio brut, puis on entraîne sur ces transcriptions. **Notre modèle de départ est trop faible pour ça** : 35 à 63 % de CER en zero-shot. Les succès publiés partent d'environ 10 à 20 % de CER. Il faut donc **d'abord un premier fine-tuning supervisé** [2, 12, 21].

### Ce qui a le mieux marché pour le zarma, langue sœur du Dendi (SALAN, LREC 2026)

Les sorties de MMS ont servi de **pré-annotation, corrigée à la main**. L'**apprentissage actif** a choisi les segments à corriger. Environ 5 h corrigées ont fait passer le WER de 30,7 à 25,3 % [6].

## 2. Ce qui est techniquement possible

| | MMS | Omnilingual |
|---|---|---|
| Checkpoint pour le CPT | `facebook/mms-1b`, `mms-300m` (quantizer présent ✅) | `omniASR_W2V_300M/1B` (quantizer présent ✅) |
| Code de CPT | Script HF `run_wav2vec2_pretraining_no_trainer.py` (supprimé de transformers le 13 oct., disponible en v5.19.0), avec 4 corrections | Recette `wav2vec2/ssl` de fairseq2 ≥ 0.7 ; notre environnement est en 0.6, donc portage nécessaire (non testé) |
| Après le CPT | **Un nouveau fine-tuning CTC complet est nécessaire** : l'adaptateur `ddn` actuel ne fonctionne plus | **Une nouvelle tête CTC est nécessaire** (recette `ctc-from-encoder`) : le fine-tuning multilingue de CTC 1B v2 est perdu |
| Fine-tuning direct, sans CPT | Adaptateur seul, initialisé depuis `ddn` : < 2 GPU-h | `ctc-finetune` depuis CTC 1B v2 : 3 à 10 A100-h |
| Licence | CC-BY-NC (non commercial) | **Apache-2.0** |

**Le coût caché du CPT :** il oblige à repartir de l'encodeur brut. On perd tout l'apprentissage supervisé que Meta a fait sur plus de 1 000 langues, Dendi compris (32,2 h pour Omnilingual). Pour Omnilingual, l'article montre même qu'aux tailles 300M et 1B, un fine-tuning parti du checkpoint CTC bat un fine-tuning parti de l'encodeur brut [16]. **Le CPT doit d'abord rattraper ce handicap avant d'apporter quoi que ce soit.**

### Calcul (estimations)

| Tâche | A100-heures |
|---|---|
| CPT 300M sur 20 à 100 h d'audio | ≈ 20–60 |
| CPT 1B sur 20 à 100 h d'audio | ≈ 40–120 (5–15 h sur 8×A100) |
| Fine-tuning CTC 1B sur 10–20 h | ≈ 3–10 |
| Fine-tuning MMS adaptateur seul | ≤ 2 |

Le V100 actuel est 2 à 3 fois plus lent et n'a pas de bf16. **Il convient pour le fine-tuning et les pilotes, pas pour le CPT d'un modèle 1B.**

## 3. Recommandation

**Ne pas commencer par le CPT.** Commencer par le fine-tuning supervisé, et ne garder le CPT que comme expérience ultérieure, sous conditions (§ 4, E3).

Trois raisons :
1. Sans données transcrites d'entraînement, le CPT ne peut de toute façon pas être évalué : il faut un fine-tuning après.
2. Nos meilleurs modèles ont déjà été entraînés sur du Dendi. Le CPT les ferait repartir de plus loin.
3. L'audio dont on dispose en quantité (la Bible) est justement celui que les modèles ont déjà vu.

## 4. Plan d'expériences

Toutes les expériences utilisent **les mêmes jeux de test** (test-zenodo, test-pangloss), le **score strict**, et des données d'entraînement qui ne contiennent **jamais** un énoncé, un texte ou un enregistrement des tests.

| ID | Expérience | Données | Modèle | Ce qu'elle mesure | Prérequis |
|---|---|---|---|---|---|
| E0 | Zero-shot | — | les 5 modèles | Référence | ✅ fait |
| **E1** | Fine-tuning supervisé | Données transcrites d'entraînement (vague 1 ≈ 2 h, puis 5 h, puis 10 h) | **Omnilingual CTC 1B v2** (`ctc-finetune`) | Gain du fine-tuning ; courbe d'apprentissage | Données transcrites |
| E2 | Fine-tuning de l'adaptateur seul | Mêmes données | MMS (adaptateur initialisé depuis `ddn`) | Référence peu coûteuse ; piste recherche (licence NC) | Idem |
| E3 | CPT puis fine-tuning | ≥ 10 h (idéalement ≥ 50 h) d'audio Dendi **varié et jamais vu par les modèles**, + zarma en « replay » ; puis les mêmes données qu'E1 | `omniASR_W2V_1B` → `ctc-from-encoder` (pilote 300M d'abord) | Apport du CPT, **à comparer à E1** | Inventaire et droits de l'audio ; A100 ; portage de la recette SSL |
| E4 | Pseudo-étiquetage | Audio non transcrit, transcrit par le modèle d'E1, filtré (confiance, accord sous dropout, ≈ 50 % gardé), mélangé aux données transcrites | Modèle d'E1 | Apport de l'audio brut sans CPT | E1 terminé, avec un CER nettement meilleur que le zero-shot |
| E5 | Pré-annotation et correction (SALAN) | Sorties du modèle d'E1 corrigées par un locuteur, segments choisis par apprentissage actif (perte CTC) | Modèle d'E1 | Meilleur rapport gain / effort selon la littérature | Un locuteur disponible pour corriger |

**Ordre recommandé : E1 + E2, puis E5 ou E4, puis E3** si l'audio non transcrit dépasse le seuil de diversité et de volume.

## 5. Ce qui bloque, et qui décide

| Blocage | Qui décide | Effet |
|---|---|---|
| **Aucune donnée transcrite d'entraînement** pour l'instant : réponse FCBH et Bibles International en attente, collecte pas commencée | Équipe | Bloque E1, E2, E4, E5, et donc l'évaluation d'E3 |
| **Inventaire de l'audio brut** (sources, heures, droits) : la Bible ne compte pas pour le CPT | Équipe | Conditionne E3 |
| **Droits sur l'audio SRTB et YouTube** pour l'entraînement | Équipe, avec les ayants droit | Conditionne la principale source variée pour E3 et E4 |
| **Notation tonale cible et conversion orthographique** du texte d'entraînement (Bible → orthographe cible), validées par un locuteur | Équipe et locuteur | Sans elles, les modèles apprennent l'orthographe de la Bible (`ɑ`, sans tons) et restent pénalisés au score strict |
| **GPU A100/H100** pour le CPT 1B | Équipe | Conditionne E3 (le V100 suffit pour E1, E2 et les pilotes) |

## 6. Ce qu'on peut faire dès maintenant, sans attendre

1. **Pipeline de fine-tuning E1 et E2**, testé techniquement sur quelques fichiers sur le V100. On n'en rapporte aucun résultat.
2. **Pipeline de préparation de l'audio brut :**
   - segmentation par détection de parole ;
   - identification de la langue (MMS-LID) pour écarter le français et l'arabe ;
   - suppression des doublons ;
   - **exclusion de toute source des tests** ;
   - rapport d'inventaire (heures, locuteurs, qualité).
3. **Pilote technique du CPT** : portage de la recette SSL de fairseq2 (ou du script HF v5.19.0), puis quelques centaines de pas sur 1 h d'audio avec `omniASR_W2V_300M`. Le but est de vérifier que la perte baisse et que le codebook ne s'effondre pas.
4. **Ébauche de la table de conversion orthographique et tonale**, à faire relire par un locuteur.

## 7. Décisions à valider

| ID | Proposition | Validé ? |
|---|---|---|
| P1 | Le fine-tuning supervisé (E1, E2) passe avant le CPT | ☐ |
| P2 | Le CPT (E3) n'est lancé qu'avec ≥ 10 h (idéalement ≥ 50 h) d'audio Dendi varié, jamais vu par les modèles et dont les droits sont clairs ; **la Bible.is en est exclue** | ☐ |
| P3 | Le CPT part d'Omnilingual W2V (licence Apache-2.0), avec un pilote 300M avant le 1B, et du zarma en « replay » | ☐ |
| P4 | Le pseudo-étiquetage (E4) n'est lancé qu'après E1 | ☐ |
| P5 | La collecte suit le modèle SALAN : pré-annotation par le modèle d'E1, correction par un locuteur, apprentissage actif (E5) | ☐ |
| P6 | Les tâches du § 6 commencent maintenant | ☐ |

## Références

1. Nowakowski et al. 2023 (Ainu) : https://arxiv.org/abs/2301.07295
2. DeHaven & Billa 2022 : https://arxiv.org/abs/2207.00659
3. Lam-Yee-Mui et al. 2023 : https://www.isca-archive.org/interspeech_2023/lamyeemui23_interspeech.pdf
4. San et al. 2024 : https://arxiv.org/abs/2402.02302
5. Hsu et al. 2021, Robust wav2vec 2.0 : https://arxiv.org/abs/2104.01027
6. SALAN (zarma), LREC 2026 : https://aclanthology.org/2026.lrec-1.460/
7. Bartelds et al. 2023 : https://arxiv.org/abs/2305.10951
11. MMS : https://arxiv.org/abs/2305.13516
12. Paraskevopoulos et al. 2024 (M2DS2) : https://arxiv.org/abs/2301.00304
14. CASTLE : https://arxiv.org/abs/2206.09783
16. Omnilingual ASR : https://arxiv.org/abs/2511.09690
21. Lugosch et al. 2022 : https://arxiv.org/abs/2111.00161
25. Osakuade & King 2024 : https://arxiv.org/abs/2410.19935
26. Lexical tone is hard to quantize : https://arxiv.org/abs/2604.07467
27. Macaire et al. 2021 : https://halshs.archives-ouvertes.fr/halshs-03475443
28. Coto-Solano 2021 : https://aclanthology.org/2021.americasnlp-1.20

Code et checkpoints :
- fairseq2, recette SSL : https://github.com/facebookresearch/fairseq2/tree/v0.7.0/recipes/wav2vec2/ssl
- Recettes Omnilingual : https://github.com/facebookresearch/omnilingual-asr/tree/main/workflows/recipes/wav2vec2/asr
- Adaptateurs MMS : https://huggingface.co/blog/mms_adapters
- Suppression des scripts d'exemple dans transformers : https://github.com/huggingface/transformers/pull/49357
