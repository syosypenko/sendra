from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from bson import ObjectId

from src.dependencies import get_current_user
from src.database import db
from src.models import CollectionModel, CollectionEmail

router = APIRouter(prefix="/collections", tags=["collections"])


@router.get("")
async def list_collections(current_user: dict = Depends(get_current_user)) -> List[dict]:
    # current_user["_id"] is a string from get_current_user, convert back to ObjectId for query
    user_id = ObjectId(current_user["_id"]) if isinstance(current_user["_id"], str) else current_user["_id"]
    print(f"DEBUG: Listing collections for user {user_id}")
    cursor = db.get_db().collections.find({"user_id": user_id}).sort("created_at", -1)
    collections = await cursor.to_list(length=100)
    print(f"DEBUG: Found {len(collections)} collections")
    # Convert ObjectId to string for serialization
    for col in collections:
        if "_id" in col:
            col["_id"] = str(col["_id"])
        if "user_id" in col:
            col["user_id"] = str(col["user_id"])
    return collections


@router.get("/{collection_id}")
async def get_collection(collection_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    # current_user["_id"] is a string from get_current_user, convert back to ObjectId
    user_id = ObjectId(current_user["_id"]) if isinstance(current_user["_id"], str) else current_user["_id"]
    try:
        collection = await db.get_db().collections.find_one({"_id": ObjectId(collection_id), "user_id": user_id})
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid collection id")

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    # Convert ObjectId to string for serialization
    if "_id" in collection:
        collection["_id"] = str(collection["_id"])
    if "user_id" in collection:
        collection["user_id"] = str(collection["user_id"])
    return collection


@router.post("")
async def create_collection(payload: dict, current_user: dict = Depends(get_current_user)) -> dict:
    name = payload.get("name")
    emails_payload = payload.get("emails", [])
    # current_user["_id"] is a string from get_current_user, convert back to ObjectId
    user_id_str = current_user["_id"]
    user_id_obj = ObjectId(user_id_str) if isinstance(user_id_str, str) else user_id_str

    print(f"DEBUG: Creating collection '{name}' for user {user_id_obj} (from string {user_id_str}) with {len(emails_payload)} emails")

    if not name:
        raise HTTPException(status_code=400, detail="Collection name is required")
    if not isinstance(emails_payload, list) or len(emails_payload) == 0:
        raise HTTPException(status_code=400, detail="At least one email is required")

    validated_emails: List[CollectionEmail] = [CollectionEmail(**email) for email in emails_payload]
    print(f"DEBUG: Validated {len(validated_emails)} emails")

    collection = CollectionModel(
        user_id=user_id_obj,  # Use ObjectId, not string
        name=name,
        emails=validated_emails,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    result = await db.get_db().collections.insert_one(collection.model_dump(by_alias=True))
    dumped = collection.model_dump(by_alias=True)
    print(f"DEBUG: Dumped model keys: {list(dumped.keys())}")
    print(f"DEBUG: user_id in dumped: {dumped.get('user_id')} (type: {type(dumped.get('user_id')).__name__})")
    print(f"DEBUG: Inserted collection with id {result.inserted_id}")
    created = await db.get_db().collections.find_one({"_id": result.inserted_id})
    # Convert ObjectId to string for serialization
    if created and "_id" in created:
        created["_id"] = str(created["_id"])
    if created and "user_id" in created:
        created["user_id"] = str(created["user_id"])
    print(f"DEBUG: Returning collection: {created.get('name') if created else 'None'}")
    return created


@router.delete("/{collection_id}")
async def delete_collection(collection_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    user_id = ObjectId(current_user["_id"]) if isinstance(current_user["_id"], str) else current_user["_id"]
    try:
        result = await db.get_db().collections.delete_one({"_id": ObjectId(collection_id), "user_id": user_id})
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid collection id")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    print(f"DEBUG: Deleted collection {collection_id} for user {user_id}")
    return {"message": "Collection deleted", "id": collection_id}
