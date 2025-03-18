import json

from pydantic import BaseModel, Field


class UserMission(BaseModel):
    main: str = Field(
        ...,
        description="The user mission when completed, concludes the scenario (include clear completion conditions).",
    )
    sub: str = Field(
        ...,
        description="The user mission that can be achieved through specific actions or dialogue choices.",
    )
    hidden: str = Field(
        ...,
        description="The user mission that can be related to the sub mission.",
    )


class ActingScriptSchema(BaseModel):
    user_wants: str = Field(
        ..., description="The scenario requirements user wants to have."
    )
    situation: str = Field(..., description="The situation of the scenario.")
    assistant_actor_role: str = Field(
        ...,
        description="The role of the ai assistant. Must include important information in scenario.",
    )
    assistant_actor_instructions: str = Field(
        ...,
        description="The acting instructions for the ai assistant for the scenario.",
    )
    user_role: str = Field(
        ...,
        description="The role of the user. Must include important information in scenario.",
    )
    user_missions: UserMission = Field(
        ..., description="The missions of the user through the scenario."
    )

    def from_json_string(json_string: str) -> "ActingScriptSchema":
        return ActingScriptSchema(**json.loads(json_string))

    def to_script_message(self) -> str:
        return f"""[Situation]
{self.situation}

[Your Role]
{self.user_role}

[Counterpart Role]
{self.assistant_actor_role}

[Your Missions]
main: {self.user_missions.main}
sub: {self.user_missions.sub}
hidden: {self.user_missions.hidden}
    """
