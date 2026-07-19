"""
VoxMed_AI - Premium SaaS UI v2 (chat history, refined spacing, hierarchy)
Backend/agent logic untouched - UI layer only.
"""

import sys
import os
import hashlib

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "voice"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "agents"))

import streamlit as st
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "voice", "mic_component"))
from mic_component import voxmed_mic

from stt import transcribe_audio
from tts import text_to_speech
from orchestrator import run_pipeline

st.set_page_config(page_title="VoxMed AI", page_icon="🩺", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {
    --s1: 8px; --s2: 16px; --s3: 24px; --s4: 32px;
    --accent: #3B82F6; --accent-light: #60A5FA;
}
* { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #0A0F1C; }
.main .block-container { padding-top: var(--s3); padding-bottom: var(--s4); max-width: 700px; }
.stApp, .stApp p, .stApp span, .stApp label, .stApp li { color: #e5e7eb; }

/* ---- Hero (full) ---- */
.vm-hero { text-align:center; margin-bottom: var(--s3); }
.vm-hero-icon { font-size:44px; margin-bottom: var(--s1); }
.vm-hero-title {
    font-size: 56px; font-weight: 800; margin: 0 0 8px; letter-spacing:-1.5px;
    background: linear-gradient(180deg, #FFFFFF 0%, #C7D2FE 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.vm-hero-sub { font-size: 15px; color: #8B93A7; margin-bottom: var(--s2); font-weight:500; letter-spacing: 0.2px; }
.vm-trust-row { display:flex; justify-content:center; gap:var(--s1); flex-wrap:wrap; }
.vm-trust-pill { background: rgba(59,130,246,0.1); color: #93C5FD; border: 1px solid rgba(59,130,246,0.25); padding: 5px 14px; border-radius: 999px; font-size: 12px; font-weight: 600; }

/* ---- Hero (compact, after first message) ---- */
.vm-hero-compact { display:flex; align-items:center; justify-content:center; gap:10px; margin-bottom:var(--s2); padding-bottom:var(--s2); border-bottom:1px solid rgba(255,255,255,0.06); }
.vm-hero-compact .icon { font-size:20px; }
.vm-hero-compact .title { font-size:24px; font-weight:800; color:#fff; }

.vm-disclaimer { background: rgba(251,191,36,0.08); border: 1px solid rgba(251,191,36,0.25); color: #FCD34D; padding: 10px 16px; border-radius: 12px; font-size: 13px; margin: var(--s2) 0; }

/* ---- Mic ---- */
.vm-mic-wrap { display:flex; flex-direction:column; align-items:center; margin: var(--s3) 0; }

.vm-processing { display:flex; align-items:center; justify-content:center; gap:8px; margin-top:var(--s1); font-size:13px; color:#38BDF8; font-weight:600; }
.vm-spinner-dot { width:7px; height:7px; border-radius:50%; background:#38BDF8; animation: vm-blink 1s ease-in-out infinite; }
@keyframes vm-blink { 0%,100%{opacity:0.3;} 50%{opacity:1;} }

/* ---- Chat ---- */
.vm-turn { animation: vm-fadein .35s ease; margin-bottom: var(--s3); }
@keyframes vm-fadein { from{opacity:0; transform:translateY(6px);} to{opacity:1; transform:translateY(0);} }
.vm-user-row { display:flex; justify-content:flex-end; margin-bottom: var(--s1); }
.vm-user-bubble { background: linear-gradient(135deg, #202C42, #182338); border: 1px solid rgba(59,130,246,0.28); border-radius: 16px 16px 4px 16px; padding: 11px 16px; max-width: 78%; font-size: 14.5px; color: #DBEAFE; letter-spacing: 0.1px; box-shadow: inset 0 1px 0 rgba(255,255,255,0.04); }

.vm-ai-card {
    background: linear-gradient(180deg, #141b2c 0%, #0f1420 100%);
    border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; padding: var(--s3);
    box-shadow: 0 6px 24px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.05);
    transition: box-shadow .2s ease;
}
.vm-ai-card:hover { box-shadow: 0 10px 34px rgba(59,130,246,0.12), inset 0 1px 0 rgba(255,255,255,0.06); }
.vm-ai-card.emergency { border: 1px solid rgba(239,68,68,0.45); box-shadow: 0 0 20px rgba(239,68,68,0.12), inset 0 1px 0 rgba(255,255,255,0.05); }
.vm-ai-header { font-size: 12px; font-weight: 700; color: #7C9CF0; letter-spacing: 1.4px; margin-bottom: var(--s1); }
.vm-badge { display:inline-block; padding: 5px 13px; border-radius: 999px; font-size: 11.5px; font-weight: 700; margin-bottom: var(--s2); }
.vm-badge-emergency { background: rgba(239,68,68,0.12); color: #FCA5A5; border: 1px solid rgba(239,68,68,0.35); }
.vm-badge-verified { background: rgba(16,185,129,0.12); color: #6EE7B7; border: 1px solid rgba(16,185,129,0.35); }
.vm-badge-general { background: rgba(59,130,246,0.12); color: #93C5FD; border: 1px solid rgba(59,130,246,0.35); }
.vm-answer-text { font-size: 15.5px; line-height: 1.75; color: #F4F6F8; margin: 0 0 var(--s2); letter-spacing: 0.1px; }
.vm-divider { height:1px; background: rgba(255,255,255,0.07); margin: var(--s2) 0; }
.vm-sources-label { font-size: 11px; color: #6B7280; text-transform: uppercase; letter-spacing: 1.1px; margin-bottom: 0; font-weight:700; }
.vm-sources-toggle { display:flex; align-items:center; gap:6px; cursor:pointer; user-select:none; width:fit-content; }
.vm-sources-arrow {
    display:flex; align-items:center; justify-content:center;
    width:16px; height:16px; border-radius:5px; font-size:9px; color:#6B7280;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    transition: transform .25s ease, color .25s ease, background .25s ease;
}
.vm-sources-wrap:hover .vm-sources-arrow { transform: rotate(180deg); color:#93C5FD; background: rgba(59,130,246,0.12); }
.vm-sources-content {
    max-height:0; opacity:0; overflow:hidden; margin-top:0;
    transition: max-height 1.1s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.9s ease, margin-top 1.1s cubic-bezier(0.22, 1, 0.36, 1);
}
.vm-sources-wrap:hover .vm-sources-content { max-height:400px; opacity:1; margin-top:10px; overflow:visible; transition-delay: 0.15s; }
.vm-source-chip {
    display:inline-flex; align-items:center; gap:7px;
    background: #141b2b; border: 1px solid rgba(255,255,255,0.08);
    color: #CBD5E1; padding: 6px 12px 6px 8px; border-radius: 10px;
    font-size: 12px; margin: 0 8px 8px 0; position: relative; cursor: default;
    transition: all .18s ease;
}
.vm-source-chip:hover { border-color: rgba(59,130,246,0.35); background: #182338; transform: translateY(-1px); }
.vm-source-icon {
    width:18px; height:18px; border-radius:6px; flex-shrink:0;
    display:flex; align-items:center; justify-content:center; font-size:10.5px;
}
.vm-source-icon.official { background: rgba(16,185,129,0.15); color:#34D399; }
.vm-source-icon.curated { background: rgba(59,130,246,0.15); color:#60A5FA; }
.vm-source-name { font-weight:600; color:#E5E7EB; }
.vm-source-tier {
    font-size:9px; font-weight:700; letter-spacing:0.6px; text-transform:uppercase;
    padding:2px 6px; border-radius:5px; margin-left:2px;
}
.vm-source-tier.official { background: rgba(16,185,129,0.12); color:#6EE7B7; }
.vm-source-tier.curated { background: rgba(59,130,246,0.12); color:#93C5FD; }
.vm-source-chip[data-tooltip]:hover::after {
    content: attr(data-tooltip);
    position:absolute; bottom:calc(100% + 9px); left:50%; transform:translateX(-50%);
    background:#1f2937; color:#E5E7EB; padding:7px 11px; border-radius:8px;
    font-size:11px; font-weight:500; white-space:nowrap; max-width:260px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.45); border:1px solid rgba(255,255,255,0.1);
    z-index:20; pointer-events:none;
}
.vm-source-chip[data-tooltip]:hover::before {
    content:''; position:absolute; bottom:calc(100% + 3px); left:50%; transform:translateX(-50%);
    border:5px solid transparent; border-top-color:#1f2937; z-index:20; pointer-events:none;
}

audio { width: 100%; height: 36px; border-radius: 999px; filter: invert(0.9) hue-rotate(180deg) brightness(1.1); }

/* Compact icon feedback buttons */
.vm-feedback-row { display:flex; gap: var(--s1); margin-top: var(--s2); }
div[data-testid="column"] .stButton > button {
    background: #1a2332 !important; color: #9CA3AF !important;
    border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 10px !important;
    padding: 4px 10px !important; font-size: 13px !important; min-height: 30px !important;
    transition: all .15s ease !important;
}
div[data-testid="column"] .stButton > button:hover { border-color: #3B82F6 !important; color: #60A5FA !important; transform: translateY(-1px); }

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


def get_source_meta(filename: str) -> dict:
    """
    Classifies a source file into a credibility tier so the UI can show
    *why* it's trustworthy, not just its name.
    """
    name = filename.replace(".txt", "").replace("_", " ").title()
    if "first aid steps" in name.lower():
        return {
            "label": "Curated First-Aid Reference",
            "icon": "✚",
            "tier_class": "curated",
            "tier_label": "Curated",
            "tooltip": "Reviewed first-aid reference compiled for this assistant",
        }
    return {
        "label": f"MedlinePlus · {name}",
        "icon": "🏛",
        "tier_class": "official",
        "tier_label": "Official",
        "tooltip": "U.S. National Library of Medicine (NIH) — government health resource",
    }


sync_secrets_to_env()
ensure_knowledge_base()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None

has_chatted = len(st.session_state.messages) > 0

if not has_chatted:
    st.markdown(
"""<div class="vm-hero">
<div class="vm-hero-icon">🩺</div>
<div class="vm-hero-title">VoxMed AI</div>
<div class="vm-hero-sub">Trusted AI Medical Assistant</div>
<div class="vm-trust-row">
<span class="vm-trust-pill">🛡 Trusted</span>
<span class="vm-trust-pill">📚 Grounded Sources</span>
<span class="vm-trust-pill">🤖 AI Powered</span>
</div>
</div>""", unsafe_allow_html=True)
    st.markdown('<div class="vm-disclaimer">⚠️ Educational demo only. Not a substitute for professional medical advice.</div>', unsafe_allow_html=True)
else:
    st.markdown(
'''<div class="vm-hero-compact">
<span class="icon">🩺</span><span class="title">VoxMed AI</span>
</div>''', unsafe_allow_html=True)

audio_bytes = voxmed_mic(key="mic")
processing_placeholder = st.empty()

if audio_bytes:
    audio_hash = hashlib.md5(audio_bytes).hexdigest()
    if audio_hash != st.session_state.last_audio_hash:
        st.session_state.last_audio_hash = audio_hash
        processing_placeholder.markdown(
            '<div class="vm-processing"><div class="vm-spinner-dot"></div>Processing...</div>',
            unsafe_allow_html=True
        )
        query = transcribe_audio(audio_bytes)
        processing_placeholder.empty()

        if query.strip():
            result = run_pipeline(query, conversation_history=st.session_state.messages)
            audio_path = text_to_speech(result["answer"])
            st.session_state.messages.append({
                "query": query,
                "answer": result["answer"],
                "sources": result["sources"],
                "is_emergency": result["is_emergency"],
                "answer_type": result["answer_type"],
                "audio_path": audio_path,
            })
            st.rerun()
        else:
            st.warning("Couldn't detect any speech. Please try again.")

for i, msg in enumerate(st.session_state.messages):
    st.markdown(
f'''<div class="vm-turn">
<div class="vm-user-row">
<div class="vm-user-bubble">{msg["query"]}</div>
</div>''', unsafe_allow_html=True)

    card_class = "vm-ai-card emergency" if msg["is_emergency"] else "vm-ai-card"
    if msg["is_emergency"]:
        badge_html = '<span class="vm-badge vm-badge-emergency">⚠ Medical Emergency</span>'
    elif msg["answer_type"] == "verified":
        badge_html = '<span class="vm-badge vm-badge-verified">✓ Verified Source</span>'
    else:
        badge_html = '<span class="vm-badge vm-badge-general">ⓘ General Knowledge</span>'

    sources_html = ""
    if msg["sources"]:
        chip_parts = []
        for s in msg["sources"]:
            meta = get_source_meta(s)
            chip_parts.append(
                f'<span class="vm-source-chip" data-tooltip="{meta["tooltip"]}">'
                f'<span class="vm-source-icon {meta["tier_class"]}">{meta["icon"]}</span>'
                f'<span class="vm-source-name">{meta["label"]}</span>'
                f'<span class="vm-source-tier {meta["tier_class"]}">{meta["tier_label"]}</span>'
                f'</span>'
            )
        chips = "".join(chip_parts)
        sources_html = (
            '<div class="vm-divider"></div>'
            '<div class="vm-sources-wrap">'
            '<div class="vm-sources-toggle">'
            '<p class="vm-sources-label">Sources</p>'
            '<span class="vm-sources-arrow">▾</span>'
            '</div>'
            f'<div class="vm-sources-content">{chips}</div>'
            '</div>'
        )

    st.markdown(
f'''<div class="{card_class}">
<p class="vm-ai-header">VOXMED</p>
{badge_html}
<p class="vm-answer-text">{msg["answer"]}</p>
{sources_html}
<div class="vm-divider"></div>
<p class="vm-sources-label">Listen</p>''', unsafe_allow_html=True)
    st.audio(msg["audio_path"], format="audio/mp3")
    st.markdown('</div></div>', unsafe_allow_html=True)

    col1, col2, _ = st.columns([0.6, 0.6, 4])
    with col1:
        st.button("👍", key=f"up_{i}")
    with col2:
        st.button("👎", key=f"down_{i}")