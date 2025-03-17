from typing import Any, Optional

from agents.player.schema import MissionItem
from agents.scriptwriter.schema import ActingScriptSchema
from pydantic import BaseModel


class SimpleMessageRequest(BaseModel):
    message: str
    session_id: str


class TextRequest(BaseModel):
    text: str


class Mission(BaseModel):
    mission_id: str
    title: str
    description: str


class ScenarioScriptResponse(BaseModel):
    ok: bool
    user_role: str
    assistant_role: str
    situation: str
    missions: list[Mission]

    @staticmethod
    def from_acting_script(
        acting_script: ActingScriptSchema,
    ) -> "ScenarioScriptResponse":
        return ScenarioScriptResponse(
            ok=True,
            user_role=acting_script.user_role,
            assistant_role=acting_script.assistant_actor_role,
            situation=acting_script.situation,
            missions=[
                Mission(
                    mission_id="main",
                    title="Main",
                    description=acting_script.user_missions.main,
                ),
                Mission(
                    mission_id="sub",
                    title="Sub",
                    description=acting_script.user_missions.sub,
                ),
                Mission(
                    mission_id="hidden",
                    title="Hidden",
                    description=acting_script.user_missions.hidden,
                ),
            ],
        )


class PlayerResponse(BaseModel):
    ok: bool
    content: str
    missions: list[MissionItem]
    action: str
    suggestions: list[dict[str, Any]]


class DirectorResponse(BaseModel):
    ok: bool
    content: str
    script_id: Optional[int] = None
