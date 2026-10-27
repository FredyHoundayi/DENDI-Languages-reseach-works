# Analyse de l'évaluation zero-shot (phase 1)

18 octobre 2026.

**Source des chiffres :** [REPORT.md](REPORT.md) et `summary.csv`.
- WER et CER sont en %.
- Les IC sont à 95 %, par bootstrap sur les énoncés (B = 2000).
- Normalisation principale : `notone`.
- Découpage : `split_v0`.

**Vérification indépendante :** `scripts/evaluation/verify_metrics.py` recalcule les 90 scores (modèle × corpus × sous-ensemble × niveau) avec une distance d'édition écrite séparément, sans `jiwer`. Écart maximal : **4×10⁻¹⁶**.

## 1. Résultats principaux (sous-ensemble `test`, `notone`)

| Modèle | Prend en charge le Dendi | **Pangloss** WER | Pangloss CER | **Zenodo** WER | Zenodo CER | RTF (V100) |
|---|---|---|---|---|---|---|
| **MMS-1b-all (ddn)** | ✅ | **77,3** [75,6–79,2] | 38,6 [36,9–40,2] | **79,7** [76,9–82,5] | **24,5** [23,3–25,7] | 0,013–0,015 |
| Omnilingual LLM 7B v2 | ✅ | 81,3 [78,6–84,6] | 38,8 [36,5–41,3] | 85,5 [82,6–88,4] | 27,9 [26,6–29,0] | 0,31–0,38 |
| Omnilingual CTC 1B v2 | ✅ | 85,2 [83,1–87,2] | **36,8** [34,3–39,9] | 95,6 [93,9–97,1] | 33,8 [32,5–35,2] | 0,02–0,04 |
| Whisper large-v3 | ❌ | 142,0 [123,1–162,2] | 109,5 [87,4–132,3] | 97,6 [95,2–100,0] | 49,3 [41,8–62,0] | 0,18–0,32 |
| Whisper large-v3-turbo | ❌ | 230,9 [184,5–281,8] | 189,8 [148,4–233,9] | 113,8 [99,5–133,4] | 61,0 [49,1–78,5] | 0,07 |

Les tailles des sous-ensembles de test :
- test-pangloss : 147 énoncés, 5 577 mots ;
- test-zenodo : locutrice F, 328 énoncés, 1 495 mots.

**Métriques complémentaires ajoutées après la revue du 24 octobre** (même sous-ensemble `test`, `notone`) :
- **CER sans espaces** : le CER calculé après suppression des espaces, ce qui neutralise les différences de découpage en mots.
- **Nombres entièrement justes** : la part des nombres dont l'hypothèse, espaces retirés, est identique à la référence. C'est le chiffre qui compte pour un usage réel (dicter un montant, un numéro).

| Modèle | Pangloss CER sans espaces | Zenodo CER sans espaces | **Zenodo : nombres entièrement justes** |
|---|---|---|---|
| MMS-1b-all (ddn) | 38,7 [36,9–40,5] | **22,5** [21,3–23,7] | **4,3** [2,1–6,7] |
| Omnilingual LLM 7B v2 | 38,8 [36,4–41,2] | 26,9 [25,6–28,1] | 3,4 [1,5–5,2] |
| Omnilingual CTC 1B v2 | **33,1** [30,5–36,1] | 29,3 [27,9–30,7] | 2,4 [0,9–4,3] |
| Whisper large-v3 | 114,3 [90,0–139,6] | 48,3 [39,5–63,2] | 0,3 [0,0–0,9] |
| Whisper large-v3-turbo | 193,6 [152,8–236,5] | 59,1 [47,4–77,8] | 0,6 [0,0–1,5] |

- **Le meilleur modèle reconnaît moins d'1 nombre sur 20 en entier.** Les écarts entre les 3 modèles Dendi ne sont pas significatifs sur cette métrique (IC appariés incluant 0). Seul l'écart avec Whisper l'est.
- **Sans les espaces, Omnilingual CTC 1B devient le meilleur sur les contes (33,1 %).** Son mauvais WER venait surtout de la fusion des mots, pas de la reconnaissance des sons.
- Pour Pangloss, aucun énoncé n'est entièrement juste, quel que soit le modèle : sur des phrases de 35 mots en médiane, cette métrique n'est pas informative.

## 2. Ce que l'on peut affirmer

1. **Aucun système n'est utilisable tel quel pour le Dendi.** Le meilleur WER est de 77 % sur les contes et de 80 % sur les nombres. Même avec un CER de 24 à 39 %, plus d'un caractère sur quatre est faux.
2. **Les modèles qui prennent en charge le Dendi (MMS, Omnilingual) sont très nettement meilleurs que Whisper.** Les écarts sont significatifs dans toutes les comparaisons appariées. Whisper ne fait pas de la reconnaissance du Dendi : il identifie une autre langue et transcrit dans cette langue (voir § 4).
3. **MMS-1b-all est la meilleure référence de base en WER sur les deux corpus.**
   - Il bat Omnilingual LLM 7B de 4,0 points sur Pangloss (IC [1,3 ; 7,4]) et de 5,8 points sur Zenodo (IC [2,7 ; 9,1]).
   - Il bat Omnilingual CTC 1B de 7,9 et de 15,9 points.
   - Il est 20 à 30 fois plus rapide que le LLM 7B (RTF 0,013–0,015 contre 0,31–0,38).
4. **En CER sur Pangloss, les trois modèles Dendi sont proches, entre 36,8 et 38,8 %.** Le CTC 1B a le CER le plus bas, mais **aucun des trois écarts n'est significatif** (les IC appariés incluent 0 ; voir `pairwise.csv`). En revanche, le CTC 1B a le pire WER, à cause d'un **taux de suppression de 42 %** (contre 21–23 % pour les autres) : il fusionne les mots (ratio de longueur médian de 0,61). Le choix du WER ou du CER change donc le classement. Il faut rapporter les deux.
5. **Le LLM 7B ne fait pas mieux que le CTC 1B en CER.** Il le bat en WER grâce à un meilleur découpage des mots, pour 9 à 19 fois plus de calcul.
6. **Le CER publié par Meta pour le Dendi (2,4 % avec le LLM 7B) ne se transpose pas à nos données.** Le chiffre est vérifié dans le tableau par langue publié par Meta (`per_language_results_table_7B_llm_asr.csv`, ligne `ddn_Latn`) : CER 2,4 %, sur leur propre jeu de test, avec **32,2 h de données Dendi à l'entraînement**. C'est plus que les 21,6 h de la Bible.is : Meta disposait donc d'autres données Dendi. Nous obtenons 39 % sur les contes et 28 % sur les nombres. Les causes probables sont le changement de domaine (Bible contre contes et nombres), l'orthographe (§ 3) et le changement de variété (Karimama 1968, Parakou 2022). Il faut citer le chiffre publié comme une référence externe, pas comme un résultat comparable.

## 3. L'orthographe pèse lourd, et c'est en partie un artefact de mesure

- **L'effet de la normalisation est massif pour les modèles Dendi.** Sur Pangloss, le WER de MMS passe de 99,3 (`raw`) à 77,7 (`notone`), et son CER de 64,2 à 38,8. Cette différence vient de deux choses : les tons, absents des sorties de MMS et d'Omnilingual, et le `ɑ` de l'orthographe biblique, ramené à `a`.
- **Les conventions d'écriture divergent systématiquement entre les sorties (orthographe biblique) et Zenodo :**
  - `nda` devient `na` ;
  - `taaci` devient `taaki` (c/k) ;
  - `ɛga` devient `iga`/`ga` ;
  - le découpage en mots diffère : `zangu fɔ` devient `zangufɔ`, `dubu wei` devient `dubuwii`. Un seul mot fusionné coûte 2 erreurs au WER.

  Résultat : **un WER de 80 % s'accompagne d'un CER de 24 % seulement.** Pour les nombres, le CER est l'indicateur le plus juste.
- **Le niveau `flat` change peu par rapport à `notone`** (de 0,5 à 1,5 point). La différence e/o contre ɛ/ɔ n'explique donc qu'une petite partie des erreurs.
- **Mais d'autres conventions pèsent plus que `flat` ne le montre** (revue du 24 octobre). Les substitutions révèlent aussi la longueur des voyelles (`ci`/`cii`), les nasales (`ka̰`/`kan`), les semi-voyelles (`hay`/`hai`), `kw`/`kp` et `c`/`k`. Le niveau **`skel`** les unifie toutes. Il est volontairement trop indulgent (il peut fusionner de vrais contrastes, comme la longueur des voyelles) : c'est un **test de sensibilité, jamais une métrique principale**. Il donne une borne haute de la part d'erreur due à l'orthographe :

  | `test`, CER sans espaces `notone` → `skel` | Zenodo | Part due à l'orthographe | Pangloss | Part due à l'orthographe |
  |---|---|---|---|---|
  | MMS-1b-all (ddn) | 22,5 → 16,6 | 26 % | 38,7 → 30,2 | 22 % |
  | Omnilingual LLM 7B v2 | 26,9 → 18,0 | 33 % | 38,8 → 32,7 | 16 % |
  | Omnilingual CTC 1B v2 | 29,3 → 18,4 | 37 % | 33,1 → 28,7 | 13 % |

  **L'orthographe explique au plus un quart à un bon tiers du CER sur les nombres, et 13 à 22 % sur les contes.** Même avec `skel`, MMS ne reconnaît que 7,6 % des nombres en entier (Omnilingual LLM 7,9 %). La conclusion ne change donc pas : aucun modèle n'est utilisable tel quel. Détail : `ortho_sensitivity.csv`, et les colonnes `skel` de `summary.csv`.
- **À faire :** valider avec un locuteur Dendi une table d'équivalences orthographiques (`nda`/`na`, c/k, fusion des numéraux composés), et ajouter éventuellement un niveau `orth` pour le papier. Elle doit être **figée avant toute nouvelle mesure** et justifiée linguistiquement, sinon elle revient à ajuster la mesure aux sorties.

## 4. Comportement de Whisper (langue non prise en charge)

- **Langues détectées :**
  - Pangloss : swahili 47 %, shona 32 %, yoruba 12 % pour large-v3 ; anglais 76 % pour turbo.
  - Zenodo : 21 (large-v3) et 23 (turbo) langues différentes, dont le coréen, le portugais et le créole haïtien.
- **Écriture non latine** dans 17 % (large-v3) et 22 % (turbo) des sorties Zenodo, en arabe ou en coréen.
- **Boucles de décodage** (même séquence répétée au moins 3 fois d'affilée) dans **21 % (large-v3) et 31 % (turbo) des contes**. D'où des taux d'insertion de 48 % et 135 %, et un WER de 231 % pour turbo. La variabilité qui en résulte rend les IC très larges.
- **Turbo est significativement pire que large-v3** : de 16 points sur Zenodo et de 89 points sur Pangloss.
- Il saisit malgré tout parfois la phonétique : « Zangufo nahinka » pour « Zangu fɔ́ nda ihinka ». Ça laisse penser qu'un fine-tuning a une marge réelle.

## 5. Problèmes de données révélés par l'évaluation

1. **Zenodo, locuteur M : une partie des enregistrements contient plus que la transcription.**
   - Même nombre de mots que la locutrice (4 en médiane), mais **2,7 fois plus de temps de parole** (5,5 s contre 2,05 s).
   - Les 5 modèles y font **3 à 13 fois plus d'insertions**.
   - Entre **7 % (MMS) et 26 % (Omnilingual CTC)** des fichiers produisent une hypothèse au moins 1,7 fois plus longue que la référence, contre 0 % chez la locutrice.
   - Les modèles CTC, qui n'inventent pas de texte, y transcrivent **le nombre entier deux fois**.

   Conséquence : les scores sur la partie `train` (locuteur M) ne sont pas fiables tels quels. Les 20 fichiers à écouter en priorité sont listés dans `listening_checklist_zenodo_male.csv`. Il faut les corriger, ou exclure ces fichiers, **avant de s'en servir pour le fine-tuning**.
2. **Réponses de l'auditoire dans Pangloss.** Les remettre dans la référence change le WER de moins d'un point pour les modèles Dendi : ils ne transcrivent pas ces réponses, et le choix de `text_clean` comme référence n'influence donc presque pas leurs résultats. Pour Whisper, l'écart est de −5,5 et −13,8 points, sans doute par effet mécanique : la référence plus longue dilue ses insertions massives.
3. **Mélange d'écritures chez Omnilingual CTC.** Le modèle produit parfois de l'arabe, du japonais ou du coréen au milieu d'un mot (« dubوفi », « wlき니が »), sur 1,1 % des énoncés Zenodo. Son vocabulaire de sortie est partagé entre les langues, et le code `ddn_Latn` ne contraint pas réellement la variante CTC.

## 6. Limites à garder en tête

- **Les jeux de test sont petits :** 147 énoncés de contes et 328 nombres d'une seule locutrice. Les écarts de moins de 3 à 4 points entre modèles Dendi sont à interpréter avec prudence. Les IC appariés sont dans `pairwise.csv`.
- **Les transcriptions Pangloss n'ont jamais été relues**, tons compris. Une partie des « erreurs » mesurées peut venir des références elles-mêmes.
- **`split_v0` est une proposition.** Si le découpage figé diffère, il suffit de relancer `evaluate.py` : les prédictions couvrent tous les énoncés.
- **Chirp 3 n'a pas encore été évalué** : en attente des identifiants Google Cloud. Il n'est pas retiré ; s'il ne peut pas être testé, la raison sera écrite ici.
- **`ssid32/wav2vec2-xlsr-dendi-ddn-for-numerals` n'a pas été évalué.** Ce modèle Dendi spécialisé dans les nombres serait directement comparable sur test-zenodo, mais ses données d'entraînement ne sont pas publiées : il a pu être entraîné sur Zenodo, ce qui fausserait la comparaison. Décision à prendre (évaluer en signalant le risque de fuite, ou écarter par écrit).
- **L'archive Zenodo contient un modèle Kaldi** (`Model/model.tar`), créé pour le challenge Zindi « Intro to ASR Africa » (2022) : **WER de 7,69 %** (9 erreurs sur 117 mots, 27 énoncés de test). Il a été entraîné sur ce même dataset, donc il ne peut pas être évalué sur test-zenodo. On le cite comme référence externe.
- **Mémoire GPU à l'inférence** (pic total, V100) : Whisper large-v3 3,9 Gio, turbo 2,1 Gio, MMS 5,7 Gio, Omnilingual CTC 1B 3,2 Gio, LLM 7B 16,9 Gio. Détail dans [../resources/GPU_MEMORY.md](../resources/GPU_MEMORY.md).

## 7. Conséquences pour la semaine 2 (fine-tuning)

- **MMS est le meilleur point de départ en WER.** Omnilingual CTC 1B a le meilleur CER, et c'est le candidat n°1 de ton protocole. Son défaut principal, la fusion des mots, est précisément ce qu'un fine-tuning sur des transcriptions correctement segmentées devrait corriger.
- **Avant tout entraînement :** corriger ou filtrer les enregistrements doublés du locuteur M, et fixer la table d'orthographe.
- Les données d'entraînement de la Bible (≈ 20 h, si FCBH donne son accord) sont dans l'orthographe des sorties de MMS. Un fine-tuning dessus risque donc de **creuser l'écart d'orthographe** avec Zenodo et Pangloss. C'est un argument supplémentaire pour la table d'équivalences.

## 8. Suivi de la revue du 24 octobre ([REVIEW.md](REVIEW.md))

| Point de la revue | Statut |
|---|---|
| Calculs justes, classement stable | ✅ Confirmé. `verify_metrics.py` couvre maintenant les 4 niveaux, le CER sans espaces et les nombres entièrement justes (120 combinaisons, écart maximal 4×10⁻¹⁶). Les chiffres de `evaluate.py` et de `ortho_sensitivity.py` concordent sur les 90 valeurs comparées |
| L'orthographe pèse plus que `flat` ; niveau `skel` | ✅ Intégré. `skel` est défini dans `normalize.py`, calculé par `evaluate.py` comme test de sensibilité, et `ortho_sensitivity.py` utilise désormais cette même définition (son CSV est reproduit à l'identique) |
| Nombres entièrement justes comme chiffre phare de Zenodo | ✅ Intégré : colonne « Entièrement justes » dans REPORT.md, avec IC et comparaisons appariées, plus le tableau du § 1. Correction : dans le tableau du § 2.1 de la revue, le point de départ « 2,4 % » est le % d'énoncés à WER nul (espaces compris). La même définition que `skel` (espaces retirés) donne **4,3 % → 7,6 %** |
| CER sans espaces | ✅ Intégré dans REPORT.md et `summary.csv` |
| Source du CER de 2,4 % de Meta | ✅ Vérifiée (§ 2, point 6) |
| Zindi et modèle Kaldi de l'archive | ✅ Vérifiés et documentés (§ 6) |
| `ssid32` et Chirp 3 : pas de retrait silencieux | ✅ Documentés (§ 6). La décision sur `ssid32` reste à prendre (D8) |
| Normalisation et découpage figés (D2) | ⏳ Les définitions sont prêtes (`notone` principal, `raw`/`flat` diagnostic, `skel` sensibilité) ; **à valider par l'équipe** |
| D1, D3 à D10 (licences, collecte, fine-tuning, calendrier) | ⏳ **À valider par l'équipe.** Ce sont des choix de projet, pas des corrections de l'évaluation |
