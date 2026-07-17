
# 🩺 VoxMed_AI

**A voice-based, retrieval-grounded medical knowledge assistant powered by agentic AI.**

Ask a medical question by speaking. VoxMed_AI transcribes it, retrieves verified information from a curated medical knowledge base, reasons through it using an LLM, checks for medical emergencies, and speaks a grounded, source-cited answer back to you.

> ⚠️ **Educational demo only.** This is not a certified medical device and does not replace professional medical advice.

---

🔗 **[Try the live demo](https://voxmed-ai-6xcqes9sdj5js97usougza.streamlit.app)**

## Why VoxMed_AI

Most AI chatbots answer medical questions from unverified internal knowledge, which can hallucinate. VoxMed_AI is built to **never do that** — every answer is generated strictly from retrieved, verified source documents (MedlinePlus and curated first-aid references), with source citations shown for every response. A dedicated Safety Agent also screens every query for emergency indicators before responding.

## Architecture



🎙️ Voice input (mic)

↓

Whisper (speech-to-text)

↓

┌─────────────────────────────────────┐

│         Agent Orchestration          │

│  Intake → Retrieval → Reasoning →    │

│              Safety                  │

└─────────────────────────────────────┘

↓                    ↓

RAG Pipeline         LLM (Groq/Llama)

(ChromaDB +

sentence-transformers)

↓

gTTS (text-to-speech)

↓

🔊 Spoken, source-cited answer



Four specialized agents work together:

- **Intake Agent** — cleans the query, does a first-pass emergency keyword check
- **Retrieval Agent** — runs the RAG pipeline to find the most relevant knowledge chunks
- **Reasoning Agent** — generates a grounded answer strictly from retrieved context (LLM)
- **Safety Agent** — classifies emergency risk using the LLM and prepends urgent-care guidance when needed

## Tech Stack

| Layer       | Technology                                                   |
| ----------- | ------------------------------------------------------------ |
| Voice (STT) | faster-whisper                                               |
| Voice (TTS) | gTTS                                                         |
| LLM         | Groq (Llama 3.3 70B)                                         |
| Vector DB   | ChromaDB                                                     |
| Embeddings  | sentence-transformers (all-MiniLM-L6-v2)                     |
| Frontend    | Streamlit                                                    |
| Data source | MedlinePlus (medlineplus.gov) + curated first-aid references |

## Project Structure



voxmed-ai/

├── agents/          # 4-agent orchestration pipeline

├── rag/             # Ingestion, retrieval, vector database

├── voice/           # Speech-to-text and text-to-speech modules

├── frontend/        # Streamlit voice interface

├── backend/         # (reserved for future API layer)

├── data/            # Medical knowledge base (source .txt files)

├── eval/            # Test question set and evaluation script

├── docs/            # SRS, SOP, and architecture documentation

└── logs/            # Session logs (gitignored)


## Setup

1. **Clone the repo and install dependencies**

```bash
   git clone https://github.com/Arsala-fds/voxmed-ai.git
   cd voxmed-ai
   python3 -m pip install -r requirements.txt
```

2. **Set up environment variables**

```bash
   cp .env.example .env
```

   Add your [Groq API key](https://console.groq.com) (free tier) to `.env`:


3. **Build the knowledge base**

```bash
   python3 rag/fetch_medlineplus.py   # pulls verified medical content
   python3 rag/ingest.py               # chunks + embeds into ChromaDB
```

4. **Run the app**

```bash
   streamlit run frontend/app.py
```

## Evaluation

VoxMed_AI is tested against a fixed set of 10 test questions covering routine first-aid queries, emergency scenarios, and out-of-scope questions (to verify the system doesn't fabricate answers).

```bash
python3 eval/run_eval.py
```

**Latest results:**

- Retrieval accuracy: **90%** (9/10)
- Emergency detection accuracy: **100%** (10/10)

See `eval/eval_notes.md` for the full breakdown and known limitations.

## Documentation

Full project documentation is in `/docs`:

- `VoxMed_AI_SRS.docx` — Software Requirements Specification
- `VoxMed_AI_SOP.docx` — Development process and phase breakdown

## Roadmap

- [ ] Multi-turn conversational memory
- [ ] Multilingual voice support (Hindi/Hinglish)
- [ ] Improve retrieval precision for overlapping topics (see eval_notes.md)
- [ ] Deploy to Streamlit Community Cloud
- [ ] Integration with AIVORA for full triage-to-guidance flow

## Disclaimer

VoxMed_AI is an educational and portfolio project. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for medical concerns.
