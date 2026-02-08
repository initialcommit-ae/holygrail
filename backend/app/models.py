from __future__ import annotations

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


class AgentResponse(BaseModel):
    message: str = Field(min_length=1, description="Next WhatsApp message to send")
    extracted_data_update: dict = Field(
        default_factory=dict,
        description="New data points extracted from this exchange",
    )
    conversation_complete: bool = Field(
        default=False,
        description="True when all schema fields are filled",
    )
    internal_reasoning: str = Field(
        default="",
        description="Agent's strategy notes (not sent to user)",
    )
