##### production ######
.PHONY: build-staging
build-staging: ## Build the development docker image.
	docker compose --env-file .env.staging  -f docker-compose.yml build --no-cache

#.PHONY: start-staging
#start-staging: ## Start the development docker container.
#	docker compose --env-file ./.env.staging  -f docker-compose.yml up -d

.PHONY: start-staging
start-staging: ## Copy the files to the static site deployment location.
		docker compose --env-file .env.staging  -f docker-compose.yml up -d;
		
		

.PHONY: stop-staging
stop-staging: ## Stop the development docker container.
	docker compose --env-file .env.staging  -f docker-compose.yml down


	##### production ######
.PHONY: build-production
build-production: ## Build the development docker image.
	docker compose --env-file .env.production  -f docker-compose.yml build

.PHONY: start-production
start-production: ## Start the development docker container.

		docker compose --env-file .env.production  -f docker-compose.yml up -d;
.PHONY: stop-production
stop-production: ## Stop the development docker container.
	docker compose --env-file .env.production  -f docker-compose.yml down