# Pizza Demo — CLAUDE.md

## Project Overview
Online pizza ordering demo with LLM-powered chatbots for both customer ordering and admin menu management. See SPEC.md for full specification.

## Architecture
- **Backend**: Python 3.12 / FastAPI / SQLAlchemy / SQLite — in `backend/`
- **Frontend**: React 18 / TypeScript / Vite / Tailwind CSS — in `frontend/`
- **LLM**: Anthropic Claude API with tool-calling for both chatbots
- **Deployment**: Docker Compose with two services (backend + frontend/nginx)

## Common Commands

### Development
```bash
# Start everything
docker compose up --build

# Backend only (local dev)
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload

# Frontend only (local dev)
cd frontend && npm install && npm run dev
```

### Testing
```bash
cd backend && python -m pytest
cd frontend && npm test
```

## Key Directories
```
backend/
  app/
    main.py          — FastAPI app entry, CORS, lifespan
    models.py        — SQLAlchemy models
    database.py      — DB engine, session, init
    seed.py          — Seed data for first run
    routers/
      menu.py        — Menu/hours endpoints
      orders.py      — Order CRUD endpoints
      admin.py       — Admin management endpoints
      chat.py        — Chat endpoints (customer + admin)
    chat/
      customer.py    — Customer chatbot (system prompt + tools)
      admin.py       — Admin chatbot (system prompt + tools)
frontend/
  src/
    pages/           — Route-level page components
    components/      — Reusable UI components
    api/             — API client functions
    store/           — State management (Zustand)
    types/           — TypeScript interfaces
```

## Environment Variables
- `ANTHROPIC_API_KEY` — Required for chatbot features. Set in `.env` at project root.
- `DATABASE_URL` — Defaults to `sqlite:///./pizza.db`

## Conventions
- Backend uses async FastAPI endpoints
- Frontend uses Zustand for state management
- Chat endpoints use streaming responses for real-time feel
- All prices in USD, stored as floats
- SQLite DB is seeded on first run if empty
