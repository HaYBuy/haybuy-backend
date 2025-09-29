from fastapi import APIRouter

from . import (
    hello,
    user_rounter,
    item_rounter,
)

router = APIRouter(prefix="/v1")
router.include_router(hello.rounter)
router.include_router(user_rounter.rounter)
router.include_router(item_rounter.rounter)