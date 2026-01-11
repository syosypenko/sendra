from typing import List, Dict
from src.database import db

class AnalyticsService:
    @staticmethod
    async def get_emails_by_position(user_id: str) -> List[Dict]:
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$position", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        result = await db.get_db().emails.aggregate(pipeline).to_list(None)
        return result or []
    
    @staticmethod
    async def get_emails_by_company(user_id: str) -> List[Dict]:
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$company", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        result = await db.get_db().emails.aggregate(pipeline).to_list(None)
        return result or []
    
    @staticmethod
    async def get_emails_by_application_status(user_id: str) -> List[Dict]:
        """New: Group by application status (applied, interview, offer, rejected)"""
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$application_status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        result = await db.get_db().emails.aggregate(pipeline).to_list(None)
        return result or []
    
    @staticmethod
    async def get_emails_by_job_type(user_id: str) -> List[Dict]:
        """New: Group by job type (full-time, contract, internship)"""
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$job_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        result = await db.get_db().emails.aggregate(pipeline).to_list(None)
        return result or []
    
    @staticmethod
    async def get_emails_by_language(user_id: str) -> List[Dict]:
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$language", "count": {"$sum": 1}}}
        ]
        result = await db.get_db().emails.aggregate(pipeline).to_list(None)
        return result or []
    
    @staticmethod
    async def get_emails_by_experience_level(user_id: str) -> List[Dict]:
        """New: Group by experience level required"""
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$experience_level", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        result = await db.get_db().emails.aggregate(pipeline).to_list(None)
        return result or []
    
    @staticmethod
    async def get_application_funnel(user_id: str) -> Dict:
        """New: Get application pipeline (applied -> interview -> offer -> etc)"""
        statuses = ["applied", "interview", "offer", "rejected"]
        funnel = {}
        
        for status in statuses:
            count = await db.get_db().emails.count_documents({
                "user_id": user_id,
                "application_status": status
            })
            funnel[status] = count
        
        return funnel
    
    @staticmethod
    async def get_top_companies(user_id: str, limit: int = 10) -> List[Dict]:
        """Top companies by number of opportunities"""
        pipeline = [
            {"$match": {"user_id": user_id, "company": {"$ne": None}}},
            {"$group": {"_id": "$company", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        result = await db.get_db().emails.aggregate(pipeline).to_list(None)
        return result or []
    
    @staticmethod
    async def get_top_positions(user_id: str, limit: int = 10) -> List[Dict]:
        """Top job positions by count"""
        pipeline = [
            {"$match": {"user_id": user_id, "position": {"$ne": None}}},
            {"$group": {"_id": "$position", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        result = await db.get_db().emails.aggregate(pipeline).to_list(None)
        return result or []
    
    @staticmethod
    async def get_email_stats(user_id: str) -> Dict:
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": 1},
                    "read": {"$sum": {"$cond": ["$read", 1, 0]}},
                    "unread": {"$sum": {"$cond": ["$read", 0, 1]}},
                    "starred": {"$sum": {"$cond": ["$starred", 1, 0]}}
                }
            }
        ]
        result = await db.get_db().emails.aggregate(pipeline).to_list(None)
        return result[0] if result else {}
    
    @staticmethod
    async def get_dashboard_summary(user_id: str) -> Dict:
        """Get comprehensive dashboard summary"""
        return {
            "stats": await AnalyticsService.get_email_stats(user_id),
            "by_status": await AnalyticsService.get_emails_by_application_status(user_id),
            "by_type": await AnalyticsService.get_emails_by_job_type(user_id),
            "by_experience": await AnalyticsService.get_emails_by_experience_level(user_id),
            "by_company": await AnalyticsService.get_top_companies(user_id),
            "funnel": await AnalyticsService.get_application_funnel(user_id),
            "top_companies": await AnalyticsService.get_top_companies(user_id, 5),
            "top_positions": await AnalyticsService.get_top_positions(user_id, 5)
        }
