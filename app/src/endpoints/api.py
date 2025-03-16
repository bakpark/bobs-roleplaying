from agents.scriptwriter.schema import ActingScriptSchema
from fastapi import APIRouter, Response

from src.db import get_acting_script
from src.schema import UserDirectingResponse
from src.tts import synthesize_text_to_speech

router = APIRouter()


@router.get("/scenario/{scenario_id}/directing")
async def user_directing_endpoint(scenario_id: str):
    json_string = await get_acting_script(scenario_id)
    if json_string is None:
        return {"ok": False, "message": "No acting script found"}
    acting_script = ActingScriptSchema.from_json_string(json_string)
    user_directing_response = await UserDirectingResponse.from_acting_script(
        acting_script
    )
    return {"ok": True, "response": user_directing_response}


@router.get("/tts")
def tts_endpoint(text: str):
    """
    쿼리 파라미터로 'text'를 받아 해당 텍스트의 음성(MP3 바이트)을 반환합니다.
    """
    audio_bytes = synthesize_text_to_speech(text)
    # MP3 오디오 바이너리를 Response로 반환 (MIME 타입 audio/mpeg)
    return Response(content=audio_bytes, media_type="audio/mpeg")
