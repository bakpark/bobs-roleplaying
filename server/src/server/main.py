from agents.player.prompt import get_player_system_prompt
from agents.player.schema import PlayerAgentSystemPromptParams
from server.chat_gtts import synthesize_text_to_speech
from server.db import DATABASE_URL, init_db, insert_acting_script, get_acting_script
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain.schema import HumanMessage
from agents.director.graph import create_director_agent
from agents.player.graph import create_player_agent
from server.schema import SimpleMessageRequest, TextRequest
from contextlib import asynccontextmanager
from util.logging import logger
from fastapi import Response

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

# CORS 설정: 모든 Origin 허용 (필요에 따라 조정 가능)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

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
    async with AsyncSqliteSaver.from_conn_string(DATABASE_URL) as conn:
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

@app.get("/tts")
def tts_endpoint(text: str):
    """
    쿼리 파라미터로 'text'를 받아 해당 텍스트의 음성(MP3 바이트)을 반환합니다.
    """
    audio_bytes = synthesize_text_to_speech(text)
    # MP3 오디오 바이너리를 Response로 반환 (MIME 타입 audio/mpeg)
    return Response(content=audio_bytes, media_type="audio/mpeg")

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)