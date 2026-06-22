"""
ingest.py

Builds the pgvector-backed knowledge base for the book RAG agent.

Phase 9: ChromaDB (local embedded) → pgvector (Postgres).
The only change from Phase 6 is build_knowledge() — everything else
(chunking, ingestion logic, agent.py, chat.py) stays the same.

SETUP (one-time, before running this script):
  1. Start the pgvector Docker container:
       docker run -d \
         --name pgvector \
         -e POSTGRES_DB=book_rag \
         -e POSTGRES_USER=agno \
         -e POSTGRES_PASSWORD=agno \
         -p 5532:5432 \
         pgvector/pgvector:pg17

  2. Add to your .env:
       DATABASE_URL=postgresql+psycopg://agno:agno@localhost:5532/book_rag

  3. Install extra dependencies:
       pip install pgvector psycopg sqlalchemy

WHEN TO RE-RUN:
  Re-run this script if you change CHUNK_SIZE/CHUNK_OVERLAP or replace
  the book PDF. Uncomment the delete line in main() first to clear old
  chunks from the table.

TUNING GUIDE (same as Phase 6):
  CHUNK_SIZE    sweet spot for books: 800–1200 tokens
  CHUNK_OVERLAP rule of thumb: ~10–15% of CHUNK_SIZE
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from agno.knowledge.knowledge import Knowledge
from agno.knowledge.chunking.recursive import RecursiveChunking
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.vectordb.pgvector import PgVector, SearchType

load_dotenv()  # reads GOOGLE_API_KEY and DATABASE_URL from .env

# --- Configuration -------------------------------------------------------

PDF_PATH    = Path("data/processed/book_clean.pdf")
TABLE_NAME  = "book_knowledge"   # Postgres table that stores chunks + embeddings
SOURCE_NAME = "book"             # label for this source, used for cleanup

# --- Chunk tuning --------------------------------------------------------

CHUNK_SIZE    = 1000   # tokens per chunk
CHUNK_OVERLAP = 150    # token overlap between adjacent chunks


def build_knowledge() -> Knowledge:
    """Construct (but do not populate) the Knowledge object.

    agent.py imports this same function so both ingestion and the
    chat agent always point at the identical vector store.

    Phase 9 swap: ChromaDb → PgVector.
    The rest of the project (agent.py, chat.py) is unchanged.
    """
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise EnvironmentError(
            "DATABASE_URL is not set. Add it to your .env file:\n"
            "  DATABASE_URL=postgresql+psycopg://agno:agno@localhost:5532/book_rag"
        )

    vector_db = PgVector(
        table_name=TABLE_NAME,
        db_url=db_url,
        search_type=SearchType.hybrid,   # vector similarity + keyword (RRF)
        embedder=GeminiEmbedder(),        # uses GOOGLE_API_KEY from .env
    )
    return Knowledge(
        name="Book Knowledge Base",
        description="Single-book Q&A knowledge base — Accounting Made Simple",
        vector_db=vector_db,
    )


def main() -> None:
    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {PDF_PATH}. Run OCR first and place the "
            f"cleaned PDF there before ingesting."
        )

    knowledge = build_knowledge()

    # --- Clear old chunks before re-ingesting ----------------------------
    # If you change CHUNK_SIZE / CHUNK_OVERLAP and re-run this script,
    # uncomment the line below first to avoid mixing old and new chunks:
    # knowledge.vector_db.delete_by_name(SOURCE_NAME)

    reader = PDFReader(
        chunking_strategy=RecursiveChunking(
            chunk_size=CHUNK_SIZE,
            overlap=CHUNK_OVERLAP,
        ),
    )

    print(f"Ingesting '{PDF_PATH}' into Postgres table '{TABLE_NAME}'...")
    print(f"  chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}, search=hybrid")
    knowledge.insert(
        path=str(PDF_PATH),
        reader=reader,
        name=SOURCE_NAME,
        metadata={"source": PDF_PATH.name},
    )
    print("Done. The knowledge base is ready for agent.py / chat.py to use.")


if __name__ == "__main__":
    main()
