"""Define the state structures for the agent."""

from dataclasses import dataclass, field
from typing_extensions import Annotated

from util.langchain import add_messages_with_logging
from langchain_core.messages import AnyMessage, SystemMessage


@dataclass
class InputState:
    """The input state for the agent."""
    messages: Annotated[list[AnyMessage], add_messages_with_logging] = field(
        default_factory=list,
    )

class State(InputState):
    system: SystemMessage = field(default_factory=SystemMessage)