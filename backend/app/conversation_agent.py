import logging
import os
from typing import Any

from pydantic_ai import Agent

from .models import AgentResponse

logger = logging.getLogger("backend.conversation_agent")


def _ai_enabled() -> bool:
    return bool(os.environ.get("GOOGLE_API_KEY"))


def build_system_prompt(
    *,
    research_brief: str,
    extraction_schema: dict[str, Any],
    extracted_data: dict[str, Any],
    system_prompt_override: str | None = None,
) -> str:
    schema_lines = "\n".join(
        f"- {key}: {field.get('description', '')} (type: {field.get('type', 'string')})"
        for key, field in extraction_schema.items()
    )

    already_collected = "\n".join(
        f"- {key}: {value}"
        for key, value in extracted_data.items()
        if value is not None
    ) or "Nothing extracted yet."

    remaining_keys = [
        key for key in extraction_schema
        if key not in extracted_data or extracted_data[key] is None
    ]
    remaining_lines = "\n".join(
        f"- {key}: {extraction_schema[key].get('description', '')}"
        for key in remaining_keys
    ) or "All data points collected."

    custom_instructions = ""
    if system_prompt_override:
        custom_instructions = f"\nADDITIONAL INSTRUCTIONS:\n{system_prompt_override}\n"

    return f"""You are a friendly, conversational research agent conducting an interview over WhatsApp.

RESEARCH CONTEXT:
{research_brief}
{custom_instructions}
YOUR OBJECTIVE:
Gather specific data points through natural conversation. You do NOT follow a script.
You have a checklist of information to collect. You decide what to ask and when, based on
the flow of conversation. Make it feel like a natural chat, not an interrogation.

DATA POINTS TO COLLECT:
{schema_lines}

ALREADY COLLECTED:
{already_collected}

STILL NEEDED:
{remaining_lines}

RULES:
1. Ask ONE question or make ONE conversational move at a time.
2. Acknowledge what the person said before moving to a new topic.
3. Use natural transitions between topics.
4. Never reveal that you are collecting specific data points or that you have a checklist.
5. If someone gives a vague answer, probe deeper with a follow-up before moving on.
6. Keep messages short — this is WhatsApp, not email. 1-3 sentences max.
7. Be warm, curious, and respectful.
8. If the person seems uncomfortable with a topic, gracefully move on.
9. If the conversation history is empty, this is your opening message. Introduce yourself briefly,
   explain you're doing a quick research chat, and start with something easy and non-threatening.

COMPLETION:
When ALL remaining data points have been naturally covered with concrete, specific answers
(not vague generalities), set conversation_complete to true and send a warm goodbye message
thanking them for their time."""


def _build_user_prompt(conversation_history: list[dict[str, str]]) -> str:
    if not conversation_history:
        return "The conversation hasn't started yet. Send your opening message."

    lines = []
    for msg in conversation_history:
        role = "You" if msg["sender"] == "agent" else "Them"
        lines.append(f"{role}: {msg['content']}")

    return (
        "Here is the conversation so far:\n\n"
        + "\n".join(lines)
        + "\n\nRespond with your next message."
    )


async def get_agent_response(
    *,
    research_brief: str,
    extraction_schema: dict[str, Any],
    extracted_data: dict[str, Any],
    conversation_history: list[dict[str, str]],
    system_prompt_override: str | None = None,
) -> AgentResponse:
    if not _ai_enabled():
        raise RuntimeError("AI is not enabled — set GEMINI_API_KEY or GOOGLE_API_KEY")

    system_prompt = build_system_prompt(
        research_brief=research_brief,
        extraction_schema=extraction_schema,
        extracted_data=extracted_data,
        system_prompt_override=system_prompt_override,
    )

    agent = Agent(
        "google-gla:gemini-2.5-flash",
        system_prompt=system_prompt,
        output_type=AgentResponse,
    )

    user_prompt = _build_user_prompt(conversation_history)

    result = await agent.run(user_prompt)
    return result.output
