from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: int
    username: str
    password_hash: str
    full_name: str
    email: str
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    last_login: datetime | None = None