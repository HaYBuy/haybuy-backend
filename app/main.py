from fastapi import FastAPI
from contextlib import asynccontextmanager
from .db.database import engine, Base

from .routers import router as api_router

from .db.database import engine, Base
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine) 
    yield

app = FastAPI(lifespan=lifespan)
    
app.include_router(api_router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}
