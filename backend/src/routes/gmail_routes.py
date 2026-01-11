from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from src.dependencies import get_current_user
from src.services.llm_service import LLMService
from src.services.gmail_service import GmailService


class NaturalQueryBody(BaseModel):
    prompt: str
    limit: int = 50
    include_gmail_fetch: bool = True


router = APIRouter(prefix="/gmail", tags=["gmail"])


@router.post("/natural-query")
async def natural_query(body: NaturalQueryBody, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    llm = await LLMService.process_natural_language_query(body.prompt)
    # Map to stable response keys
    search_query = llm.get("gmail_query") or llm.get("search_query") or body.prompt
    query_intent = llm.get("query_intent", "search_emails")
    summary = llm.get("summary", f"Searching for: {body.prompt}")

    emails = []
    count = 0
    error = None
    
    if body.include_gmail_fetch:
        access_token = current_user.get("gmail_access_token")
        refresh_token = current_user.get("gmail_refresh_token")
        
        print(f"DEBUG: access_token exists: {bool(access_token)}")
        print(f"DEBUG: search_query: {search_query}")
        
        if access_token:
            try:
                gmail = GmailService(access_token=access_token, refresh_token=refresh_token)
                emails = await gmail.fetch_emails(query=search_query, max_results=body.limit)
                count = len(emails)
                print(f"DEBUG: Fetched {count} emails")
            except Exception as e:
                error = str(e)
                print(f"ERROR fetching emails: {error}")
        else:
            error = "No Gmail access token found. User needs to authenticate with Gmail."

    return {
        "query_intent": query_intent,
        "search_query": search_query,
        "summary": summary,
        "count": count,
        "emails": emails,
        "error": error,
    }


class SyncBody(BaseModel):
    prompt: Optional[str] = ""
    limit: int = 50


@router.post("/sync")
async def sync_emails(body: SyncBody, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    # Basic placeholder sync: perform search and return count
    search = body.prompt or ""
    emails = []
    access_token = current_user.get("gmail_access_token")
    refresh_token = current_user.get("gmail_refresh_token")
    if access_token:
        gmail = GmailService(access_token=access_token, refresh_token=refresh_token)
        emails = await gmail.fetch_emails(query=search, max_results=body.limit)
    return {"synced": len(emails)}
