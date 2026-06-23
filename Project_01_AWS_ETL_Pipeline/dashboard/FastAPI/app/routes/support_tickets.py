# app/routes/support_tickets.py
from fastapi import APIRouter, HTTPException
from app.redshift_client import RedshiftDataClient
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tickets", tags=["support-tickets"])

@router.get("/dashboard")
async def get_ticket_dashboard() -> Dict[str, Any]:
    """Get complete ticket dashboard data from Redshift"""
    client = RedshiftDataClient()
    try:
        return client.get_ticket_dashboard()
    except Exception as e:
        logger.error(f"Error fetching ticket dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Redshift read error: {str(e)}")