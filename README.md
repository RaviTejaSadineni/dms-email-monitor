# Legal Contract Intelligence Platform

A full-stack React + FastAPI workspace for importing Gmail Takeout `.mbox` data, classifying contract-related emails with Azure OpenAI-ready services, tracking the end-to-end legal review lifecycle, and visualizing bottlenecks, SLA risk, and attachment insights.

## Included capabilities
- JWT bearer authentication with JSON request bodies
- Async SQLAlchemy models for users, emails, threads, contracts, attachments, import jobs, and audit data
- Streaming-style Gmail Takeout mbox parsing with attachment extraction and deduplication by `message-id`
- Contract lifecycle analytics endpoints for dashboards, pipeline metrics, response-time trends, and AI insight cards
- React + Material UI + Tailwind executive dashboard with lifecycle, email, import, contract, attachment, insight, and feature-catalog views
- Focused backend tests for auth, import, email analytics, contracts, and classification heuristics

## Quick start
1. Copy `.env.example` to `.env` and fill in the real `SECRET_KEY` and Azure OpenAI API key.
2. Start infrastructure with `docker-compose up --build`.
3. Backend API: `http://localhost:8000/docs`
4. Frontend dashboard: `http://localhost:5173`

## Local development
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Tests
```bash
cd backend
pytest
```
