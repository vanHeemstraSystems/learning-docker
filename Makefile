.PHONY: help build up down restart logs clean test shell db-shell redis-shell health init

# Colors for output

BLUE := \033[0;34m
GREEN := \033[0;32m
NC := \033[0m # No Color

help: ## Show this help message
@echo “$(BLUE)Learning Docker - Available Commands$(NC)”
@echo “”
@grep -E ‘^[a-zA-Z_-]+:.*?## .*$$’ $(MAKEFILE_LIST) | sort | awk ‘BEGIN {FS = “:.*?## “}; {printf “  $(GREEN)%-15s$(NC) %s\n”, $$1, $$2}’

init: ## Initialize project with secure passwords and start services
@chmod +x scripts/init.sh
@./scripts/init.sh

build: ## Build all Docker images
@echo “$(BLUE)Building Docker images…$(NC)”
@docker-compose build

up: ## Start all services in detached mode
@echo “$(BLUE)Starting services…$(NC)”
@docker-compose up -d
@echo “$(GREEN)Services started! Check status with: make logs$(NC)”

down: ## Stop all services
@echo “$(BLUE)Stopping services…$(NC)”
@docker-compose down

down-v: ## Stop all services and remove volumes (WARNING: deletes data)
@echo “$(BLUE)Stopping services and removing volumes…$(NC)”
@docker-compose down -v

restart: down up ## Restart all services

logs: ## Show logs from all services (Ctrl+C to exit)
@docker-compose logs -f

logs-backend: ## Show logs from backend service only
@docker-compose logs -f backend

logs-nginx: ## Show logs from nginx service only
@docker-compose logs -f nginx

ps: ## Show running containers
@docker-compose ps

shell: ## Open shell in backend container
@docker-compose exec backend sh

db-shell: ## Open PostgreSQL shell
@docker-compose exec postgres psql -U dbuser -d taskdb

redis-shell: ## Open Redis CLI
@docker-compose exec redis redis-cli -a $$(grep REDIS_PASSWORD .env | cut -d ‘=’ -f2)

health: ## Check health of all services
@echo “$(BLUE)Checking service health…$(NC)”
@curl -s http://localhost/api/health | python3 -m json.tool || echo “$(RED)Services not responding$(NC)”

test: ## Run a quick test of the API
@echo “$(BLUE)Testing API endpoints…$(NC)”
@echo “\n$(GREEN)1. Health Check:$(NC)”
@curl -s http://localhost/api/health | python3 -m json.tool
@echo “\n$(GREEN)2. Get all tasks:$(NC)”
@curl -s http://localhost/api/tasks | python3 -m json.tool
@echo “\n$(GREEN)3. Create a task:$(NC)”
@curl -s -X POST http://localhost/api/tasks   
-H “Content-Type: application/json”   
-d ‘{“title”:“Test Docker”,“description”:“Testing the API”}’ | python3 -m json.tool

stats: ## Show resource usage statistics
@docker stats –no-stream

clean: ## Remove all containers, images, and volumes (WARNING: deletes everything)
@echo “$(BLUE)Cleaning up Docker resources…$(NC)”
@docker-compose down -v –rmi all
@echo “$(GREEN)Cleanup complete!$(NC)”

rebuild: clean build up ## Clean, rebuild, and start services

scan: ## Scan images for vulnerabilities (requires Docker scan)
@echo “$(BLUE)Scanning backend image…$(NC)”
@docker scan learning-docker-backend || echo “Docker scan not available”

inspect-network: ## Inspect Docker networks
@docker network ls
@echo “\n$(BLUE)Backend Network:$(NC)”
@docker network inspect learning-docker_backend-network
@echo “\n$(BLUE)Frontend Network:$(NC)”
@docker network inspect learning-docker_frontend-network

inspect-volumes: ## Inspect Docker volumes
@docker volume ls
@echo “\n$(BLUE)Postgres Volume:$(NC)”
@docker volume inspect learning-docker_postgres-data
