# 📖 Accounting Made Simple — Book Q&A Agent

A conversational AI agent that answers questions about *Accounting Made Simple* by Mike Piper using Retrieval-Augmented Generation (RAG). Built with [Agno](https://docs.agno.com), Gemini, and pgvector.

## How it works

```
book.pdf ──► OCR ──► ingest.py ──► pgvector (Postgres)
                                         │
                          ┌──────────────┴──────────────┐
                     agent.py                        team.py
               (single agentic RAG)        (Searcher → Analyzer → Synthesizer)
                          │                            │
                      chat.py                   team_chat.py
                   (terminal loop)             (terminal loop)
```

The agent(s) search the book as a **tool** — deciding when and how many times to retrieve — rather than blindly injecting chunks on every response. Conversation history is persisted across turns via SQLite.

## Project structure

```
book-rag-agno/
├── .env                       # GOOGLE_API_KEY + DATABASE_URL
├── requirements.txt
├── data/
│   ├── raw/book.pdf           # original PDF (mixed text + scanned pages)
│   └── processed/book_clean.pdf  # OCR'd output — feed this to Agno
├── tmp/                       # auto-created; stores SQLite session DB
├── ingest.py                  # build the vector knowledge base (run once)
├── agent.py                   # single-agent definition (get_agent)
├── chat.py                    # single-agent terminal chat loop
├── team.py                    # 3-agent team definition (get_team)
├── team_chat.py               # team terminal chat loop
└── test_agent.py              # structured stress-test suite
```

## Prerequisites

- Python 3.10+
- Docker (for the pgvector Postgres container)
- A [Google AI Studio](https://aistudio.google.com) API key (Gemini)
- `ocrmypdf` installed on your system ([install guide](https://ocrmypdf.readthedocs.io/en/latest/installation.html))

## Setup

**1. Install Python dependencies**

```bash
pip install agno pgvector psycopg sqlalchemy python-dotenv google-generativeai
```

**2. Start the pgvector container**

```bash
docker run -d \
  --name pgvector \
  -e POSTGRES_DB=book_rag \
  -e POSTGRES_USER=agno \
  -e POSTGRES_PASSWORD=agno \
  -p 5532:5432 \
  pgvector/pgvector:pg17
```

> [!TIP]
> To persist data across container restarts, add `-v pgvector_data:/var/lib/postgresql/data` to the command above.

**3. Configure your `.env`**

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql+psycopg://agno:agno@localhost:5532/book_rag
```

**4. OCR the book** *(one-time — skips pages that already have selectable text)*

```bash
ocrmypdf --skip-text data/raw/book.pdf data/processed/book_clean.pdf
```

> [!TIP]
> After OCR, open `book_clean.pdf` and confirm you can select/copy text on pages that were previously scanned images.

**5. Build the knowledge base** *(one-time — re-run only if the book or chunk settings change)*

```bash
python ingest.py
```

**6. Start chatting**

```bash
# Single agent
python chat.py

# Or the 3-agent team
python team_chat.py
```

## Chat commands

Both `chat.py` and `team_chat.py` support these commands:

| Command | Action |
|---|---|
| `exit` / `quit` / `q` | End the session |
| `new` | Start a fresh session (clears conversation history) |
| `session` | Print the current session ID |
| `help` | Print all available commands |

`chat.py` also supports summarization and quiz modes:

| Command | Action |
|---|---|
| `/summarize` | Summarize the entire book |
| `/summarize <topic>` | Summarize a chapter or topic, e.g. `/summarize chapter 3` |
| `/quiz` | Generate 5 mixed-difficulty questions from the whole book |
| `/quiz <topic>` | Generate 5 questions on a topic, e.g. `/quiz depreciation` |
| `/quiz easy` | 5 straightforward recall questions |
| `/quiz hard` | 5 inferential, cross-chapter questions |

## Single agent vs. team

| | `chat.py` (single agent) | `team_chat.py` (3-agent team) |
|---|---|---|
| Speed | Faster | Slower (3 model calls per turn) |
| Best for | Q&A, quick lookups, `/quiz`, `/summarize` | Complex questions spanning multiple sections |
| Agents | 1 | Searcher → Analyzer → Synthesizer |
| Retrieval | Agentic (multi-search) | Agentic (dedicated Searcher agent) |

> [!TIP]
> Set `show_members_responses=True` in `team.py` to see each agent's individual output — useful for debugging which step produced a poor answer.

## Testing

Fill in the placeholder questions in `test_agent.py` with questions specific to the book, then run:

```bash
python test_agent.py
```

Results are printed to the terminal and saved to `test_results.md`. The suite covers five categories:

| Category | Tests for |
|---|---|
| Factual lookup | Retrieval surfacing the right chunk |
| Multi-chunk reasoning | Synthesizing across sections |
| Out-of-book questions | Hallucination / over-reliance on general knowledge |
| Conversation memory | `add_history_to_context` working correctly |
| Edge cases | OCR gaps, ambiguous queries, broad summarization |

## Tuning retrieval

If answers feel incomplete or noisy, adjust these constants in `ingest.py`, then re-run ingestion (clear the old table first using the commented-out delete line in `main()`):

| Setting | Too small | Too large | Sweet spot |
|---|---|---|---|
| `CHUNK_SIZE` | Ideas cut off mid-thought | Retrieval returns the right chapter but wrong paragraph | 800–1200 tokens |
| `CHUNK_OVERLAP` | Context lost at boundaries | Redundant content bloats DB | ~10–15% of `CHUNK_SIZE` |

## Configuration reference

| File | Setting | What it controls |
|---|---|---|
| `agent.py` / `team.py` | `MODEL_ID` | Gemini model for all agents |
| `agent.py` | `NUM_HISTORY_RUNS` | Prior turns kept in context |
| `ingest.py` | `TABLE_NAME` | Postgres table for embeddings |
| `ingest.py` | `CHUNK_SIZE` / `CHUNK_OVERLAP` | Chunking granularity |

## Stack

| Layer | Tool |
|---|---|
| Agent framework | [Agno](https://docs.agno.com) |
| LLM + embeddings | [Gemini](https://ai.google.dev) (`gemini-3.5-flash` + `gemini-embedding-001`) |
| Vector store | [pgvector](https://github.com/pgvector/pgvector) on Postgres (Docker) |
| Search strategy | Hybrid (vector similarity + keyword via RRF) |
| Session memory | SQLite via Agno's `SqliteDb` |
| OCR | [ocrmypdf](https://ocrmypdf.readthedocs.io) |
