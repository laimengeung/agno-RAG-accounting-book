"""
chat.py

Terminal chat loop for the book Q&A agent.

Usage:
    python chat.py

General commands:
    exit / quit / q        — end the session
    new                    — start a fresh session (clears conversation history)
    session                — print the current session ID
    help                   — print all available commands

Summarization commands:
    /summarize             — summarize the entire book
    /summarize <topic>     — summarize a specific topic, chapter, or section
                             e.g. /summarize chapter 3
                             e.g. /summarize the author's argument on memory

Quiz commands:
    /quiz                  — generate 5 mixed questions from the whole book
    /quiz <topic>          — generate 5 questions focused on a topic or section
                             e.g. /quiz part 2
                             e.g. /quiz the conclusion
    /quiz hard             — generate 5 challenging, inferential questions
    /quiz easy             — generate 5 straightforward recall questions
"""

import uuid
from datetime import datetime

from agent import get_agent

# --- Prompt templates for each mode ------------------------------------
# These are injected as the user message so the agent applies the right
# task framing while still using the same knowledge base and memory.

SUMMARIZE_PROMPT = """\
Please summarize {target} from the book.

Your summary should:
- Search the knowledge base thoroughly before writing
- Be structured: open with the main idea, cover key points, close with the takeaway
- Be concise but not superficial — aim for depth over breadth
- Use your own words; avoid reproducing large blocks of text verbatim
"""

QUIZ_PROMPT = """\
Generate exactly 5 quiz questions about {target} from the book.

Difficulty: {difficulty}

Format each question like this:
  Q1. [Question]
  A.  [Option A]
  B.  [Option B]
  C.  [Option C]
  D.  [Option D]
  Answer: [Correct letter]
  Explanation: [1–2 sentences explaining why, grounded in the book]

Rules:
- All questions and answers must be grounded in the book's content
- Search the knowledge base before writing each question
- Do not invent facts or options that aren't supported by the text
- Space questions out with a blank line between each
"""

DIFFICULTY_DESCRIPTIONS = {
    "easy":   "straightforward recall — answers are stated directly in the text",
    "hard":   "inferential and analytical — require connecting ideas across sections",
    "mixed":  "a mix of recall and inferential questions at medium difficulty",
}


# --- Helpers -----------------------------------------------------------

def new_session_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"book-session-{timestamp}-{uuid.uuid4().hex[:6]}"


def print_banner(session_id: str) -> None:
    print("\n" + "=" * 60)
    print("  📖  Book Q&A Agent")
    print("=" * 60)
    print(f"  Session : {session_id}")
    print("  Type 'help' to see all commands.")
    print("=" * 60 + "\n")


def print_help() -> None:
    print("""
┌─────────────────────────────────────────────────────────┐
│  COMMANDS                                               │
├─────────────────────────────────────────────────────────┤
│  General                                                │
│    exit / quit / q        End the session               │
│    new                    Fresh session (clear memory)  │
│    session                Show current session ID       │
│                                                         │
│  Summarization                                          │
│    /summarize             Summarize the whole book      │
│    /summarize <topic>     Summarize a topic or chapter  │
│                                                         │
│  Quiz                                                   │
│    /quiz                  5 mixed questions (whole book)│
│    /quiz <topic>          5 questions on a topic        │
│    /quiz easy             5 easy recall questions       │
│    /quiz hard             5 hard inferential questions  │
│                                                         │
│  Anything else is treated as a Q&A question.            │
└─────────────────────────────────────────────────────────┘
""")


def build_summarize_prompt(args: str) -> str:
    target = args.strip() if args.strip() else "the entire book"
    return SUMMARIZE_PROMPT.format(target=target)


def build_quiz_prompt(args: str) -> str:
    args = args.strip().lower()

    if args in ("easy", "hard"):
        difficulty = DIFFICULTY_DESCRIPTIONS[args]
        target = "the entire book"
    elif args == "":
        difficulty = DIFFICULTY_DESCRIPTIONS["mixed"]
        target = "the entire book"
    else:
        # e.g. "/quiz chapter 3" or "/quiz the conclusion"
        difficulty = DIFFICULTY_DESCRIPTIONS["mixed"]
        target = args

    return QUIZ_PROMPT.format(target=target, difficulty=difficulty)


def parse_command(user_input: str) -> tuple[str, str]:
    """Split '/command rest of input' into ('command', 'args')."""
    parts = user_input.strip().split(maxsplit=1)
    command = parts[0].lstrip("/").lower()
    args = parts[1] if len(parts) > 1 else ""
    return command, args


# --- Main loop ---------------------------------------------------------

def main() -> None:
    agent = get_agent()
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

        # --- General commands (no slash) ---
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

        # --- Slash commands (/summarize, /quiz) ---
        if user_input.startswith("/"):
            command, args = parse_command(user_input)

            if command == "summarize":
                prompt = build_summarize_prompt(args)
                label = f"[Summarizing: {args.strip() or 'entire book'}]"

            elif command == "quiz":
                prompt = build_quiz_prompt(args)
                label = f"[Generating quiz: {args.strip() or 'whole book, mixed difficulty'}]"

            else:
                print(f"\n[Unknown command: /{command}. Type 'help' for available commands.]\n")
                continue

            print(f"\n{label}")
            print()
            agent.print_response(
                prompt,
                session_id=session_id,
                stream=True,
                markdown=True,
            )
            print()
            continue

        # --- Default: Q&A ---
        print()
        agent.print_response(
            user_input,
            session_id=session_id,
            stream=True,
            markdown=True,
        )
        print()


if __name__ == "__main__":
    main()
