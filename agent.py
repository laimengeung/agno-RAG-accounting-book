"""
agent.py

Defines the book Q&A agent: Gemini model + agentic search over the
ChromaDB knowledge base built by ingest.py + persistent conversation
memory.

This file does NOT ingest anything — it assumes ingest.py has already
been run and chroma_db/ is populated. Both chat.py (and any future
summarization/quiz feature) should import get_agent() from here rather
than constructing their own Agent, so they all share one definition.
"""

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.google import Gemini

from ingest import build_knowledge

MODEL_ID = "gemini-3.1-flash-lite"
AGENT_DB_PATH = "tmp/agents.db"
NUM_HISTORY_RUNS = 5

INSTRUCTIONS = [
    "You are a knowledgeable assistant that answers questions about the "
    "'Accounting Made Simple: Accounting Explained in 100 Pages Or Less.' book",
    "Always search your knowledge base before answering questions about the book's content.",
    "If the knowledge base search does not return relevant information, say so clearly "
    "rather than guessing or relying on general knowledge.",
    "Quote or reference specific details from the retrieved passages when possible.",
    "Keep answers focused and avoid padding with unrelated commentary.",
]

def get_agent() -> Agent:
    knowledge = build_knowledge()
    agent_db = SqliteDb(db_file=AGENT_DB_PATH)

    return Agent(
        name="Book Q&A Agent",
        model=Gemini(id=MODEL_ID),
        instructions=INSTRUCTIONS,
        knowledge=knowledge,
        search_knowledge=True,         # agentic RAG: search is a tool, agent decides when to call it 
        db=agent_db,
        add_history_to_context=True,
        num_history_runs=NUM_HISTORY_RUNS,
        markdown=True
    )

if __name__ == "__main__":
    agent = get_agent()
    agent.print_response(
        "Give me a brief overview of what this book covers.",
        session_id="testing12",
        markdown=True
    )   