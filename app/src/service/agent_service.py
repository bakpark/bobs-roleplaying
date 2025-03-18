import asyncio
from typing import cast
from agents.director.graph import create_director_agent
from agents.player.graph import create_player_agent
from agents.player.prompt import get_player_system_prompt
from agents.scriptwriter.schema import ActingScriptSchema
from langchain.schema import HumanMessage, AIMessage
from pydantic import BaseModel, Field
from src.schema import DirectorResponse, PlayerResponse
from src.translation import to_korean_with_agent
from src.infra.db import DATABASE_URL, insert_script, get_script
from util.logging import logger
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

beginning_message = "안녕하세요! 어떤 시나리오를 만들어 볼까요?"


async def direct(email: str, message: str, session_id: str) -> DirectorResponse:
    async with AsyncSqliteSaver.from_conn_string(DATABASE_URL) as async_saver:
        director_agent = create_director_agent(checkpointer=async_saver)
        messages = []

        checkpoint = await async_saver.aget({"configurable": {"thread_id": session_id}})
        if checkpoint is None:
            logger.info(f"No checkpoint found for session_id: {session_id}")
            messages = [AIMessage(content=beginning_message)]

        response = await director_agent.ainvoke(
            {"messages": messages + [HumanMessage(content=message)]},
            config={"configurable": {"thread_id": session_id}},
        )

        ai_message = response["messages"][-1].content

        if response["done"]:
            acting_script = response["script"]

            # Insert script into db
            script_id = await insert_script(acting_script.model_dump_json(), email)
            return DirectorResponse(ok=True, content=ai_message, script_id=script_id)

        keywords = response["question"].options

        return DirectorResponse(ok=True, content=ai_message, keywords=keywords)


class TranslationSchema(BaseModel):
    message: str = Field(..., description="The translation of the message.")
    possible_answers: list[str] = Field(
        ..., description="The translation of the possible answers."
    )


async def _translate_agent_response(response: dict) -> TranslationSchema:
    message = response["messages"][-1].content
    answers = ",".join([answer.response for answer in response["expected_response"]])

    original = """
    [Message]
    {message}

    [Possible Answers]
    {answers}
    """.format(
        message=message, answers=answers
    )

    translated: TranslationSchema = cast(
        TranslationSchema, await to_korean_with_agent(original, TranslationSchema)
    )
    logger.info(f"Translated: {translated}")

    return translated


async def play(script_id: str, message: str, session_id: str) -> PlayerResponse:
    async with AsyncSqliteSaver.from_conn_string(DATABASE_URL) as async_saver:
        player_agent = create_player_agent(checkpointer=async_saver)
        script_info = await get_script(script_id)
        if script_info is None:
            return {"ok": False, "message": "No acting script found"}
        acting_script = ActingScriptSchema.from_json_string(script_info["script_json"])
        player_system_prompt = get_player_system_prompt(acting_script)

        response = await player_agent.ainvoke(
            input={"messages": [HumanMessage(content=message)]},
            config={
                "configurable": {
                    "thread_id": session_id,
                    "model": "openai/gpt-4o-mini",
                    "system_prompt": player_system_prompt,
                }
            },
        )
        translated_response = await _translate_agent_response(response)

        return PlayerResponse(
            ok=True,
            content=response["messages"][-1].content,
            missions=response["missions"],
            action=response["action"],
            suggestions=[
                {
                    "id": f"suggestion_{i+1}",
                    "title": suggestion.response,
                    "tags": [suggestion.difficulty],
                    "description": translated_response.possible_answers[i],
                }
                for i, suggestion in enumerate(response["expected_response"])
            ],
        )
