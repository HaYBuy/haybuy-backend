from fastapi import APIRouter
from sqlalchemy import text
from database import engine

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint for CI/CD and monitoring"""
    try:
        # Check database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
            "service": "haybuy-backend",
        }
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
