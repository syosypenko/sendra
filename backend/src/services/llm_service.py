from src.config import settings
from typing import Dict, List, Optional
import json

class LLMService:
    """Service to interact with LLM providers (OpenAI or Anthropic)"""
    
    @staticmethod
    async def process_natural_language_query(prompt: str) -> Dict:
        """Convert natural language prompt to Gmail search query and extract intent"""
        
        if settings.llm_provider == "openai":
            return await LLMService._process_with_openai(prompt)
        elif settings.llm_provider == "anthropic":
            return await LLMService._process_with_anthropic(prompt)
        elif settings.llm_provider == "gemini":
            return await LLMService._process_with_gemini(prompt)
        else:
            return await LLMService._process_locally(prompt)
    
    @staticmethod
    async def _process_with_openai(prompt: str) -> Dict:
        """Process prompt with OpenAI GPT"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            
            system_message = """You are an email analysis assistant. Given a natural language prompt, extract:
1. query_intent: The user's intention (e.g., "find_job_offers", "find_rejections", "find_interviews")
2. gmail_query: The Gmail search query to use (e.g., "subject:(job offer) OR subject:(offer)")
3. categories: What to categorize emails by (e.g., ["company", "job_type", "salary"])

Respond in JSON format:
{
    "query_intent": "string",
    "gmail_query": "string",
    "categories": ["string"],
    "summary": "Brief explanation of the query"
}"""
            
            response = client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"OpenAI Error: {e}")
            return await LLMService._process_locally(prompt)
    
    @staticmethod
    async def _process_with_anthropic(prompt: str) -> Dict:
        """Process prompt with Anthropic Claude"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            
            system_message = """You are an email analysis assistant. Given a natural language prompt, extract:
1. query_intent: The user's intention
2. gmail_query: The Gmail search query to use
3. categories: What to categorize emails by

Respond in JSON format."""
            
            response = client.messages.create(
                model=settings.llm_model,
                max_tokens=500,
                system=system_message,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = json.loads(response.content[0].text)
            return result
        except Exception as e:
            print(f"Anthropic Error: {e}")
            return await LLMService._process_locally(prompt)
    
    @staticmethod
    async def _process_with_gemini(prompt: str) -> Dict:
        """Process prompt with Google Gemini"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel(settings.llm_model)
            
            system_message = """You are an email analysis assistant. Given a natural language prompt, extract:
1. query_intent: The user's intention (e.g., "find_job_offers", "find_rejections", "find_interviews")
2. gmail_query: The Gmail search query to use (e.g., "subject:(job offer) OR subject:(offer)")
3. categories: What to categorize emails by (e.g., ["company", "job_type", "salary"])

Respond ONLY with valid JSON format:
{
    "query_intent": "string",
    "gmail_query": "string",
    "categories": ["string"],
    "summary": "Brief explanation of the query"
}"""
            
            full_prompt = f"{system_message}\n\nUser prompt: {prompt}"
            response = model.generate_content(full_prompt)
            
            # Extract JSON from response
            text = response.text.strip()
            # Remove markdown code blocks if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            result = json.loads(text.strip())
            return result
        except Exception as e:
            print(f"Gemini Error: {e}")
            return await LLMService._process_locally(prompt)
    
    @staticmethod
    async def _process_locally(prompt: str) -> Dict:
        """Fallback: Simple keyword-based processing"""
        prompt_lower = prompt.lower()
        
        # Map keywords to intents
        intent_map = {
            "reject": "find_rejections",
            "offer": "find_job_offers",
            "interview": "find_interviews",
            "application": "find_applications",
            "applied": "find_applications",
        }
        
        query_intent = "search_emails"
        for keyword, intent in intent_map.items():
            if keyword in prompt_lower:
                query_intent = intent
                break
        
        gmail_query = prompt
        categories = ["company", "position", "job_type"]
        
        return {
            "query_intent": query_intent,
            "gmail_query": gmail_query,
            "categories": categories,
            "summary": f"Searching for: {prompt}"
        }
    
    @staticmethod
    async def extract_email_metadata(subject: str, body: str, from_email: str) -> Dict:
        """Use LLM to extract rich metadata from email"""
        
        if not settings.openai_api_key and not settings.anthropic_api_key and not settings.gemini_api_key:
            return LLMService._extract_metadata_locally(subject, body)
        
        # Try Gemini first if configured
        if settings.gemini_api_key:
            try:
                import google.generativeai as genai
                
                genai.configure(api_key=settings.gemini_api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                extraction_prompt = f"""Extract email metadata from this email:
Subject: {subject}
Body: {body[:1000]}

Extract:
1. job_type: full-time/part-time/contract/internship/other
2. application_status: applied/interview/offer/rejected/other
3. salary: salary range if mentioned, or null
4. experience_level: junior/mid/senior/executive/other
5. job_title: the job title
6. key_skills: required skills mentioned

Respond ONLY with valid JSON format."""
                
                response = model.generate_content(extraction_prompt)
                text = response.text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                
                result = json.loads(text.strip())
                return result
            except Exception as e:
                print(f"Gemini metadata extraction error: {e}")
        
        # Fallback to OpenAI if available
        if settings.openai_api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.openai_api_key)
                
                extraction_prompt = f"""Extract email metadata from this email:
Subject: {subject}
Body: {body[:1000]}

Extract:
1. job_type: full-time/part-time/contract/internship/other
2. application_status: applied/interview/offer/rejected/other
3. salary: salary range if mentioned, or null
4. experience_level: junior/mid/senior/executive/other
5. job_title: the job title
6. key_skills: required skills mentioned

Respond in JSON format."""
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": extraction_prompt}],
                    temperature=0.3,
                    max_tokens=300
                )
                
                result = json.loads(response.choices[0].message.content)
                return result
            except Exception as e:
                print(f"OpenAI metadata extraction error: {e}")
        
        return LLMService._extract_metadata_locally(subject, body)
    
    @staticmethod
    def _extract_metadata_locally(subject: str, body: str) -> Dict:
        """Fallback metadata extraction using keywords"""
        text = f"{subject} {body}".lower()
        
        job_type = "other"
        if "full-time" in text or "full time" in text:
            job_type = "full-time"
        elif "part-time" in text or "part time" in text:
            job_type = "part-time"
        elif "contract" in text:
            job_type = "contract"
        elif "internship" in text:
            job_type = "internship"
        
        status = "other"
        if "reject" in text or "rejected" in text:
            status = "rejected"
        elif "interview" in text:
            status = "interview"
        elif "offer" in text and "job offer" in text:
            status = "offer"
        elif "applied" in text or "application" in text:
            status = "applied"
        
        return {
            "job_type": job_type,
            "application_status": status,
            "salary": None,
            "experience_level": "other",
            "job_title": None,
            "key_skills": []
        }
