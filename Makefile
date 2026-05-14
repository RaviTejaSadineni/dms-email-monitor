.PHONY: backend frontend test

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev -- --host 0.0.0.0 --port 5173

test:
	cd backend && pytest
