from datetime import datetime

from pydantic import BaseModel, Field, field_serializer

from confiacim_api.const import MAX_TAG_NAME_LENGTH


class CaseCreate(BaseModel):
    tag: str = Field(max_length=MAX_TAG_NAME_LENGTH)


class CasePublic(BaseModel):
    id: int
    user_id: int = Field(serialization_alias="user")
    tag: str = Field(max_length=MAX_TAG_NAME_LENGTH)
    tencim_results: list = Field(serialization_alias="tencim_result_ids")
    created_at: datetime
    updated_at: datetime

    @field_serializer("tencim_results")
    def tencim_result_ids(self, tencim_results, _info) -> list[int]:
        return [t.id for t in tencim_results]


class CaseList(BaseModel):
    cases: list[CasePublic]
