"""
team.py

Phase 10: Multi-agent team for the book Q&A pipeline.

Replaces the single agent from agent.py with three specialized agents
in Agno's coordinate mode:

  Knowledge Searcher   → searches the book knowledge base (agentic RAG)
  Content Analyzer     → organizes and critiques the retrieved passages
  Response Synthesizer → writes the final grounded, user-facing answer

The Team leader (Gemini) decides the delegation order and synthesizes
the overall result. Conversation memory is shared across the team via
the same SqliteDb used in agent.py.

HOW TO USE:
  Run team_chat.py (the team equivalent of chat.py) to interact with
  the team in the terminal. Or import get_team() here directly.

WHY THREE AGENTS?
  The single agent in agent.py handles search + analysis + synthesis
  all in one context window. Splitting these into three narrow-scope
  agents means:
    - The Searcher can issue multiple focused searches without losing
      track of what it's synthesizing
    - The Analyzer can push back if retrieved content is insufficient
      before synthesis begins
    - The Synthesizer always receives pre-organized content, so the
      final answer is more structured and grounded
"""

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.google import Gemini
from agno.team.team import Team

from ingest import build_knowledge

# --- Configuration ---------------------------------------------------

MODEL_ID      = "gemini-3.5-flash"
AGENT_DB_PATH = "tmp/agents.db"


def get_team() -> Team:
    """Build and return the coordinated RAG team.

    Import and call this in team_chat.py the same way agent.py's
    get_agent() is called in chat.py.
    """
    knowledge = build_knowledge()  # same ChromaDb/PgVector as ingest.py
    agent_db  = SqliteDb(db_file=AGENT_DB_PATH)

    # ------------------------------------------------------------------
    # Agent 1 — Knowledge Searcher
    # Only responsibility: search the book thoroughly and return raw
    # passages with enough context to be useful to the next agent.
    # ------------------------------------------------------------------
    knowledge_searcher = Agent(
        name="Knowledge Searcher",
        model=Gemini(id=MODEL_ID),
        role="Search the book knowledge base and return all relevant passages",
        knowledge=knowledge,
        search_knowledge=True,
        instructions=[
            "You are searching the book 'Accounting Made Simple' by Mike Piper.",
            "Your ONLY job is to find relevant passages — do NOT write a final answer.",
            "Search the knowledge base at least twice using different search terms "
            "extracted from the query to maximize recall.",
            "Return the retrieved passages with their context (section/chapter if available).",
            "If a search returns nothing useful, say so clearly so the Analyzer can flag it.",
        ],
        markdown=True,
    )

    # ------------------------------------------------------------------
    # Agent 2 — Content Analyzer
    # Takes the raw passages from the Searcher and organizes them:
    # identifies the key points, flags gaps, and structures the content
    # ready for the Synthesizer to write from.
    # ------------------------------------------------------------------
    content_analyzer = Agent(
        name="Content Analyzer",
        model=Gemini(id=MODEL_ID),
        role="Analyze and organize retrieved passages into structured key points",
        instructions=[
            "You receive raw passages retrieved from 'Accounting Made Simple'.",
            "Your job is to organize — NOT to write the final answer.",
            "Extract the key points relevant to the question.",
            "Flag any gaps: if the passages don't fully answer the question, say so explicitly.",
            "Preserve the book's own terminology and examples (equations, journal entries, etc.).",
            "Structure your output as a numbered list of key points the Synthesizer can write from.",
        ],
        markdown=True,
    )

    # ------------------------------------------------------------------
    # Agent 3 — Response Synthesizer
    # Writes the final user-facing answer from the Analyzer's structured
    # key points. This is the only agent whose output the user sees.
    # ------------------------------------------------------------------
    response_synthesizer = Agent(
        name="Response Synthesizer",
        model=Gemini(id=MODEL_ID),
        role="Write the final clear, grounded answer from the analyzed key points",
        instructions=[
            "You write the final answer the user will read.",
            "Base your answer ONLY on the key points provided by the Content Analyzer.",
            "Do not introduce facts not present in the analyzed content.",
            "If the Analyzer flagged gaps, acknowledge them honestly in your answer.",
            "Match the book's accessible tone — Mike Piper writes for non-accountants, "
            "so keep explanations plain and use the book's own examples where available.",
            "Structure your response clearly: lead with a direct answer, "
            "then supporting detail, then a brief takeaway if relevant.",
        ],
        markdown=True,
    )

    # ------------------------------------------------------------------
    # Team — coordinate mode
    # The Team leader delegates in order (Searcher → Analyzer → Synthesizer)
    # and produces the final cohesive response.
    # ------------------------------------------------------------------
    return Team(
        name="Book RAG Team",
        model=Gemini(id=MODEL_ID),
        mode="coordinate",
        members=[knowledge_searcher, content_analyzer, response_synthesizer],
        db=agent_db,
        add_history_to_context=True,
        instructions=[
            "You are coordinating a Q&A team for 'Accounting Made Simple' by Mike Piper.",
            "Always follow this delegation order:",
            "  1. Knowledge Searcher — retrieve relevant passages from the book",
            "  2. Content Analyzer  — organize and critique the retrieved content",
            "  3. Response Synthesizer — write the final grounded answer",
            "Do not skip steps. If the Searcher finds nothing, instruct the Synthesizer "
            "to say so honestly rather than answering from general knowledge.",
        ],
        show_members_responses=True,  
        markdown=True,
    )


if __name__ == "__main__":
    # Quick smoke test: python team.py
    team = get_team()
    team.print_response(
        "What is the difference between cash-basis and accrual-basis accounting?",
        session_id="team-testing",
        stream=True,
    )
