import asyncio
from agents.director.schema.schema import DirectorState
from agents.director.graph import create_director_agent
from agents.player.graph import create_player_agent
from agents.player.prompt import get_player_system_prompt
from agents.scriptwriter.schema import ActingScriptSchema
from langchain.schema import HumanMessage
from src.schema import DirectorResponse, PlayerResponse
from src.translation import toKorean
from src.infra.db import insert_script, get_script
from src.infra.checkpointer import async_saver
from src.infra.session import SessionData

director_agent = create_director_agent(checkpointer=async_saver)
player_agent = create_player_agent(checkpointer=async_saver)


async def direct(message: str, session_data: SessionData) -> DirectorResponse:
    response: DirectorState = await director_agent.ainvoke(
        {"messages": [HumanMessage(content=message)]},
        config={"configurable": {"thread_id": session_data.session_id}},
    )

    end = response["user_intent"] in ["Acceptance [FINAL OUTPUT]", "Stop"]
    script_id = None
    if end:
        acting_script = response["script"]
        script_id = await insert_script(
            acting_script.model_dump_json(), session_data.email
        )

    assistant_message = response["messages"][-1].content
    return DirectorResponse(ok=True, content=assistant_message, script_id=script_id)


async def play(
    script_id: str, message: str, session_data: SessionData
) -> PlayerResponse:
    script_info = await get_script(script_id)
    if script_info is None:
        return {"ok": False, "message": "No acting script found"}
    acting_script = ActingScriptSchema.from_json_string(script_info["script_json"])
    player_system_prompt = get_player_system_prompt(acting_script)

    response = await player_agent.ainvoke(
        input={"messages": [HumanMessage(content=message)]},
        config={
            "configurable": {
                "thread_id": session_data.session_id,
                "model": "openai/gpt-4o-mini",
                "system_prompt": player_system_prompt,
            }
        },
    )

    # 비동기 병렬 번역
    translated_suggestions = await asyncio.gather(
        *[toKorean(content.response) for content in response["expected_response"]]
    )

    return PlayerResponse(
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
