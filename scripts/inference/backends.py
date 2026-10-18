"""One class per model family. Heavy libraries are imported inside each class so that
each family can live in its own environment (transformers / omnilingual-asr / google-cloud-speech)."""
import importlib.metadata as md

import numpy as np

from common import SR, split_on_silence


def _versions(*pkgs):
    out = {}
    for p in pkgs:
        try:
            out[p] = md.version(p)
        except md.PackageNotFoundError:
            out[p] = None
    return out


class MMS:
    """facebook/mms-1b-all with the Dendi adapter (CTC, greedy decoding)."""

    def __init__(self, model_id="facebook/mms-1b-all", lang="ddn", device=None):
        import torch
        from transformers import AutoProcessor, Wav2Vec2ForCTC

        self.torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.processor.tokenizer.set_target_lang(lang)
        self.model = Wav2Vec2ForCTC.from_pretrained(model_id, target_lang=lang,
                                                    ignore_mismatched_sizes=True).to(self.device).eval()
        self.name = "mms-1b-all-ddn"
        self.config = dict(model_id=model_id, target_lang=lang, decoding="greedy CTC",
                           revision=getattr(self.model.config, "_commit_hash", None), device=self.device)

    def versions(self):
        return _versions("torch", "transformers")

    def transcribe(self, audio: np.ndarray, row):
        inputs = self.processor(audio, sampling_rate=SR, return_tensors="pt").to(self.device)
        with self.torch.inference_mode():
            logits = self.model(**inputs).logits
        ids = logits.argmax(dim=-1)[0]
        return self.processor.decode(ids), "ddn", 1


class Whisper:
    """openai/whisper-large-v3(-turbo), automatic language detection, greedy decoding.
    Audio over 30 s uses Whisper's sequential long-form decoding."""

    def __init__(self, model_id="openai/whisper-large-v3", device=None):
        import torch
        from transformers import AutoProcessor, WhisperForConditionalGeneration

        self.torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = WhisperForConditionalGeneration.from_pretrained(
            model_id, torch_dtype=self.dtype).to(self.device).eval()
        gc = self.model.generation_config
        self.lang_ids = {tok: i for tok, i in gc.lang_to_id.items()}
        self.sot = gc.decoder_start_token_id
        self.gen_kwargs = dict(task="transcribe", num_beams=1, do_sample=False,
                               condition_on_prev_tokens=False, max_new_tokens=440)
        self.name = model_id.split("/")[-1]
        self.config = dict(model_id=model_id, language="auto-detect", dtype=str(self.dtype),
                           revision=getattr(self.model.config, "_commit_hash", None),
                           long_form="sequential, return_timestamps=True, >30 s only",
                           device=self.device, **self.gen_kwargs)

    def versions(self):
        return _versions("torch", "transformers")

    def _features(self, audio, long_form):
        kw = dict(truncation=False, padding="longest", return_attention_mask=True) if long_form else {}
        f = self.processor(audio, sampling_rate=SR, return_tensors="pt", **kw)
        return f.to(self.device, self.dtype) if hasattr(f, "to") else f

    def _detect_language(self, feats):
        """Language token with the highest probability after <|startoftranscript|> (first 30 s)."""
        dec = self.torch.tensor([[self.sot]], device=self.device)
        with self.torch.inference_mode():
            logits = self.model(input_features=feats[:, :, :3000], decoder_input_ids=dec).logits[0, -1]
        ids = list(self.lang_ids.values())
        best = ids[int(logits[ids].argmax())]
        return next(t for t, i in self.lang_ids.items() if i == best).strip("<|>")

    def transcribe(self, audio: np.ndarray, row):
        long_form = len(audio) > 30 * SR
        lang = self._detect_language(self._features(audio[: 30 * SR], False).input_features)
        f = self._features(audio, long_form)
        kw = dict(self.gen_kwargs)
        if long_form:
            kw.update(attention_mask=f.attention_mask, return_timestamps=True)
        with self.torch.inference_mode():
            ids = self.model.generate(f.input_features, **kw)
        text = self.processor.batch_decode(ids, skip_special_tokens=True)[0]
        return text.strip(), lang, int(np.ceil(len(audio) / (30 * SR)))


class Omnilingual:
    """Meta Omnilingual ASR (omniASR_CTC_1B_v2, omniASR_LLM_7B_v2) with lang=ddn_Latn.
    Inputs over max_s are cut at pauses (common.split_on_silence) and the parts' outputs joined."""

    def __init__(self, model_card="omniASR_LLM_7B_v2", lang="ddn_Latn", max_s=39.0):
        from omnilingual_asr.models.inference.pipeline import ASRInferencePipeline

        self.pipeline = ASRInferencePipeline(model_card=model_card)
        self.lang, self.max_s = lang, max_s
        self.name = model_card
        self.config = dict(model_card=model_card, lang=lang, batch_size=1,
                           chunking=f"split_on_silence above {max_s} s (API limit: < 40 s)")

    def versions(self):
        return _versions("omnilingual-asr", "fairseq2", "torch")

    def transcribe(self, audio: np.ndarray, row):
        chunks = split_on_silence(audio, self.max_s)
        data = [{"waveform": c, "sample_rate": SR} for c in chunks]
        out = self.pipeline.transcribe(data, lang=[self.lang] * len(data), batch_size=1)
        texts = [o if isinstance(o, str) else getattr(o, "text", str(o)) for o in out]
        return " ".join(t.strip() for t in texts), self.lang, len(chunks)


class Chirp3:
    """Google Cloud Speech-to-Text v2, model chirp_3, language_codes=["auto"] (Dendi is not an
    officially supported language: results are exploratory). Needs GOOGLE_CLOUD_PROJECT and
    application-default credentials. Sync Recognize accepts < 60 s, our longest input is 48 s."""

    def __init__(self, project=None, region="us"):
        import os

        from google.api_core.client_options import ClientOptions
        from google.cloud.speech_v2 import SpeechClient
        from google.cloud.speech_v2.types import cloud_speech

        self.cs = cloud_speech
        self.project = project or os.environ["GOOGLE_CLOUD_PROJECT"]
        self.region = region
        self.client = SpeechClient(client_options=ClientOptions(api_endpoint=f"{region}-speech.googleapis.com"))
        self.recognizer = f"projects/{self.project}/locations/{region}/recognizers/_"
        self.rec_config = cloud_speech.RecognitionConfig(
            auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
            language_codes=["auto"], model="chirp_3")
        self.name = "chirp_3"
        self.config = dict(model="chirp_3", language_codes=["auto"], region=region,
                           api="speech_v2 Recognize (sync)", denoiser=False)

    def versions(self):
        return _versions("google-cloud-speech")

    def transcribe(self, audio: np.ndarray, row):
        from common import ROOT

        content = (ROOT / row.audio_path).read_bytes()
        resp = self.client.recognize(request=self.cs.RecognizeRequest(
            recognizer=self.recognizer, config=self.rec_config, content=content))
        texts = [r.alternatives[0].transcript for r in resp.results if r.alternatives]
        langs = sorted({r.language_code for r in resp.results if r.language_code})
        return " ".join(texts), ",".join(langs), len(resp.results)
