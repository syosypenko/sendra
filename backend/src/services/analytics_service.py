from typing import List, Dict, Optional, Tuple
import re
from datetime import datetime, timedelta
from src.database import db

class AnalyticsService:
    @staticmethod
    def _derive_company(from_str: Optional[str]) -> Optional[str]:
        """Best-effort extraction of a company name from an email 'from' field.
        - Prefer domain from email address (e.g., user@acme.com -> acme)
        - Fallback to words in the display name portion
        """
        if not from_str:
            return None

        s = from_str.strip()
        # Try to extract domain from email address
        m = re.search(r"[\w\.-]+@([\w\.-]+)", s)
        if m:
            domain = m.group(1).lower()
            # Remove common subdomains
            parts = [p for p in re.split(r"[\.-]", domain) if p]
            common = {"mail", "email", "info", "support", "noreply", "no", "reply", "contact"}
            core = next((p for p in parts if p not in common), None)
            if core and len(core) > 1:
                return core.capitalize()

        # Fallback: find capitalized word sequences in the string (e.g., "Acme Inc")
        name_match = re.findall(r"([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)", s)
        if name_match:
            # Choose the longest sequence
            return max(name_match, key=len)

        return None

    @staticmethod
    async def _get_collections_emails(user_id: str) -> List[Dict]:
        """Fetch all emails nested inside collections for a user."""
        # Convert string user_id to ObjectId if needed
        try:
            from bson import ObjectId
            user_obj_id = ObjectId(user_id)
        except Exception:
            user_obj_id = user_id
        cursor = db.get_db().collections.find({"user_id": user_obj_id}, {"emails": 1})
        collections = await cursor.to_list(None)
        emails: List[Dict] = []
        for col in collections:
            for e in col.get("emails", []) or []:
                emails.append(e)
        return emails

    @staticmethod
    async def get_collections_email_stats(user_id: str) -> Dict:
        emails = await AnalyticsService._get_collections_emails(user_id)
        total = len(emails)
        # We don't track read/starred in collections; return minimal stats
        return {"total": total, "read": 0, "unread": total, "starred": 0}

    @staticmethod
    async def get_collections_top_companies(user_id: str, limit: int = 10) -> List[Dict]:
        emails = await AnalyticsService._get_collections_emails(user_id)
        counts: Dict[str, int] = {}
        for e in emails:
            company = AnalyticsService._derive_company(e.get("from"))
            if not company:
                continue
            counts[company] = counts.get(company, 0) + 1
        # Convert to list and sort
        items = [{"_id": name, "count": cnt} for name, cnt in counts.items()]
        items.sort(key=lambda x: x["count"], reverse=True)
        return items[:limit]

    @staticmethod
    async def get_collections_company_count(user_id: str) -> int:
        emails = await AnalyticsService._get_collections_emails(user_id)
        companies = set()
        for e in emails:
            c = AnalyticsService._derive_company(e.get("from"))
            if c:
                companies.add(c)
        return len(companies)
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
    async def get_company_count(user_id: str) -> int:
        """Count distinct companies for the user"""
        pipeline = [
            {"$match": {"user_id": user_id, "company": {"$ne": None}}},
            {"$group": {"_id": "$company"}},
            {"$count": "count"}
        ]
        result = await db.get_db().emails.aggregate(pipeline).to_list(None)
        return (result[0]["count"] if result else 0)

    @staticmethod
    def _infer_status(subject: str, body: str) -> Optional[str]:
        """Infer application status from email subject/body keywords."""
        text = (subject or "") + " " + (body or "")
        text_lower = text.lower()

        # Check for offer/congratulations
        if any(kw in text_lower for kw in ["offer", "congratulations", "excited", "we're pleased", "accepted", "approved"]):
            return "offer"
        # Check for rejection
        if any(kw in text_lower for kw in ["reject", "unfortunately", "not move", "not selected", "decline", "unsuccessful", "regret"]):
            return "rejected"
        # Check for interview
        if any(kw in text_lower for kw in ["interview", "call", "schedule", "meeting", "discuss", "next step"]):
            return "interview"
        # Default to applied
        return "applied"

    @staticmethod
    async def get_applications_over_time(user_id: str) -> List[Dict]:
        """Get application counts grouped by date and status from collections.
        Returns list of {date, applied, interview, offer, rejected} for charting.
        """
        emails = await AnalyticsService._get_collections_emails(user_id)
        print(f"DEBUG: get_applications_over_time - found {len(emails)} emails")
        
        # Group by date and status
        by_date_status: Dict[str, Dict[str, int]] = {}
        
        for i, e in enumerate(emails):
            # Parse received_at (RFC 2822, ISO string, or datetime)
            received_at_str = e.get("received_at")
            print(f"DEBUG: Email {i} received_at: {received_at_str}")
            
            if not received_at_str:
                continue
            
            date_key = None
            try:
                # Try to extract date using multiple patterns
                if isinstance(received_at_str, str):
                    # RFC 2822: "Fri, 7 Nov 2025 16:49:07 +0000"
                    # ISO: "2025-11-07T16:49:07Z"
                    
                    # Try extracting YYYY-MM-DD directly
                    iso_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', received_at_str)
                    if iso_match:
                        date_key = iso_match.group(0)
                        print(f"DEBUG: Matched ISO pattern: {date_key}")
                    else:
                        # Try RFC 2822 pattern: "Fri, 7 Nov 2025" -> extract day, month, year
                        rfc_match = re.search(r'(\d+)\s+(\w+)\s+(\d{4})', received_at_str)
                        if rfc_match:
                            day, month_str, year = rfc_match.groups()
                            months = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                                     "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
                            month = months.get(month_str, 1)
                            date_key = f"{year}-{month:02d}-{int(day):02d}"
                            print(f"DEBUG: Matched RFC pattern: {date_key} (day={day}, month={month_str}, year={year})")
                else:
                    # If it's a datetime object
                    date_key = received_at_str.strftime("%Y-%m-%d")
            except Exception as ex:
                print(f"DEBUG: Exception parsing date '{received_at_str}': {ex}")
                continue
            
            if not date_key:
                print(f"DEBUG: No date_key extracted from '{received_at_str}'")
                continue
            
            # Infer status from subject + body
            status = AnalyticsService._infer_status(
                e.get("subject", ""),
                e.get("body", "")
            )
            print(f"DEBUG: Inferred status: {status}")
            
            if date_key not in by_date_status:
                by_date_status[date_key] = {"applied": 0, "interview": 0, "offer": 0, "rejected": 0}
            by_date_status[date_key][status] += 1
        
        # Convert to list sorted by date
        result = []
        for date_key in sorted(by_date_status.keys()):
            result.append({
                "date": date_key,
                **by_date_status[date_key]
            })
        
        print(f"DEBUG: applications_over_time result: {result}")
        return result
    
    @staticmethod
    async def get_predictive_insights(user_id: str) -> Dict:
        """Analyze application trends and predict offer likelihood."""
        emails = await AnalyticsService._get_collections_emails(user_id)
        
        if not emails:
            return {
                "offer_probability_30d": 0,
                "expected_days_to_offer": None,
                "momentum": "insufficient_data",
                "total_applications": 0,
                "recent_activity": 0,
                "conversion_rate": 0
            }
        
        # Parse and categorize emails with dates
        categorized = {"applied": [], "interview": [], "offer": [], "rejected": []}
        
        for e in emails:
            received_at_str = e.get("received_at")
            if not received_at_str:
                continue
            
            # Parse date
            date_parsed = None
            try:
                if isinstance(received_at_str, str):
                    iso_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', received_at_str)
                    if iso_match:
                        date_parsed = datetime.strptime(iso_match.group(0), "%Y-%m-%d")
                    else:
                        rfc_match = re.search(r'(\d+)\s+(\w+)\s+(\d{4})', received_at_str)
                        if rfc_match:
                            day, month_str, year = rfc_match.groups()
                            months = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                                     "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
                            month = months.get(month_str, 1)
                            date_parsed = datetime(int(year), month, int(day))
            except Exception:
                continue
            
            if not date_parsed:
                continue
            
            status = AnalyticsService._infer_status(e.get("subject", ""), e.get("body", ""))
            categorized[status].append(date_parsed)
        
        total = sum(len(v) for v in categorized.values())
        offers = len(categorized["offer"])
        
        # Calculate conversion rate
        conversion_rate = (offers / total * 100) if total > 0 else 0
        
        # Recent activity (last 30 days)
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        recent_count = sum(1 for dates in categorized.values() for d in dates if d >= thirty_days_ago)
        
        # Calculate average days to offer
        avg_days_to_offer = None
        if categorized["applied"] and categorized["offer"]:
            earliest_applied = min(categorized["applied"])
            earliest_offer = min(categorized["offer"])
            if earliest_offer > earliest_applied:
                avg_days_to_offer = (earliest_offer - earliest_applied).days
        
        # Momentum: compare last 15 days vs previous 15 days
        fifteen_days_ago = now - timedelta(days=15)
        last_15_days = sum(1 for dates in categorized.values() for d in dates if d >= fifteen_days_ago)
        prev_15_days = sum(1 for dates in categorized.values() for d in dates if thirty_days_ago <= d < fifteen_days_ago)
        
        if prev_15_days == 0:
            momentum = "neutral"
        elif last_15_days > prev_15_days:
            momentum = "increasing"
        else:
            momentum = "decreasing"
        
        # Predict offer probability
        if recent_count > 0:
            activity_multiplier = min(recent_count / 5, 2.0)
            offer_prob = min(conversion_rate * activity_multiplier, 95)
        else:
            offer_prob = conversion_rate * 0.5
        
        return {
            "offer_probability_30d": round(offer_prob, 1),
            "expected_days_to_offer": avg_days_to_offer,
            "momentum": momentum,
            "total_applications": total,
            "recent_activity": recent_count,
            "conversion_rate": round(conversion_rate, 1)
        }

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
        stats = await AnalyticsService.get_email_stats(user_id)
        # If no emails in primary collection, fallback to collections-based metrics
        if not stats or stats.get("total", 0) == 0:
            stats = await AnalyticsService.get_collections_email_stats(user_id)
            company_count = await AnalyticsService.get_collections_company_count(user_id)
            top_companies = await AnalyticsService.get_collections_top_companies(user_id, 5)
        else:
            company_count = await AnalyticsService.get_company_count(user_id)
            top_companies = await AnalyticsService.get_top_companies(user_id, 5)

        # The advanced breakdowns rely on fields that exist only in the emails collection
        # Keep them, but they may be empty when falling back.
        return {
            "stats": stats,
            "company_count": company_count,
            "by_status": await AnalyticsService.get_emails_by_application_status(user_id),
            "by_type": await AnalyticsService.get_emails_by_job_type(user_id),
            "by_experience": await AnalyticsService.get_emails_by_experience_level(user_id),
            "by_company": await AnalyticsService.get_top_companies(user_id),
            "funnel": await AnalyticsService.get_application_funnel(user_id),
            "top_companies": top_companies,
            "applications_over_time": await AnalyticsService.get_applications_over_time(user_id),
            "predictive_insights": await AnalyticsService.get_predictive_insights(user_id),
            "top_positions": await AnalyticsService.get_top_positions(user_id, 5)
        }
