# 🍕 Slice of Heaven — Pizza Ordering Demo

A full-stack pizza restaurant ordering website with LLM-powered chatbots for both customer ordering and admin menu management.

## Features

- **Online Menu** — Browse pizzas, sides, drinks, and desserts with live pricing
- **Pizza Customizer** — Choose size, add extra toppings, adjust quantity
- **Shopping Cart** — Add/remove items, see running total, place order
- **Customer Chatbot** — Order pizzas conversationally ("I'd like a large pepperoni with extra cheese")
- **Admin Dashboard** — Manage menu, toppings, specials, and hours via AI chat
- **Live Updates** — Admin chat mutations are immediately reflected in the UI

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- An [Anthropic API key](https://console.anthropic.com/)

## Quick Start

1. **Clone and configure:**
   ```bash
   cd pizza-demo
   cp .env.example .env
   ```

2. **Add your API key** — edit `.env` and set:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

3. **Build and run:**
   ```bash
   docker compose up --build
   ```

4. **Open in browser:**
   - Customer site: [http://localhost:3000](http://localhost:3000)
   - Admin dashboard: [http://localhost:3000/admin](http://localhost:3000/admin)
   - Backend API: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)

## Local Development (without Docker)

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` requests to `http://localhost:8000`.

## Project Structure

```
├── docker-compose.yml          # Orchestrates backend + frontend
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI app, CORS, lifespan
│       ├── models.py           # SQLAlchemy models
│       ├── database.py         # DB engine + session
│       ├── seed.py             # Initial menu data
│       ├── routers/            # API endpoints (menu, orders, admin, chat)
│       └── chat/
│           ├── customer.py     # Customer ordering chatbot
│           └── admin.py        # Admin management chatbot
└── frontend/
    ├── Dockerfile              # Multi-stage: Node build → nginx
    ├── nginx.conf              # SPA routing + API proxy
    └── src/
        ├── pages/              # MenuPage, AdminPage, OrderConfirmation
        ├── components/         # Reusable UI components
        ├── api/                # REST API client
        ├── store/              # Zustand state management
        └── types/              # TypeScript interfaces
```

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | React 18, TypeScript, Vite, Tailwind CSS |
| State      | Zustand                             |
| Backend    | Python, FastAPI, SQLAlchemy          |
| Database   | SQLite                              |
| LLM        | Anthropic Claude (claude-sonnet-4-5) |
| Deploy     | Docker Compose, nginx               |

## Notes

- This is a **demo application** — order placement and payment are simulated.
- The database is seeded automatically on first run with sample pizzas, toppings, sizes, hours, and a sample daily special.
- SQLite data persists in a Docker volume (`db-data`). To reset, run `docker compose down -v`.
- Both chatbots use restrictive system prompts to stay on-topic.
