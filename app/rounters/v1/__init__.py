from fastapi import APIRouter

from . import (
    hello,
    user,
)

router = APIRouter(prefix="/v1")
router.include_router(hello.rounter)
router.include_router(user.rounter)