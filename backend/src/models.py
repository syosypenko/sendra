from pydantic import BaseModel, Field, field_validator
from pydantic_core import core_schema
from typing import Optional, List, Any
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler):
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.no_info_plain_validator_function(cls.validate),
        ])

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid objectid")

class EmailModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    gmail_id: str
    from_email: str = Field(..., alias="from")
    to: List[str]
    subject: str
    body: Optional[str] = None
    html_body: Optional[str] = None
    language: Optional[str] = "other"
    position: Optional[str] = None
    job_type: Optional[str] = None  # e.g., "full-time", "contract", "internship"
    company: Optional[str] = None
    application_status: Optional[str] = None  # e.g., "applied", "interview", "offer", "rejected"
    salary: Optional[str] = None  # e.g., "100k-120k"
    experience_level: Optional[str] = None  # e.g., "junior", "mid", "senior"
    tags: List[str] = []
    starred: bool = False
    read: bool = False
    received_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True

class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    google_id: str
    email: str
    name: Optional[str] = None
    avatar: Optional[str] = None
    gmail_access_token: Optional[str] = None
    gmail_refresh_token: Optional[str] = None
    last_synced_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True

class NaturalLanguageQueryRequest(BaseModel):
    prompt: str
    limit: int = 50
    include_gmail_fetch: bool = True

class NaturalLanguageQueryResponse(BaseModel):
    query_intent: str
    search_query: str
    emails: List[dict]
    summary: str
