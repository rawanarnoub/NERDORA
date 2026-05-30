"""Prompt templates for each NerdoRA feature.

Keep these as pure functions returning (system, user) message pairs so the AI
layer stays dumb about what it's being asked to do.
"""

SYSTEM_TUTOR = (
    "You are NerdoRA, a friendly study tutor. Be accurate, concise, and "
    "encouraging. Use Markdown formatting. When unsure, say so."
)


def explain_prompt(topic: str, level: str, extra_context: str = "") -> tuple[str, str]:
    user = (
        f"Explain the following topic for a {level} learner.\n\n"
        f"Topic: {topic}\n\n"
        "Structure your answer as:\n"
        "1. **TL;DR** — one short paragraph\n"
        "2. **Step-by-step explanation** — numbered list\n"
        "3. **Worked example**\n"
        "4. **Key terms** — short glossary\n"
    )
    if extra_context:
        user += f"\nAdditional source material to ground your answer in:\n---\n{extra_context}\n---"
    return SYSTEM_TUTOR, user


def solve_prompt(problem: str, subject: str) -> tuple[str, str]:
    user = (
        f"Subject: {subject}\n\n"
        f"Problem:\n{problem}\n\n"
        "Solve it step by step. Show your reasoning, then give the final answer "
        "on its own line prefixed with **Answer:**. Finally, suggest 2 similar "
        "practice questions (without solutions)."
    )
    return SYSTEM_TUTOR, user


def flashcards_prompt(topic: str, count: int, extra_context: str = "") -> tuple[str, str]:
    user = (
        f"Create exactly {count} study flashcards about: {topic}.\n\n"
        "Return ONLY a valid JSON array. Each item must have keys "
        '`"question"` and `"answer"`. No prose, no code fences, no trailing text.'
    )
    if extra_context:
        user += f"\n\nGround the cards in this source material:\n---\n{extra_context}\n---"
    return SYSTEM_TUTOR, user


def exam_prompt(
    topic: str, difficulty: str, num_mcq: int, num_short: int
) -> tuple[str, str]:
    user = (
        f"Generate a {difficulty} exam on: {topic}.\n\n"
        f"Include {num_mcq} multiple-choice questions (4 options each, mark the correct one) "
        f"and {num_short} short-answer questions.\n\n"
        "Format in Markdown with two sections:\n"
        "## Questions\n"
        "## Answer Key\n\n"
        "Number questions consistently across both sections."
    )
    return SYSTEM_TUTOR, user


# -- Vision prompts (OpenAI GPT-4o) -------------------------------------------

def explain_image_prompt(level: str, hint: str = "") -> tuple[str, list]:
    """Returns (system_prompt, user_content_list) for OpenAI vision."""
    system = SYSTEM_TUTOR
    text = (
        f"Look at this image — it shows educational content (a textbook page, "
        f"diagram, equation, or notes). Explain what is shown for a {level} learner.\n\n"
        "Structure your answer as:\n"
        "1. **What is shown** — brief description\n"
        "2. **Explanation** — step by step\n"
        "3. **Key takeaways**\n"
        "Use Markdown."
    )
    if hint:
        text += f"\n\nUser is specifically asking about: {hint}"
    return system, text


def solve_image_prompt(subject: str) -> tuple[str, str]:
    """Returns (system_prompt, text_prompt) for OpenAI vision."""
    text = (
        f"This image contains a {subject} problem. Read it carefully, then solve "
        "it step by step. Show your reasoning in Markdown, and give the final "
        "answer on its own line prefixed with **Answer:**. Finally, suggest 2 "
        "similar practice questions (without solutions)."
    )
    return SYSTEM_TUTOR, text


def flashcards_image_prompt(count: int) -> tuple[str, str]:
    """Returns (system_prompt, text_prompt) for OpenAI vision."""
    text = (
        f"Look at this image (notes, textbook page, or diagram). Create exactly "
        f"{count} study flashcards based on its content.\n\n"
        "Return ONLY a valid JSON array. Each item must have keys "
        '`"question"` and `"answer"`. No prose, no code fences, no trailing text.'
    )
    return SYSTEM_TUTOR, text