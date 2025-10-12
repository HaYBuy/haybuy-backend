from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.Carts.cart import Cart
from app.db.models.Carts.cart_item import CartItem
from app.db.models.items.item import Item
from app.schemas.cart_schema import CartResponse, CartItemResponse
from app.schemas.cart_item_response import CartItemCreate, CartItemResponse
from ...core.security import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/", response_model=CartResponse)
def get_my_cart(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == current_user["id"]).first()
    if not cart:
        cart = Cart(user_id=current_user["id"])
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


@router.post("/add", response_model=CartItemResponse)
def add_to_cart(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    cart = db.query(Cart).filter(Cart.user_id == current_user["id"]).first()
    if not cart:
        cart = Cart(user_id=current_user["id"])
        db.add(cart)
        db.commit()
        db.refresh(cart)


    product = db.get(Item, item_data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing_item = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id, CartItem.product_id == item_data.product_id)
        .first()
    )
    if existing_item:
        existing_item.quantity += item_data.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item

    new_item = CartItem(
        cart_id=cart.id,
        product_id=item_data.product_id,
        quantity=item_data.quantity,
        price=product.price,

    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.delete("/remove/{item_id}")
def remove_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    item = (
        db.query(CartItem)
        .join(Cart)
        .filter(CartItem.id == item_id, Cart.user_id == current_user["id"])
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in your cart")

    db.delete(item)
    db.commit()
    return {"detail": "Item removed"}


@router.delete("/clear")
def clear_cart(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == current_user["id"]).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    return {"detail": "Cart cleared"}
