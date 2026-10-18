# Données exploitables et préparation de la phase 1

12 octobre 2026. Ce rapport complète [DATA_AUDIT.md](DATA_AUDIT.md) et [RESOURCE_SURVEY.md](RESOURCE_SURVEY.md).

## 1. Conclusion

**Oui, la phase 1 peut être terminée avec les données déjà en main.** Elle consiste à mesurer les modèles existants sans entraînement (phase A du protocole, semaine 1). Pour cela, il faut seulement **des jeux de test**, pas de données d'entraînement. Zenodo et Pangloss suffisent.

La Bible.is n'intervient qu'en **semaine 2**, pour l'entraînement. Elle n'ira jamais en test, parce que MMS et Omnilingual ont été entraînés dessus. L'attente d'une semaine pour l'API ne bloque donc pas la phase 1.

## 2. Données exploitables aujourd'hui

| Données | Volume | Transcrit | Licence | Rôle |
|---|---|---|---|---|
| **Pangloss**, 6 contes (1968) | 174 énoncés, 39,4 min, 6 606 mots | ✅ | CC-BY-NC-SA | **Test principal** (Dendi général) |
| **Zenodo**, nombres (2022) | 668 énoncés, 48,7 min | ✅ | CC-BY-4.0 | **Test secondaire** (tâche limitée aux nombres) |
| Bible.is NT, audio non dramatisé | 260 chapitres, 21,55 h | ⏳ texte et horodatages dans environ 1 semaine | © FCBH, avenant demandé | Entraînement (semaine 2) |
| GRN (`AfriSpeech/grn-african-speech`) | 1,78 h, 3 variétés | ❌ | © GRN, usage recherche | Adaptation non supervisée, test de variété si on le transcrit |
| Zarma (corpus `omnilingual-asr-corpus`, `dje_Latn`) | ≈ 10,7 h | ✅ | CC-BY-4.0 | Transfert (semaine 2) |
| Textes Dendi : Open Bible Stories (CC BY-SA), Wikipédia Incubator (71 articles), DUDH (58 lignes) | Petit | — | Libres | Normalisation, modèle de langue, script d'enregistrement |

Tout le reste (≈ 130 h de journaux SRTB et de prêches, Jesus Film, Genesis) est non transcrit et sous droits. Ce n'est pas utilisable pour la phase 1.

## 3. Découpage proposé (à valider le mercredi 14)

Le jeu de test doit être figé **avant** les premières mesures, et rester le même jusqu'à la fin du projet.

| Jeu | Contenu | Énoncés | Durée | Justification |
|---|---|---|---|---|
| **test-pangloss** | contes 2, 3, 4, 6 | 147 | 33,0 min | Le gros du corpus de parole naturelle |
| **dev-pangloss** | contes 1 et 5 | 27 | 6,4 min | Choix des checkpoints en semaine 2, sur le domaine cible. Le découpage par conte évite toute fuite de texte |
| **test-zenodo** | locutrice F (toute) | 334 → **328** | 14,6 min | Locutrice jamais vue à l'entraînement. Le vocabulaire, lui, est identique |
| **train-zenodo** | locuteur M (tout) | 334 → **328** | 34,1 min | Entraînement en semaine 2 |
| *exclus* | 3 paires de nombres à la transcription identique, chez les 2 locuteurs | 12 | — | Transcription fausse dans au moins un cas sur deux |
| **train-bible** | NT (semaine 2) | ≈ 7 900 | ≈ 20 h | Uniquement pour l'entraînement |

Pour la phase 1, les modèles tournent sans entraînement sur **test-pangloss, dev-pangloss et test-zenodo**.

Pour le papier, il faudra écrire noir sur blanc que :
- test-zenodo est **indépendant du locuteur mais pas du texte** : ce sont les mêmes 331 nombres ;
- les conteurs de Pangloss ne sont pas identifiés.

## 4. Points bloquants à régler avant de calculer un WER

1. **Figer la normalisation.** Les sorties des modèles et les références n'utilisent pas la même orthographe :

   | Source | Orthographe |
   |---|---|
   | MMS (ddn) | `ɑ`, ɛ, ɔ, presque pas de tons |
   | Pangloss | e/o, tons partout |
   | Zenodo | ɛ/ɔ, peu de tons |

   Proposition : calculer **3 niveaux** pour chaque modèle.

   | Niveau | Règle | Statut |
   |---|---|---|
   | `strict` | `text_norm_v0` | Diagnostic |
   | `notone` | sans tons ni tilde souscrit | **Métrique principale** |
   | `flat` | `notone` + `ɑ→a`, `ɛ→e`, `ɔ→o` | Pour séparer les erreurs d'orthographe des vraies erreurs de reconnaissance |

   Dans tous les cas : `ℇ→ɛ`, minuscules, ponctuation supprimée.
2. **Segments trop longs.** 8 segments Pangloss dépassent 30 s (le plus long fait 48 s).
   - Whisper : utiliser le découpage en fenêtres du pipeline Hugging Face (`chunk_length_s=30`).
   - MMS : il accepte ces longueurs sur GPU.
   - Omnilingual : vérifier sa limite de durée d'entrée.
3. **Réponses de l'auditoire.** Les « nam » et « tô » sont audibles dans l'audio mais retirés de `text_clean`. La référence à utiliser est `text_clean`. Les modèles qui transcrivent ces réponses seront pénalisés par des insertions : c'est à noter dans l'analyse des erreurs.

## 5. Modèles réalisables en phase 1

| Modèle | Dendi pris en charge ? | Statut dans le papier | Remarque |
|---|---|---|---|
| **MMS-1b-all + adaptateur `ddn`** | ✅ Oui | Référence de base principale | Entraîné sur la Bible : nos tests (contes, nombres) sont **hors de ce domaine**, ce qui est bien |
| **Omnilingual ASR (`ddn_Latn`)** | ✅ Oui | Référence de base principale | Licence Apache-2.0. Plusieurs tailles existent. Environnement fairseq2 |
| **Whisper large-v3** (et une taille moyenne) | ❌ Non | Exploratoire, « langue non prise en charge » | Avec détection automatique de langue, ou forcée sur `ha`/`yo`. WER attendu proche de 100 % ; on l'utilisera comme base de comparaison pour le fine-tuning |
| `ssid32/wav2vec2-xlsr-dendi-ddn-for-numerals` | Nombres seulement | test-zenodo uniquement | ⚠️ Ses données d'entraînement sont inconnues et peuvent inclure Zenodo. À demander à l'auteur, sinon signaler la fuite possible |
| Google Chirp (Speech-to-Text v2) | À vérifier | Exploratoire | Vérifier la liste des langues prises en charge ; noter la version et la date d'accès |
| XLS-R / w2v-BERT | ❌ Il faut une tête ASR | Semaine 2 | Pas de mesure sans entraînement possible |

**Calcul :** pas de GPU en local (7 Go de RAM, pas de PyTorch). Toute l'inférence se fait sur SageMaker. Un GPU de 16 Go suffit pour MMS-1b et Whisper large-v3.

## 6. Plan pour la semaine 1

| Jour | Action | Dépend de |
|---|---|---|
| Lun 12 | ✅ Audit des données, inventaire des ressources, demande d'API Bible.is | — |
| Mar 13 | Configurer SageMaker ; pilote MMS-ddn sur 20 énoncés ; vérifier Omnilingual et Chirp | — |
| Mer 14 | **Figer** la normalisation et le découpage (§ 3 et § 4) ; écrire les manifests de test ; script WER/CER (jiwer) testé sur un échantillon | Décision commune |
| Jeu 15 – Ven 16 | Inférence : MMS, Omnilingual, Whisper ×2, modèle des nombres, Chirp si éligible ; conserver toutes les sorties brutes | Tests figés |
| Sam 17 – Dim 18 | Tableau comparatif (strict / notone / flat, WER et CER, intervalles de confiance par bootstrap sur les énoncés) ; journal des échecs ; note de décision pour la semaine 2 | — |

## 7. À lancer en parallèle (pas bloquant)

- **Relecture par un locuteur Dendi** : d'abord un échantillon de test-pangloss (orthographe, tons), puis les 3 paires de nombres douteuses à réécouter.
- **Écrire aux contacts :** l'équipe Noulinmon (données du modèle des nombres), Ross Patrick Azogbonon (communauté Wikipédia Dendi), et la SRTB (archives des journaux).
- **Préparer le script Bible** (découpage par verset, alignement, manifest) avec des données fictives, pour qu'il soit prêt à l'arrivée de l'API.
