from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MenuItem, PizzaSize, Topping, DailySpecial, OperatingHours, HolidayClosure
from datetime import date

router = APIRouter(prefix="/api", tags=["menu"])


@router.get("/menu")
def get_menu(db: Session = Depends(get_db)):
    items = db.query(MenuItem).filter(MenuItem.is_available == True).order_by(MenuItem.category, MenuItem.sort_order).all()
    sizes = db.query(PizzaSize).order_by(PizzaSize.sort_order).all()
    toppings = db.query(Topping).filter(Topping.is_available == True).all()

    return {
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "category": item.category,
                "base_price": item.base_price,
                "image_url": item.image_url,
                "sort_order": item.sort_order,
                "max_toppings": item.max_toppings,
                "included_toppings": item.included_toppings,
            }
            for item in items
        ],
        "sizes": [
            {
                "id": s.id,
                "name": s.name,
                "price_multiplier": s.price_multiplier,
            }
            for s in sizes
        ],
        "toppings": [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category,
                "price": t.price,
            }
            for t in toppings
        ],
    }


@router.get("/menu/specials")
def get_specials(db: Session = Depends(get_db)):
    specials = db.query(DailySpecial).filter(DailySpecial.is_active == True).all()
    return [
        {
            "id": s.id,
            "title": s.title,
            "description": s.description,
            "discount_percent": s.discount_percent,
            "discount_amount": s.discount_amount,
            "day_of_week": s.day_of_week,
            "specific_date": str(s.specific_date) if s.specific_date else None,
            "menu_item_id": s.menu_item_id,
        }
        for s in specials
    ]


@router.get("/hours")
def get_hours(db: Session = Depends(get_db)):
    hours = db.query(OperatingHours).order_by(OperatingHours.day_of_week).all()
    closures = db.query(HolidayClosure).filter(HolidayClosure.date >= date.today()).order_by(HolidayClosure.date).all()

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return {
        "hours": [
            {
                "id": h.id,
                "day_of_week": h.day_of_week,
                "day_name": day_names[h.day_of_week],
                "open_time": h.open_time,
                "close_time": h.close_time,
                "is_closed": h.is_closed,
            }
            for h in hours
        ],
        "closures": [
            {
                "id": c.id,
                "date": str(c.date),
                "reason": c.reason,
            }
            for c in closures
        ],
    }
