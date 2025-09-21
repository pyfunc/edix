.PHONY: help test test-all test-watch test-spec test-debug test-coverage test-ui test-api test-e2e test-verbose test-retry test-report test-fix up down build logs restart clean dev logs-api logs-backend logs-frontend stop install install-frontend install-backend install-api

# Default target
help:
	@echo "Available commands:"
	@echo "  make test           - Run all tests (headless, will fail on error)"
	@echo "  make test-all       - Run all tests and continue on error"
	@echo "  make test-watch     - Open Cypress test runner"
	@echo "  make test-spec      - Run specific test (spec=path/to/test.cy.js)"
	@echo "  make test-debug     - Run tests with debug output"
	@echo "  make test-coverage  - Generate test coverage report"
	@echo "  make test-ui        - Run only UI tests"
	@echo "  make test-api       - Run only API tests"
	@echo "  make test-e2e       - Run only E2E tests"
	@echo "  make test-verbose   - Run tests with verbose output"
	@echo "  make test-retry     - Retry failed tests up to 3 times"
	@echo "  make test-report    - Generate HTML test report"
	@echo "  make test-fix       - Try to automatically fix test issues"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make build          - Build all services"
	@echo "  make logs           - Show logs for all services"
	@echo "  make restart        - Restart all services"
	@echo "  make clean          - Remove all containers, volumes, and images"
	@echo "  make dev            - Start development environment"
	@echo "  make install        - Install all dependencies"
	@echo "  make help           - Show this help"

# Docker commands
up:
	docker compose up --build

down:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

restart: down up

# Test commands
test:
	@echo "🚀 Running backend tests with pytest..."
	python -m pytest edix/tests/ -v
	@echo "🚀 Running frontend tests with jest..."
	cd frontend_src && npm test

test-all:
	@echo "🏃 Running all tests (continue on error)..."
	@if ! curl -s http://localhost:3004 >/dev/null; then \
		echo "⚠️  Starting test server..."; \
		make up; \
		sleep 10; \
	fi
	npx cypress run --headless --browser chrome --no-exit

test-watch:
	@echo "👀 Opening Cypress test runner..."
	npx cypress open

test-spec:
	@if [ -z "$(spec)" ]; then \
		echo "❌ Error: Please specify test file with spec=path/to/test.cy.js"; \
		exit 1; \
	fi
	@echo "🔍 Running specific test: $(spec)"
	npx cypress run --headless --browser chrome --spec "$(spec)"

test-debug:
	@echo "🐛 Running tests with debug information..."
	DEBUG=cypress:* npx cypress run --headless --browser chrome

test-coverage:
	@echo "📊 Generating test coverage report..."
	npx cypress run --headless --browser chrome --env coverage=true

test-ui:
	@echo "🎨 Running UI tests..."
	npx cypress run --headless --browser chrome --spec "cypress/e2e/**/ui-*.cy.js"

test-api:
	@echo "🔌 Running API tests..."
	npx cypress run --headless --browser chrome --spec "cypress/e2e/**/api-*.cy.js"

test-e2e:
	@echo "🏃 Running end-to-end tests..."
	npx cypress run --headless --browser chrome --spec "cypress/e2e/**/e2e-*.cy.js"

test-verbose:
	@echo "🔊 Running tests with verbose output..."
	npx cypress run --headless --browser chrome --browser-args="--log-level=DEBUG"

test-retry:
	@echo "🔄 Retrying failed tests (max 3 attempts)..."
	@n=0; until [ "$$n" -ge 3 ]; do \
		echo "Attempt $$((n+1))/3..."; \
		if npx cypress run --headless --browser chrome; then \
			exit 0; \
		fi; \
		n=$$((n+1)); \
		echo "Retrying..."; \
		sleep 2; \
	done; \
	echo "❌ All attempts failed"; \
	exit 1

test-report:
	@echo "📄 Generating HTML test report..."
	@if ! command -v mochawesome-merge >/dev/null 2>&1; then \
		echo "Installing mochawesome-merge..."; \
		npm install -g mochawesome-merge mochawesome-report-generator; \
	fi
	@rm -rf cypress/results cypress/reports || true
	@mkdir -p cypress/results cypress/reports
	npx cypress run --headless --browser chrome --reporter mochawesome --reporter-options "reportDir=cypress/results,overwrite=false,html=false,json=true"
	npx mochawesome-merge "cypress/results/*.json" > cypress/reports/mochawesome.json
	npx marge cypress/reports/mochawesome.json -f cypress-test-report -o cypress/reports
	@echo "✅ Report generated at: cypress/reports/cypress-test-report.html"

test-fix:
	@echo "🔧 Attempting to fix test issues..."
	@echo "1. Cleaning up test environment..."
	@make clean
	@echo "2. Reinstalling dependencies..."
	@rm -rf node_modules
	@npm install
	@echo "3. Starting services..."
	@make up
	@echo "4. Waiting for services to be ready..."
	@sleep 10
	@echo "✅ Fix attempt complete. Try running tests again."

# Logs
logs-api:
	docker-compose logs -f api

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

# Cleanup
clean:
	docker-compose down --volumes --rmi all

stop: down

# Installation
install:
	make install-frontend
	make install-backend
	make install-api

install-frontend:
	cd frontend && npm install

install-backend:
	cd backend-node && npm install

install-api:
	cd api-python && pip install -r requirements.txt



# ==============================================================================
# PUBLISHING
# ==============================================================================
publish: ## Publish project to PyPI
	@bash scripts/publish.sh
