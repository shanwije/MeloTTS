import io
import re
import struct
import threading

import numpy as np
import soundfile
import torch

from melo.api import TTS


_lock = threading.Lock()
_models: dict[str, TTS] = {}
_voice_to_language: dict[str, str] = {}
_voice_to_speaker: dict[str, str] = {}


def init_models(device: str = "auto"):
    languages = {"EN": "EN-US", "ZH": "ZH"}
    for lang in languages:
        model = TTS(language=lang, device=device)
        _models[lang] = model
        for speaker_name in model.hps.data.spk2id:
            voice_key = speaker_name.lower()
            _voice_to_language[voice_key] = lang
            _voice_to_speaker[voice_key] = speaker_name


def get_voices() -> list[str]:
    return list(_voice_to_language.keys())


def _resolve_voice(voice: str) -> tuple[TTS, int]:
    voice_key = voice.lower()
    if voice_key not in _voice_to_language:
        raise ValueError(
            f"Unknown voice: {voice}. Available: {list(_voice_to_language.keys())}"
        )
    lang = _voice_to_language[voice_key]
    speaker_name = _voice_to_speaker[voice_key]
    model = _models[lang]
    speaker_id = model.hps.data.spk2id[speaker_name]
    return model, speaker_id


def _synthesize_sentence(model: TTS, text: str, speaker_id: int, speed: float) -> np.ndarray:
    language = model.language
    if language in ["EN", "ZH_MIX_EN"]:
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)

    from melo import utils

    device = model.device
    bert, ja_bert, phones, tones, lang_ids = utils.get_text_for_tts_infer(
        text, language, model.hps, device, model.symbol_to_id
    )
    with torch.no_grad():
        x_tst = phones.to(device).unsqueeze(0)
        tones = tones.to(device).unsqueeze(0)
        lang_ids = lang_ids.to(device).unsqueeze(0)
        bert = bert.to(device).unsqueeze(0)
        ja_bert = ja_bert.to(device).unsqueeze(0)
        x_tst_lengths = torch.LongTensor([phones.size(0)]).to(device)
        speakers = torch.LongTensor([speaker_id]).to(device)
        audio = (
            model.model.infer(
                x_tst, x_tst_lengths, speakers, tones, lang_ids, bert, ja_bert,
                sdp_ratio=0.2, noise_scale=0.6, noise_scale_w=0.8,
                length_scale=1.0 / speed,
            )[0][0, 0]
            .data.cpu()
            .float()
            .numpy()
        )
        del x_tst, tones, lang_ids, bert, ja_bert, x_tst_lengths, speakers
    return audio


def _silence_samples(sample_rate: int, speed: float) -> np.ndarray:
    n = int((sample_rate * 0.05) / speed)
    return np.zeros(n, dtype=np.float32)


def synthesize(text: str, voice: str, speed: float = 1.0, fmt: str = "wav") -> bytes:
    model, speaker_id = _resolve_voice(voice)
    sr = model.hps.data.sampling_rate
    sentences = model.split_sentences_into_pieces(text, model.language, quiet=True)

    audio_list = []
    with _lock:
        for sentence in sentences:
            audio_list.append(_synthesize_sentence(model, sentence, speaker_id, speed))
    torch.cuda.empty_cache()

    audio = TTS.audio_numpy_concat(audio_list, sr=sr, speed=speed)
    bio = io.BytesIO()
    soundfile.write(bio, audio, sr, format=fmt)
    bio.seek(0)
    return bio.read()


def synthesize_stream(text: str, voice: str, speed: float = 1.0, sample_rate: int | None = None):
    model, speaker_id = _resolve_voice(voice)
    sr = sample_rate or model.hps.data.sampling_rate
    sentences = model.split_sentences_into_pieces(text, model.language, quiet=True)
    silence = _silence_samples(sr, speed)

    with _lock:
        for i, sentence in enumerate(sentences):
            audio = _synthesize_sentence(model, sentence, speaker_id, speed)
            chunk = np.concatenate([audio.reshape(-1), silence]).astype(np.float32)
            is_last = i == len(sentences) - 1
            yield chunk, sr, i, is_last
    torch.cuda.empty_cache()


def audio_to_wav_bytes(audio: np.ndarray, sample_rate: int) -> bytes:
    bio = io.BytesIO()
    soundfile.write(bio, audio, sample_rate, format="wav")
    bio.seek(0)
    return bio.read()
