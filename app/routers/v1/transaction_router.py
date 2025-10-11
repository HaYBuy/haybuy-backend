from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.models.Users.User import User
from app.schemas.item_schema import ItemStatus
from ...db.database import get_db
from ...db.models.items.item import Item
from app.schemas.transaction_schema import (
    TransactionResponse,
    TransactionAccepted,
    TransactionAdd,
    TransactionStatus,
    TransactionRole,
    TransactionCreate,
)
from ...core.security import get_current_user
from app.db.models.Transactions.transaction_model import Transaction

router = APIRouter(prefix="/transaction", tags=["transaction"])


@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    data: TransactionAdd,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    existing_item = db.query(Item).filter(Item.id == data.item_id).first()
    if not existing_item:
        raise HTTPException(status_code=404, detail=" Item not found")

    # seller_id comes from item owner
    seller_id = existing_item.owner_id

    if existing_item.owner_id == current_user["id"]:
        raise HTTPException(
            status_code=403, detail="You cannot perform this action on your own item"
        )

    if (
        existing_item.quantity < data.amount
        or existing_item.status != ItemStatus.AVAILABLE
    ):
        raise HTTPException(status_code=400, detail="Item is not available")

    existing_seller = db.query(User).filter(User.id == seller_id).first()
    if not existing_seller:
        raise HTTPException(status_code=404, detail="seller not found")

    new_transaction = Transaction(
        item_id=data.item_id,
        seller_id=seller_id,
        buyer_id=current_user["id"],
        status=TransactionStatus.PENDING.value,
        agreed_price=existing_item.price * data.amount,
        amount=data.amount,
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


@router.patch("/buyer/acception/{transaction_id}", response_model=TransactionResponse)
async def buyer_accept(
    transaction_id: int,
    accepted: TransactionAccepted,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return update_transaction_accept(
        db=db,
        transaction_id=transaction_id,
        current_user=current_user,
        role=TransactionRole.buyer.value,
        accepter=accepted.accepter,
        accept_at=accepted.accept_at,
    )


@router.patch("/seller/acception/{transaction_id}", response_model=TransactionResponse)
async def seller_accept(
    transaction_id: int,
    accepted: TransactionAccepted,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return update_transaction_accept(
        db=db,
        transaction_id=transaction_id,
        current_user=current_user,
        role=TransactionRole.seller.value,
        accepter=accepted.accepter,
        accept_at=accepted.accept_at,
    )


@router.patch(
    "/transaction/cancel/{transaction_id}", response_model=TransactionResponse
)
def cancel_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    user_id = current_user["id"]

    # ตรวจสอบสิทธิ์
    if transaction.buyer_id != user_id and transaction.seller_id != user_id:
        raise HTTPException(
            status_code=403, detail="You are not part of this transaction"
        )

    if (
        transaction.status == TransactionStatus.ACCEPTED
        and transaction.buyer_id == user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="This transaction is already accepted, buyer cannot cancel",
        )

    # # ตรวจสอบว่าทั้งสองฝ่าย accept หรือยัง
    # if transaction.buyer_accept and transaction.seller_accept:
    #     raise HTTPException(status_code=400, detail="Transaction already accepted by both parties, cannot cancel")

    if transaction.status == TransactionStatus.ACCEPTED:
        item_db = db.query(Item).filter(Item.id == transaction.item_id).first()
        if item_db:
            item_db.quantity += transaction.amount

    # ยกเลิก transaction
    transaction.status = TransactionStatus.CANCELLED
    transaction.cancelled_at = datetime.now(
        ZoneInfo("Asia/Bangkok")
    )  # ถ้ามี column สำหรับเวลา cancel

    db.commit()
    db.refresh(transaction)
    db.refresh(item_db)
    return transaction


@router.patch("/paid/{transaction_id}")
async def paid_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    user_id = current_user["id"]

    if transaction.buyer_id != user_id:
        raise HTTPException(
            status_code=403, detail="You are not buyer of this transaction"
        )

    transaction.status = TransactionStatus.PAID
    transaction.paid_at = datetime.now(ZoneInfo("Asia/Bangkok"))

    db.commit()
    db.refresh(transaction)

    return transaction


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def change_transaction_detail(
    transaction_id: int,
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    existing_transaction = (
        db.query(Transaction).filter(Transaction.id == transaction_id).first()
    )

    if not existing_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if (
        existing_transaction.seller_id != current_user["id"]
        and existing_transaction.buyer_id != current_user["id"]
    ):
        raise HTTPException(
            status_code=403, detail="You are not the part of this transaction"
        )

    if existing_transaction.status in [
        TransactionStatus.CANCELLED,
        TransactionStatus.ACCEPTED,
    ]:
        raise HTTPException(
            status_code=400,
            detail=f"Transaction cannot be modified because it is {existing_transaction.status}",
        )

    existing_transaction.agreed_price = data.agreed_price
    existing_transaction.amount = data.amount

    db.commit()
    db.refresh(existing_transaction)

    return existing_transaction


@router.get("/my", response_model=List[TransactionResponse])
async def get_my_transaction(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    transactions = (
        db.query(Transaction)
        .filter(
            or_(
                Transaction.seller_id == current_user["id"],
                Transaction.buyer_id == current_user["id"],
            )
        )
        .all()
    )

    return transactions


def update_transaction_accept(
    db: Session,
    transaction_id: int,
    current_user: dict,
    role: TransactionRole,
    accepter: bool,
    accept_at: datetime,
):

    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    user_id = current_user["id"]
    if role == TransactionRole.buyer and transaction.buyer_id != user_id:
        raise HTTPException(
            status_code=403, detail="You are not the buyer of this transaction"
        )
    elif role == TransactionRole.seller and transaction.seller_id != user_id:
        raise HTTPException(
            status_code=403, detail="You are not the seller of this transaction"
        )

    if transaction.status in [TransactionStatus.CANCELLED, TransactionStatus.ACCEPTED]:
        raise HTTPException(
            status_code=400,
            detail=f"Transaction cannot be modified because it is {transaction.status}",
        )

    if role == TransactionRole.buyer:
        transaction.buyer_accept = accepter
        transaction.buyer_accept_at = accept_at
    elif role == TransactionRole.seller:
        transaction.seller_accept = accepter
        transaction.seller_accept_at = accept_at
    else:
        raise HTTPException(status_code=400, detail=f"Invalid role: {role}")

    if transaction.buyer_accept and transaction.seller_accept:
        transaction.status = TransactionStatus.ACCEPTED
        item_db = db.query(Item).filter(Item.id == transaction.item_id).first()

        if not item_db:
            raise HTTPException(status_code=404, detail="Item not found")

        if item_db.quantity >= transaction.amount:
            item_db.quantity -= transaction.amount
            db.commit()
            db.refresh(item_db)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Item is not available ,remaining :{item_db.quantity}",
            )
    else:
        transaction.status = TransactionStatus.PENDING.value

    db.commit()
    db.refresh(transaction)
    return transaction
