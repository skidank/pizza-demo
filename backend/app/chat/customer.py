import json
import anthropic
from sqlalchemy.orm import Session
from app.models import MenuItem, PizzaSize, Topping, Order, OrderItem, OrderItemTopping

SYSTEM_PROMPT = """You are a friendly pizza ordering assistant for "Slice of Heaven" pizza restaurant. Your ONLY job is to help customers build their pizza order.

RULES:
- Only discuss topics related to ordering food from our menu.
- If a customer asks about anything unrelated to ordering (politics, weather, tech, etc.), politely redirect them: "I'm here to help you order delicious pizza! What can I get for you?"
- Be warm, enthusiastic, and helpful. Use a casual, friendly tone.
- When a customer wants to order, help them choose a pizza, size, and toppings.
- Always confirm details before adding items.
- Proactively suggest popular additions (extra toppings, sides, drinks).
- When showing prices, format them as USD (e.g., $12.99).
- You can view the menu, add items to the order, remove items, and show the order summary.
- For non-pizza items (sides, drinks, desserts), no size selection is needed.
- If the customer seems done ordering, ask if they'd like anything else, then suggest placing the order.

TOPPING RULES — STRICTLY ENFORCED:
- Some menu items have a "max_toppings" limit. If set, you MUST NOT add more toppings than that limit. The add_to_order tool will reject orders that exceed the limit.
- Some items have "included_toppings" — this is how many toppings come free with the item. Extra toppings beyond that number cost extra.
- If a customer requests more toppings than allowed, politely explain the limit and ask them to choose which toppings they want within the limit. Do NOT offer to add extra toppings beyond the max — it is not possible.
- Always check the menu data for max_toppings before adding an item with toppings.

PERSONALITY: You're like a friendly pizza shop employee who genuinely loves pizza. Enthusiastic but not overbearing."""

TOOLS = [
    {
        "name": "get_menu",
        "description": "Get the full restaurant menu including pizzas, sides, drinks, sizes, and toppings.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "add_to_order",
        "description": "Add an item to the customer's order. For pizzas, include size_id and optional topping_ids. For sides/drinks/desserts, just the menu_item_id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "menu_item_id": {"type": "integer", "description": "ID of the menu item to add"},
                "size_id": {"type": "integer", "description": "ID of the pizza size (required for pizzas)"},
                "quantity": {"type": "integer", "description": "Number of this item", "default": 1},
                "topping_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "IDs of extra toppings to add",
                    "default": [],
                },
            },
            "required": ["menu_item_id"],
        },
    },
    {
        "name": "remove_from_order",
        "description": "Remove an item from the customer's order by order item ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_item_id": {"type": "integer", "description": "ID of the order item to remove"},
            },
            "required": ["order_item_id"],
        },
    },
    {
        "name": "get_order_summary",
        "description": "Get the current order summary with all items and total price.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "place_order",
        "description": "Finalize and place the current order. Only call this when the customer explicitly confirms they want to place the order.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


def get_menu_data(db: Session) -> dict:
    items = db.query(MenuItem).filter(MenuItem.is_available == True).order_by(MenuItem.category, MenuItem.sort_order).all()
    sizes = db.query(PizzaSize).order_by(PizzaSize.sort_order).all()
    toppings = db.query(Topping).filter(Topping.is_available == True).all()
    return {
        "items": [{"id": i.id, "name": i.name, "description": i.description, "category": i.category, "base_price": i.base_price, "max_toppings": i.max_toppings, "included_toppings": i.included_toppings} for i in items],
        "sizes": [{"id": s.id, "name": s.name, "price_multiplier": s.price_multiplier} for s in sizes],
        "toppings": [{"id": t.id, "name": t.name, "category": t.category, "price": t.price} for t in toppings],
    }


def get_order_data(order: Order) -> dict:
    if not order:
        return {"items": [], "total_price": 0}
    items = []
    for item in order.items:
        toppings = [{"id": t.topping.id, "name": t.topping.name, "price": t.topping.price} for t in item.toppings]
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
    return {"items": items, "total_price": order.total_price, "status": order.status}


def execute_tool(tool_name: str, tool_input: dict, db: Session, order: Order) -> tuple[str, dict]:
    """Execute a tool and return (result_text, updated_order_state)."""

    if tool_name == "get_menu":
        menu = get_menu_data(db)
        return json.dumps(menu), get_order_data(order)

    elif tool_name == "add_to_order":
        menu_item = db.query(MenuItem).filter(MenuItem.id == tool_input["menu_item_id"]).first()
        if not menu_item:
            return json.dumps({"error": "Menu item not found"}), get_order_data(order)

        topping_ids = tool_input.get("topping_ids", [])

        # Enforce max_toppings limit
        if menu_item.max_toppings is not None and len(topping_ids) > menu_item.max_toppings:
            return json.dumps({
                "error": f"This item allows a maximum of {menu_item.max_toppings} toppings, but {len(topping_ids)} were requested. Please ask the customer to choose only {menu_item.max_toppings}."
            }), get_order_data(order)

        price = menu_item.base_price
        size_id = tool_input.get("size_id")
        if size_id and menu_item.category == "pizza":
            size = db.query(PizzaSize).filter(PizzaSize.id == size_id).first()
            if size:
                price *= size.price_multiplier

        # Only charge for toppings beyond the included count
        chargeable_toppings = topping_ids[menu_item.included_toppings:]
        for tid in chargeable_toppings:
            topping = db.query(Topping).filter(Topping.id == tid).first()
            if topping:
                price += topping.price

        quantity = tool_input.get("quantity", 1)
        price = round(price * quantity, 2)

        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            size_id=size_id,
            quantity=quantity,
            item_price=price,
        )
        db.add(order_item)
        db.flush()

        for tid in topping_ids:
            db.add(OrderItemTopping(order_item_id=order_item.id, topping_id=tid))

        db.refresh(order)
        order.total_price = round(sum(i.item_price for i in order.items), 2)
        db.commit()
        db.refresh(order)
        return json.dumps({"success": True, "added": menu_item.name, "price": price}), get_order_data(order)

    elif tool_name == "remove_from_order":
        item = db.query(OrderItem).filter(
            OrderItem.id == tool_input["order_item_id"],
            OrderItem.order_id == order.id,
        ).first()
        if not item:
            return json.dumps({"error": "Item not found in order"}), get_order_data(order)
        name = item.menu_item.name
        db.delete(item)
        db.commit()
        db.refresh(order)
        order.total_price = round(sum(i.item_price for i in order.items), 2)
        db.commit()
        db.refresh(order)
        return json.dumps({"success": True, "removed": name}), get_order_data(order)

    elif tool_name == "get_order_summary":
        return json.dumps(get_order_data(order)), get_order_data(order)

    elif tool_name == "place_order":
        if not order.items:
            return json.dumps({"error": "Cannot place empty order"}), get_order_data(order)
        order.status = "placed"
        db.commit()
        db.refresh(order)
        return json.dumps({"success": True, "order_id": order.id, "total": order.total_price}), get_order_data(order)

    return json.dumps({"error": "Unknown tool"}), get_order_data(order)


def chat(messages: list[dict], db: Session, order: Order) -> tuple[str, dict]:
    """Process a customer chat message. Returns (assistant_reply, order_state)."""
    client = anthropic.Anthropic()

    # Inject current order state so the LLM always knows the full order,
    # including items added via the UI (not just via chat)
    current_order = get_order_data(order)
    order_context = ""
    if current_order["items"]:
        order_context = "\n\nCURRENT ORDER STATE (includes items added via the website UI — treat these as part of the customer's order):\n"
        order_context += json.dumps(current_order, indent=2)
    else:
        order_context = "\n\nCURRENT ORDER STATE: Empty (no items yet)."

    system_with_order = SYSTEM_PROMPT + order_context

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        system=system_with_order,
        tools=TOOLS,
        messages=messages,
    )

    # Process tool calls in a loop
    while response.stop_reason == "tool_use":
        tool_results = []
        order_state = get_order_data(order)

        for block in response.content:
            if block.type == "tool_use":
                result_text, order_state = execute_tool(block.name, block.input, db, order)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_text,
                })

        # Serialize content blocks to plain dicts for the next API call
        assistant_content = []
        for block in response.content:
            if block.type == "text":
                assistant_content.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                assistant_content.append({"type": "tool_use", "id": block.id, "name": block.name, "input": block.input})

        messages.append({"role": "assistant", "content": assistant_content})
        messages.append({"role": "user", "content": tool_results})

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            system=system_with_order,
            tools=TOOLS,
            messages=messages,
        )

    # Extract final text
    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text += block.text

    final_order_state = get_order_data(order)
    return text, final_order_state
