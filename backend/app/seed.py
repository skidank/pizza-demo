from sqlalchemy.orm import Session
from app.models import MenuItem, PizzaSize, Topping, OperatingHours, DailySpecial


def seed_database(db: Session):
    # Check if already seeded
    if db.query(MenuItem).first():
        return

    # Pizza sizes
    sizes = [
        PizzaSize(name="Small (10\")", price_multiplier=0.8, sort_order=0),
        PizzaSize(name="Medium (12\")", price_multiplier=1.0, sort_order=1),
        PizzaSize(name="Large (14\")", price_multiplier=1.3, sort_order=2),
        PizzaSize(name="XL (16\")", price_multiplier=1.6, sort_order=3),
    ]
    db.add_all(sizes)

    # Pizzas
    pizzas = [
        MenuItem(name="Margherita", description="Fresh mozzarella, tomato sauce, basil", category="pizza", base_price=12.99, sort_order=0),
        MenuItem(name="Pepperoni", description="Classic pepperoni with mozzarella and tomato sauce", category="pizza", base_price=14.99, sort_order=1),
        MenuItem(name="BBQ Chicken", description="Grilled chicken, BBQ sauce, red onion, cilantro", category="pizza", base_price=16.99, sort_order=2),
        MenuItem(name="Veggie Supreme", description="Bell peppers, mushrooms, onions, olives, tomatoes", category="pizza", base_price=15.99, sort_order=3),
        MenuItem(name="Hawaiian", description="Ham, pineapple, mozzarella", category="pizza", base_price=14.99, sort_order=4),
        MenuItem(name="Meat Lover's", description="Pepperoni, sausage, bacon, ham, ground beef", category="pizza", base_price=17.99, sort_order=5),
        MenuItem(name="Buffalo Chicken", description="Spicy buffalo chicken, blue cheese crumbles, celery", category="pizza", base_price=16.99, sort_order=6),
        MenuItem(name="Four Cheese", description="Mozzarella, parmesan, ricotta, gorgonzola", category="pizza", base_price=15.99, sort_order=7),
    ]
    db.add_all(pizzas)

    # Sides
    sides = [
        MenuItem(name="Garlic Bread", description="Toasted bread with garlic butter and herbs", category="side", base_price=5.99, sort_order=0),
        MenuItem(name="Buffalo Wings (8pc)", description="Crispy wings tossed in buffalo sauce", category="side", base_price=10.99, sort_order=1),
        MenuItem(name="Caesar Salad", description="Romaine, croutons, parmesan, Caesar dressing", category="side", base_price=8.99, sort_order=2),
        MenuItem(name="Mozzarella Sticks (6pc)", description="Breaded mozzarella with marinara dipping sauce", category="side", base_price=7.99, sort_order=3),
    ]
    db.add_all(sides)

    # Drinks
    drinks = [
        MenuItem(name="Soda (can)", description="Coke, Diet Coke, Sprite, or Fanta", category="drink", base_price=1.99, sort_order=0),
        MenuItem(name="Iced Tea", description="Fresh brewed, sweetened or unsweetened", category="drink", base_price=2.49, sort_order=1),
        MenuItem(name="Lemonade", description="House-made lemonade", category="drink", base_price=2.99, sort_order=2),
        MenuItem(name="Water Bottle", description="Purified water", category="drink", base_price=1.49, sort_order=3),
    ]
    db.add_all(drinks)

    # Desserts
    desserts = [
        MenuItem(name="Chocolate Lava Cake", description="Warm chocolate cake with molten center", category="dessert", base_price=6.99, sort_order=0),
        MenuItem(name="Tiramisu", description="Classic Italian coffee-flavored dessert", category="dessert", base_price=7.99, sort_order=1),
    ]
    db.add_all(desserts)

    # Toppings
    toppings = [
        # Meats
        Topping(name="Pepperoni", category="meat", price=1.99),
        Topping(name="Italian Sausage", category="meat", price=1.99),
        Topping(name="Bacon", category="meat", price=2.49),
        Topping(name="Ham", category="meat", price=1.99),
        Topping(name="Grilled Chicken", category="meat", price=2.49),
        Topping(name="Ground Beef", category="meat", price=1.99),
        Topping(name="Anchovies", category="meat", price=2.49),
        # Veggies
        Topping(name="Mushrooms", category="veggie", price=1.49),
        Topping(name="Bell Peppers", category="veggie", price=1.49),
        Topping(name="Red Onion", category="veggie", price=1.29),
        Topping(name="Black Olives", category="veggie", price=1.49),
        Topping(name="Jalapeños", category="veggie", price=1.29),
        Topping(name="Tomatoes", category="veggie", price=1.29),
        Topping(name="Spinach", category="veggie", price=1.49),
        Topping(name="Pineapple", category="veggie", price=1.49),
        # Cheese
        Topping(name="Extra Mozzarella", category="cheese", price=1.99),
        Topping(name="Parmesan", category="cheese", price=1.99),
        Topping(name="Ricotta", category="cheese", price=1.99),
        Topping(name="Gorgonzola", category="cheese", price=2.49),
    ]
    db.add_all(toppings)

    # Operating hours (Mon-Sat 11am-10pm, Sun closed)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for i, day in enumerate(days):
        is_closed = (i == 6)  # Sunday
        hours = OperatingHours(
            day_of_week=i,
            open_time="11:00",
            close_time="22:00",
            is_closed=is_closed,
        )
        db.add(hours)

    # Sample special
    special = DailySpecial(
        title="Margherita Monday",
        description="20% off all Margherita pizzas every Monday!",
        discount_percent=20.0,
        day_of_week=0,
        menu_item_id=1,
        is_active=True,
    )
    db.add(special)

    db.commit()
