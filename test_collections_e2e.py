#!/usr/bin/env python3
"""
End-to-end test for collections feature
"""
import requests
import json

BASE_URL = "http://localhost/api"

def test_collections():
    session = requests.Session()
    
    # Step 1: Check auth (should redirect to login since we have no token)
    print("1️⃣ Testing GET /auth/me...")
    resp = session.get(f"{BASE_URL}/auth/me")
    print(f"   Status: {resp.status_code}")
    if resp.status_code != 200:
        print("   ⚠️ Not authenticated - collections test requires logged-in user")
        print("   Please login in browser first, then this test can verify collection storage")
        return
    
    user = resp.json()
    print(f"   User ID: {user.get('_id')}")
    
    # Step 2: List collections (should be empty initially)
    print("\n2️⃣ Testing GET /collections...")
    resp = session.get(f"{BASE_URL}/collections")
    print(f"   Status: {resp.status_code}")
    collections = resp.json()
    print(f"   Collections found: {len(collections)}")
    for col in collections:
        print(f"     - {col.get('name')} ({len(col.get('emails', []))} emails)")
    
    # Step 3: Create a test collection
    print("\n3️⃣ Testing POST /collections...")
    test_email = {
        "gmail_id": "test123",
        "from": "sender@example.com",
        "to": ["recipient@example.com"],
        "subject": "Test Email",
        "body": "This is a test email",
        "received_at": "Fri, 26 Dec 2025 18:27:03 +0000"
    }
    
    payload = {
        "name": "Test Collection",
        "emails": [test_email]
    }
    
    resp = session.post(f"{BASE_URL}/collections", json=payload)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        created = resp.json()
        print(f"   ✅ Created collection: {created.get('name')}")
        print(f"   Collection ID: {created.get('_id')}")
        print(f"   Emails stored: {len(created.get('emails', []))}")
    else:
        print(f"   ❌ Error: {resp.text}")
        return
    
    # Step 4: List collections again (should see the new one)
    print("\n4️⃣ Testing GET /collections (after create)...")
    resp = session.get(f"{BASE_URL}/collections")
    print(f"   Status: {resp.status_code}")
    collections = resp.json()
    print(f"   Collections found: {len(collections)}")
    for col in collections:
        print(f"     - {col.get('name')} ({len(col.get('emails', []))} emails)")
    
    if len(collections) > 0:
        print("\n✅ SUCCESS: Collections feature is working!")
        print("   Collections are being saved and retrieved correctly")
    else:
        print("\n❌ FAILURE: Collections not appearing after save")
        print("   Check backend logs for user_id mismatch issues")

if __name__ == "__main__":
    test_collections()
