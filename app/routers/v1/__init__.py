from fastapi import APIRouter

from . import (
    hello,
    user_rounter,
    item_rounter,
    group_item_rounter,
    group_rounter,
    group_member_rounter,
    category_rounter,
    wish_item_rounter,
    auth_rounter,
    user_profile_rounter,
    transaction_rounter,
    chat_router,
)

router = APIRouter(prefix="/v1")
router.include_router(auth_rounter.rounter)
router.include_router(hello.rounter)
router.include_router(user_rounter.rounter)
router.include_router(item_rounter.rounter)
router.include_router(group_item_rounter.rounter)
router.include_router(group_rounter.rounter)
router.include_router(group_member_rounter.rounter)
router.include_router(category_rounter.rounter)
router.include_router(wish_item_rounter.rounter)
router.include_router(user_profile_rounter.rounter)
router.include_router(transaction_rounter.rounter)
router.include_router(chat_router.router)