# 📖 Book Q&A Agent

A conversational AI agent that answers questions about a book using Retrieval-Augmented Generation (RAG). Built with [Agno](https://docs.agno.com), Gemini, and ChromaDB.

## How it works

```
book.pdf ──► OCR ──► ingest.py ──► ChromaDB
                                       │
                               agent.py (Gemini + agentic search)
                                       │
                                   chat.py (terminal loop)
```

The agent searches the book's content as a **tool** — it decides when and how many times to search, rather than blindly injecting chunks on every response. Conversation history is persisted across turns via SQLite.

## Project structure

```
book-rag-agno/
├── .env                      # GOOGLE_API_KEY
├── requirements.txt
├── data/
│   ├── raw/book.pdf          # original PDF (text + scanned pages)
│   └── processed/book_clean.pdf  # OCR'd output — feed this to Agno
├── chroma_db/                # auto-created on first ingest
├── tmp/                      # auto-created; stores SQLite session DB
├── ingest.py                 # build the vector knowledge base (run once)
├── agent.py                  # agent definition — import get_agent() from here
├── chat.py                   # interactive terminal chat loop
└── test_agent.py             # structured Phase 5 stress-test
```

## Prerequisites

- Python 3.10+
- A [Google AI Studio](https://aistudio.google.com) API key (Gemini)
- `ocrmypdf` installed on your system ([install guide](https://ocrmypdf.readthedocs.io/en/latest/installation.html))

## Setup

**1. Install dependencies**

```bash
pip install agno chromadb python-dotenv google-generativeai
```

**2. Set your API key**

```bash
# .env
GOOGLE_API_KEY=your_key_here
```

**3. OCR the book** *(one-time step — skips pages that already have text)*

```bash
ocrmypdf --skip-text data/raw/book.pdf data/processed/book_clean.pdf
```

> [!TIP]
> After OCR, open `book_clean.pdf` and confirm you can select/copy text on pages that were previously scanned images.

**4. Build the knowledge base** *(one-time step — re-run only if the book changes)*

```bash
python ingest.py
```

**5. Start chatting**

```bash
python chat.py
```

## Chat commands

| Command | Action |
|---|---|
| `exit` / `quit` / `q` | End the session |
| `new` | Start a fresh session (clears conversation history) |
| `session` | Print the current session ID |

## Testing

Fill in the placeholder questions in `test_agent.py` with questions specific to your book, then run:

```bash
python test_agent.py
```

Results are printed to the terminal and saved to `test_results.md`. The test suite covers five categories: factual lookup, multi-chunk reasoning, out-of-book questions, conversation memory, and edge cases.

## Configuration

Key settings live at the top of each file — no need to dig into the logic to change them.

| File | Setting | What it controls |
|---|---|---|
| `agent.py` | `MODEL_ID` | Gemini model used for reasoning |
| `agent.py` | `NUM_HISTORY_RUNS` | How many prior turns the agent remembers |
| `ingest.py` | `COLLECTION_NAME` | ChromaDB collection name |
| `ingest.py` | `chunk_size` / `overlap` | Chunk granularity — tune if answers feel incomplete or noisy |

## Stack

| Layer | Tool |
|---|---|
| Agent framework | [Agno](https://docs.agno.com) |
| LLM + embeddings | [Gemini](https://ai.google.dev) (`gemini-3.5-flash` + `gemini-embedding-001`) |
| Vector store | [ChromaDB](https://www.trychroma.com) (local, embedded) |
| Session memory | SQLite via Agno's `SqliteDb` |
| OCR | [ocrmypdf](https://ocrmypdf.readthedocs.io) |
