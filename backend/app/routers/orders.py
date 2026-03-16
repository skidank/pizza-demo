from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import Order, OrderItem, OrderItemTopping, MenuItem, PizzaSize, Topping

router = APIRouter(prefix="/api/orders", tags=["orders"])


class AddItemRequest(BaseModel):
    menu_item_id: int
    size_id: Optional[int] = None
    quantity: int = 1
    topping_ids: list[int] = []


class CreateOrderRequest(BaseModel):
    customer_name: str = "Guest"


def serialize_order(order: Order) -> dict:
    items = []
    for item in order.items:
        toppings = [
            {"id": t.topping.id, "name": t.topping.name, "price": t.topping.price}
            for t in item.toppings
        ]
        items.append({
            "id": item.id,
            "menu_item_id": item.menu_item_id,
            "menu_item_name": item.menu_item.name,
            "category": item.menu_item.category,
            "size": {"id": item.size.id, "name": item.size.name} if item.size else None,
            "quantity": item.quantity,
            "item_price": item.item_price,
            "toppings": toppings,
        })

    return {
        "id": order.id,
        "customer_name": order.customer_name,
        "status": order.status,
        "total_price": order.total_price,
        "items": items,
    }


@router.post("")
def create_order(req: CreateOrderRequest, db: Session = Depends(get_db)):
    order = Order(customer_name=req.customer_name)
    db.add(order)
    db.commit()
    db.refresh(order)
    return serialize_order(order)


@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return serialize_order(order)


@router.post("/{order_id}/items")
def add_item(order_id: int, req: AddItemRequest, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "building":
        raise HTTPException(status_code=400, detail="Order already placed")

    menu_item = db.query(MenuItem).filter(MenuItem.id == req.menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    # Enforce max_toppings
    if menu_item.max_toppings is not None and len(req.topping_ids) > menu_item.max_toppings:
        raise HTTPException(status_code=400, detail=f"This item allows a maximum of {menu_item.max_toppings} toppings")

    # Calculate price
    price = menu_item.base_price
    if req.size_id and menu_item.category == "pizza":
        size = db.query(PizzaSize).filter(PizzaSize.id == req.size_id).first()
        if size:
            price *= size.price_multiplier

    # Add topping prices (only charge beyond included count)
    chargeable_toppings = req.topping_ids[menu_item.included_toppings:]
    topping_total = 0.0
    for tid in chargeable_toppings:
        topping = db.query(Topping).filter(Topping.id == tid).first()
        if topping:
            topping_total += topping.price

    price += topping_total
    price = round(price * req.quantity, 2)

    order_item = OrderItem(
        order_id=order.id,
        menu_item_id=req.menu_item_id,
        size_id=req.size_id,
        quantity=req.quantity,
        item_price=price,
    )
    db.add(order_item)
    db.flush()

    for tid in req.topping_ids:
        db.add(OrderItemTopping(order_item_id=order_item.id, topping_id=tid))

    # Recalculate total (new item is already in order.items after flush)
    db.refresh(order)
    order.total_price = round(sum(i.item_price for i in order.items), 2)
    db.commit()
    db.refresh(order)
    return serialize_order(order)


@router.delete("/{order_id}/items/{item_id}")
def remove_item(order_id: int, item_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    item = db.query(OrderItem).filter(OrderItem.id == item_id, OrderItem.order_id == order_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    db.refresh(order)
    order.total_price = round(sum(i.item_price for i in order.items), 2)
    db.commit()
    db.refresh(order)
    return serialize_order(order)


@router.post("/{order_id}/place")
def place_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not order.items:
        raise HTTPException(status_code=400, detail="Cannot place empty order")
    order.status = "placed"
    db.commit()
    db.refresh(order)
    return serialize_order(order)
