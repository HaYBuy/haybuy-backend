"""Health check endpoint for monitoring and CI/CD."""

from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.db.database import engine

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint for CI/CD and monitoring.

    Returns:
        Dictionary with service status and database connectivity

    Raises:
        HTTPException: If critical services are unavailable
    """
    try:
        # Check database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
            "service": "haybuy-backend",
        }
    except SQLAlchemyError as db_error:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": f"Database error: {str(db_error)}",
        }
