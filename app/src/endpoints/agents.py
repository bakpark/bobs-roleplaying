import asyncio
from fastapi import APIRouter
from langchain.schema import HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from src.db import DATABASE_URL, get_acting_script, insert_acting_script
from src.schema import (
    DirectorMessageRequest,
    PlayerActingResponse,
    SimpleMessageRequest,
)
from src.translation import toKorean, toKoreanWithAgent

from agents.director.graph import create_director_agent
from agents.player.graph import create_player_agent
from agents.player.prompt import get_player_system_prompt
from agents.player.schema import ActingScriptSchema

router = APIRouter()


@router.post("/director")
async def director_endpoint(message_request: DirectorMessageRequest):
    async with AsyncSqliteSaver.from_conn_string(DATABASE_URL) as conn:
        director_agent = create_director_agent(checkpointer=conn)

        response = await director_agent.ainvoke(
            {"messages": [HumanMessage(content=message_request.message)]},
            config={"configurable": {"thread_id": message_request.session_id}},
        )

        assistant_message = response["messages"][-1].content
        if str(assistant_message).find("[FINAL OUTPUT]") != -1:
            final_output = (
                assistant_message.split("[FINAL OUTPUT]")[1]
                .strip()
                .replace("\n", "")
                .replace("\\", "")
            )
            translated: ActingScriptSchema = await toKoreanWithAgent(
                final_output, ActingScriptSchema
            )
            await insert_acting_script(
                message_request.scenario_id, translated.model_dump_json()
            )
        return {"ok": True, "content": assistant_message}


@router.post("/scenario/{scenario_id}/player")
async def player_endpoint(scenario_id: str, message_request: SimpleMessageRequest):
    async with AsyncSqliteSaver.from_conn_string(DATABASE_URL) as conn:
        player_agent = create_player_agent(checkpointer=conn)

        json_string = await get_acting_script(scenario_id)
        if json_string is None:
            return {"ok": False, "message": "No acting script found"}
        acting_script = ActingScriptSchema.from_json_string(json_string)
        player_system_prompt = get_player_system_prompt(acting_script)

        response = await player_agent.ainvoke(
            input={"messages": [HumanMessage(content=message_request.message)]},
            config={
                "configurable": {
                    "thread_id": message_request.session_id,
                    "model": "openai/gpt-4o-mini",
                    "system_prompt": player_system_prompt,
                }
            },
        )

        # 비동기 병렬 번역
        translated_suggestions = await asyncio.gather(
            *[toKorean(content.response) for content in response["expected_response"]]
        )

        return PlayerActingResponse(
            ok=True,
            content=response["messages"][-1].content,
            missions=response["missions"],
            action=response["action"],
            suggestions=[
                {
                    "id": f"suggestion_{i+1}",
                    "title": content.response,
                    "tags": [content.difficulty],
                    "description": translated_suggestions[i],
                }
                for i, content in enumerate(response["expected_response"])
            ],
        )
