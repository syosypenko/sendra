import asyncio
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import List, Dict
import base64
from email.mime.text import MIMEText
import re
from html import unescape


def strip_html(html_text: str) -> str:
    """Remove HTML tags and decode HTML entities"""
    if not html_text:
        return ""
    # Remove script and style tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities
    text = unescape(text)
    # Clean up whitespace and normalize
    text = re.sub(r'\s+', ' ', text).strip()
    return text


class GmailService:
    def __init__(self, access_token: str, refresh_token: str):
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=None,
            client_secret=None
        )
        self.service = build('gmail', 'v1', credentials=creds)
    
    async def fetch_emails(self, query: str = '', max_results: int = 10) -> List[Dict]:
        try:
            results = await asyncio.to_thread(
                lambda: self.service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=max_results
                ).execute()
            )
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                email_data = await self.get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
        except Exception as e:
            print(f"Error fetching emails: {e}")
            raise
    
    async def get_email_details(self, message_id: str) -> Dict:
        try:
            message = await asyncio.to_thread(
                lambda: self.service.users().messages().get(
                    userId='me',
                    id=message_id,
                    format='full'
                ).execute()
            )
            
            headers = message['payload']['headers']
            header_dict = {h['name']: h['value'] for h in headers}
            
            from_email = header_dict.get('From', '')
            to_email = header_dict.get('To', '')
            subject = header_dict.get('Subject', '').strip()
            date = header_dict.get('Date', '')
            
            # Extract body - prefer plain text, fallback to HTML converted to text
            body = ''
            
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                
                # If no plain text, try HTML
                if not body:
                    for part in message['payload']['parts']:
                        if part['mimeType'] == 'text/html' and 'data' in part['body']:
                            html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            body = strip_html(html)
                            break
            elif 'body' in message['payload'] and 'data' in message['payload']['body']:
                body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
            
            # Clean up body - limit to first 5000 chars
            body = body.strip()[:5000] if body else ''
            
            return {
                'gmail_id': message_id,
                'from': from_email.strip(),
                'to': [to_email.strip()] if to_email else [],
                'subject': subject,
                'body': body,
                'received_at': date
            }
        except Exception as e:
            print(f"Error getting email details: {e}")
            return None
    
    async def search_emails(self, query: str) -> List[Dict]:
        return await self.fetch_emails(query, 50)
