# Dendi data audit v1

12 October 2026. Every figure below was computed from the downloaded files (`data/audit/stats.json`).
Durations are measured on the audio, not taken from the sources' descriptions.

## 1. Summary

| | Zenodo 6591186 | Pangloss Dendi | Total |
|---|---|---|---|
| Content | Numerals read aloud (counting from 1 to 5 billion) | 6 folk tales, narrated live | |
| Speech style | Read, isolated words and short phrases | Spontaneous narration with listener responses | |
| Variety / place | Dendi of Parakou, recorded in Cotonou, 2022 | Karimama (Benin–Niger border), 1968 | |
| Utterances | 668 | 174 | 842 |
| Total duration | 48.7 min (0.81 h) | 39.4 min (0.66 h) | **88.1 min (1.47 h)** |
| Median duration | 3.9 s | 12.0 s | |
| Speakers | 2 (1 female aged 21, 1 male aged 30) | Unknown: no speaker metadata | |
| Original audio | 16-bit WAV, 334 files at 48 kHz (female), 334 at 16 kHz (male) | 96 kHz WAV, 24- or 32-bit | |
| Tokens / vocabulary | 3,034 / **39 word types** | 6,606 / 1,211 types (734 without tones) | |
| Orthography | Modern: ɛ, ɔ, few tone marks | Phonetic 1968 notation: e/o, full tone marking, tilde below | |
| Licence | CC-BY-4.0 | CC-BY-NC-SA-4.0 | |

All 842 audio–transcript pairs are complete. No files are missing, empty or corrupted, there is no clipping, and no two audio files are identical.

## 2. Zenodo: "Dendi of Parakou multi-speaker speech dataset"

- **The domain is numbers only.** The record says "reading a script … one sentence at a time", but the archive's own documentation is titled "Counting in Dendi". The script is `Dataset/kabuyo.xlsx`, 334 numerals from 1 to 5,000,000,000. There are only 39 distinct words (`cindi`, `nda`, `zangu`, `fɔ́`, `dubu`, …).
- **Both speakers read the same 334 prompts.** All 331 unique prompts appear in both voices. An utterance-level split would put the same sentence in train and test.
- **The speakers differ in their recordings.**
  - Female: 334 utterances, 14.6 min, mean 2.6 s, recorded at 48 kHz.
  - Male: 334 utterances, 34.1 min, mean 6.1 s, recorded at 16 kHz.
- **Transcript errors.** Three pairs of different numbers have the same transcript, so at least one transcript in each pair is wrong:
  - 100,000 and 100,000,000: both `Dubu dubu Zangu fɔ́`.
  - 200,000 and 200,000,000: both `Dubu dubuZangu hinka`.
  - 900,000 and 900,000,000: both `Dubu dubu Zangu ɛga`.
- **Inconsistent spelling.** Capitalisation is random, and word boundaries vary (`dubuZangu` vs `dubu zangu`). 6 transcripts contain double spaces.
- Files: in the male folder, each WAV name has a `220402-` prefix that its TXT name lacks. The metadata spreadsheet records this correctly.
- Not used here: `Model/model.tar` (33 MB), a 2022 Kaldi model from the Zindi challenge.

## 3. Pangloss: Dendi tales (Nicole Tersis, CNRS, 1968)

| Tale | Utterances | Minutes | Words |
|---|---|---|---|
| conte1: Pourquoi le chameau ne reste pas en brousse | 14 | 3.4 | 614 |
| conte2: Jodi la petite fille et les co-épouses | 13 | 4.4 | 735 |
| conte3: L'enfant aux pouvoirs magiques | 62 | 11.4 | 2,165 |
| conte4: La tourterelle à la douce voix | 31 | 6.4 | 989 |
| conte5: Quand Tamindi cessa d'être muette | 13 | 3.0 | 415 |
| conte6: La vieille femme et les épreuves de deux garçons | 41 | 10.8 | 1,688 |

- **Long segments.** The XML segments are groups of several sentences, from 1.3 s to 48.1 s. 8 segments are longer than 30 s, which exceeds Whisper's input window. These must be split (for example with forced alignment) or handled separately.
- **Overlapping speech.** The transcripts contain 591 listener back-channels (`│nam│`, `│tô│`) spoken by someone other than the narrator. `text_clean` removes them, but they are still audible in the audio.
- **Unreviewed transcripts.** The archive itself warns that the transcriptions, and the tones in particular, were never revised.
  - Known defect: conte1 S1 starts with `y jàndé` where `ǎy jàndé` is expected.
  - Encoding error: the character `ℇ` (U+2107, the Euler constant) appears in place of `ɛ` in `wℇrgídà`.
- **No speaker metadata.** The narrators are listed as "unknown". We do not know whether the 6 tales have 6 narrators or fewer. Each tale is treated as a separate pseudo-speaker.
- 1968 recordings have archival tape quality: median level −21 dBFS and about 21% silence on average. They should be listened to before use.
- Some narrators use Hausa words and phrases (stated on the Pangloss page).

## 4. Can the two corpora be used together?

- **Different orthographies.** Pangloss never uses ɛ or ɔ and marks tones on almost every vowel. Zenodo uses ɛ and ɔ and has only a few acute accents. Without a mapping, a model trained on one cannot be scored fairly on the other.
- **Almost no shared vocabulary.** With tones removed, the corpora share only 7 word types: `bambata`, `hinka`, `hinza`, `iddu`, `na`, `nda`, `taaci`.
- **Different varieties and eras.** Parakou in 2022 versus Karimama in 1968.
- No audio overlap and no shared speakers are possible: the recordings are 54 years apart.

## 5. Consequences for the protocol (decision due Wed 14 Oct)

1. **A speaker-disjoint split is not possible inside Zenodo.** With only 2 speakers, holding one out leaves one speaker for training. Holding out prompts is also of little use, because the vocabulary is closed: 39 words reused in every number. Zenodo measures recognition of numbers, not general Dendi ASR. The paper must say so.
2. **Pangloss is the only source of open-vocabulary speech.** At 39 min, it is better used as a test set, or split by tale, than as a training set. Its unreviewed transcripts limit how reliable WER can be.
3. **Report WER separately for each corpus.** Do not combine them into one aggregate figure.
4. **Normalisation.** Choose between keeping tones (`text_norm_v0`) and removing them (`text_norm_v0_notone`). Report CER with tones removed, as a minimum. Map `ℇ` to `ɛ`, and decide whether `e/o` in Pangloss should map to `ɛ/ɔ`; that decision needs a Dendi speaker.
5. **Fix or exclude** the 3 duplicated Zenodo transcripts, after checking them by ear.
6. **Total data is about 1.5 hours.** Training data for fine-tuning is very scarce, which makes the data-scaling experiment (RQ4) of doubtful value. Look for more Dendi data (Bible recordings, radio, community recordings) as early as possible.
7. **Licence.** Pangloss is CC-BY-NC-SA. Models and derived transcripts must stay non-commercial and share-alike.
