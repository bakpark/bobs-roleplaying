from agents.scriptwriter.schema import ActingScriptSchema
from fastapi import APIRouter, Response

from src.schema import ScenarioScriptResponse
from src.service.acting_script_service import get_or_translate_acting_script
from src.service.audio_service import synthesize_text_to_speech

router = APIRouter()


@router.get("/scenario/{scenario_id}/script")
async def script_endpoint(scenario_id: str, language: str = "kr"):
    acting_script: ActingScriptSchema = await get_or_translate_acting_script(
        scenario_id, language
    )

    return ScenarioScriptResponse.from_acting_script(acting_script)


@router.get("/tts")
def tts_endpoint(text: str):
    """
    쿼리 파라미터로 'text'를 받아 해당 텍스트의 음성(MP3 바이트)을 반환합니다.
    """
    audio_bytes = synthesize_text_to_speech(text)
    # MP3 오디오 바이너리를 Response로 반환 (MIME 타입 audio/mpeg)
    return Response(content=audio_bytes, media_type="audio/mpeg")
