from typing import Literal, Optional

from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field
from util.langchain import AgentState

from agents.scriptwriter.schema import ActingScriptSchema

intention_literal = Literal["RESPOND", "REVISION", "INSTRUCTION", "STOP", "SKIP"]


class Question(BaseModel):
    message: str = Field(..., description="The text of the question in Korean.")
    options: list[str] = Field(
        ...,
        description="A list of options available for the question in Korean.",
    )


class DirectorState(AgentState):
    done: bool = False
    intention: Optional[intention_literal] = None
    script: Optional[ActingScriptSchema] = None
    question: Optional[Question] = None

    @staticmethod
    def get_initial_state():
        return {
            "messages": [
                AIMessage(content="시나리오 연기의 목적은 무엇인가요?"),
            ],
        }

    def is_include_script(self):
        return self.script is not None


class IntentionLlmResponse(BaseModel):
    reasoning: str = Field(
        ...,
        description="Brief explanation of why choose that.",
    )
    intention: intention_literal = Field(
        ...,
        description="The intention of the user's last message.",
    )
    confidence: int = Field(
        ...,
        description="1-10",
    )


class QuestionLlmResponse(BaseModel):
    question: Question = Field(
        ...,
        description="A question related to a specific scenario category.",
    )
