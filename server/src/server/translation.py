from typing import Union
from googletrans import Translator
from agents.translator import create_translator_agent
from pydantic import BaseModel

# 전역 변수로 선언하여 재사용
translator = Translator()
translator_agent = create_translator_agent()

async def toKorean(text: str) -> str:
    translation = await translator.translate(text, src="en", dest="ko")
    return translation.text

async def toKoreanWithAgent(input: Union[str, BaseModel], output_schema: type[BaseModel] = None):
    result = await translator_agent.ainvoke({"original": input, "output_schema": output_schema})
    return result["output"]
