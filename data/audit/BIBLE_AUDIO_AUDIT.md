# Audit de l'audio Bible.is : Nouveau Testament Dendi (DDNBIVN1DA)

2 novembre 2026.

**Fichier analysé :** `DDNBIVN1DA.zip` (580,8 Mo, MD5 `c65e3cb10bea57b3b469fbbfeba707bf`), extrait dans `data/raw/bibleis_DDNBIVN1DA/`. L'audio est sous droits et n'est jamais commité.

**Méthode :** `scripts/analyze_bible_audio.py`. Le détail par chapitre est dans `bible_audio_chapters.csv` (statistiques uniquement).

## 1. Contenu

| | |
|---|---|
| Fichiers | 260 MP3, un par chapitre, 27 livres (Matthieu → Apocalypse) |
| Version | « Audio Non-Drama » (pas de musique ni de bruitages), code produit N1DDN/BIV |
| Droits | Texte © 2018 Bibles International ; audio ℗ 2020 Hosanna / Faith Comes By Hearing |
| Durée totale | **21,55 h** |
| Parole nette | **≈ 14,9 h** (69 % du temps ; le reste est fait de pauses) |
| Durée d'un chapitre | 1,8 à 11,5 min (médiane 4,6 min) |
| **Ce qui manque** | **Le texte** (`DDNBIVN_ET`) et **les horodatages par verset** (7 958 versets) : demandés via l'API, réponse en attente |

## 2. Qualité technique

| Contrôle | Résultat | Conséquence |
|---|---|---|
| Intégrité | **0 erreur de décodage** sur les 260 fichiers | ✅ |
| Format | MP3 64 kbit/s, 24 kHz, stéréo | — |
| Stéréo | En pratique **du mono** : corrélation gauche/droite de 0,999 en médiane, canal différence à −21 dB. Exceptions mineures : Apocalypse 13 (0,90) et Matthieu 8 (0,96) | Convertir en mono ne perd rien |
| Bande passante | Coupure du codec à **10,3 kHz** | Le ré-échantillonnage à 16 kHz (limite 8 kHz) ne perd rien |
| Niveau | Masterisé très fort : niveau moyen −15 dB, crêtes au-dessus de 0 dBFS après décodage, 0,2 % des échantillons saturés | ⚠️ **Baisser le gain d'environ 3 dB avant la conversion en WAV 16 bits**, sinon l'audio sera écrêté |
| Début des chapitres | Silence de 0,55 s, puis directement la voix. **Pas de générique commun** : similarité maximale de 0,42 avec le début de Matthieu 1, alors qu'un générique identique donnerait plus de 0,9 | Pas de musique à retirer |
| Annonce du chapitre | Probable (pratique habituelle de FCBH), non vérifiée sans transcription | Les horodatages de FCBH permettent de l'exclure |

## 3. Parole et lecteurs

- **Lecture studio, posée.** Pause médiane de 0,54 s. Au total, 29 364 pauses de 300 ms ou plus, et **10 077 pauses de 700 ms ou plus**, soit le même ordre de grandeur que les **7 958 versets**.
  - On peut donc découper l'audio sur les pauses en segments de la taille d'un verset.
  - Mais ce découpage ne s'aligne pas exactement sur les versets. Pour associer chaque segment à son texte, il faut **les horodatages de FCBH ou un alignement forcé** (aligneur MMS).
- **Hauteur de voix** (médiane par chapitre) : 154 à 258 Hz, médiane de 198 Hz, un seul registre dominant.
  - Livres les plus graves : Philippiens (163 Hz) et Colossiens (174 Hz). Le plus aigu : 1 Jean (235 Hz). Philippiens 1 est vérifié à 154 Hz, sans erreur d'octave de l'estimateur.
  - Interprétation : **un lecteur principal, peut-être un deuxième sur quelques livres. À confirmer à l'écoute** (Philippiens 1, 1 Jean 1, Matthieu 1) ou avec un modèle d'identification du locuteur.
  - Dans tous les cas : **très peu de voix différentes**.

## 4. Ce que ça implique pour la phase 2 ([PHASE2_PLAN.md](../../docs/PHASE2_PLAN.md))

| Usage | Verdict | Pourquoi |
|---|---|---|
| **Pré-entraînement continu (CPT)** | ❌ Non | L'audio du Nouveau Testament de FCBH fait partie du pré-entraînement de MMS. Et une lecture homogène par un ou deux lecteurs est le cas où la littérature observe que le CPT n'aide pas |
| **Fine-tuning supervisé (E1, E2)** | ✅ **La principale source d'entraînement disponible** | Environ 7 958 versets et environ 15 h de parole nette, propre, en studio. À condition d'obtenir **le texte, les horodatages et l'autorisation d'entraîner** |
| Jeu de test | ❌ Jamais | MMS et probablement Omnilingual l'ont déjà vu |

**Précautions pour l'entraînement :**
1. Convertir le texte biblique vers l'orthographe cible (`ɑ`, tons) avant l'entraînement, conformément au score strict.
2. Baisser le gain d'environ 3 dB avant la conversion en 16 bits.
3. Exclure l'annonce des chapitres.
4. Mélanger avec d'autres voix dès que possible : un ou deux lecteurs seulement, c'est le cas de MMS, qui fait 99 % de WER strict sur nos tests.
