import asyncio
from agents.director.schema.schema import DirectorState
from agents.director.graph import create_director_agent
from agents.player.graph import create_player_agent
from agents.player.prompt import get_player_system_prompt
from agents.scriptwriter.schema import ActingScriptSchema
from langchain.schema import HumanMessage
from src.schema import DirectorResponse, PlayerResponse
from src.translation import toKorean
from src.infra.db import insert_acting_script, get_acting_script
from src.infra.checkpointer import async_saver


director_agent = create_director_agent(checkpointer=async_saver)
player_agent = create_player_agent(checkpointer=async_saver)


async def direct(scenario_id: str, message: str, session_id: str) -> DirectorResponse:
    response: DirectorState = await director_agent.ainvoke(
        {"messages": [HumanMessage(content=message)]},
        config={"configurable": {"thread_id": session_id}},
    )

    end = response["user_intent"] in ["Acceptance [FINAL OUTPUT]", "Stop"]
    if end:
        acting_script = response["script"]
        await insert_acting_script(scenario_id, acting_script.model_dump_json())

    assistant_message = response["messages"][-1].content
    return DirectorResponse(ok=True, content=assistant_message, end=end)


async def play(scenario_id: str, message: str, session_id: str) -> PlayerResponse:
    json_string = await get_acting_script(scenario_id)
    if json_string is None:
        return {"ok": False, "message": "No acting script found"}
    acting_script = ActingScriptSchema.from_json_string(json_string)
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
