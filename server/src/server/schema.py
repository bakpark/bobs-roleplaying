from typing import Any
from pydantic import BaseModel
from agents.player.schema import ActingScriptSchema, MissionItem

class SimpleMessageRequest(BaseModel):
    message: str
    session_id: str
    
class DirectorMessageRequest(SimpleMessageRequest):
    scenario_id: str

class TextRequest(BaseModel):
    text: str
    
class Mission(BaseModel):
    mission_id: str
    title: str
    description: str

class UserDirectingResponse(BaseModel):
    user_role: str
    assistant_role: str
    situation: str
    missions: list[Mission]
    
    def from_acting_script(acting_script: ActingScriptSchema) -> "UserDirectingResponse":
        return UserDirectingResponse(
            user_role=acting_script.user_role,
            assistant_role=acting_script.assistant_actor_role,
            situation=acting_script.situation,
            missions=[
                Mission(
                    mission_id="main",
                    title="Main",
                    description=acting_script.user_missions["main"]
                ),
                Mission(
                    mission_id="sub",
                    title="Sub",
                    description=acting_script.user_missions["sub"]
                ),
                Mission(
                    mission_id="hidden",
                    title="Hidden Mission",
                    description=acting_script.user_missions["hidden"]
                )
            ]
        )
        
class PlayerActingResponse(BaseModel):
    ok: bool
    content: str
    missions: list[MissionItem]
    action: str
    suggestions: list[dict[str, Any]]