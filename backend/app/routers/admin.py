from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.database import get_db
from app.models import MenuItem, Topping, DailySpecial, OperatingHours, HolidayClosure

router = APIRouter(prefix="/api/admin", tags=["admin"])


# --- Menu Items ---

class MenuItemCreate(BaseModel):
    name: str
    description: str = ""
    category: str = "pizza"
    base_price: float
    image_url: Optional[str] = None
    is_available: bool = True
    sort_order: int = 0
    max_toppings: Optional[int] = None
    included_toppings: int = 0


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    base_price: Optional[float] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    sort_order: Optional[int] = None
    max_toppings: Optional[int] = None
    included_toppings: Optional[int] = None


class ReorderRequest(BaseModel):
    item_ids: list[int]


@router.get("/menu")
def admin_get_menu(db: Session = Depends(get_db)):
    items = db.query(MenuItem).order_by(MenuItem.category, MenuItem.sort_order).all()
    return [
        {
            "id": i.id, "name": i.name, "description": i.description,
            "category": i.category, "base_price": i.base_price,
            "image_url": i.image_url, "is_available": i.is_available,
            "sort_order": i.sort_order,
            "max_toppings": i.max_toppings, "included_toppings": i.included_toppings,
        }
        for i in items
    ]


@router.post("/menu")
def create_menu_item(req: MenuItemCreate, db: Session = Depends(get_db)):
    item = MenuItem(**req.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "name": item.name, "category": item.category, "base_price": item.base_price}


@router.put("/menu/{item_id}")
def update_menu_item(item_id: int, req: MenuItemUpdate, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    for key, value in req.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "name": item.name, "category": item.category, "base_price": item.base_price, "is_available": item.is_available}


@router.delete("/menu/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(item)
    db.commit()
    return {"deleted": True, "id": item_id}


@router.put("/menu/reorder")
def reorder_menu(req: ReorderRequest, db: Session = Depends(get_db)):
    for idx, item_id in enumerate(req.item_ids):
        item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        if item:
            item.sort_order = idx
    db.commit()
    return {"reordered": True}


# --- Toppings ---

class ToppingCreate(BaseModel):
    name: str
    category: str = "veggie"
    price: float
    is_available: bool = True


class ToppingUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None


@router.get("/toppings")
def admin_get_toppings(db: Session = Depends(get_db)):
    toppings = db.query(Topping).all()
    return [{"id": t.id, "name": t.name, "category": t.category, "price": t.price, "is_available": t.is_available} for t in toppings]


@router.post("/toppings")
def create_topping(req: ToppingCreate, db: Session = Depends(get_db)):
    t = Topping(**req.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"id": t.id, "name": t.name, "price": t.price}


@router.put("/toppings/{topping_id}")
def update_topping(topping_id: int, req: ToppingUpdate, db: Session = Depends(get_db)):
    t = db.query(Topping).filter(Topping.id == topping_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Topping not found")
    for key, value in req.model_dump(exclude_unset=True).items():
        setattr(t, key, value)
    db.commit()
    return {"id": t.id, "name": t.name, "price": t.price, "is_available": t.is_available}


@router.delete("/toppings/{topping_id}")
def delete_topping(topping_id: int, db: Session = Depends(get_db)):
    t = db.query(Topping).filter(Topping.id == topping_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Topping not found")
    db.delete(t)
    db.commit()
    return {"deleted": True, "id": topping_id}


# --- Specials ---

class SpecialCreate(BaseModel):
    title: str
    description: str = ""
    discount_percent: Optional[float] = None
    discount_amount: Optional[float] = None
    day_of_week: Optional[int] = None
    specific_date: Optional[date] = None
    menu_item_id: Optional[int] = None
    is_active: bool = True


class SpecialUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    discount_percent: Optional[float] = None
    discount_amount: Optional[float] = None
    day_of_week: Optional[int] = None
    specific_date: Optional[date] = None
    menu_item_id: Optional[int] = None
    is_active: Optional[bool] = None


@router.get("/specials")
def admin_get_specials(db: Session = Depends(get_db)):
    specials = db.query(DailySpecial).all()
    return [
        {
            "id": s.id, "title": s.title, "description": s.description,
            "discount_percent": s.discount_percent, "discount_amount": s.discount_amount,
            "day_of_week": s.day_of_week,
            "specific_date": str(s.specific_date) if s.specific_date else None,
            "menu_item_id": s.menu_item_id, "is_active": s.is_active,
        }
        for s in specials
    ]


@router.post("/specials")
def create_special(req: SpecialCreate, db: Session = Depends(get_db)):
    s = DailySpecial(**req.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"id": s.id, "title": s.title}


@router.put("/specials/{special_id}")
def update_special(special_id: int, req: SpecialUpdate, db: Session = Depends(get_db)):
    s = db.query(DailySpecial).filter(DailySpecial.id == special_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Special not found")
    for key, value in req.model_dump(exclude_unset=True).items():
        setattr(s, key, value)
    db.commit()
    return {"id": s.id, "title": s.title, "is_active": s.is_active}


@router.delete("/specials/{special_id}")
def delete_special(special_id: int, db: Session = Depends(get_db)):
    s = db.query(DailySpecial).filter(DailySpecial.id == special_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Special not found")
    db.delete(s)
    db.commit()
    return {"deleted": True, "id": special_id}


# --- Hours & Closures ---

class HoursUpdate(BaseModel):
    hours: list[dict]  # [{day_of_week, open_time, close_time, is_closed}]


class ClosureCreate(BaseModel):
    date: date
    reason: str


@router.put("/hours")
def update_hours(req: HoursUpdate, db: Session = Depends(get_db)):
    for h in req.hours:
        existing = db.query(OperatingHours).filter(OperatingHours.day_of_week == h["day_of_week"]).first()
        if existing:
            existing.open_time = h.get("open_time", existing.open_time)
            existing.close_time = h.get("close_time", existing.close_time)
            existing.is_closed = h.get("is_closed", existing.is_closed)
        else:
            db.add(OperatingHours(**h))
    db.commit()
    return {"updated": True}


@router.get("/closures")
def get_closures(db: Session = Depends(get_db)):
    closures = db.query(HolidayClosure).order_by(HolidayClosure.date).all()
    return [{"id": c.id, "date": str(c.date), "reason": c.reason} for c in closures]


@router.post("/closures")
def add_closure(req: ClosureCreate, db: Session = Depends(get_db)):
    c = HolidayClosure(date=req.date, reason=req.reason)
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"id": c.id, "date": str(c.date), "reason": c.reason}


@router.delete("/closures/{closure_id}")
def delete_closure(closure_id: int, db: Session = Depends(get_db)):
    c = db.query(HolidayClosure).filter(HolidayClosure.id == closure_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Closure not found")
    db.delete(c)
    db.commit()
    return {"deleted": True, "id": closure_id}
