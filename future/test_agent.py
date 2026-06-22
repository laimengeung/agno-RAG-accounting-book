"""
test_agent.py

Phase 5: Structured stress-test for the book Q&A agent.

Fill in the placeholder questions in each TEST_CASES category below
with questions relevant to YOUR book, then run:

    python test_agent.py

Results are printed to the terminal AND saved to test_results.md
so you can review, compare runs, and track improvements over time.

HOW TO FILL IN THE QUESTIONS:
Each test case is a dict with:
  - "q"        : your question (string)
  - "expect"   : what a GOOD answer should contain/do (your note, not checked automatically)
  - "watch_for": what a BAD answer looks like (your note, not checked automatically)
"""

import textwrap
from datetime import datetime

from agent import get_agent

# ─────────────────────────────────────────────────────────────
# FILL IN YOUR TEST QUESTIONS HERE
# ─────────────────────────────────────────────────────────────

TEST_CASES = {

    # ----------------------------------------------------------
    # CATEGORY 1 — Factual lookup
    # Single, specific facts that live in one place in the book.
    # Tests: does retrieval surface the right chunk at all?
    # ----------------------------------------------------------
    "1_factual_lookup": [
        {
            "q": "REPLACE ME: e.g. What year did X happen according to the book?",
            "expect": "A specific fact or figure directly from the book.",
            "watch_for": "Vague answer, hallucinated number, or 'I don't know' when the answer IS in the book.",
        },
        {
            "q": "REPLACE ME: e.g. Who is [character/person] and what is their role?",
            "expect": "Correct name + role grounded in a retrieved passage.",
            "watch_for": "Confabulated biography or mixing up characters.",
        },
        {
            "q": "REPLACE ME: e.g. What does the book say about [specific term or concept]?",
            "expect": "A clear definition or description sourced from the book.",
            "watch_for": "Generic textbook definition that ignores what the book actually says.",
        },
    ],

    # ----------------------------------------------------------
    # CATEGORY 2 — Multi-chunk / cross-section reasoning
    # Questions whose full answer is spread across multiple
    # sections, chapters, or passages.
    # Tests: does the agent search more than once? Can it
    # synthesize across chunks coherently?
    # ----------------------------------------------------------
    "2_multi_chunk_reasoning": [
        {
            "q": "REPLACE ME: e.g. How does the book's argument in Chapter 1 connect to its conclusion?",
            "expect": "Agent searches multiple times and draws a coherent thread across sections.",
            "watch_for": "Only reflects one section, misses the connection, or repeats one chunk twice.",
        },
        {
            "q": "REPLACE ME: e.g. Compare how [topic A] and [topic B] are treated differently in the book.",
            "expect": "Contrast drawn from at least two different retrieved passages.",
            "watch_for": "Answers only one side, or invents a comparison not in the book.",
        },
    ],

    # ----------------------------------------------------------
    # CATEGORY 3 — Out-of-book questions
    # Topics the book does NOT cover.
    # Tests: does the agent correctly decline, or does it
    # hallucinate / fall back on Gemini's general knowledge?
    # ----------------------------------------------------------
    "3_out_of_book": [
        {
            "q": "REPLACE ME: e.g. Ask about a topic, event, or person NOT mentioned in the book.",
            "expect": "Agent says it couldn't find this in the book and declines to speculate.",
            "watch_for": "Confident answer drawn from Gemini's general knowledge with no disclaimer.",
        },
        {
            "q": "What is the capital of France?",
            "expect": "Agent either answers from general knowledge OR notes this isn't in the book. "
                      "Either is acceptable — note which behaviour you observe.",
            "watch_for": "Pretending to retrieve this from the book.",
        },
    ],

    # ----------------------------------------------------------
    # CATEGORY 4 — Conversation memory / follow-up
    # Each question here builds on the previous one.
    # Tests: does add_history_to_context actually work?
    # Run these as a sequence in a single session.
    # ----------------------------------------------------------
    "4_conversation_memory": [
        {
            "q": "REPLACE ME: e.g. What is the main theme of the book?",
            "expect": "A grounded answer about the book's central theme.",
            "watch_for": "Generic or vague answer that could apply to any book.",
        },
        {
            "q": "Can you expand on the second point you just mentioned?",
            "expect": "Agent correctly references its own prior response without re-searching.",
            "watch_for": "Agent asks 'what second point?' — means history isn't working.",
        },
        {
            "q": "How does that relate to what the author says in the introduction?",
            "expect": "Agent connects the prior answer to the introduction section.",
            "watch_for": "Agent loses the thread or treats this as a completely new question.",
        },
    ],

    # ----------------------------------------------------------
    # CATEGORY 5 — Edge cases
    # Stress the boundaries: ambiguous questions, very broad
    # questions, and questions about missing/scanned pages.
    # ----------------------------------------------------------
    "5_edge_cases": [
        {
            "q": "Summarize the entire book in three sentences.",
            "expect": "A coherent high-level summary. Agent may search multiple times.",
            "watch_for": "Hallucinated plot points, or refusal because 'the book is too long'.",
        },
        {
            "q": "REPLACE ME: e.g. Ask about content you know was on a scanned/image page.",
            "expect": "Correct answer if OCR worked on that page.",
            "watch_for": "'I couldn't find that' — means the OCR missed that page. Go back and check.",
        },
        {
            "q": "What is the most important sentence in the book?",
            "expect": "Agent picks something defensible and cites where it came from.",
            "watch_for": "Completely made-up quote, or paralysis ('I cannot determine importance').",
        },
    ],
}

# ─────────────────────────────────────────────────────────────
# TEST RUNNER — no need to edit below this line
# ─────────────────────────────────────────────────────────────

SEPARATOR = "─" * 60
SESSION_PREFIX = "test-session"


def run_tests() -> None:
    agent = get_agent()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results: list[str] = []

    header = f"\n{'=' * 60}\n  PHASE 5 TEST RUN — {timestamp}\n{'=' * 60}\n"
    print(header)
    results.append(header)

    for category, cases in TEST_CASES.items():
        cat_header = f"\n{'━' * 60}\n  CATEGORY: {category.upper()}\n{'━' * 60}"
        print(cat_header)
        results.append(cat_header)

        # Each category gets its own session so memory tests are isolated
        session_id = f"{SESSION_PREFIX}-{category}"

        for i, case in enumerate(cases, 1):
            q = case["q"]
            expect = case["expect"]
            watch_for = case["watch_for"]

            q_header = f"\n[Q{i}] {q}"
            meta = (
                f"  ✅ Expect    : {expect}\n"
                f"  ⚠️  Watch for : {watch_for}"
            )
            divider = SEPARATOR

            print(q_header)
            print(meta)
            print(divider)
            results.append(q_header)
            results.append(meta)
            results.append(divider)

            # Capture agent response by printing to terminal (stream=True)
            # and separately capturing the text for the log file
            response = agent.run(q, session_id=session_id)

            # Extract text from response
            answer_text = ""
            if hasattr(response, "content"):
                for block in (response.content or []):
                    if hasattr(block, "text") and block.text:
                        answer_text += block.text
            if not answer_text:
                answer_text = str(response)

            wrapped = textwrap.fill(answer_text, width=80)
            print(wrapped)
            print()

            entry = f"ANSWER:\n{wrapped}\n"
            results.append(entry)

    # Save results to markdown file
    output_path = "test_results.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Phase 5 Test Results\n\n**Run at:** {timestamp}\n\n")
        for line in results:
            f.write(line + "\n")

    footer = f"\n{'=' * 60}\n  Results saved to: {output_path}\n{'=' * 60}\n"
    print(footer)


if __name__ == "__main__":
    run_tests()
