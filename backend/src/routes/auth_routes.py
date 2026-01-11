from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
import requests
from src.config import settings
from src.database import db
from datetime import datetime
from jose import jwt

router = APIRouter(prefix="/auth", tags=["auth"])

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/gmail.readonly'
]

def create_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.google_redirect_uri]
            }
        },
        scopes=SCOPES,
        redirect_uri=settings.google_redirect_uri
    )

@router.get("/google")
async def google_login():
    flow = create_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return {"authorization_url": authorization_url, "state": state}

@router.get("/google/callback")
async def google_callback(code: str, response: Response):
    try:
        # Exchange code for tokens directly via Google OAuth endpoint
        token_resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=15,
        )
        token_resp.raise_for_status()
        token_data = token_resp.json()

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token returned from Google")

        # Get user info using the access token
        userinfo_resp = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        userinfo_resp.raise_for_status()
        user_info = userinfo_resp.json()

        # Find or create user
        user = await db.get_db().users.find_one({"google_id": user_info["id"]})
        if not user:
            user_doc = {
                "google_id": user_info["id"],
                "email": user_info["email"],
                "name": user_info.get("name"),
                "avatar": user_info.get("picture"),
                "gmail_access_token": access_token,
                "gmail_refresh_token": refresh_token,
                "last_synced_at": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            result = await db.get_db().users.insert_one(user_doc)
            user_doc["_id"] = str(result.inserted_id)
            user = user_doc
        else:
            await db.get_db().users.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "gmail_access_token": access_token,
                        "gmail_refresh_token": refresh_token or user.get("gmail_refresh_token"),
                        "updated_at": datetime.utcnow(),
                    }
                },
            )
            user["gmail_access_token"] = access_token

        # Create app JWT and set cookie, then redirect to dashboard
        jwt_payload = {"user_id": str(user["_id"]), "email": user["email"]}
        app_token = jwt.encode(jwt_payload, settings.secret_key, algorithm=settings.algorithm)

        redir = RedirectResponse(url=f"{settings.frontend_url}/dashboard")
        redir.set_cookie(
            key="access_token",
            value=f"Bearer {app_token}",
            httponly=True,
            max_age=settings.access_token_expire_minutes * 60,
            samesite="lax",
            path="/"
        )
        return redir
    except requests.HTTPError as re:
        raise HTTPException(status_code=500, detail=f"Google OAuth HTTP error: {re.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth error: {str(e)}")

@router.post("/google/exchange")
async def google_exchange_code(request: Request, response: Response):
    """Exchange OAuth code for token - called by frontend"""
    try:
        body = await request.json()
        code = body.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="No code provided")
        
        # Exchange code for tokens
        token_resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=15,
        )
        token_resp.raise_for_status()
        token_data = token_resp.json()

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token from Google")

        # Get user info
        userinfo_resp = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        userinfo_resp.raise_for_status()
        user_info = userinfo_resp.json()

        # Find or create user
        user = await db.get_db().users.find_one({"google_id": user_info["id"]})
        if not user:
            user_doc = {
                "google_id": user_info["id"],
                "email": user_info["email"],
                "name": user_info.get("name"),
                "avatar": user_info.get("picture"),
                "gmail_access_token": access_token,
                "gmail_refresh_token": refresh_token,
                "last_synced_at": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            result = await db.get_db().users.insert_one(user_doc)
            user_doc["_id"] = str(result.inserted_id)
            user = user_doc
        else:
            await db.get_db().users.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "gmail_access_token": access_token,
                        "gmail_refresh_token": refresh_token or user.get("gmail_refresh_token"),
                        "updated_at": datetime.utcnow(),
                    }
                },
            )
            user["gmail_access_token"] = access_token
            user["_id"] = str(user["_id"])

        # Create JWT and set cookie
        jwt_payload = {"user_id": str(user["_id"]), "email": user["email"]}
        app_token = jwt.encode(jwt_payload, settings.secret_key, algorithm=settings.algorithm)
        
        response.set_cookie(
            key="access_token",
            value=f"Bearer {app_token}",
            httponly=True,
            max_age=settings.access_token_expire_minutes * 60,
            samesite="lax",
            path="/"
        )
        
        return {"success": True, "user": user}
    except requests.HTTPError as re:
        raise HTTPException(status_code=500, detail=f"Google OAuth error: {re.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exchange error: {str(e)}")

@router.get("/me")
async def get_current_user_route(request: Request):
    from src.dependencies import get_current_user
    try:
        user = await get_current_user(request)
        return user
    except HTTPException:
        raise HTTPException(status_code=401, detail="Not authenticated")

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}
