"""
VoxMed_AI - Speech-to-Text
Takes recorded audio bytes (from the mic in the Streamlit app) and
returns the transcribed text using faster-whisper.
"""

import tempfile
import os
from faster_whisper import WhisperModel

# "small" gives noticeably better accuracy than "base", still runs
# reasonably fast on a laptop CPU. First run downloads the model
# (~500MB for "small"); it's cached after that.
_model = None


def get_model():
    """Load the Whisper model once and reuse it (loading is slow, so we cache it)."""
    global _model
    if _model is None:
        _model = WhisperModel("small", device="cpu", compute_type="int8")
    return _model


def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Takes raw audio bytes (e.g. from audio_recorder_streamlit),
    saves them temporarily, and returns the transcribed text.
    """
    model = get_model()

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        segments, info = model.transcribe(
            tmp_path,
            language="en",       # skip auto-detection, we know it's English
            vad_filter=True,     # strips silence/noise before transcribing
            beam_size=5,         # slightly more thorough search for best transcription
        )
        text = " ".join(segment.text for segment in segments)
        return text.strip()
    finally:
        os.remove(tmp_path)


if __name__ == "__main__":
    print("This module is meant to be used with recorded audio from the app.")
    print("Run frontend/app.py to test it with your microphone.")