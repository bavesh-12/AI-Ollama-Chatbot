# 🤖 AI Chat Interface

A local AI chatbot with document memory, multi-conversation support, and RAG-powered file Q&A — built with FastAPI and Gemini.

---

## Features

- 💬 **Multi-conversation** — create, switch, and delete chats with auto-generated titles
- 📄 **Document upload & RAG** — upload PDFs, DOCX, PPTX, CSV, images, and more; ask questions about them
- 🧠 **Conversation memory** — recent context is passed with every message
- 🎙️ **Speech input** — transcribe audio via Google Speech Recognition
- ⚡ **Gemini-powered** — uses `gemini-1.5-flash` with a fallback model

---

## Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI + Uvicorn |
| AI | Google Gemini (`google-genai`) |
| Embeddings | `sentence-transformers` + FAISS |
| Document parsing | PyMuPDF, pdfplumber, python-docx, python-pptx |
| Speech | SpeechRecognition + pydub |

---

## Getting Started

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your Gemini API key
# Edit ai_client.py and memory_manager.py → set GEMINI_API_KEY

# 3. Run
python run.py
```

Open **http://localhost:8000**

---

## Project Structure

```
├── main.py            # FastAPI routes
├── ai_client.py       # Gemini API calls
├── memory_manager.py  # Conversation storage (JSON)
├── rag.py             # Document ingestion + FAISS retrieval
├── speech_handler.py  # Audio transcription
├── run.py             # Entrypoint
└── cleanup.py         # Reset conversations/vectors
```

---

## Supported File Types

PDF · DOCX · PPTX · TXT · MD · CSV · XLSX · JPG/PNG · ZIP

---

> To reset all data: `python cleanup.py`
