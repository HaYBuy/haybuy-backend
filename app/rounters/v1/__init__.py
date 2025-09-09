from fastapi import APIRouter

from . import (
    hello,
)

router = APIRouter(prefix="/v1")
router.include_router(hello.rounter)