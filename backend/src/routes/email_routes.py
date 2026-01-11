from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from src.models import EmailModel
from src.database import db
from src.dependencies import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/emails", tags=["emails"])

@router.get("/")
async def get_emails(
    language: Optional[str] = None,
    position: Optional[str] = None,
    company: Optional[str] = None,
    status: Optional[str] = None,
    job_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    query_filter = {"user_id": current_user["_id"]}
    
    if language:
        query_filter["language"] = language
    if position:
        query_filter["position"] = position
    if company:
        query_filter["company"] = company
    if status:
        query_filter["application_status"] = status
    if job_type:
        query_filter["job_type"] = job_type
    
    skip = (page - 1) * limit
    
    emails = await db.get_db().emails.find(query_filter).sort("received_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.get_db().emails.count_documents(query_filter)
    
    return {
        "emails": emails,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    }

@router.get("/{email_id}")
async def get_email(
    email_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        email = await db.get_db().emails.find_one({"_id": ObjectId(email_id)})
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        return email
    except:
        raise HTTPException(status_code=404, detail="Invalid email ID")

@router.patch("/{email_id}")
async def update_email(
    email_id: str,
    tags: Optional[List[str]] = None,
    starred: Optional[bool] = None,
    read: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    update_data = {"updated_at": datetime.utcnow()}
    
    if tags is not None:
        update_data["tags"] = tags
    if starred is not None:
        update_data["starred"] = starred
    if read is not None:
        update_data["read"] = read
    
    try:
        result = await db.get_db().emails.find_one_and_update(
            {"_id": ObjectId(email_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Email not found")
        
        return result
    except:
        raise HTTPException(status_code=404, detail="Invalid email ID")

@router.delete("/{email_id}")
async def delete_email(
    email_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        result = await db.get_db().emails.delete_one({"_id": ObjectId(email_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Email not found")
        return {"message": "Email deleted"}
    except:
        raise HTTPException(status_code=404, detail="Invalid email ID")
