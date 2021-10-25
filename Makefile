# Export application env vars
include deploy/.env.test
export

PROJECT_NAME := yandex-messager
PROJECT_SRC := messenger
VERSION := 0.1

IMAGE_NAME := app-messenger
CONTAINER_NAME := $(PROJECT_NAME)

DOCKER := env docker
PYTHON := env python3
COMPOSE := env docker-compose

DB_CONTAINER_NAME := pg
RMQ_CONTAINER_NAME := rmq
REDIS_CONTAINER_NAME := redis

TASK_CONSUMER_SRC := services/task_consumer
TASK_CONSUMER_IMAGE_NAME := task-consumer
TASK_CONSUMER_CONTAINER_NAME := task-consumer

help:
	@echo "Run:"
	@echo "make run-dev                    - Run app in dev mode"
	@echo "make run-prod                   - Run app in prod mode"
	@echo "make venv                       - Create python venv"
	@echo
	@echo "Code style:"
	@echo "make lint                       - Run pylint and flake8 for checking code style"
	@echo "make cs                         - Fix code style with black"
	@echo
	@echo "Tests:"
	@echo "make test                       - Run tests with coverage"
	@echo "make tests-coverage-report      - Run tests and print coverage report"
	@echo "make tests-html-coverage-report - Run tests and show html coverage report"
	@echo
	@echo "Config:"
	@echo "make show-config                - Show project env vars"
	@echo "make show-prod-config           - Show project prod env vars"
	@echo
	@echo "Docker:"
	@echo "make docker-build               - Build app with docker-compose"
	@echo "make docker-run                 - Run app with docker-compose"
	@echo "make docker-start               - Start stopped app with docker-compose"
	@echo "make docker-stop                - Stop docker-compose with app"
	@exit 0


run-dev: start-db start-rmq start-redis
	$(PYTHON) -m gunicorn -k aiohttp.GunicornWebWorker $(PROJECT_SRC).app:app

run-prod: docker-run

venv:
	$(PYTHON) -m venv venv
	$(PYTHON) -m pip install -r requirements.dev.txt


show-config:
	cat deploy/.env

show-prod-config:
	cat deploy/.env.prod


pylint:
	$(PYTHON) -m pylint $(PROJECT_SRC)

flake8:
	$(PYTHON) -m flake8 $(PROJECT_SRC)

lint: pylint flake8


cs:
	$(PYTHON) -m black $(PROJECT_SRC)


docker-build:
	sudo $(COMPOSE) build

docker-run: docker-build
	sudo $(COMPOSE) down
	sudo $(COMPOSE) up -d

docker-stop:
	sudo $(COMPOSE) stop

docker-start:
	sudo $(COMPOSE) start || sudo $(COMPOSE) up -d


start-rmq:
	sudo $(DOCKER) start $(RMQ_CONTAINER_NAME)

start-redis:
	sudo $(DOCKER) start $(REDIS_CONTAINER_NAME)


docker-build-task-consumer:
	sudo $(DOCKER) build -t $(TASK_CONSUMER_IMAGE_NAME) $(TASK_CONSUMER_SRC)

docker-run-task-consumer: docker-build-task-consumer
	sudo $(DOCKER) run -d --name $(TASK_CONSUMER_CONTAINER_NAME) $(TASK_CONSUMER_IMAGE_NAME)

start-task-consumer:
	sudo $(DOCKER) start $(TASK_CONSUMER_CONTAINER_NAME)

stop-task-consumer:
	sudo $(DOCKER) stop $(TASK_CONSUMER_CONTAINER_NAME)


start-db:
	sudo $(DOCKER) start $(DB_CONTAINER_NAME) || sudo $(DOCKER) run --name $(DB_CONTAINER_NAME) -e POSTGRES_USER=$(POSTGRES_USER) -e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) -e POSTGRES_DB=$(POSTGRES_DB) postgres:13.0

create-test-db:
	sudo $(DOCKER) exec -i $(DB_CONTAINER_NAME) psql -U $(TEST_POSTGRES_USER) -c "CREATE DATABASE $(TEST_POSTGRES_DB)"

drop-test-db:
	sudo $(DOCKER) exec -i $(DB_CONTAINER_NAME) psql -U $(TEST_POSTGRES_USER) -c "DROP DATABASE $(TEST_POSTGRES_DB)"


tests-coverage-report: test
	$(PYTHON) -m coverage report

tests-html-coverage-report: test
	$(PYTHON) -m coverage html
	$(PYTHON) -m webbrowser htmlcov/index.html

run-tests:
	$(PYTHON) -m pytest -vv --cov=$(PROJECT_SRC) --cov-report=term-missing tests 2> /dev/null

test: start-db start-rmq start-redis create-test-db run-tests drop-test-db


migrate:
	$(PYTHON) -m alembic upgrade head
