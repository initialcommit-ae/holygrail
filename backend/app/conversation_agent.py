import logging
import os
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent

logger = logging.getLogger("backend.conversation_agent")


class NextMessage(BaseModel):
    message: str = Field(min_length=1)


_SYSTEM_PROMPT = """
You write the NEXT outgoing WhatsApp message for a survey bot.

Rules:
- Be warm and conversational, but concise.
- You may acknowledge the user's last answer briefly (e.g. "Nice to meet you, <name>.").
- Then ask the next question.
- Ask exactly ONE question in total.
- Preserve the intent of the next question (do not change what info is required).
- Do not add extra questions, options, or explanations.
- Output ONLY the final message text.
""".strip()


def _ai_enabled() -> bool:
    # pydantic-ai google-gla uses GOOGLE_API_KEY (we map GEMINI_API_KEY -> GOOGLE_API_KEY in config.py)
    return bool(os.environ.get("GOOGLE_API_KEY"))


_agent: Agent[Any, NextMessage] | None = None


def _get_agent() -> Agent[Any, NextMessage]:
    global _agent
    if _agent is None:
        _agent = Agent(
            "google-gla:gemini-2.5-flash",
            system_prompt=_SYSTEM_PROMPT,
            output_type=NextMessage,
        )
    return _agent


def compose_next_message_sync(
    *,
    last_question: str | None,
    last_answer: str | None,
    next_question: str,
    answers_so_far: list[dict[str, Any]] | None,
) -> str:
    """
    Returns the next outgoing WhatsApp message.
    If AI is not configured or fails, returns `next_question`.
    """
    next_question = (next_question or "").strip()
    if not next_question:
        return next_question

    if not _ai_enabled():
        return next_question

    answers = answers_so_far or []
    last_q = (last_question or "").strip()
    last_a = (last_answer or "").strip()

    prompt = (
        "Write the next outgoing WhatsApp message.\n\n"
        f"Last question (may be empty):\n{last_q}\n\n"
        f"User's last answer (may be empty):\n{last_a}\n\n"
        f"Next question to ask (must preserve intent):\n{next_question}\n\n"
        f"Conversation so far (may be empty):\n{answers}\n"
    )

    try:
        result = _get_agent().run_sync(prompt)
        message = (result.output.message or "").strip()
        return message or next_question
    except Exception:
        logger.exception("Conversation agent failed; falling back to next_question")
        return next_question

