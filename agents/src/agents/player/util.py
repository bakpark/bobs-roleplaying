from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AnyMessage, MessageLikeRepresentation
from typing import Optional, Literal, Union
from langgraph.graph import add_messages
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

log_dir = os.path.join(os.getenv("LOG_PATH", os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 현재 시각으로 로그 파일명 설정
log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
log_filepath = os.path.join(log_dir, log_filename)

logging.basicConfig(level=logging.INFO, format="%(asctime)s :: %(message)s", 
                    handlers=[logging.StreamHandler(), logging.FileHandler(log_filepath)])
logger = logging.getLogger(__name__)


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