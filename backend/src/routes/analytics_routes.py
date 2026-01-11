from fastapi import APIRouter, Depends, Query
from typing import Optional
from src.dependencies import get_current_user
from src.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard-summary")
async def dashboard_summary(current_user: dict = Depends(get_current_user)):
    user_id = current_user["_id"]
    return await AnalyticsService.get_dashboard_summary(user_id)


@router.get("/by-status")
async def by_status(current_user: dict = Depends(get_current_user)):
    user_id = current_user["_id"]
    return await AnalyticsService.get_emails_by_application_status(user_id)


@router.get("/by-job-type")
async def by_job_type(current_user: dict = Depends(get_current_user)):
    user_id = current_user["_id"]
    return await AnalyticsService.get_emails_by_job_type(user_id)


@router.get("/by-experience")
async def by_experience(current_user: dict = Depends(get_current_user)):
    user_id = current_user["_id"]
    return await AnalyticsService.get_emails_by_experience_level(user_id)


@router.get("/application-funnel")
async def application_funnel(current_user: dict = Depends(get_current_user)):
    user_id = current_user["_id"]
    return await AnalyticsService.get_application_funnel(user_id)


@router.get("/top-companies")
async def top_companies(
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["_id"]
    return await AnalyticsService.get_top_companies(user_id, limit)


@router.get("/top-positions")
async def top_positions(
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["_id"]
    return await AnalyticsService.get_top_positions(user_id, limit)


@router.get("/stats")
async def stats(current_user: dict = Depends(get_current_user)):
    user_id = current_user["_id"]
    return await AnalyticsService.get_email_stats(user_id)
