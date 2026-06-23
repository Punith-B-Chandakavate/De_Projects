# app/routes/support_logs.py
from fastapi import APIRouter, HTTPException, Query
from app.redshift_client import RedshiftDataClient
from typing import Dict, Any

router = APIRouter(prefix="/api/logs", tags=["support-logs"])

@router.get("/dashboard")
async def get_log_dashboard(
    days: int = Query(30, ge=1, le=90, description="Number of days to look back")
) -> Dict[str, Any]:
    """Get complete log dashboard data from Redshift"""
    client = RedshiftDataClient()
    try:
        return client.get_log_dashboard(days=days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redshift read error: {str(e)}")