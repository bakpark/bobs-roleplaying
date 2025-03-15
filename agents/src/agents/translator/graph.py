from dataclasses import field
from typing import Optional, Type, TypedDict, Union, cast

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a translator. Just translate the following text from English to Korean.",
        ),
        ("user", "{text}"),
    ]
)


class TranslatorState(TypedDict):
    original: Union[BaseModel, str]
    output_schema: Type[BaseModel]
    output: Union[BaseModel, str]


def translate(state: TranslatorState) -> TranslatorState:
    """
    주어진 상태의 원본 텍스트를 번역하고 결과를 반환하는 함수

    Args:
        state: 번역할 텍스트와 설정이 포함된 상태 객체

    Returns:
        번역된 결과가 포함된 새로운 상태 객체
    """
    # 입력 텍스트 처리: 문자열 또는 Pydantic 모델을 처리
    user_input = None
    if isinstance(state["original"], str):
        user_input = state["original"]
    else:
        user_input = state["original"].model_dump_json()

    output = None
    if state["output_schema"] is None:
        output = model.invoke(prompt.format(text=user_input))
    else:
        output_schema = state["output_schema"]
        model_with_schema = model.with_structured_output(output_schema)
        output = model_with_schema.invoke(prompt.format(text=user_input))

    # 번역된 결과를 직접 반환
    return {"output": output}


def create_translator_agent():
    builder = StateGraph(state_schema=TranslatorState)
    builder.add_node("translate", translate)
    builder.add_edge(START, "translate")
    builder.add_edge("translate", END)

    return builder.compile(name="translator")
