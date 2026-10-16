.PHONY: help build up down restart logs dev build-staging start-staging stop-staging build-production start-production stop-production

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

##### Default / Local Deployment (.env) #####
build: ## Build the docker image using .env
	docker compose --env-file .env build

up: ## Start the container in detached mode
	docker compose --env-file .env up -d

down: ## Stop the container
	docker compose --env-file .env down

restart: ## Restart the container
	docker compose --env-file .env restart

logs: ## Follow container logs
	docker compose --env-file .env logs -f

dev: ## Start container with code mount and hot-reloading for local dev
	docker compose --env-file .env -f docker-compose.yml -f docker-compose.dev.yml up --build

##### Staging Deployment (.env.staging) #####
build-staging: ## Build the staging docker image without cache
	docker compose --env-file .env.staging -f docker-compose.yml build --no-cache

start-staging: ## Start the staging container in detached mode
	docker compose --env-file .env.staging -f docker-compose.yml up -d

stop-staging: ## Stop the staging container
	docker compose --env-file .env.staging -f docker-compose.yml down

##### Production Deployment (.env.production) #####
build-production: ## Build the production docker image
	docker compose --env-file .env.production -f docker-compose.yml build

start-production: ## Start the production container in detached mode
	docker compose --env-file .env.production -f docker-compose.yml up -d

stop-production: ## Stop the production container
	docker compose --env-file .env.production -f docker-compose.yml down