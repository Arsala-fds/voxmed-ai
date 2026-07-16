"""
VoxMed_AI - Text-to-Speech
Takes the final text answer from the orchestrator and converts it
to a spoken audio file using gTTS (Google Text-to-Speech).
"""

import tempfile
from gtts import gTTS


def text_to_speech(text: str) -> str:
    """
    Converts text into an audio file and returns the file path.
    The Streamlit app will play this file with st.audio().
    """
    tts = gTTS(text=text, lang="en")

    # mktemp just reserves a filename; gTTS creates the actual file
    out_path = tempfile.mktemp(suffix=".mp3")
    tts.save(out_path)

    return out_path


if __name__ == "__main__":
    sample_text = (
        "To treat a nosebleed, sit upright and lean slightly forward, "
        "then pinch the soft part of your nose for ten to fifteen minutes."
    )
    path = text_to_speech(sample_text)
    print(f"Audio saved to: {path}")
    print("Open this file to check it worked (e.g. 'open' command on Mac).")