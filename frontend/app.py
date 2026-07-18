"""
VoxMed_AI - Premium SaaS UI
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "voice"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "agents"))

import streamlit as st
from audio_recorder_streamlit import audio_recorder

from stt import transcribe_audio
from tts import text_to_speech
from orchestrator import run_pipeline

st.set_page_config(page_title="VoxMed AI", page_icon="🩺", layout="centered")

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
* { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #0B1220; }
.main .block-container { padding-top: 3rem; padding-bottom: 4rem; max-width: 700px; }
.stApp, .stApp p, .stApp span, .stApp label, .stApp li { color: #e5e7eb; }

/* ---------- Hero ---------- */
.vm-hero { text-align:center; margin-bottom: 32px; }
.vm-hero-icon { font-size:36px; }
.vm-hero-title {
    font-size: 44px; font-weight: 800; margin: 8px 0 6px; letter-spacing:-1.2px;
    background: linear-gradient(90deg, #3B82F6, #60A5FA, #38BDF8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.vm-hero-sub { font-size: 16px; color: #9CA3AF; margin-bottom: 14px; font-weight:500; }
.vm-trust-row { display:flex; justify-content:center; gap:10px; flex-wrap:wrap; }
.vm-trust-pill {
    background: rgba(59,130,246,0.1); color: #93C5FD; border: 1px solid rgba(59,130,246,0.25);
    padding: 6px 16px; border-radius: 999px; font-size: 12.5px; font-weight: 600;
    transition: all .2s ease;
}
.vm-trust-pill:hover { background: rgba(59,130,246,0.18); transform: translateY(-1px); }

/* ---------- Disclaimer ---------- */
.vm-disclaimer {
    background: rgba(251,191,36,0.08); border: 1px solid rgba(251,191,36,0.25);
    color: #FCD34D; padding: 12px 18px; border-radius: 14px; font-size: 13.5px;
    margin: 22px 0; display:flex; align-items:center; gap:10px;
}

/* ---------- Mic ---------- */
.vm-mic-wrap { display:flex; flex-direction:column; align-items:center; margin: 36px 0 30px; }
.vm-mic-glow {
    width: 96px; height: 96px; border-radius: 50%;
    background: radial-gradient(circle, rgba(59,130,246,0.35) 0%, rgba(59,130,246,0.05) 70%);
    display:flex; align-items:center; justify-content:center;
    animation: vm-pulse 2.4s ease-in-out infinite;
    margin-bottom: 4px;
}
@keyframes vm-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(59,130,246,0.25); }
    50% { box-shadow: 0 0 0 18px rgba(59,130,246,0); }
}
.vm-mic-label {
    margin-top: 14px; font-size: 13px; font-weight: 700; letter-spacing: 1.2px;
    color: #60A5FA; text-transform: uppercase;
}
.vm-mic-processing {
    margin-top: 10px; font-size: 12.5px; color: #38BDF8; font-weight:600;
    animation: vm-blink 1.4s ease-in-out infinite;
}
@keyframes vm-blink { 0%,100%{opacity:1;} 50%{opacity:0.4;} }

/* audio-recorder component container */
div[title="record-icon"], .audio-recorder { margin: 0 auto !important; }

/* ---------- Chat ---------- */
.vm-user-row { display:flex; justify-content:flex-end; margin: 20px 0 10px; animation: vm-fadein .35s ease; }
.vm-user-bubble {
    background: linear-gradient(135deg, #1E293B, #1a2436); border: 1px solid rgba(59,130,246,0.25);
    border-radius: 18px 18px 4px 18px; padding: 13px 18px; max-width: 78%;
    font-size: 15px; color: #DBEAFE; box-shadow: 0 4px 14px rgba(0,0,0,0.25);
}
.vm-ai-row { margin: 6px 0 22px; animation: vm-fadein .45s ease; }
@keyframes vm-fadein { from{opacity:0; transform:translateY(6px);} to{opacity:1; transform:translateY(0);} }

.vm-ai-card {
    background: #111827; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; padding: 24px 26px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.35);
    transition: box-shadow .25s ease;
}
.vm-ai-card:hover { box-shadow: 0 8px 36px rgba(59,130,246,0.12); }
.vm-ai-card.emergency { border: 1px solid rgba(239,68,68,0.45); box-shadow: 0 0 24px rgba(239,68,68,0.15); }

.vm-ai-name { font-size: 13px; font-weight: 700; color: #60A5FA; letter-spacing: 1px; margin-bottom: 12px; }
.vm-answer-text { font-size: 15.5px; line-height: 1.7; color: #F1F5F9; margin: 4px 0 18px; }

/* ---------- Badges ---------- */
.vm-badge { display:inline-block; padding: 6px 15px; border-radius: 999px; font-size: 12px; font-weight: 700; margin-bottom: 16px; }
.vm-badge-emergency { background: rgba(239,68,68,0.12); color: #FCA5A5; border: 1px solid rgba(239,68,68,0.35); }
.vm-badge-verified { background: rgba(16,185,129,0.12); color: #6EE7B7; border: 1px solid rgba(16,185,129,0.35); }
.vm-badge-general { background: rgba(59,130,246,0.12); color: #93C5FD; border: 1px solid rgba(59,130,246,0.35); }

/* ---------- Sources ---------- */
.vm-sources-label { font-size: 11.5px; color: #6B7280; text-transform: uppercase; letter-spacing: 1.2px; margin: 4px 0 10px; font-weight:700; }
.vm-source-chip {
    display:inline-block; background: #1a2332; border: 1px solid rgba(255,255,255,0.1);
    color: #CBD5E1; padding: 6px 14px; border-radius: 999px; font-size: 12px; margin: 0 6px 6px 0;
    transition: all .2s ease;
}
.vm-source-chip:hover { border-color: #3B82F6; color: #93C5FD; }

/* ---------- Divider ---------- */
.vm-divider { height:1px; background: rgba(255,255,255,0.08); margin: 18px 0; }

/* ---------- Audio player ---------- */
audio { width: 100%; border-radius: 999px; height: 40px; }
audio::-webkit-media-controls-panel { background-color: #1a2332; }

/* ---------- Feedback buttons ---------- */
.stButton > button {
    background: #1a2332 !important; color: #CBD5E1 !important;
    border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 12px !important;
    padding: 6px 16px !important; font-size: 13px !important; font-weight:600 !important;
    transition: all .2s ease !important;
}
.stButton > button:hover { border-color: #3B82F6 !important; color: #60A5FA !important; transform: translateY(-1px); }

.stSpinner > div { border-top-color: #3B82F6 !important; }
</style>
""", unsafe_allow_html=True)


def sync_secrets_to_env():
    try:
        if "GROQ_API_KEY" in st.secrets:
            os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass


def ensure_knowledge_base():
    db_path = os.path.join(os.path.dirname(__file__), "..", "rag", "chroma_db")
    if not os.path.exists(db_path):
        with st.spinner("First-time setup: building the medical knowledge base..."):
            sys.path.append(os.path.join(os.path.dirname(__file__), "..", "rag"))
            import fetch_medlineplus
            import ingest
            fetch_medlineplus.main()
            ingest.main()


def pretty_source(filename: str) -> str:
    name = filename.replace(".txt", "").replace("_", " ").title()
    if "first aid steps" in name.lower():
        return "Curated First-Aid Reference"
    return f"MedlinePlus · {name}"


sync_secrets_to_env()
ensure_knowledge_base()

# ---------- Hero ----------
st.markdown('''
<div class="vm-hero">
    <div class="vm-hero-icon">🩺</div>
    <div class="vm-hero-title">VoxMed AI</div>
    <div class="vm-hero-sub">Voice-based Medical Assistant</div>
    <div class="vm-trust-row">
        <span class="vm-trust-pill">Trusted</span>
        <span class="vm-trust-pill">Source Grounded</span>
        <span class="vm-trust-pill">AI Powered</span>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div class="vm-disclaimer">⚠️ Educational demo only. Not a substitute for professional medical advice.</div>
''', unsafe_allow_html=True)

# ---------- Mic ----------
st.markdown('<div class="vm-mic-wrap"><div class="vm-mic-glow">', unsafe_allow_html=True)
audio_bytes = audio_recorder(pause_threshold=2.0, icon_size="2x", recording_color="#EF4444", neutral_color="#3B82F6")
st.markdown('</div><p class="vm-mic-label">Tap to Speak</p></div>', unsafe_allow_html=True)

if audio_bytes:
    processing_placeholder = st.empty()
    processing_placeholder.markdown('<p style="text-align:center" class="vm-mic-processing">● Processing your question...</p>', unsafe_allow_html=True)

    query = transcribe_audio(audio_bytes)
    processing_placeholder.empty()

    if query.strip():
        st.markdown(f'''
        <div class="vm-user-row">
            <div class="vm-user-bubble">{query}</div>
        </div>
        ''', unsafe_allow_html=True)

        with st.spinner(""):
            result = run_pipeline(query)

        card_class = "vm-ai-card emergency" if result["is_emergency"] else "vm-ai-card"

        if result["is_emergency"]:
            badge_html = '<span class="vm-badge vm-badge-emergency">⚠ Medical Emergency</span>'
        elif result["answer_type"] == "verified":
            badge_html = '<span class="vm-badge vm-badge-verified">✓ Verified Source</span>'
        else:
            badge_html = '<span class="vm-badge vm-badge-general">ⓘ General Knowledge</span>'

        sources_html = ""
        if result["sources"]:
            chips = "".join(f'<span class="vm-source-chip">{pretty_source(s)}</span>' for s in result["sources"])
            sources_html = f'<div class="vm-divider"></div><p class="vm-sources-label">Sources</p>{chips}'

        st.markdown(f'''
        <div class="vm-ai-row">
            <div class="{card_class}">
                <p class="vm-ai-name">VOXMED</p>
                {badge_html}
                <p class="vm-answer-text">{result["answer"]}</p>
                {sources_html}
            </div>
        </div>
        ''', unsafe_allow_html=True)

        audio_path = text_to_speech(result["answer"])
        st.markdown('<p class="vm-sources-label" style="margin-top:18px">🔊 Listen</p>', unsafe_allow_html=True)
        st.audio(audio_path, format="audio/mp3")

        col1, col2, _ = st.columns([1, 1, 3])
        with col1:
            st.button("👍 Helpful", key="helpful_btn")
        with col2:
            st.button("👎 Not helpful", key="not_helpful_btn")
    else:
        st.warning("Couldn't detect any speech. Please try again.")