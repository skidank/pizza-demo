# Pizza Demo — Online Ordering Website Specification

## Overview

A full-stack pizza restaurant ordering website with two modes:

1. **Customer Mode** — Browse the menu, customize pizzas, and place orders via traditional UI or an LLM-powered chatbot.
2. **Admin Mode** — Manage menu items, prices, specials, and operating hours via an LLM-powered chatbot with live UI preview.

This is a demo application; payment processing and order fulfillment are out of scope.

---

## Technology Stack

| Layer        | Technology                        |
|--------------|-----------------------------------|
| Frontend     | React 18 + TypeScript + Vite      |
| UI Library   | Tailwind CSS                      |
| Backend API  | Python / FastAPI                  |
| Database     | SQLite (via SQLAlchemy)           |
| LLM          | Anthropic Claude API (claude-sonnet-4-5) |
| Containerization | Docker + Docker Compose       |

---

## Data Model

### MenuItem
| Field          | Type     | Description                          |
|----------------|----------|--------------------------------------|
| id             | int (PK) | Auto-increment                       |
| name           | string   | e.g. "Margherita"                    |
| description    | string   | Short description                    |
| category       | string   | "pizza", "side", "drink", "dessert"  |
| base_price     | float    | Price in USD                         |
| image_url      | string?  | Optional image                       |
| is_available   | bool     | Whether currently on the menu        |
| sort_order     | int      | Display ordering                     |
| created_at     | datetime |                                      |
| updated_at     | datetime |                                      |

### PizzaSize
| Field       | Type     | Description                 |
|-------------|----------|-----------------------------|
| id          | int (PK) |                             |
| name        | string   | "Small", "Medium", "Large"  |
| price_mult  | float    | Multiplier on base_price    |

### Topping
| Field       | Type     | Description                 |
|-------------|----------|-----------------------------|
| id          | int (PK) |                             |
| name        | string   | e.g. "Pepperoni"            |
| category    | string   | "meat", "veggie", "cheese"  |
| price       | float    | Additional cost             |
| is_available| bool     |                             |

### DailySpecial
| Field       | Type     | Description                           |
|-------------|----------|---------------------------------------|
| id          | int (PK) |                                       |
| title       | string   | e.g. "Two-for-Tuesday"               |
| description | string   | Details                               |
| discount_pct| float?   | Optional percentage discount          |
| discount_amt| float?   | Optional flat discount                |
| day_of_week | int?     | 0=Mon..6=Sun, null=specific date      |
| specific_date| date?   | For one-off specials                  |
| menu_item_id| int? (FK)| If tied to a specific item            |
| is_active   | bool     |                                       |

### OperatingHours
| Field       | Type     | Description                           |
|-------------|----------|---------------------------------------|
| id          | int (PK) |                                       |
| day_of_week | int      | 0=Mon..6=Sun                          |
| open_time   | time     |                                       |
| close_time  | time     |                                       |
| is_closed   | bool     | Override: closed for this day         |

### HolidayClosure
| Field       | Type     | Description                           |
|-------------|----------|---------------------------------------|
| id          | int (PK) |                                       |
| date        | date     | The date of closure                   |
| reason      | string   | e.g. "Christmas Day"                  |

### Order (lightweight, no payment)
| Field          | Type     | Description                        |
|----------------|----------|------------------------------------|
| id             | int (PK) |                                    |
| customer_name  | string   |                                    |
| status         | string   | "building", "placed"               |
| total_price    | float    |                                    |
| created_at     | datetime |                                    |

### OrderItem
| Field          | Type     | Description                        |
|----------------|----------|------------------------------------|
| id             | int (PK) |                                    |
| order_id       | int (FK) |                                    |
| menu_item_id   | int (FK) |                                    |
| size_id        | int (FK) |                                    |
| quantity       | int      |                                    |
| item_price     | float    | Computed at time of add            |

### OrderItemTopping
| Field          | Type     | Description                        |
|----------------|----------|------------------------------------|
| id             | int (PK) |                                    |
| order_item_id  | int (FK) |                                    |
| topping_id     | int (FK) |                                    |

---

## API Endpoints

### Menu
- `GET /api/menu` — Full menu (items, sizes, toppings)
- `GET /api/menu/specials` — Active daily specials
- `GET /api/hours` — Operating hours + closures

### Orders
- `POST /api/orders` — Create new order
- `GET /api/orders/{id}` — Get order details
- `POST /api/orders/{id}/items` — Add item to order
- `DELETE /api/orders/{id}/items/{item_id}` — Remove item
- `POST /api/orders/{id}/place` — Finalize order

### Admin
- `PUT /api/admin/menu/{id}` — Update menu item
- `POST /api/admin/menu` — Create menu item
- `DELETE /api/admin/menu/{id}` — Remove menu item
- `PUT /api/admin/menu/reorder` — Reorder items
- `POST /api/admin/toppings` — Add topping
- `PUT /api/admin/toppings/{id}` — Update topping
- `DELETE /api/admin/toppings/{id}` — Remove topping
- `POST /api/admin/specials` — Create special
- `PUT /api/admin/specials/{id}` — Update special
- `DELETE /api/admin/specials/{id}` — Remove special
- `PUT /api/admin/hours` — Update operating hours
- `POST /api/admin/closures` — Add closure
- `DELETE /api/admin/closures/{id}` — Remove closure

### Chat
- `POST /api/chat/customer` — Customer chatbot (sends message, returns response + order state)
- `POST /api/chat/admin` — Admin chatbot (sends message, returns response + mutation result)

---

## Chatbot Design

### Customer Chatbot
- **System prompt** constrains conversation to pizza ordering only.
- Uses tool-calling to interact with the order: `add_pizza`, `remove_item`, `set_size`, `add_topping`, `remove_topping`, `get_order_summary`, `get_menu`.
- Each response returns the updated order state so the UI can reflect changes.
- Friendly, helpful tone. Refuses off-topic requests politely.

### Admin Chatbot
- **System prompt** constrains conversation to menu/restaurant management only.
- Uses tool-calling to modify the restaurant: `add_menu_item`, `update_menu_item`, `remove_menu_item`, `reorder_menu`, `add_topping`, `update_topping`, `remove_topping`, `create_special`, `update_special`, `remove_special`, `update_hours`, `add_closure`, `remove_closure`, `get_current_menu`, `get_current_hours`.
- Each response returns mutation results so the UI can live-update.

---

## Frontend Pages

### Customer Side
1. **Home / Menu** — Hero section, menu categories, pizza cards with prices.
2. **Pizza Customizer** — Select size, toppings, see live price.
3. **Cart / Order Summary** — Review items, see total, place order.
4. **Chat Panel** — Slide-out or sidebar chat for conversational ordering. Order state syncs with cart.
5. **Order Confirmation** — Simple "your order has been placed" screen.

### Admin Side (`/admin`)
1. **Dashboard** — Overview of menu items, specials, hours.
2. **Chat Panel** — Full-screen chat with live preview of changes.
3. **Menu Editor** — Table/card view of menu items (also updated by chat).
4. **Specials Manager** — Create/edit daily specials.
5. **Hours Manager** — Set operating hours and closures.

---

## Docker Architecture

```
docker-compose.yml
├── backend   (Python FastAPI, port 8000)
│   └── Dockerfile
└── frontend  (Node build → nginx, port 3000)
    └── Dockerfile (multi-stage: build + nginx serve)
```

- SQLite database stored in a Docker volume for persistence.
- Environment variable `ANTHROPIC_API_KEY` required for LLM features.
- Health checks on both services.

---

## Seed Data

The database will be seeded on first run with:
- **Pizzas**: Margherita, Pepperoni, BBQ Chicken, Veggie Supreme, Hawaiian, Meat Lover's, Buffalo Chicken, Four Cheese
- **Sizes**: Small (0.8x), Medium (1.0x), Large (1.3x), XL (1.6x)
- **Toppings**: ~15 options across meat/veggie/cheese categories
- **Sides**: Garlic Bread, Wings, Caesar Salad, Mozzarella Sticks
- **Drinks**: Soda, Iced Tea, Lemonade, Water
- **Operating Hours**: 11 AM–10 PM daily, closed Sundays
- **Sample Special**: "Margherita Monday" — 20% off Margherita on Mondays
