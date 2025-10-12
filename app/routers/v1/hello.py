from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter

router = APIRouter(prefix="/hello", tags=["hello"])


@router.get("/")
async def say_hello():
    now_thai = datetime.now(ZoneInfo("Asia/Bangkok"))
    return {"message": "Hello, World!", "timestamp": now_thai.isoformat()}
