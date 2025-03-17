import os
from fastapi.responses import RedirectResponse
import httpx
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.infra.session import create_session, cookie
from util.logging import logger


router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "YOUR_GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000")
FRONTEND_REDIRECT_URL = os.getenv("FRONTEND_REDIRECT_URL", "http://localhost:8000")


class GoogleUserInfo(BaseModel):
    id: str
    email: str


class GoogleTokenData(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    id_token: Optional[str] = None


@router.get("/login/google")
async def login_google():
    """Google OAuth 로그인 URL로 리디렉션합니다"""
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }

    authorize_url = (
        f"{google_auth_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    )
    return RedirectResponse(url=authorize_url)


@router.get("/google/callback")
async def auth_google_callback(code: str = None, error: str = None):
    """Google OAuth 콜백 처리"""
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth 인증 오류: {error}")

    if not code:
        raise HTTPException(status_code=400, detail="인증 코드가 제공되지 않았습니다")

    # 코드를 액세스 토큰으로 교환
    token_url = "https://oauth2.googleapis.com/token"
    async with httpx.AsyncClient() as client:
        token_data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        token_response = await client.post(token_url, data=token_data)

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=400, detail=f"토큰 교환 실패: {token_response.text}"
            )

        token_info = GoogleTokenData(**token_response.json())

        # 액세스 토큰으로 사용자 정보 가져오기
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {token_info.access_token}"}
        userinfo_response = await client.get(userinfo_url, headers=headers)

        logger.info(f"userinfo_response: {userinfo_response.json()}")

        if userinfo_response.status_code != 200:
            raise HTTPException(status_code=400, detail="사용자 정보 가져오기 실패")

        user_info = GoogleUserInfo(**userinfo_response.json())

        session_id = await create_session(user_info.email)
        redirect = RedirectResponse(url="/", status_code=302)
        cookie.attach_to_response(redirect, session_id)
        return redirect
