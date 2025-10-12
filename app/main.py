from fastapi import FastAPI
from contextlib import asynccontextmanager
from .db.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from .routers import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(api_router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}

origins = ["*"]  # dev เท่านั้น, production ค่อยจำกัดให้แคบลง

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
