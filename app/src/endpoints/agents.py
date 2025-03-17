from fastapi import APIRouter, Depends
from src.infra.session import SessionData, get_session_data
from src.service import agent_service
from src.schema import (
    PlayerResponse,
    SimpleMessageRequest,
    DirectorResponse,
)

router = APIRouter()


@router.post("/director")
async def director_endpoint(
    message_request: SimpleMessageRequest,
    session_data: SessionData = Depends(get_session_data),
) -> DirectorResponse:
    response = await agent_service.direct(message_request.message, session_data)
    return response


@router.post("/script/{script_id}/player")
async def player_endpoint(
    script_id: str,
    message_request: SimpleMessageRequest,
    session_data: SessionData = Depends(get_session_data),
) -> PlayerResponse:
    response = await agent_service.play(
        script_id, message_request.message, session_data
    )
    return response
