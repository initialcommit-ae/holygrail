from typing import List

from pydantic import BaseModel, Field


class StartRequest(BaseModel):
    questions: List[str] = Field(min_length=1)

