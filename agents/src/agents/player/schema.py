from typing import List, Literal

from pydantic import BaseModel, Field


class MissionItem(BaseModel):
    id: Literal["main", "sub", "hidden"]
    achievement: int = Field(..., description="The achievement of the mission. [0-100]")


class ExpectedUserResponse(BaseModel):
    response: str
    difficulty: Literal["Basic", "Intermediate", "Complex"]


class PlayerLlmResponseSchema(BaseModel):
    response: str
    missions: List[MissionItem]
    expected_user_response: List[ExpectedUserResponse]
