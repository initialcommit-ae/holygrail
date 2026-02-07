import logging
import os
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent

logger = logging.getLogger("backend.analytics_agent")


class AnalyticsAgentOutput(BaseModel):
    tsx: str = Field(min_length=1)


_SYSTEM_PROMPT = """
You generate a single React component for an analytics report.

Constraints:
- Output MUST be valid TSX module source code.
- NO imports, NO requires.
- Must export default function Report({ data }) { ... }.
- You may use hooks ONLY via global React: assume App sets `globalThis.React = React`.
  - If you need hooks, start with: `const React = globalThis.React;`
  - Then use `React.useMemo`, `React.useState` etc.
- Use only HTML + inline SVG (no external chart libs).
- Must render:
  - A summary section (status, total duration, question count, answer count).
  - A Q/A table.
  - A simple visualization: response time per question (bar chart in SVG).
- Keep it compact and readable.
- Do not access network, storage, cookies, or window/document.
""".strip()


def _ai_enabled() -> bool:
    return bool(os.environ.get("GOOGLE_API_KEY"))


_agent: Agent[Any, AnalyticsAgentOutput] | None = None


def _get_agent() -> Agent[Any, AnalyticsAgentOutput]:
    global _agent
    if _agent is None:
        _agent = Agent(
            "google-gla:gemini-2.5-flash",
            system_prompt=_SYSTEM_PROMPT,
            output_type=AnalyticsAgentOutput,
        )
    return _agent


def generate_report_tsx_sync(*, analysis_context: dict[str, Any]) -> str:
    if not _ai_enabled():
        raise RuntimeError("AI is not enabled (missing GOOGLE_API_KEY/GEMINI_API_KEY)")

    prompt = (
        "Generate a React analytics report component.\n\n"
        "Here is the input data JSON (use it via `data` prop):\n"
        f"{analysis_context}\n"
    )

    result = _get_agent().run_sync(prompt)
    tsx = (result.output.tsx or "").strip()
    if not tsx:
        raise RuntimeError("Empty TSX from agent")
    logger.info("Generated TSX length=%s", len(tsx))
    return tsx

