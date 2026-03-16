from datetime import datetime, date, time
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    category = Column(String, nullable=False)  # pizza, side, drink, dessert
    base_price = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    max_toppings = Column(Integer, nullable=True)  # null = unlimited
    included_toppings = Column(Integer, default=0)  # number of free toppings included
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PizzaSize(Base):
    __tablename__ = "pizza_sizes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price_multiplier = Column(Float, nullable=False)
    sort_order = Column(Integer, default=0)


class Topping(Base):
    __tablename__ = "toppings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # meat, veggie, cheese
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)


class DailySpecial(Base):
    __tablename__ = "daily_specials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    discount_percent = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)
    day_of_week = Column(Integer, nullable=True)  # 0=Mon..6=Sun
    specific_date = Column(Date, nullable=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=True)
    is_active = Column(Boolean, default=True)


class OperatingHours(Base):
    __tablename__ = "operating_hours"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Integer, nullable=False, unique=True)
    open_time = Column(String, nullable=False)  # "HH:MM" format
    close_time = Column(String, nullable=False)
    is_closed = Column(Boolean, default=False)


class HolidayClosure(Base):
    __tablename__ = "holiday_closures"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    reason = Column(String, nullable=False)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, default="Guest")
    status = Column(String, default="building")  # building, placed
    total_price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    size_id = Column(Integer, ForeignKey("pizza_sizes.id"), nullable=True)
    quantity = Column(Integer, default=1)
    item_price = Column(Float, nullable=False)
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")
    size = relationship("PizzaSize")
    toppings = relationship("OrderItemTopping", cascade="all, delete-orphan")


class OrderItemTopping(Base):
    __tablename__ = "order_item_toppings"

    id = Column(Integer, primary_key=True, index=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=False)
    topping_id = Column(Integer, ForeignKey("toppings.id"), nullable=False)
    topping = relationship("Topping")
