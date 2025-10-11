from fastapi import APIRouter

from . import (
    hello,
    user_router,
    item_router,
    group_item_router,
    group_router,
    group_member_router,
    category_router,
    wish_item_router,
    auth_router,
    user_profile_router,
    transaction_router,
    chat_router,
    cart_router,
)

router = APIRouter(prefix="/v1")
router.include_router(auth_router.router)
router.include_router(hello.router)
router.include_router(user_router.router)
router.include_router(item_router.router)
router.include_router(group_item_router.router)
router.include_router(group_router.router)
router.include_router(group_member_router.router)
router.include_router(category_router.router)
router.include_router(wish_item_router.router)
router.include_router(user_profile_router.router)
router.include_router(transaction_router.router)
router.include_router(chat_router.router)
router.include_router(cart_router.router)
