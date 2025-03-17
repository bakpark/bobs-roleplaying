from fastapi import APIRouter, Depends, Response

from util.logging import logger
from src.infra.session import SessionData, get_session_data
from src.service.script_service import (
    get_or_translate_script_info,
    get_user_scripts,
    delete_script,
)
from src.service.audio_service import synthesize_text_to_speech

router = APIRouter()


@router.get("/script/{script_id}")
async def script_endpoint(script_id: str, language: str = "kr"):
    script_info = await get_or_translate_script_info(script_id, language)
    if script_info is None:
        return Response(status_code=404, content="Script not found")

    return {"content": script_info.to_script_message(), "script_info": script_info}


@router.get("/brief-scripts")
async def user_scripts_endpoint(
    language: str = "kr",
    session_data: SessionData = Depends(get_session_data),
):
    scripts = await get_user_scripts(session_data.email, language)
    return {"scripts": scripts}


@router.delete("/script/{script_id}")
async def delete_script_endpoint(
    script_id: int, session_data: SessionData = Depends(get_session_data)
):
    await delete_script(session_data.email, script_id)
    return {"ok": True}


@router.get("/tts")
def tts_endpoint(text: str):
    """
    쿼리 파라미터로 'text'를 받아 해당 텍스트의 음성(MP3 바이트)을 반환합니다.
    """
    audio_bytes = synthesize_text_to_speech(text)
    # MP3 오디오 바이너리를 Response로 반환 (MIME 타입 audio/mpeg)
    return Response(content=audio_bytes, media_type="audio/mpeg")
