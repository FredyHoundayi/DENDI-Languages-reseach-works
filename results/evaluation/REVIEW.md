# Revue de la phase 1 et proposition pour la suite

24 octobre 2026. Ce document complète [ANALYSIS.md](ANALYSIS.md). Les chiffres nouveaux viennent de `scripts/evaluation/ortho_sensitivity.py`, qui écrit `ortho_sensitivity.csv`.

## 1. Résumé

- **Les calculs sont justes.** `verify_metrics.py`, relancé, donne un écart maximal de 4×10⁻¹⁶, et le classement des modèles tient.
- **Aucun modèle n'est utilisable en production.** Même avec la notation la plus indulgente, MMS reconnaît moins d'1 nombre sur 12 en entier sur Zenodo, qui est pourtant la condition la plus facile.
- **L'orthographe explique un quart à un tiers du CER**, mais elle ne change pas cette conclusion.
- **MMS ne peut pas servir à des clients** (licence CC-BY-NC). Le candidat pour la production est Omnilingual CTC 1B (Apache-2.0).

## 2. Remarques sur la phase 1

1. **L'orthographe pèse plus que ne le montre `flat`.** Ce niveau ne traite que e/o et ɛ/ɔ. Or les substitutions montrent d'autres conventions, tout aussi systématiques : longueur des voyelles (`ci → cii`), nasales (`ka̰ → kan`), semi-voyelles (`hay → hai`), `kw/kp`, `c/k`, découpage des mots (`zangu fɔ → zangufɔ`). Avec une notation volontairement trop indulgente qui les unifie (`skel`, test de sensibilité uniquement) :

   | MMS, sous-ensemble `test` | WER `notone` → `skel` | CER sans espaces `notone` → `skel` | Nombres entièrement justes |
   |---|---|---|---|
   | Zenodo | 79,7 → 73,1 | 22,5 → 16,6 | 2,4 % → 7,6 % |
   | Pangloss | 77,3 → 69,9 | 38,7 → 30,2 | — |

2. **Le pourcentage de nombres entièrement justes devrait être le chiffre phare pour Zenodo.** C'est la métrique qui compte en production, et elle n'apparaît aujourd'hui que dans une colonne de REPORT.md.
3. **Le découpage et la normalisation ne sont pas figés**, alors que le protocole le demandait pour le 14 octobre.
4. **Aucun retrait silencieux :**
   - `ssid32` n'a été ni évalué ni écarté par écrit ;
   - l'exclusion de Chirp 3 doit être documentée ;
   - le CER de 2,4 % attribué à Meta doit être vérifié dans leur papier avant d'être cité.
5. **Zenodo, deux points à citer :**
   - le dataset a été créé pour le challenge Zindi « Intro to ASR Africa » ;
   - son archive contient un modèle Kaldi entraîné sur la seule locutrice (7,7 % de WER sur 27 nombres de la même voix). Ce modèle ne peut pas être évalué sur test-zenodo, car il a été entraîné sur ces mêmes fichiers.

## 3. Licences

Trois éléments sont non commerciaux : MMS, Pangloss et notre future lecture de la Bible. **Le modèle de production sera donc Omnilingual CTC 1B, entraîné uniquement sur les textes libres de la collecte.**

## 4. Plan de collecte

- **10 h d'un seul locuteur, en lecture**, puisque personne n'est disponible pour transcrire :
  - environ 8 h de Bible DDNBIV, si l'autorisation pour le texte est accordée ;
  - 1 à 2 h de textes libres en CC BY-SA (Open Bible Stories, Wikipédia Incubator).
- **Tests :**
  - Zenodo et Pangloss, sur les mêmes énoncés qu'en zero-shot, ce qui donne une comparaison avant/après directe ;
  - 30 min de textes libres du même locuteur, mises de côté ;
  - jamais de texte biblique en test.
- **Trois précautions :**
  - convertir le texte biblique vers l'orthographe de Zenodo avant l'entraînement ;
  - remplacer le transcripteur par un contrôle automatique (sortie d'un modèle comparée au texte lu, puis réécoute des seuls fichiers signalés) ;
  - n'inclure dans les textes lus aucun des nombres de Zenodo ni aucun texte des contes Pangloss.
- **Limite :** une seule voix lisant la Bible, c'est le cas de MMS, qui fait 80 % de WER sur nos données. Les tests sur d'autres voix sont donc indispensables.

## 5. Décisions à valider

| ID | Proposition | Validé ? |
|---|---|---|
| D1 | Zenodo (locutrice F et locuteur M, après écoute des 20 fichiers suspects) et Pangloss servent uniquement de test, et restent les tests principaux après fine-tuning | ☐ |
| D2 | Figer la normalisation : `notone` en principal, `raw` et `flat` en diagnostic, `skel` en test de sensibilité | ☐ |
| D3 | Métriques : WER, CER et pourcentage de nombres entièrement justes, plus le RTF et la mémoire GPU | ☐ |
| D4 | Fine-tuner MMS (adaptateur `ddn`) et Omnilingual CTC 1B, avec les mêmes données | ☐ |
| D5 | Collecte en lecture, en 3 vagues (2 h, 5 h, puis 10 h), pour obtenir une courbe d'apprentissage | ☐ |
| D6 | Faire valider par un locuteur la table de conversion orthographique (Bible → Zenodo) avant le premier entraînement | ☐ |
| D7 | Optionnel : un mini-test de 5 à 10 locuteurs (environ 30 min) si des moyens se libèrent | ☐ |
| D8 | Clore la phase 1 : `ssid32`, Chirp 3, source du chiffre de Meta | ☐ |
| D9 | Le fine-tuning commence quand la vague 1 est prête ; la date du 8 novembre est repoussée si nécessaire | ☐ |
| D10 | Deux pistes : recherche (avec la Bible, non commerciale) et production (textes libres seulement). Leur comparaison mesure l'apport de la Bible | ☐ |

## 6. Objectifs pour le dimanche 1ᵉʳ novembre (sans entraînement)

- **O1.** Décisions D1 à D10 validées.
- **O2.** Table de conversion orthographique relue par un locuteur.
- **O3.** Réponse de dbs.org obtenue (ou relance envoyée), texte de la vague 1 découpé en versets, consentement signé.
- **O4.** Séance pilote de 30 min, contrôlée automatiquement, avec les temps mesurés.
- **O5.** Pipeline de fine-tuning prêt pour les deux modèles, testé techniquement sur le pilote.
- **O6.** Phase 1 close : 20 fichiers écoutés, `ssid32` traité, `evaluate.py` mis à jour.

## 7. Ensuite

1. Quand la vague 1 (2 h) est prête : premier fine-tuning des deux modèles et réévaluation, soit le premier résultat avant/après.
2. Avec les vagues 2 et 3 : la courbe d'apprentissage.
3. Puis l'analyse des erreurs et la rédaction.
