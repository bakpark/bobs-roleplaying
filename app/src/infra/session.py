from uuid import UUID, uuid4
from fastapi import Depends, HTTPException
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sessions.frontends.implementations import CookieParameters, SessionCookie
from pydantic import BaseModel
from typing import Optional
from util.logging import logger
from fastapi_sessions.backends.session_backend import SessionBackend
import os


DEFAULT_EXPIRED_MINUTES = 60


class SessionData(BaseModel):
    email: str
    session_id: UUID


# Secure cookie parameters
cookie_params = CookieParameters(
    name="session_id",
    max_age=DEFAULT_EXPIRED_MINUTES * 60,  # 1 hour
    httponly=True,
    secure=False,  # Use HTTPS only
    samesite="lax",
)


# Create session cookie
cookie = SessionCookie(
    cookie_name="session_id",
    identifier="general_session",
    auto_error=False,
    secret_key=os.getenv("SESSION_SECRET_KEY", "secret"),
    cookie_params=cookie_params,
)

# Create session backend
backend = InMemoryBackend[UUID, SessionData]()


async def create_session(email: str) -> UUID:
    session_id = uuid4()
    session_data = SessionData(email=email, session_id=session_id)
    await backend.create(session_id=session_id, data=session_data)
    logger.info(f"Session {session_id} created. email: {email}")
    return session_id


async def refresh_session(session_id: UUID, email: str):
    await backend.delete(session_id=session_id)
    logger.info(f"Session {session_id} deleted. email: {email}")
    return await create_session(email)


async def delete_session(session_id: UUID):
    await backend.delete(session_id=session_id)


class Verifier(SessionVerifier[UUID, SessionData]):

    @property
    def identifier(self) -> str:
        return "general_session"

    @property
    def backend(self) -> SessionBackend[UUID, SessionData]:
        return backend

    @property
    def auto_error(self) -> bool:
        return False

    @property
    def auth_http_exception(self) -> HTTPException:
        return HTTPException(status_code=401, detail="Unauthorized")

    async def verify_session(self, model: SessionData) -> Optional[SessionData]:
        session_data = await backend.read(model.session_id)
        if session_data is None:
            return None
        if session_data.session_id != model.session_id:
            return None
        return session_data

    async def verify(self, session_id: UUID) -> Optional[SessionData]:
        session_data = await backend.read(session_id)
        if session_data is None:
            return None
        if session_data.session_id != session_id:
            return None
        return session_data


verifier = Verifier()


async def get_session_data(session_id: UUID = Depends(cookie)) -> Optional[SessionData]:
    return await verifier.verify(session_id=session_id)
