# Dendi (ddn) resource survey

12 October 2026. Four parallel searches covered:
- ML speech datasets;
- religious and missionary media;
- linguistic archives;
- broadcast media, text and related languages.

Labels used below:
- **V** (verified): we checked the resource directly through an API, a file listing or an HTTP status.
- **M** (mentioned): it was only seen in secondary sources.

Hours marked "≈" are estimates.

## 1. Summary

- **No other openly licensed, transcribed Dendi speech corpus exists.** We checked Hugging Face, Zenodo, OpenSLR, Common Voice, CMU Wilderness, FLEURS, OLAC, ELAR, PARADISEC and TLA. Zenodo 6591186 and the Pangloss tales are the only ones.
- **The largest transcribed source is the Bible.is New Testament (DDNBIV):** 21.6 h of read speech, already aligned verse by verse. It is copyrighted, and MMS was almost certainly trained on it.
- **There is a lot of untranscribed Dendi audio:** about 130 h of broadcast and sermons on YouTube, plus about 12 h of religious media. All of it is copyrighted.
- **Zarma (dje) is the closest language with open transcribed speech:** Omnilingual corpus, about 10.7 h, CC-BY-4.0.

## 2. Transcribed or alignable Dendi speech

| Resource | Size | Text | Licence / access | Status | Notes |
|---|---|---|---|---|---|
| Bible.is DDNBIV, non-drama (`DDNBIVN1DA`) | 21.55 h, 260 chapters, 7,958 verse timestamps (`mms_align`) | NT text `DDNBIVN_ET` (plain/USX/JSON) | Text © 2018 Bibles International, audio ℗ 2020 Hosanna/FCBH. `open_access: false`. DBP API key required. Training needs written permission | V | Single narrator, read speech, Bible domain. **Used to train MMS ddn, so do not use it as a test set for MMS or Omnilingual** |
| Bible.is DDNBIV, drama (`DDNBIVN2DA`) | 21.56 h | Same text, no timestamps | Same | V | Multiple voices plus music. Needs re-alignment |
| Bible.is Gospel Films (`DDNBIVP2DV`) | Mark ≈ 2.2 h, Luke ≈ 3.6 h | Same text | Same | V | Probably the drama soundtrack |
| Zenodo 6591186 (in use) | 48.7 min | Yes | CC-BY-4.0 | V | Numerals only |
| Pangloss Tersis 1968 (in use) | 39.4 min | Yes | CC-BY-NC-SA-4.0 | V | Tales from Karimama |
| JW tracts T-30…T-37 (jw.org, code DND) | ≈ 21 min, 8 MP3s | PDF/JWPUB text | © Watch Tower, personal use only | V | Small, read speech |

## 3. Untranscribed Dendi audio

| Resource | Size | Variety | Licence | Status |
|---|---|---|---|---|
| YouTube "Bénin TV Alafia – SRTB", Dendi news | 320 videos, ≈ 79 h (the channel has 626 h in total) | Benin | © SRTB | V |
| YouTube "Radio Bénin Alafia – SRTB", Dendi news | 45 videos, 9.5 h | Benin | © SRTB | V |
| Benin Eden TV "JT DENDI" | 44 videos, 11.5 h | Benin | © | V |
| Anfani Medias press reviews | 41 videos, 5.9 h | Benin | © | V |
| Sermons by Imam A. D. Touré (channel Mouhamadou NARO) | 49 videos, 29.3 h | Parakou | © | V |
| Other news and sermon channels (KOBOUROU TV, VFC, …) | ≈ 5 h | Benin | © | V |
| Health and civic spots (UNICEF, REDISSE, PNLP, Amnesty, …) | ≈ 2–3 h | Benin | © producers; scripts can be requested | V |
| Learner lessons (KOUGNANDE, ONG UP "Asuka Dendi") | ≈ 1.4 h | Benin | © | V |
| Niger (Gaya) vlogs and music | ≈ 1–10 h | Niger | © | V |
| JESUS Film, Malanville (id 1344) and Djougou (id 53326) | 121.7 + 127.9 min | **2 varieties** | © Jesus Film Project | V |
| GENESIS video (Scripture Earth) | 44 clips, ≈ 5.2 h (measured) | Benin | Rights unknown | V |
| Global Recordings Network: "Good News" (Malanville) and "Words of Life" (Djougou) | 49 + 22 min | 2 varieties | GRN, reportedly CC BY-NC-SA | V |
| `AfriSpeech/grn-african-speech` (GRN clips: ddn_dendi_benin, 2799 Malanville, 22743 Djougou) | 1.78 h, 15 s clips at 16 kHz | 3 varieties | "© GRN, research use" | V |
| `espnet/mms_ulab_v2`, ddn portion | Unknown (GRN-derived) | — | CC-BY-NC-SA-4.0 | V |

## 4. Models (baselines)

| Model | Licence | Status | Notes |
|---|---|---|---|
| `facebook/mms-1b-all` and `mms-1b-l1107`, `ddn` adapter | CC-BY-NC-4.0 | V | Its vocabulary uses `ɑ` (Latin alpha), ɛ, ɔ and few tones |
| Meta Omnilingual ASR, `ddn_Latn` | Apache-2.0 | V | No ddn data in the released corpus |
| `facebook/mms-tts-ddn` (VITS) | CC-BY-NC-4.0 | V | Synthetic augmentation only |
| `ssid32/wav2vec2-xlsr-dendi-ddn-for-numerals` (Noulinmon app, CreaTiv Team) | CC-BY-NC-4.0 | V | WER 18.18 on numerals. Directly comparable on Zenodo |
| `markjosims/wav2vec2-large-mms-1b-ddn-asr` | — | V | Empty |

## 5. Dendi text (language model, normalisation, prompts)

| Resource | Size | Licence | Status |
|---|---|---|---|
| Bible.is NT text (DDNBIV) | ≈ 8k verses | © | V |
| Open Bible Stories, Door43 `sostheneh/ddn-textStories-Dendi_OBS` | 50 stories | **CC BY-SA 4.0** | V |
| Wikipedia Incubator Wp/ddn | 71 articles | CC BY-SA | V |
| UDHR in Dendi (`cis-lmu/udhr-lid`) | 58 lines | CC0 | V |
| PanLex (ddn) | Word list | CC0 | V |
| Zima 1994, *Lexique Dendi (Djougou)* | ≈ 2,500 entries | Print (Köppe) | V |
| Tersis 1968, *Le parler dendi* | 87 pp | Print | V |
| CENALA alphabet; Moudachirou & Dossou 1988 transcription guide | Orthography | Print / IDRC | V / M |
| FineWeb-2 ddn, OPUS, NLLB, FLORES, MADLAD, Tatoeba | ≈ none | — | V (negative) |

GlotLID v3 identifies ddn_Latn and can be used to mine more text.

## 6. Related languages for transfer

| Resource | Language | Size | Licence | Status |
|---|---|---|---|---|
| `facebook/omnilingual-asr-corpus`, `dje_Latn` | Zarma | ≈ 10.7 h transcribed, 5 speakers | **CC-BY-4.0** | V |
| `27Group/salan` (LREC 2026) | Zarma + 7 Niger languages | dje archive 10.7 GB, partly pseudo-labels | CC-BY-4.0 on the card; gated | V |
| GRN clips (AfriSpeech): dje 6.57 h, ses 4.54 h, khq 3.65 h, hmb 0.91 h | Songhay | Untranscribed | © GRN | V |
| Bible.is SESNEW (ses), KHQBIV (khq), DJEBSC/DJEDPI (dje) | Songhay | ≈ 20 h+ each | © | V (IDs) |
| MMS adapters `ses`, `khq` | Songhay | — | CC-BY-NC | V |
| Zarma text: bible-uedin (CC0), google/smol, MT560, noisy_zarma, Feriji | Zarma | Up to 509k sentences | Various | V |

## 7. Not found

The following searches found nothing for Dendi:
- **Speech catalogues:** Common Voice, FLEURS, CMU Wilderness, OpenSLR, VoxLingua107, Kaggle, WaxalNLP, AfriSpeech-200, NaijaVoices, Kallaama.
- **Zenodo:** no other Dendi records; there was only one Dendi entry in the Zindi 2022 challenge.
- **Archives:** ELAR, PARADISEC, AILLA, Nakala. TLA has only incidental mentions.
- **Researchers and institutions:** no Dendi work by Jeffrey Heath, and no digitised Dendi audio at CELHTO.
- **Bible and religious platforms:** eBible, YouVersion, Bloom Library, QuranEnc, Quran.com.
- **Wikimedia and crowdsourced audio:** Lingua Libre, Commons audio, Wiktionary.
- **Other:** online radio archives for the named stations, and Dendi ASR or TTS papers.

## 8. People to contact

| Person | Why |
|---|---|
| Ross Patrick Azogbonon | Leads Wikipedia Wp/ddn; community contact |
| Jamiil Touré Ali | Author of Zenodo 6591186 |
| CreaTiv Team / Noulinmon (noulinmon.baruwuu.bj) | Private Dendi numerals data |
| Nicole Tersis (CNRS) | Pangloss tales; corrections are welcome |
| Robert Nicolaï | Dendi dialectology |
| SIL Bénin (M. Buchanan) | Survey and orthography |
| Anne Haour (UEA), Olivier Gosselain (ULB) | "Crossroads" project field audio |
| FCBH / Bibles International | Licence for DDNBIV |
| SRTB | Permission for Dendi news archives |
| UNICEF Bénin, PNLP, GANGAN PROD | Scripts of Dendi spots |

## 9. Implications for the benchmark

1. **Baselines:**
   - MMS-1b-all (ddn);
   - Omnilingual ASR (ddn_Latn);
   - Whisper (zero-shot);
   - the numerals XLSR model, on Zenodo only.
2. **Test sets must stay free of Bible audio**, because MMS and Omnilingual were very likely trained on it.
   - Candidate test sets: Pangloss, Zenodo, and a newly transcribed set of 1–2 h from SRTB news or the two JESUS Film varieties.
   - The JESUS Film script follows Luke, which helps with transcription.
3. **Training data:**
   - Zenodo and Pangloss (open);
   - plus DDNBIV if FCBH grants permission;
   - plus Zarma Omnilingual for transfer.
   - Pseudo-labelling the ≈ 130 h of broadcast audio is an option if SRTB agrees.
4. **Normalisation must reconcile 4 conventions:**
   - Zenodo (ɛ, ɔ, few tones);
   - Pangloss (e/o, full tones);
   - DDNBIV/MMS (ɑ, ɛ, ɔ, nasal marks);
   - OBS/JW ("Irikpɛ" vs "Ikpɛ").
5. **The cleanest way to get open data is to record OBS stories (CC BY-SA)** with several speakers from Parakou, Malanville and Djougou. That gives a redistributable, multi-speaker, multi-variety test set.
