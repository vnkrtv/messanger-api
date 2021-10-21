# Export application env vars
include deploy/.env.test
export

PROJECT_NAME := yandex-messager
PROJECT_SRC := messenger
VERSION := 0.1

IMAGE_NAME := app-messenger
CONTAINER_NAME := $(PROJECT_NAME)

DOCKER := env docker
PYTHON := env python

DB_CONTAINER_NAME := pg
RMQ_CONTAINER_NAME := rmq
REDIS_CONTAINER_NAME := redis

TASK_CONSUMER_SRC := services/task_consumer
TASK_CONSUMER_IMAGE_NAME := task-consumer
TASK_CONSUMER_CONTAINER_NAME := task-consumer

help:
	@echo "Run:"
	@echo "make run-dev                    - Run app"
	@echo
	@echo "Code linting:"
	@echo "make lint                       - Run pylint and flake8 for checking code style"
	@echo
	@echo "Tests:"
	@echo "make test                       - Run tests with coverage"
	@echo "make tests-coverage-report      - Print coverage report"
	@echo "make tests-html-coverage-report - Generate html coverage report"
	@echo
	@echo "Config:"
	@echo "make show-config                - Show project envs"
	@echo "make configure                  - Edit project envs"
	@echo
	@echo "Docker:"
	@echo "make docker-build               - Build a docker image"
	@echo "make docker-run                 - Run docker image"
	@exit 0


run-dev:
	$(PYTHON) -m gunicorn -k aiohttp.GunicornWebWorker $(PROJECT_SRC).app:app


show-config:
	cat deploy/.env

show-prod-config:
	cat deploy/.env.prod

configure:
	./deploy/edit_envs


pylint:
	$(PYTHON) -m pylint $(PROJECT_SRC)

flake8:
	$(PYTHON) -m flake8 $(PROJECT_SRC)

lint: pylint flake8

cs:
	$(PYTHON) -m black $(PROJECT_SRC)


docker-build:
	sudo $(DOCKER) build -t $(IMAGE_NAME):$(VERSION) .

docker-run: docker-build
	sudo $(DOCKER) rm -f $(CONTAINER_NAME)
	sudo $(DOCKER) run --name $(CONTAINER_NAME) -p 0.0.0.0:8080:$(PORT) -d --env-file=deploy/.env $(IMAGE_NAME):$(VERSION)


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
	sudo $(DOCKER) start $(DB_CONTAINER_NAME)

create-test-db:
	sudo $(DOCKER) exec -i $(DB_CONTAINER_NAME) psql -U $(TEST_POSTGRES_USER) -c "CREATE DATABASE $(TEST_POSTGRES_DB)"

drop-test-db:
	sudo $(DOCKER) exec -i $(DB_CONTAINER_NAME) psql -U $(TEST_POSTGRES_USER) -c "DROP DATABASE $(TEST_POSTGRES_DB)"


tests-coverage-report:
	$(PYTHON) -m coverage report

tests-html-coverage-report:
	$(PYTHON) -m coverage html
	@echo "\nHTML coverage report:"
	@echo "htmlcov/index.html"

run-tests:
	$(PYTHON) -m pytest -vv --cov=$(PROJECT_SRC) --cov-report=term-missing tests 2> /dev/null

test: start-db start-rmq start-redis create-test-db run-tests drop-test-db


migrate:
	$(PYTHON) -m alembic upgrade head
