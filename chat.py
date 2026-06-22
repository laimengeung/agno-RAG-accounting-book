"""
chat.py

Terminal chat loop for the book Q&A agent.

Usage:
    python chat.py

Commands during chat:
    exit / quit / q   — end the session
    new               — start a fresh session (clears conversation history)
    session           — print the current session ID
"""

import uuid
from datetime import datetime

from agent import get_agent

def new_session_id() -> str:
    """Genereate a unique session ID with current timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"book-session-{timestamp}-{uuid.uuid4().hex[:6]}"

def print_banner(session_id: str) -> None:
    print("\n" + "=" * 60)
    print("  📖  Book Q&A Agent")
    print("=" * 60)
    print(f"  Session : {session_id}")
    print("  Commands: 'new' = fresh session | 'session' = show ID")
    print("            'exit' / 'quit' / 'q' = end chat")
    print("=" * 60 + "\n")

def main() -> None:
    agent = get_agent()
    session_id = new_session_id()
    print_banner(session_id)

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye")
            break

        if not user_input:
            continue

        # Built-in commands
        if user_input.lower() in ("exit", "quit", "q"):
            print("\nGoodbye")
            break

        if user_input.lower() == "new":
            session_id = new_session_id()
            print(f"\n[New session started: {session_id}]\n")
            continue            

        if user_input.lower() == "session":
            print(f"\n[Current session: {session_id}]\n")
            continue

        print()  
        agent.print_response(
            user_input,
            session_id=session_id,
            stream=True,        # streams tokens as they arrive instead of waiting for the full response
            markdown=True,
        )
        print()  

if __name__ == "__main__":
    main()