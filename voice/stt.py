"""
VoxMed_AI - Speech-to-Text
Takes recorded audio bytes (from the mic in the Streamlit app) and
returns the transcribed text using faster-whisper.
"""

import tempfile
import os
from faster_whisper import WhisperModel

# "base" is a good balance of speed vs accuracy for a laptop.
# First run downloads the model (~150MB); it's cached after that.
_model = None


def get_model():
    """Load the Whisper model once and reuse it (loading is slow, so we cache it)."""
    global _model
    if _model is None:
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    return _model


def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Takes raw audio bytes (e.g. from audio_recorder_streamlit),
    saves them temporarily, and returns the transcribed text.
    """
    model = get_model()

    # Whisper needs a file path, so we write the bytes to a temp .wav file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        segments, info = model.transcribe(tmp_path)
        text = " ".join(segment.text for segment in segments)
        return text.strip()
    finally:
        os.remove(tmp_path)  # clean up the temp file either way


if __name__ == "__main__":
    print("This module is meant to be used with recorded audio from the app.")
    print("Run frontend/app.py to test it with your microphone.")