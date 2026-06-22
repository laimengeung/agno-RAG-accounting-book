"""
team_chat.py

Terminal chat loop for the multi-agent RAG team (Phase 10).
A drop-in replacement for chat.py — same commands, same session
memory format, but routes through the 3-agent team instead of
the single agent.

Run alongside chat.py to compare response quality:
  Terminal 1: python chat.py        (single agent)
  Terminal 2: python team_chat.py   (3-agent team)

Commands:
    exit / quit / q   — end the session
    new               — start a fresh session
    session           — print the current session ID
    help              — print all commands
"""

import uuid
from datetime import datetime

from team import get_team


def new_session_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"team-session-{timestamp}-{uuid.uuid4().hex[:6]}"


def print_banner(session_id: str) -> None:
    print("\n" + "=" * 60)
    print("  📖  Book Q&A — Multi-Agent Team")
    print("  Searcher → Analyzer → Synthesizer")
    print("=" * 60)
    print(f"  Session : {session_id}")
    print("  Type 'help' for commands.")
    print("=" * 60 + "\n")


def print_help() -> None:
    print("""
┌─────────────────────────────────────────────────────────┐
│  COMMANDS                                               │
│    exit / quit / q   End the session                    │
│    new               Fresh session (clear memory)       │
│    session           Show current session ID            │
│                                                         │
│  Any other input is sent to the agent team as a Q&A.   │
└─────────────────────────────────────────────────────────┘
""")


def main() -> None:
    team = get_team()
    session_id = new_session_id()
    print_banner(session_id)

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "q"):
            print("\nGoodbye!")
            break

        if user_input.lower() == "new":
            session_id = new_session_id()
            print(f"\n[New session started: {session_id}]\n")
            continue

        if user_input.lower() == "session":
            print(f"\n[Current session: {session_id}]\n")
            continue

        if user_input.lower() == "help":
            print_help()
            continue

        print()
        team.print_response(
            user_input,
            session_id=session_id,
            stream=True,
            markdown=True,
        )
        print()


if __name__ == "__main__":
    main()
