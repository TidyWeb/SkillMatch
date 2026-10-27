# SkillMatch. Local path needing no keys: make install && make fixtures && make test && make run
.PHONY: install fixtures etl-live export-snapshot test lint run docker-build docker-run

PORT ?= 8080
IMAGE ?= skillmatch
# Podman works too: make docker-build DOCKER=podman
DOCKER ?= docker

install:
	uv sync

fixtures:
	uv run python -m skillmatch.etl --mode fixtures

etl-live:
	uv run python -m skillmatch.etl --mode live $(if $(RECOVER_RUN),--recover-run $(RECOVER_RUN),)

export-snapshot:
	@test -n "$(TARGET)"
	uv run python -m skillmatch.etl.export --target "$(TARGET)"

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

run:
	uv run flask --app skillmatch.web:create_app run --port 5000

docker-build:
	@db=$$(find data/processed -maxdepth 1 -type f -name 'skillmatch_live_*.db' -printf '%f\n' | sort | tail -n 1); \
	 test -n "$$db" || { echo "No dated live database found; run make etl-live first."; exit 1; }; \
	 $(DOCKER) build --build-arg SKILLMATCH_DATABASE="data/processed/$$db" -t $(IMAGE) .

docker-run:
	$(DOCKER) run --rm -p $(PORT):8080 -e PORT=8080 $(IMAGE)
