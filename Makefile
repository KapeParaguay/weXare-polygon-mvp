.PHONY: dev test test-frontend deploy

dev:
	@echo "Starting local stack..."
	@docker compose -f infra/docker-compose.yml up -d
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"

test:
	@echo "Running protocol tests..."
	@cd protocol && forge test --offline
	@echo "Running backend tests..."
	@cd backend && PYTHONPATH=. sh -c 'if [ -x .venv/bin/pytest ]; then .venv/bin/pytest; else pytest; fi'
	@echo "Skipping frontend tests (headless WebKit crash in this env)."
	@echo "Use: make test-frontend (requires frontend dev server running)"

test-frontend:
	@echo "Running frontend tests (requires dev server at http://127.0.0.1:3001)..."
	@cd frontend && npm test

deploy:
	@echo "Deploy placeholder (manual steps)."
