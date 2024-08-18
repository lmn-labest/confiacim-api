from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from confiacim_api.const import MAX_TAG_NAME_LENGTH
from confiacim_api.schemes.tencim import TencimResultSummary


class CaseCreate(BaseModel):
    tag: str = Field(max_length=MAX_TAG_NAME_LENGTH)
    description: Optional[str] = None


class CasePublic(BaseModel):
    id: int
    user_id: int = Field(serialization_alias="user")
    tag: str = Field(max_length=MAX_TAG_NAME_LENGTH)
    description: Optional[str] = None
    tencim_results: list[TencimResultSummary] = Field(serialization_alias="tencim_result_ids")
    created_at: datetime
    updated_at: datetime
