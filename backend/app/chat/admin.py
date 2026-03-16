import json
import anthropic
from datetime import date
from sqlalchemy.orm import Session
from app.models import MenuItem, Topping, DailySpecial, OperatingHours, HolidayClosure, PizzaSize

SYSTEM_PROMPT = """You are a restaurant management assistant for "Slice of Heaven" pizza restaurant. Your ONLY job is to help the admin manage the restaurant's menu, specials, and operating hours.

RULES:
- Only discuss topics related to managing the restaurant (menu items, prices, toppings, specials, hours, closures).
- If asked about anything unrelated, politely redirect: "I'm here to help you manage the restaurant. What would you like to update?"
- Always confirm changes before executing them.
- When making changes, explain what you're doing clearly.
- Show current state when asked, and summarize changes after making them.
- For day_of_week values: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday.

CAPABILITIES:
- View and modify menu items (add, update, remove, reorder)
- View and modify toppings (add, update, remove)
- View and modify daily specials (add, update, remove)
- View and modify operating hours
- Add and remove holiday closures

Be professional, efficient, and clear in your communication."""

TOOLS = [
    {
        "name": "get_current_menu",
        "description": "Get all menu items, including unavailable ones.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_current_toppings",
        "description": "Get all toppings, including unavailable ones.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_current_sizes",
        "description": "Get all pizza sizes.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "add_menu_item",
        "description": "Add a new menu item. Use max_toppings to limit how many toppings can be added (null = unlimited). Use included_toppings to specify how many toppings are included free in the base price.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string", "default": ""},
                "category": {"type": "string", "enum": ["pizza", "side", "drink", "dessert"]},
                "base_price": {"type": "number"},
                "is_available": {"type": "boolean", "default": True},
                "max_toppings": {"type": "integer", "description": "Maximum number of toppings allowed. Null means unlimited."},
                "included_toppings": {"type": "integer", "description": "Number of toppings included free in the base price. Default 0."},
            },
            "required": ["name", "category", "base_price"],
        },
    },
    {
        "name": "update_menu_item",
        "description": "Update an existing menu item. Only include fields you want to change. Use max_toppings to limit toppings (null = unlimited), included_toppings for free toppings in base price.",
        "input_schema": {
            "type": "object",
            "properties": {
                "item_id": {"type": "integer"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "category": {"type": "string", "enum": ["pizza", "side", "drink", "dessert"]},
                "base_price": {"type": "number"},
                "is_available": {"type": "boolean"},
                "max_toppings": {"type": "integer", "description": "Maximum number of toppings allowed. Null means unlimited."},
                "included_toppings": {"type": "integer", "description": "Number of toppings included free in the base price."},
            },
            "required": ["item_id"],
        },
    },
    {
        "name": "remove_menu_item",
        "description": "Remove a menu item by ID.",
        "input_schema": {
            "type": "object",
            "properties": {"item_id": {"type": "integer"}},
            "required": ["item_id"],
        },
    },
    {
        "name": "add_topping",
        "description": "Add a new topping option.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "category": {"type": "string", "enum": ["meat", "veggie", "cheese"]},
                "price": {"type": "number"},
            },
            "required": ["name", "category", "price"],
        },
    },
    {
        "name": "update_topping",
        "description": "Update an existing topping.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topping_id": {"type": "integer"},
                "name": {"type": "string"},
                "category": {"type": "string", "enum": ["meat", "veggie", "cheese"]},
                "price": {"type": "number"},
                "is_available": {"type": "boolean"},
            },
            "required": ["topping_id"],
        },
    },
    {
        "name": "remove_topping",
        "description": "Remove a topping by ID.",
        "input_schema": {
            "type": "object",
            "properties": {"topping_id": {"type": "integer"}},
            "required": ["topping_id"],
        },
    },
    {
        "name": "get_specials",
        "description": "Get all daily specials.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "create_special",
        "description": "Create a new daily special.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string", "default": ""},
                "discount_percent": {"type": "number", "description": "Percentage discount (e.g., 20 for 20% off)"},
                "discount_amount": {"type": "number", "description": "Flat dollar discount"},
                "day_of_week": {"type": "integer", "description": "0=Mon..6=Sun, for recurring weekly specials"},
                "specific_date": {"type": "string", "description": "YYYY-MM-DD for one-time specials"},
                "menu_item_id": {"type": "integer", "description": "If special applies to a specific menu item"},
            },
            "required": ["title"],
        },
    },
    {
        "name": "update_special",
        "description": "Update an existing special.",
        "input_schema": {
            "type": "object",
            "properties": {
                "special_id": {"type": "integer"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "discount_percent": {"type": "number"},
                "discount_amount": {"type": "number"},
                "day_of_week": {"type": "integer"},
                "specific_date": {"type": "string"},
                "menu_item_id": {"type": "integer"},
                "is_active": {"type": "boolean"},
            },
            "required": ["special_id"],
        },
    },
    {
        "name": "remove_special",
        "description": "Remove a special by ID.",
        "input_schema": {
            "type": "object",
            "properties": {"special_id": {"type": "integer"}},
            "required": ["special_id"],
        },
    },
    {
        "name": "get_hours",
        "description": "Get current operating hours for all days.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "update_hours",
        "description": "Update operating hours for one or more days.",
        "input_schema": {
            "type": "object",
            "properties": {
                "hours": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "day_of_week": {"type": "integer"},
                            "open_time": {"type": "string", "description": "HH:MM format"},
                            "close_time": {"type": "string", "description": "HH:MM format"},
                            "is_closed": {"type": "boolean"},
                        },
                        "required": ["day_of_week"],
                    },
                },
            },
            "required": ["hours"],
        },
    },
    {
        "name": "get_closures",
        "description": "Get all scheduled holiday closures.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "add_closure",
        "description": "Add a holiday closure.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "YYYY-MM-DD"},
                "reason": {"type": "string"},
            },
            "required": ["date", "reason"],
        },
    },
    {
        "name": "remove_closure",
        "description": "Remove a holiday closure by ID.",
        "input_schema": {
            "type": "object",
            "properties": {"closure_id": {"type": "integer"}},
            "required": ["closure_id"],
        },
    },
]


def execute_tool(tool_name: str, tool_input: dict, db: Session) -> str:
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    if tool_name == "get_current_menu":
        items = db.query(MenuItem).order_by(MenuItem.category, MenuItem.sort_order).all()
        return json.dumps([
            {"id": i.id, "name": i.name, "description": i.description, "category": i.category,
             "base_price": i.base_price, "is_available": i.is_available, "sort_order": i.sort_order,
             "max_toppings": i.max_toppings, "included_toppings": i.included_toppings}
            for i in items
        ])

    elif tool_name == "get_current_toppings":
        toppings = db.query(Topping).all()
        return json.dumps([
            {"id": t.id, "name": t.name, "category": t.category, "price": t.price, "is_available": t.is_available}
            for t in toppings
        ])

    elif tool_name == "get_current_sizes":
        sizes = db.query(PizzaSize).order_by(PizzaSize.sort_order).all()
        return json.dumps([{"id": s.id, "name": s.name, "price_multiplier": s.price_multiplier} for s in sizes])

    elif tool_name == "add_menu_item":
        max_order = db.query(MenuItem).filter(MenuItem.category == tool_input["category"]).count()
        item = MenuItem(
            name=tool_input["name"],
            description=tool_input.get("description", ""),
            category=tool_input["category"],
            base_price=tool_input["base_price"],
            is_available=tool_input.get("is_available", True),
            sort_order=max_order,
            max_toppings=tool_input.get("max_toppings"),
            included_toppings=tool_input.get("included_toppings", 0),
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return json.dumps({"success": True, "id": item.id, "name": item.name, "base_price": item.base_price})

    elif tool_name == "update_menu_item":
        item = db.query(MenuItem).filter(MenuItem.id == tool_input["item_id"]).first()
        if not item:
            return json.dumps({"error": "Menu item not found"})
        for key in ["name", "description", "category", "base_price", "is_available", "max_toppings", "included_toppings"]:
            if key in tool_input:
                setattr(item, key, tool_input[key])
        db.commit()
        return json.dumps({"success": True, "id": item.id, "name": item.name, "base_price": item.base_price, "is_available": item.is_available, "max_toppings": item.max_toppings, "included_toppings": item.included_toppings})

    elif tool_name == "remove_menu_item":
        item = db.query(MenuItem).filter(MenuItem.id == tool_input["item_id"]).first()
        if not item:
            return json.dumps({"error": "Menu item not found"})
        name = item.name
        db.delete(item)
        db.commit()
        return json.dumps({"success": True, "removed": name})

    elif tool_name == "add_topping":
        t = Topping(name=tool_input["name"], category=tool_input["category"], price=tool_input["price"])
        db.add(t)
        db.commit()
        db.refresh(t)
        return json.dumps({"success": True, "id": t.id, "name": t.name})

    elif tool_name == "update_topping":
        t = db.query(Topping).filter(Topping.id == tool_input["topping_id"]).first()
        if not t:
            return json.dumps({"error": "Topping not found"})
        for key in ["name", "category", "price", "is_available"]:
            if key in tool_input:
                setattr(t, key, tool_input[key])
        db.commit()
        return json.dumps({"success": True, "id": t.id, "name": t.name, "price": t.price})

    elif tool_name == "remove_topping":
        t = db.query(Topping).filter(Topping.id == tool_input["topping_id"]).first()
        if not t:
            return json.dumps({"error": "Topping not found"})
        name = t.name
        db.delete(t)
        db.commit()
        return json.dumps({"success": True, "removed": name})

    elif tool_name == "get_specials":
        specials = db.query(DailySpecial).all()
        return json.dumps([
            {"id": s.id, "title": s.title, "description": s.description,
             "discount_percent": s.discount_percent, "discount_amount": s.discount_amount,
             "day_of_week": s.day_of_week,
             "day_name": day_names[s.day_of_week] if s.day_of_week is not None else None,
             "specific_date": str(s.specific_date) if s.specific_date else None,
             "menu_item_id": s.menu_item_id, "is_active": s.is_active}
            for s in specials
        ])

    elif tool_name == "create_special":
        s = DailySpecial(
            title=tool_input["title"],
            description=tool_input.get("description", ""),
            discount_percent=tool_input.get("discount_percent"),
            discount_amount=tool_input.get("discount_amount"),
            day_of_week=tool_input.get("day_of_week"),
            specific_date=date.fromisoformat(tool_input["specific_date"]) if tool_input.get("specific_date") else None,
            menu_item_id=tool_input.get("menu_item_id"),
            is_active=True,
        )
        db.add(s)
        db.commit()
        db.refresh(s)
        return json.dumps({"success": True, "id": s.id, "title": s.title})

    elif tool_name == "update_special":
        s = db.query(DailySpecial).filter(DailySpecial.id == tool_input["special_id"]).first()
        if not s:
            return json.dumps({"error": "Special not found"})
        for key in ["title", "description", "discount_percent", "discount_amount", "day_of_week", "menu_item_id", "is_active"]:
            if key in tool_input:
                setattr(s, key, tool_input[key])
        if "specific_date" in tool_input:
            s.specific_date = date.fromisoformat(tool_input["specific_date"]) if tool_input["specific_date"] else None
        db.commit()
        return json.dumps({"success": True, "id": s.id, "title": s.title})

    elif tool_name == "remove_special":
        s = db.query(DailySpecial).filter(DailySpecial.id == tool_input["special_id"]).first()
        if not s:
            return json.dumps({"error": "Special not found"})
        title = s.title
        db.delete(s)
        db.commit()
        return json.dumps({"success": True, "removed": title})

    elif tool_name == "get_hours":
        hours = db.query(OperatingHours).order_by(OperatingHours.day_of_week).all()
        return json.dumps([
            {"id": h.id, "day_of_week": h.day_of_week, "day_name": day_names[h.day_of_week],
             "open_time": h.open_time, "close_time": h.close_time, "is_closed": h.is_closed}
            for h in hours
        ])

    elif tool_name == "update_hours":
        for h in tool_input["hours"]:
            existing = db.query(OperatingHours).filter(OperatingHours.day_of_week == h["day_of_week"]).first()
            if existing:
                if "open_time" in h:
                    existing.open_time = h["open_time"]
                if "close_time" in h:
                    existing.close_time = h["close_time"]
                if "is_closed" in h:
                    existing.is_closed = h["is_closed"]
        db.commit()
        return json.dumps({"success": True, "updated_days": [day_names[h["day_of_week"]] for h in tool_input["hours"]]})

    elif tool_name == "get_closures":
        closures = db.query(HolidayClosure).order_by(HolidayClosure.date).all()
        return json.dumps([{"id": c.id, "date": str(c.date), "reason": c.reason} for c in closures])

    elif tool_name == "add_closure":
        c = HolidayClosure(date=date.fromisoformat(tool_input["date"]), reason=tool_input["reason"])
        db.add(c)
        db.commit()
        db.refresh(c)
        return json.dumps({"success": True, "id": c.id, "date": str(c.date), "reason": c.reason})

    elif tool_name == "remove_closure":
        c = db.query(HolidayClosure).filter(HolidayClosure.id == tool_input["closure_id"]).first()
        if not c:
            return json.dumps({"error": "Closure not found"})
        reason = c.reason
        db.delete(c)
        db.commit()
        return json.dumps({"success": True, "removed": reason})

    return json.dumps({"error": "Unknown tool"})


def chat(messages: list[dict], db: Session) -> tuple[str, dict]:
    """Process an admin chat message. Returns (assistant_reply, mutation_info)."""
    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages,
    )

    mutations = []

    while response.stop_reason == "tool_use":
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result_text = execute_tool(block.name, block.input, db)
                mutations.append({"tool": block.name, "input": block.input, "result": json.loads(result_text)})
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
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text += block.text

    return text, {"mutations": mutations}
