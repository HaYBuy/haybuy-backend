from fastapi import APIRouter
from datetime import datetime
import pytz

router = APIRouter(prefix="/hello", tags=["hello"])


@router.get("/")
async def say_hello():
    thai_tz = pytz.timezone("Asia/Bangkok")
    now_thai = datetime.now(thai_tz)
    return {"message": "Hello, World!", "timestamp": now_thai.isoformat()}
