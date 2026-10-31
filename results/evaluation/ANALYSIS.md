# Analyse de l'évaluation zero-shot (phase 1)

Version du 31 octobre 2026. Elle remplace celle du 18 octobre, qui utilisait `notone` comme niveau principal.

**Source des chiffres :** [REPORT.md](REPORT.md), `summary.csv`, `pairwise.csv` et `ortho_decomposition.csv`.
- WER et CER sont en %, sur le sous-ensemble `test`, sauf mention contraire.
- Les IC sont à 95 %, par bootstrap sur les énoncés (B = 2000).
- Découpage : `split_v0`.

**Vérification indépendante :** `scripts/evaluation/verify_metrics.py` recalcule les 120 scores (modèle × corpus × sous-ensemble × niveau) avec une distance d'édition écrite séparément, sans `jiwer`. Écart maximal : **4×10⁻¹⁶**.

## 0. Décision de normalisation (31 octobre)

**Le score officiel utilise une normalisation minimale** (niveau `raw`) :
- minuscules ;
- ponctuation retirée ;
- espaces nettoyés ;
- deux corrections techniques sans effet sur la langue : la forme Unicode NFC (une même lettre accentuée peut être codée de deux façons) et l'erreur d'encodage `ℇ`→`ɛ` de Pangloss.

**Aucun caractère propre au Dendi n'est substitué, et les tons sont conservés.** Raison : en Dendi, les tons distinguent des mots, et remplacer des caractères spéciaux dénature la langue. Un score qui les efface récompenserait un modèle qui ignore une partie de la langue.

Les niveaux `notone`, `flat` et `skel` restent calculés, mais **uniquement comme diagnostic**, pour expliquer d'où viennent les erreurs (§ 3). Ils ne servent jamais de score.

## 1. Résultats officiels (`test`, normalisation minimale)

**Pangloss, contes (147 énoncés, 5 577 mots)**

| Modèle | Prend en charge le Dendi | WER | CER | RTF (V100) |
|---|---|---|---|---|
| Omnilingual CTC 1B v2 | ✅ | 99,7 [99,5–100,0] | **62,7** [60,9–64,7] | 0,02 |
| MMS-1b-all (ddn) | ✅ | **99,3** [98,5–100,4] | 64,0 [62,8–65,3] | 0,013 |
| Omnilingual LLM 7B v2 | ✅ | 101,8 [100,3–104,5] | 63,2 [61,3–65,5] | 0,38 |
| Whisper large-v3 | ❌ | 147,3 [128,6–167,1] | 131,3 [109,3–154,0] | 0,32 |
| Whisper large-v3-turbo | ❌ | 234,3 [187,7–285,2] | 201,1 [159,7–246,1] | 0,07 |

**Zenodo, nombres (locutrice F, 328 énoncés, 1 495 mots)**

| Modèle | Prend en charge le Dendi | **Nombres entièrement justes** | WER | CER | RTF (V100) |
|---|---|---|---|---|---|
| **Omnilingual CTC 1B v2** | ✅ | **2,4** [0,9–4,3] | **95,8** [94,1–97,3] | **35,0** [33,6–36,3] | 0,035 |
| MMS-1b-all (ddn) | ✅ | 0,3 [0,0–0,9] | 98,9 [97,2–100,7] | 37,3 [36,2–38,3] | 0,015 |
| Omnilingual LLM 7B v2 | ✅ | 0,0 | 104,5 [102,3–106,5] | 39,6 [38,6–40,7] | 0,31 |
| Whisper large-v3 | ❌ | 0,3 [0,0–0,9] | 97,6 [95,2–100,0] | 49,9 [42,5–62,4] | 0,18 |
| Whisper large-v3-turbo | ❌ | 0,6 [0,0–1,5] | 114,0 [99,6–133,6] | 62,1 [50,4–79,2] | 0,07 |

« Nombres entièrement justes » : la part des nombres dont la transcription, espaces retirés, est identique à la référence. C'est le chiffre qui compte pour un usage réel (dicter un montant, un numéro). Pour les contes, aucun énoncé n'est entièrement juste, quel que soit le modèle : sur des phrases de 35 mots en médiane, cette métrique n'y est pas informative.

## 2. Ce que l'on peut affirmer

1. **Aucun système n'est utilisable tel quel pour le Dendi écrit correctement.** Les modèles Dendi font 96 à 105 % de WER : presque aucun mot n'est écrit exactement comme la référence. Leur CER est de 35 à 40 % sur les nombres et de 63 à 64 % sur les contes. Le meilleur reconnaît 2,4 % des nombres en entier.
2. **En écriture stricte, le WER ne départage presque plus les modèles**, puisque tous sont proches de 100 %. Sur les nombres, l'écart de WER entre Whisper large-v3 et MMS n'est même pas significatif (−1,3 point, IC [−4,2 ; 1,4]). **Le CER, lui, départage clairement** : les modèles Dendi font 10 à 15 points de CER de mieux que Whisper large-v3 (écarts significatifs). Il faut donc rapporter le CER à côté du WER, et le pourcentage de nombres entièrement justes pour Zenodo.
3. **Sur les nombres, Omnilingual CTC 1B est le meilleur sur toutes les métriques**, et tous ses écarts sont significatifs :
   - contre MMS : 3,1 points de WER (IC [1,1 ; 5,3]), 2,3 points de CER (IC [1,0 ; 3,7]), et 2,1 points de plus en nombres entièrement justes ;
   - contre Omnilingual LLM 7B : 8,7 points de WER, 4,6 points de CER, 2,4 points de plus en nombres entièrement justes.

   La raison principale est orthographique : MMS et le LLM écrivent `ɑ` (l'orthographe de la Bible) là où Zenodo écrit `a`, et pas le CTC (§ 3).
4. **Sur les contes, les trois modèles Dendi sont à égalité en CER** (62,7 à 64,0 ; aucun écart significatif). En WER, MMS et le CTC sont à égalité (écart de 0,4 point, non significatif), et le LLM 7B est un peu derrière (2 à 2,5 points, significatif).
5. **Le LLM 7B ne fait mieux nulle part**, pour 9 à 30 fois plus de calcul que le CTC 1B et MMS (RTF 0,31–0,38 contre 0,013–0,035).
6. **Le CER publié par Meta pour le Dendi (2,4 % avec le LLM 7B) ne se transpose pas à nos données.** Il est vérifié dans le tableau par langue publié par Meta (`per_language_results_table_7B_llm_asr.csv`, ligne `ddn_Latn`) : CER 2,4 %, sur leur propre jeu de test, avec **32,2 h de données Dendi à l'entraînement**. C'est plus que les 21,6 h de la Bible.is : Meta disposait donc d'autres données Dendi. Nous obtenons 63 % sur les contes et 40 % sur les nombres. Les causes : les tons et l'orthographe (§ 3), le changement de domaine (Bible contre contes et nombres) et de variété (Karimama 1968, Parakou 2022). Il faut citer ce chiffre comme une référence externe, pas comme un résultat comparable.

## 3. D'où viennent les erreurs ? Décomposition par convention d'écriture (diagnostic)

**Pourquoi le WER réagit beaucoup plus que le CER :** le WER compte les mots. Un seul ton manquant suffit à rendre tout le mot faux. Le CER compte les caractères : le même oubli ne coûte qu'un caractère.

Pour savoir quelle part de l'erreur vient de chaque convention, `scripts/evaluation/ortho_decomposition.py` part du score officiel et **neutralise une convention à la fois**. La baisse du CER à chaque étape mesure ce que coûte cette convention.

**CER (`test`) après chaque étape cumulée :**

| Étape neutralisée | MMS contes | CTC 1B contes | LLM 7B contes | MMS nombres | CTC 1B nombres | LLM 7B nombres | Whisper v3 contes |
|---|---|---|---|---|---|---|---|
| 0. Score officiel (minimal) | 64,0 | 62,7 | 63,2 | 37,3 | 35,0 | 39,6 | 131,3 |
| 1. Tons | 52,2 | 36,8 | 45,7 | 35,9 | 33,8 | 38,6 | 109,5 |
| 2. `ɑ` → `a` | 38,6 | 36,8 | 38,8 | 24,5 | 33,8 | 27,9 | 109,5 |
| 3. Autres diacritiques, `ɛ`/`ɔ` → `e`/`o` | 36,7 | 36,2 | 37,9 | 24,0 | 31,2 | 27,0 | 109,2 |
| 4. Semi-voyelles (`ay` → `ai`) | 35,2 | 35,3 | 36,6 | 24,0 | 31,1 | 27,0 | 108,7 |
| 5. `kp` → `kw`, `ŋm` → `ŋ` | 34,3 | 35,3 | 36,6 | 24,0 | 31,1 | 27,0 | 108,7 |
| 6. `c` → `k` | 34,2 | 34,6 | 35,5 | 22,4 | 27,7 | 23,6 | 107,3 |
| 7. Longueur des voyelles, consonnes doubles | 32,5 | 33,6 | 34,3 | 19,6 | 25,0 | 21,0 | 105,0 |

Les étapes 1 et 2 cumulées correspondent à `notone`, l'étape 3 à `flat`, l'étape 7 à `skel`.

**Ce que ça montre :**

1. **Les tons sont la première cause d'erreur sur les contes.** Les références de Pangloss notent un ton sur presque chaque voyelle, et **aucun modèle ne produit de tons** : leurs vocabulaires de sortie n'en contiennent presque pas. Les tons coûtent 12 à 26 points de CER selon le modèle. Ce n'est pas un artefact de mesure : c'est **une vraie lacune de reconnaissance**, et c'est pour ça qu'elle est comptée dans le score officiel. Sur les nombres, les références n'ont presque pas de tons, d'où un effet faible (1 à 1,4 point).
2. **Le `ɑ` de l'orthographe biblique coûte 7 à 14 points de CER à MMS et au LLM 7B**, sur les deux corpus. Le CTC 1B écrit `a` et n'est pas touché. C'est ce qui le fait passer devant sur les nombres. Ici, c'est une **convention d'écriture**, pas une erreur d'écoute : on la compte dans le score officiel par choix méthodologique, et on l'explique ici.
3. **Les autres conventions** (`ɛ`/`e`, semi-voyelles, `kp`/`kw`, `c`/`k`, longueur) coûtent ensemble 3 à 9 points de plus selon le modèle et le corpus. La plus marquée est `c`/`k` sur les nombres (`taaci` contre `taaki`) : 1,6 à 3,4 points.
4. **Les nasales (`ka̰` contre `kan`) ne sont neutralisées par aucune étape.** Elles restent comptées comme erreurs, même dans le diagnostic le plus indulgent.
5. **Whisper ne bouge presque pas** (131 → 105) : ses erreurs viennent de la reconnaissance elle-même, pas de l'orthographe.

**Bilan :** même en neutralisant toutes les conventions, les modèles Dendi gardent **33 à 34 % de CER sur les contes et 20 à 25 % sur les nombres**. C'est la part qui relève de la reconnaissance des sons. Et ils reconnaissent alors au mieux 6 à 8 % des nombres en entier. **Aucune normalisation, même indulgente, ne rend ces modèles utilisables.**

## 4. Comportement de Whisper (langue non prise en charge)

- **Langues détectées :**
  - Pangloss : swahili 47 %, shona 32 %, yoruba 12 % pour large-v3 ; anglais 76 % pour turbo.
  - Zenodo : 21 (large-v3) et 23 (turbo) langues différentes, dont le coréen, le portugais et le créole haïtien.
- **Écriture non latine** dans 17 % (large-v3) et 22 % (turbo) des sorties Zenodo, en arabe ou en coréen.
- **Boucles de décodage** (même séquence répétée au moins 3 fois d'affilée) dans **21 % (large-v3) et 31 % (turbo) des contes**. D'où des taux d'insertion de 48 % et 135 %, et un WER de 234 % pour turbo. Ces boucles rendent les IC très larges.
- **Turbo est significativement pire que large-v3** : de 16,5 points de WER sur les nombres et de 87 points sur les contes.
- Il saisit malgré tout parfois la phonétique : « Zangufo nahinka » pour « Zangu fɔ́ nda ihinka ».

## 5. Problèmes de données révélés par l'évaluation

1. **Zenodo, locuteur M : une partie des enregistrements contient plus que la transcription.**
   - Même nombre de mots que la locutrice (4 en médiane), mais **2,7 fois plus de temps de parole** (5,5 s contre 2,05 s).
   - Les 5 modèles y font **3 à 13 fois plus d'insertions**.
   - Entre **7 % (MMS) et 26 % (Omnilingual CTC)** des fichiers produisent une transcription au moins 1,7 fois plus longue que la référence, contre 0 % chez la locutrice.
   - Les modèles CTC, qui n'inventent pas de texte, y transcrivent **le nombre entier deux fois**.

   Conséquence : les scores sur la partie `train` (locuteur M) ne sont pas fiables tels quels. Les 20 fichiers à écouter en priorité sont listés dans `listening_checklist_zenodo_male.csv`.
2. **Réponses de l'auditoire dans Pangloss.** Les remettre dans la référence change le WER de moins d'un point pour les modèles Dendi (−0,1 à −0,9) : ils ne transcrivent pas ces réponses. Pour Whisper, l'écart est de −5,7 et −13,8 points, sans doute par effet mécanique : la référence plus longue dilue ses insertions massives.
3. **Mélange d'écritures chez Omnilingual CTC.** Le modèle produit parfois de l'arabe, du japonais ou du coréen au milieu d'un mot (« dubوفi », « wlき니が »), sur 1,1 % des énoncés Zenodo. Son vocabulaire de sortie est partagé entre les langues, et le code `ddn_Latn` ne contraint pas réellement la variante CTC.

## 6. Limites à garder en tête

- **Les jeux de test sont petits :** 147 énoncés de contes et 328 nombres d'une seule locutrice. Les écarts de moins de 3 à 4 points entre modèles Dendi sont à interpréter avec prudence. Les IC appariés sont dans `pairwise.csv`.
- **Les transcriptions Pangloss n'ont jamais été relues**, tons compris. Avec un score qui compte les tons, une partie des « erreurs » mesurées peut venir des références elles-mêmes.
- **`split_v0` est une proposition.** Si le découpage figé diffère, il suffit de relancer `evaluate.py` : les prédictions couvrent tous les énoncés.
- **Chirp 3 n'a pas encore été évalué** : en attente des identifiants Google Cloud. Il n'est pas retiré ; s'il ne peut pas être testé, la raison sera écrite ici.
- **`ssid32/wav2vec2-xlsr-dendi-ddn-for-numerals` n'a pas été évalué.** Ce modèle Dendi spécialisé dans les nombres serait directement comparable sur test-zenodo, mais ses données d'entraînement ne sont pas publiées : il a pu être entraîné sur Zenodo, ce qui fausserait la comparaison. Décision à prendre (évaluer en signalant le risque de fuite, ou écarter par écrit).
- **L'archive Zenodo contient un modèle Kaldi** (`Model/model.tar`), créé pour le challenge Zindi « Intro to ASR Africa » (2022) : **WER de 7,69 %** (9 erreurs sur 117 mots, 27 énoncés de test). Il a été entraîné sur ce même dataset, donc il ne peut pas être évalué sur test-zenodo. On le cite comme référence externe.
- **Mémoire GPU à l'inférence** (pic total, V100) : Whisper large-v3 3,9 Gio, turbo 2,1 Gio, MMS 5,7 Gio, Omnilingual CTC 1B 3,2 Gio, LLM 7B 16,9 Gio. Détail dans [../resources/GPU_MEMORY.md](../resources/GPU_MEMORY.md).

## 7. Conséquences pour la suite (fine-tuning)

- **Omnilingual CTC 1B est le meilleur point de départ** : meilleur sur les nombres, à égalité sur les contes, rapide, et sous licence Apache-2.0 (MMS est en CC-BY-NC). C'est aussi le candidat n°1 du protocole.
- **Les tons :** aucun modèle n'en produit. Si le score officiel compte les tons, il faut entraîner sur des références tonales. La Bible.is ne note qu'une partie des tons. Il faut donc décider quelle notation tonale viser, et la faire valider par un locuteur.
- **Le `ɑ` :** un modèle entraîné sur le texte de la Bible écrira `ɑ`, et sera pénalisé sur Zenodo et Pangloss en écriture stricte. Il faut **convertir le texte d'entraînement vers l'orthographe cible avant l'entraînement** (décision D6 de la revue), et non pas assouplir la mesure.
- **Avant tout entraînement :** écouter et corriger (ou exclure) les enregistrements doublés du locuteur M.

## 8. Suivi de la revue du 24 octobre ([REVIEW.md](REVIEW.md))

| Point de la revue | Statut |
|---|---|
| Calculs justes, classement stable | ✅ Confirmé. `verify_metrics.py` couvre les 4 niveaux, le CER sans espaces et les nombres entièrement justes (120 combinaisons, écart maximal 4×10⁻¹⁶). `evaluate.py` et `ortho_sensitivity.py` concordent sur les 90 valeurs comparées. **Le classement change en écriture stricte** (§ 2) |
| L'orthographe pèse plus que `flat` ; niveau `skel` | ✅ Intégré, et détaillé convention par convention (§ 3, `ortho_decomposition.py`). `skel` est défini dans `normalize.py` et reste un diagnostic |
| Nombres entièrement justes comme chiffre phare de Zenodo | ✅ Intégré (§ 1, REPORT.md, comparaisons appariées). Correction : dans le tableau du § 2.1 de la revue, le point de départ « 2,4 % » est le % d'énoncés à WER nul (espaces compris) ; avec la même définition que `skel` (espaces retirés), c'est 4,3 % au niveau `notone` |
| CER sans espaces | ✅ Intégré dans REPORT.md et `summary.csv` |
| Source du CER de 2,4 % de Meta | ✅ Vérifiée (§ 2, point 6) |
| Zindi et modèle Kaldi de l'archive | ✅ Vérifiés et documentés (§ 6) |
| `ssid32` et Chirp 3 : pas de retrait silencieux | ✅ Documentés (§ 6). La décision sur `ssid32` reste à prendre (D8) |
| **D2 : figer la normalisation** | ✅ **Décidé le 31 octobre : score officiel = normalisation minimale (`raw`).** La revue proposait `notone` en principal ; l'équipe a retenu l'écriture stricte (§ 0). `notone`, `flat` et `skel` restent des diagnostics |
| D1, D3 à D10 (licences, collecte, fine-tuning, calendrier) | ⏳ À valider par l'équipe |
