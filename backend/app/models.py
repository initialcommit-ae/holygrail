from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExtractionField(BaseModel):
    type: str = Field(min_length=1, description="e.g. 'string', 'number', 'number(1-10)'")
    description: str = Field(min_length=1)


class CreateCampaignRequest(BaseModel):
    name: str = Field(min_length=1)
    research_brief: str = Field(min_length=1)
    extraction_schema: dict[str, ExtractionField]
    phone_numbers: list[str] = Field(min_length=1)
    system_prompt_override: str | None = None
    reward_text: str | None = None
    reward_link: str | None = None
    targeting: dict[str, Any] | None = None  # V2 — schema-ready, not used in launch yet


class AgentResponse(BaseModel):
    message: str = Field(min_length=1, description="Next WhatsApp message to send")
    extracted_data_update: dict = Field(
        default_factory=dict,
        description="New data points extracted from this exchange",
    )
    user_demographics_update: dict = Field(
        default_factory=dict,
        description="Demographics extracted (city, neighborhood, age_range, gender)",
    )
    conversation_complete: bool = Field(
        default=False,
        description="True when all required data is collected",
    )
    bounty_accepted: bool | None = Field(
        default=None,
        description="For bounty_sent interpretation — True=accepted, False=declined, None=ambiguous",
    )
    internal_reasoning: str = Field(
        default="",
        description="Agent's strategy notes (not sent to user)",
    )
