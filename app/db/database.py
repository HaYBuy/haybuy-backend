from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from dotenv import load_dotenv

# โหลด .env เฉพาะตอนรันนอก Docker (กรณี dev ในเครื่อง)
if os.getenv("RUNNING_IN_DOCKER") != "true":
    load_dotenv()

# ดึงค่า DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")

# สร้าง engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # ช่วยตรวจสอบ connection ก่อนใช้
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# Dependency สำหรับ FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
