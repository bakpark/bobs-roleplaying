from typing import List, Literal

from pydantic import BaseModel

mission_ids = Literal["main", "sub", "hidden"]


class MissionItem(BaseModel):
    id: mission_ids
    success: bool


class ExpectedUserResponse(BaseModel):
    response: str
    difficulty: Literal["Basic", "Intermediate", "Complex"]


class PlayerLlmResponseSchema(BaseModel):
    response: str
    missions: List[MissionItem]
    action: str
    expected_user_response: List[ExpectedUserResponse]
