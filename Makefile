.PHONY: dev test deploy

dev:
	@echo "Starting local stack..."
	@docker compose -f infra/docker-compose.yml up -d
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"

test:
	@echo "Running protocol tests..."
	@cd protocol && forge test
	@echo "Running backend tests..."
	@cd backend && pytest
	@echo "Running frontend tests..."
	@cd frontend && npm test

deploy:
	@echo "Deploy placeholder (manual steps)."
