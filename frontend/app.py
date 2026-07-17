"""
VoxMed_AI - Voice Interface
The main Streamlit app: mic input -> Whisper -> Orchestrator (4 agents)
-> TTS -> spoken answer.

Run with:
    streamlit run frontend/app.py
"""

import sys
import os

# allow importing from voice/ and agents/ (sibling folders)
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "voice"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "agents"))

import streamlit as st
from audio_recorder_streamlit import audio_recorder

from stt import transcribe_audio
from tts import text_to_speech
from orchestrator import run_pipeline


st.set_page_config(page_title="VoxMed_AI", page_icon="🩺")
st.title("🩺 VoxMed_AI")
st.caption("Voice-based medical knowledge assistant (grounded, source-cited)")

st.warning(
    "Educational demo only. Not a substitute for professional medical advice.",
    icon="⚠️",
)

st.subheader("🎙️ Press the mic and ask your question")
audio_bytes = audio_recorder(pause_threshold=2.0)

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")

    with st.spinner("Transcribing your question..."):
        query = transcribe_audio(audio_bytes)

    st.markdown(f"**You asked:** {query}")

    if query.strip():
        with st.spinner("Thinking through your question..."):
            result = run_pipeline(query)

        if result["is_emergency"]:
            st.error("⚠️ This may be a medical emergency - see details below.")

        st.markdown(f"**VoxMed:** {result['answer']}")

        with st.expander("📚 Sources used"):
            for src in result["sources"]:
                st.write(f"- {src}")

        with st.spinner("Generating voice response..."):
            audio_path = text_to_speech(result["answer"])
        st.audio(audio_path, format="audio/mp3")
    else:
        st.warning("Couldn't detect any speech. Please try again.")