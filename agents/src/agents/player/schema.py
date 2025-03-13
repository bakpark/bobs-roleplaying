from pydantic import BaseModel
from typing import List, Literal, TypedDict

class MissionItem(BaseModel):
    id: Literal["main", "sub1", "sub2", "sub3"]
    success: bool
    
class PlayerLlmResponseSchema(BaseModel):
    content: str
    missions: List[MissionItem]
    action: str
    counterpart_response: List[str]

class PlayerAgentSystemPromptParams(BaseModel):
    situation: str
    role: str
    information: str
    missions: str
    scenario: str
    guidelines: str