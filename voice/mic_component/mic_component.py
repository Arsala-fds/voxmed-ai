"""
VoxMed_AI - Custom Mic Component (Python wrapper)
Wraps the static HTML/JS frontend in voice/mic_component/frontend/
as a real Streamlit bidirectional component.
"""

import os
import base64
import streamlit.components.v1 as components

_frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
_mic_component = components.declare_component("voxmed_mic", path=_frontend_dir)


def voxmed_mic(key: str = "voxmed_mic"):
    """
    Renders the custom animated mic button.
    Returns raw audio bytes (webm) once a recording completes, or None
    if nothing has been recorded yet / rerun didn't produce a new value.
    """
    result = _mic_component(key=key, default=None)
    if result and "audio_base64" in result:
        return base64.b64decode(result["audio_base64"])
    return None