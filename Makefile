.PHONY: setup dev api web worker seed lint api-test web-typecheck

setup:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r apps/api/requirements.txt -r apps/api/requirements-dev.txt && pip install -r apps/worker/requirements.txt
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
	cd apps/api && python3 -m app.db.seed

lint:
	cd apps/web && npm run lint

api-test:
	cd apps/api && python3 -m pytest tests -q

web-typecheck:
	cd apps/web && npm run typecheck
