from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.infra.session import SessionData, delete_session, get_session_data
from util.logging import logger

router = APIRouter()

templates = Jinja2Templates(directory="static")


@router.get("/")
async def get_index(
    request: Request, session: Optional[SessionData] = Depends(get_session_data)
):
    if session:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"email": session.email, "session_id": session.session_id},
        )

    return RedirectResponse(url="/login", status_code=302)


@router.get("/login")
async def get_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={})


@router.get("/logout")
async def get_logout(session: Optional[SessionData] = Depends(get_session_data)):
    if session is None:
        return RedirectResponse(url="/login")
    await delete_session(session.session_id)
    return RedirectResponse(url="/login")


@router.get("/scenario/{scenario_id}/play")
async def get_play(
    request: Request,
    scenario_id: str,
    session: Optional[SessionData] = Depends(get_session_data),
):
    if session is None:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        request=request,
        name="play.html",
        context={"scenario_id": scenario_id, "session_id": session.session_id},
    )
