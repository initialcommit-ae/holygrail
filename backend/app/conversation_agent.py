import logging
import os
from dataclasses import dataclass, field
from typing import Any

from pydantic_ai import Agent, RunContext

from .models import AgentResponse

logger = logging.getLogger("backend.conversation_agent")


def _ai_enabled() -> bool:
    return bool(os.environ.get("GOOGLE_API_KEY"))


# ---------------------------------------------------------------------------
# MeshContext — runtime deps for the single global agent
# ---------------------------------------------------------------------------


@dataclass
class MeshContext:
    mode: str  # "onboarding" | "campaign" | "general" | "bounty"
    conversation_history: list[dict[str, str]]
    user_demographics: dict[str, Any] = field(default_factory=dict)
    # Campaign-specific (None when not in campaign/bounty mode)
    research_brief: str | None = None
    extraction_schema: dict[str, Any] | None = None
    extracted_data: dict[str, Any] | None = None
    reward_text: str | None = None
    reward_link: str | None = None
    system_prompt_override: str | None = None


# ---------------------------------------------------------------------------
# Single global agent
# ---------------------------------------------------------------------------

agent = Agent(
    "google-gla:gemini-2.5-flash",
    deps_type=MeshContext,
    output_type=AgentResponse,
)


# ---------------------------------------------------------------------------
# Shared personality prompt (always present)
# ---------------------------------------------------------------------------


@agent.system_prompt
def personality() -> str:
    return (
        "You are MeshAI. You pay people for quick research chats "
        "on WhatsApp. Your vibe: fun, warm, quick. Like texting a friend "
        "who happens to pay you. 1-3 sentences max per message. "
        "Emojis natural, not forced. Never corporate."
    )


# ---------------------------------------------------------------------------
# Context-aware prompt (switches on mode)
# ---------------------------------------------------------------------------


@agent.system_prompt
def context(ctx: RunContext[MeshContext]) -> str:
    mode = ctx.deps.mode
    if mode == "onboarding":
        return _onboarding_block(ctx.deps)
    elif mode == "campaign":
        return _campaign_block(ctx.deps)
    elif mode == "bounty":
        return _bounty_block(ctx.deps)
    else:  # general
        return _general_block(ctx.deps)


# ---------------------------------------------------------------------------
# Context block builders
# ---------------------------------------------------------------------------


def _onboarding_block(deps: MeshContext) -> str:
    demos = deps.user_demographics
    collected = []
    missing = []

    for key, required in [("city", True), ("neighborhood", False), ("age_range", True), ("gender", True)]:
        val = demos.get(key)
        if val:
            collected.append(f"- {key}: {val}")
        else:
            label = {
                "city": "city (required — ask directly)",
                "neighborhood": "neighborhood (probe once — 'which part of [city]?', accept if skipped)",
                "age_range": "age_range (required — offer brackets: 18-24, 25-34, 35-44, 45+)",
                "gender": "gender (required — Male / Female / Other)",
            }[key]
            missing.append(f"- {label}")

    collected_str = "\n".join(collected) if collected else "Nothing yet."
    missing_str = "\n".join(missing) if missing else "All collected!"

    return f"""MODE: ONBOARDING
A new person just messaged. Your job:
1. Welcome them warmly. Explain MeshAI in one sentence.
2. Collect their demographics naturally:
{missing_str}

ALREADY KNOWN:
{collected_str}

3. When done (city, age_range, and gender all filled), tell them they're set
   and bounties will come their way. Set conversation_complete = true.

Return demographics in user_demographics_update as you collect them.
Keys: city, neighborhood, age_range, gender."""


def _campaign_block(deps: MeshContext) -> str:
    extraction_schema = deps.extraction_schema or {}
    extracted_data = deps.extracted_data or {}

    schema_lines = "\n".join(
        f"- {key}: {field_def.get('description', '')} (type: {field_def.get('type', 'string')})"
        for key, field_def in extraction_schema.items()
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

    # Demographics section
    demos = deps.user_demographics
    demo_lines = "\n".join(
        f"- {k}: {demos.get(k) or 'unknown'}"
        for k in ("city", "neighborhood", "age_range", "gender")
    )

    custom_instructions = ""
    if deps.system_prompt_override:
        custom_instructions = f"\nADDITIONAL INSTRUCTIONS:\n{deps.system_prompt_override}\n"

    reward_line = f"REWARD: {deps.reward_text}" if deps.reward_text else ""
    reward_link_line = ""
    if deps.reward_link:
        reward_link_line = f"REWARD LINK (include when conversation_complete): {deps.reward_link}"

    return f"""MODE: CAMPAIGN CONVERSATION
{reward_line}
RESEARCH CONTEXT:
{deps.research_brief or ''}
{custom_instructions}
KNOWN ABOUT THIS PERSON:
{demo_lines}

DATA POINTS TO COLLECT:
{schema_lines}

ALREADY COLLECTED:
{already_collected}

STILL NEEDED:
{remaining_lines}

{reward_link_line}

RULES:
1. Your first message after they accept should signal the start clearly.
2. If any demographics above are "unknown", weave them in naturally
   at the start before the research questions. Return them in user_demographics_update.
3. Ask ONE question at a time. 1-3 sentences max.
4. Acknowledge what the person said before changing topics.
5. Use natural transitions. Never reveal you have a checklist.
6. Probe vague answers before moving on.
7. Be warm, fun, curious. This should feel enjoyable.
8. When ALL data points are collected with concrete answers,
   send a thank-you message and include the reward link.
   Set conversation_complete = true."""


def _bounty_block(deps: MeshContext) -> str:
    return f"""MODE: BOUNTY INTERPRETATION
The user was sent a bounty notification and has replied.
Research topic: {deps.research_brief or 'N/A'}
Reward: {deps.reward_text or 'N/A'}

Your job: interpret whether they ACCEPT or DECLINE the bounty.

Accept signals: "go", "sure", "yes", "let's do it", "ok", "start", "yeah", anything affirmative.
Decline signals: "no", "pass", "not now", "nah", "skip", anything negative.

If they ACCEPT:
- Set bounty_accepted = true
- Send an enthusiastic kickoff message like "Let's do it! 🚀" and ask the first question.
- Do NOT set conversation_complete.

If they DECLINE:
- Set bounty_accepted = false
- Send "No worries, catch you next time! 👋"
- Set conversation_complete = true

If AMBIGUOUS (can't tell):
- Set bounty_accepted = null (do not set it)
- Ask for clarification naturally: "Just checking — want to jump in? Reply 'go' to start!"
- Do NOT set conversation_complete."""


def _general_block(deps: MeshContext) -> str:
    return """MODE: GENERAL
This person is in the MeshAI paid research network.
They've messaged outside of an active bounty. They might be:
- Asking how MeshAI works
- Asking about rewards or payments
- Just saying hi
- Asking when the next bounty is

Be friendly, brief, helpful. If they ask when the next bounty is,
tell them we'll send one when something matches their profile.
If they have a question you can't answer, tell them to reach out
to support.

Keep it to 1-2 sentences. Don't over-explain.
Never set conversation_complete to true."""


# ---------------------------------------------------------------------------
# User prompt builder
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Single entry point
# ---------------------------------------------------------------------------


async def get_agent_response(deps: MeshContext) -> AgentResponse:
    if not _ai_enabled():
        raise RuntimeError("AI is not enabled — set GOOGLE_API_KEY")

    user_prompt = _build_user_prompt(deps.conversation_history)
    result = await agent.run(user_prompt, deps=deps)
    return result.output
