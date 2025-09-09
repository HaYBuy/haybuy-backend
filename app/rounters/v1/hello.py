from fastapi import APIRouter

rounter = APIRouter(prefix="/hello", tags=["hello"])

@rounter.get("/")
async def say_hello():
    return {"message": "Hello, World!"}