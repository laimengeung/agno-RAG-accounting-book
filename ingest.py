"""
ingest.py

Builds the ChromaDB-backed knowledge base for the book RAG agent.

Run this once (or again whenever the source PDF changes) to (re)populate
the vector database. The chat agent (agent.py / chat.py) reads from the
same ChromaDB collection but does NOT re-run this ingestion step.
"""

from pathlib import Path

from dotenv import load_dotenv

# from agno.agent import Agent
from agno.knowledge.chunking.recursive import RecursiveChunking
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.vectordb.chroma import ChromaDb
# from agno.vectordb.search import SearchType

load_dotenv()

PDF_PATH = Path("data/processed/book_clean.pdf")
CHROME_PATH = "chroma_db"
COLLECTION_NAME = "book_knowledge"
SOURCE_NAME = "book"

CHUNK_SIZE = 4000
OVERLAP = 200

# For Semantic Chunking
# SIMILARITY_WINDOW = 3
# SIMILARITY_THRESHOLD = 0.5


# Knowledge is the external, domain-specific information you store so AI agents can access it.
def build_knowledge() -> Knowledge:
    vector_db = ChromaDb(
        collection=COLLECTION_NAME,
        path=CHROME_PATH,
        persistent_client=True,
        embedder=GeminiEmbedder()
    )
    return Knowledge(
        name="Book Knowledge Base",
        description="Single book Q&A knowledge base - recursive chunking",
        vector_db=vector_db
    )

# print(build_knowledge().vector_db.search_type.SearchType)
def main() -> None:
    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {PDF_PATH}. Run OCR first and place the "
            f"cleaned PDF there before ingesting."
        )
    
    knowledge = build_knowledge()

    reader = PDFReader(
        chunking_strategy=RecursiveChunking(
            chunk_size=CHUNK_SIZE,
            overlap=OVERLAP,
        ),
    )

    # --- Read and filter empty chunks ------------------------------------
    # Some PDF pages produce empty text after extraction (blank pages,
    # section dividers, OCR misses). Gemini's embedding API rejects empty
    # strings with a 400 error, so we filter them out before upserting.
    print(f"Reading '{PDF_PATH}'...")
    documents = reader.read(pdf=str(PDF_PATH))
 
    before = len(documents)
    documents = [doc for doc in documents if doc.content and doc.content.strip()]
    after = len(documents)
    skipped = before - after
 
    print(f"  Chunks total   : {before}")
    print(f"  Empty (skipped): {skipped}")
    print(f"  Inserting      : {after}")
 
    print(f"\nUpserting into Chroma collection '{COLLECTION_NAME}'...")
    knowledge.vector_db.upsert(content_hash=SOURCE_NAME, documents=documents)
    print("Done. The knowledge base is ready for agent.py / chat.py to use.")
 

if __name__ == "__main__":
    main()