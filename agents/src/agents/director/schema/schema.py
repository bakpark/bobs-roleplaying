from typing import Literal, Optional

from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field
from util.langchain import AgentState

from agents.director.prompt import system_prompt
from agents.scriptwriter.schema import ActingScriptSchema

intent_literal = Literal[
    "Answer",
    "Stop",
    "Just do it",
    "Acceptance [FINAL OUTPUT]",
]


class Question(BaseModel):
    message: str = Field(..., description="The text of the question in Korean.")
    options: list[str] = Field(
        ...,
        description="A list of options available for the question in Korean.",
    )


class DirectorState(AgentState):
    user_intent: Optional[intent_literal] = None
    script: Optional[ActingScriptSchema] = None
    question: Optional[Question] = None

    @staticmethod
    def get_initial_state():
        return {
            "messages": [
                AIMessage(content="시나리오 연기의 목적은 무엇인가요?"),
            ],
        }


class IntentLlmResponse(BaseModel):
    intent: intent_literal = Field(
        ...,
        description="The intent of the user's last message.",
    )


class QuestionLlmResponse(BaseModel):
    question: Question = Field(
        ...,
        description="A question related to a specific scenario category.",
    )
