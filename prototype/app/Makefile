# SkillMatch. Local path needing no keys: make install && make fixtures && make test && make run
.PHONY: install fixtures etl-live test lint run docker-build docker-run

PORT ?= 8080
IMAGE ?= skillmatch
# Podman works too: make docker-build DOCKER=podman
DOCKER ?= docker

install:
	uv sync

fixtures:
	uv run python -m skillmatch.etl --mode fixtures

etl-live:
	uv run python -m skillmatch.etl --mode live

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

run:
	uv run flask --app skillmatch.web:create_app run --port 5000

docker-build:
	@test -f data/processed/skillmatch.db || $(MAKE) $$(grep -qs '^REED_API_KEY=.' .env && echo etl-live || echo fixtures)
	$(DOCKER) build -t $(IMAGE) .

docker-run:
	$(DOCKER) run --rm -p $(PORT):8080 -e PORT=8080 $(IMAGE)
