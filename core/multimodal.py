# File: core/multimodal.py
"""
Multimodal input processing module.
Handles text, image (OCR with EasyOCR), and audio (ASR with faster-whisper).
"""

import io
import tempfile
import numpy as np
from pathlib import Path
from typing import Union

import easyocr
from faster_whisper import WhisperModel
from PIL import Image

from core.config import Config

# Lazy-loaded global models
_ocr_reader = None
_asr_model = None


def _get_ocr_reader():
    global _ocr_reader
    if _ocr_reader is None:
        _ocr_reader = easyocr.Reader(['en'], gpu=True)  # GPU if available, else CPU
    return _ocr_reader


def _get_asr_model():
    global _asr_model
    if _asr_model is None:
        _asr_model = WhisperModel("small", device="cpu", compute_type="int8")
    return _asr_model


def process_text_input(text: str) -> dict:
    return {
        "raw_text": text.strip(),
        "confidence": 1.0,
        "source": "text"
    }


def process_image_input(image: Union[Image.Image, bytes, Path, str]) -> dict:
    if isinstance(image, (str, Path)):
        image = Image.open(image)
    elif isinstance(image, bytes):
        image = Image.open(io.BytesIO(image))

    if image.mode != "RGB":
        image = image.convert("RGB")

    reader = _get_ocr_reader()
    results = reader.readtext(np.array(image), detail=1, paragraph=True)

    # Safe text extraction
    raw_text_parts = []
    confidences = []
    for res in results:
        if len(res) >= 2:
            raw_text_parts.append(res[1])
        if len(res) >= 3 and isinstance(res[2], (int, float)):
            confidences.append(res[2])

    raw_text = " ".join(raw_text_parts) if raw_text_parts else "(No text detected)"
    confidence = sum(confidences) / len(confidences) if confidences else 0.0

    return {
        "raw_text": raw_text.strip(),
        "confidence": round(float(confidence), 3),
        "source": "image"
    }


def process_audio_input(audio: Union[bytes, Path, str]) -> dict:
    model = _get_asr_model()

    if isinstance(audio, bytes):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio)
            audio_path = tmp.name
    else:
        audio_path = str(audio)

    segments, _ = model.transcribe(audio_path, beam_size=5, language="en")

    raw_text_parts = [seg.text.strip() for seg in segments]
    raw_text = " ".join(raw_text_parts)

    confidences = []
    for seg in segments:
        if hasattr(seg, "avg_logprob") and seg.avg_logprob is not None:
            confidences.append(np.exp(seg.avg_logprob))

    confidence = float(np.mean(confidences)) if confidences else 0.8

    if isinstance(audio, bytes):
        try:
            Path(audio_path).unlink(missing_ok=True)
        except Exception:
            pass  # ignore cleanup errors

    return {
        "raw_text": raw_text.strip() if raw_text else "(No audio detected)",
        "confidence": round(confidence, 3),
        "source": "audio"
    }