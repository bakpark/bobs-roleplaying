from langchain_core.language_models import BaseChatModel
from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, MessageLikeRepresentation
from typing import Annotated, Optional, Literal, TypedDict, Union
from .logging import logger
from langgraph.graph import add_messages

def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    provider, model = fully_specified_name.split("/", maxsplit=1)
    return init_chat_model(model, model_provider=provider)

def add_messages_with_logging(
    left: Union[list[MessageLikeRepresentation], MessageLikeRepresentation],
    right: Union[list[MessageLikeRepresentation], MessageLikeRepresentation],
    *,
    format: Optional[Literal["langchain-openai"]] = None,
) -> Union[list[MessageLikeRepresentation], MessageLikeRepresentation]:
    """Add logging to the messages."""
    logger.info(f">> add_messages: {right}")
    return add_messages(left, right, format=format)

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    
class LoggableState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages_with_logging]