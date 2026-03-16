from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import Order
from app.chat import customer as customer_chat
from app.chat import admin as admin_chat

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_history: list[dict] = []
    order_id: int | None = None


@router.post("/customer")
def customer_chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    # Get or create order
    order = None
    if req.order_id:
        order = db.query(Order).filter(Order.id == req.order_id).first()
    if not order:
        order = Order(customer_name="Guest")
        db.add(order)
        db.commit()
        db.refresh(order)

    # Build messages
    messages = list(req.conversation_history)
    messages.append({"role": "user", "content": req.message})

    reply, order_state = customer_chat.chat(messages, db, order)

    return {
        "reply": reply,
        "order_id": order.id,
        "order_state": order_state,
    }


@router.post("/admin")
def admin_chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    messages = list(req.conversation_history)
    messages.append({"role": "user", "content": req.message})

    reply, mutation_info = admin_chat.chat(messages, db)

    return {
        "reply": reply,
        "mutations": mutation_info.get("mutations", []),
    }
