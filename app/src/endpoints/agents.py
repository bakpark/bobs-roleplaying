from fastapi import APIRouter
from src.service import agent_service
from src.schema import (
    DirectorMessageRequest,
    PlayerResponse,
    SimpleMessageRequest,
    DirectorResponse,
)

router = APIRouter()


@router.post("/director")
async def director_endpoint(
    message_request: DirectorMessageRequest,
) -> DirectorResponse:
    response = await agent_service.direct(
        message_request.scenario_id, message_request.message, message_request.session_id
    )
    return response


@router.post("/scenario/{scenario_id}/player")
async def player_endpoint(
    scenario_id: str, message_request: SimpleMessageRequest
) -> PlayerResponse:
    response = await agent_service.play(
        scenario_id, message_request.message, message_request.session_id
    )
    return response
