from typing import Union

from agents.translator import create_translator_agent
from googletrans import Translator
from pydantic import BaseModel
from util.logging import logger

# 전역 변수로 선언하여 재사용
translator = Translator()
translator_agent = create_translator_agent()


async def to_korean(text: str) -> str:
    translation = await translator.translate(text, src="en", dest="ko")
    return translation.text


async def to_korean_in_conversation(prev: str, current: str) -> str:
    translation = await translator.translate(
        f"A :{prev}\nB :{current}", src="en", dest="ko"
    )
    splited = translation.text.split("B :")
    if len(splited) == 2:
        return splited[1]
    else:
        logger.error(f"Failed to translate conversation: {translation.text}")
        return translation.text


async def to_korean_with_agent(
    input: Union[str, BaseModel], output_schema: type[BaseModel] = None
):
    result = await translator_agent.ainvoke(
        {
            "original": input,
            "output_schema": output_schema,
            "src_language": "en",
            "dist_language": "ko",
        }
    )
    return result["output"]
