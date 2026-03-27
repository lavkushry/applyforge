.PHONY: setup dev api web worker seed lint

setup:
	python -m venv .venv && . .venv/bin/activate && pip install -r apps/api/requirements.txt && pip install -r apps/worker/requirements.txt
	cd apps/web && npm install

dev:
	@echo "Run services in separate terminals:"
	@echo "1) cd apps/api && uvicorn app.main:app --reload --port 8000"
	@echo "2) cd apps/worker && celery -A app.celery_app worker --loglevel=info"
	@echo "3) cd apps/web && npm run dev"

api:
	cd apps/api && uvicorn app.main:app --reload --port 8000

web:
	cd apps/web && npm run dev

worker:
	cd apps/worker && celery -A app.celery_app worker --loglevel=info

seed:
	cd apps/api && python -m app.db.seed

lint:
	cd apps/web && npm run lint
