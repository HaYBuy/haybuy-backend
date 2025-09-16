from fastapi import FastAPI

from .rounters import router as api_router
app = FastAPI()
    
app.include_router(api_router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}
