from agents.player.prompt import get_player_system_prompt
from agents.player.schema import PlayerAgentSystemPromptParams
from server.query import DATABASE_URL, init_db, insert_acting_script, get_acting_script
import uvicorn
from fastapi import FastAPI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain.schema import HumanMessage
from agents.director.graph import create_director_agent
from agents.player.graph import create_player_agent
from server.schema import SimpleMessageRequest
from contextlib import asynccontextmanager
from util.logging import logger
        
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/director")
async def director_endpoint(message_request: SimpleMessageRequest):
    async with AsyncSqliteSaver.from_conn_string(DATABASE_URL) as conn:
        director_agent = create_director_agent(checkpointer=conn)
        
        response = await director_agent.ainvoke(
            {"messages": [HumanMessage(content=message_request.message)]}, 
            config={"configurable": {"thread_id": message_request.session_id}}
        )
        if str(response["messages"][-1].content).find("[Acting Script]") != -1:
            await insert_acting_script(
                message_request.session_id, 
                response["messages"][-1].content.split("[Acting Script]")[1].strip()
            )
        return {"response": response["messages"][-1]}    

@app.post("/player")
async def player_endpoint(message_request: SimpleMessageRequest):
    async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as conn:
        player_agent = create_player_agent(checkpointer=conn)
        
        acting_script = await get_acting_script(message_request.session_id)
        if acting_script is None:
            return {"response": "No acting script found"}
        logger.info(f"Acting script: {acting_script}")
        prompt_params = PlayerAgentSystemPromptParams.from_json_string(acting_script)
        player_system_prompt = get_player_system_prompt(prompt_params)
        
        response = await player_agent.ainvoke(
            input={
                "messages": [HumanMessage(content=message_request.message)]
            }, 
            config={
                "configurable": {
                    "thread_id": message_request.session_id,
                    "model": "openai/gpt-4o-mini",
                    "system_prompt": player_system_prompt
                }
            }
        )
        logger.info(f"Player response: {response}")
    return {"response": response["messages"][-1]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)