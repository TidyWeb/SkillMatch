# SkillMatch: small image, fast cold start on Cloud Run.
# The SQLite database is built before `docker build` (make docker-build does this) and baked in
# read-only. No database server, no user storage.

# ---- build stage: resolve and install dependencies with uv from the lock file ----
FROM python:3.12-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.12.3 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-default-groups --no-install-project
COPY skillmatch ./skillmatch
RUN uv sync --frozen --no-default-groups --no-editable

# ---- runtime stage: just Python, the virtualenv, the app and its data ----
FROM python:3.12-slim
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    SKILLMATCH_ROOT=/app
WORKDIR /app
RUN useradd --create-home --uid 10001 app
COPY --from=build /app/.venv /app/.venv
COPY wsgi.py ./
COPY data/taxonomy ./data/taxonomy
COPY data/personas.yaml data/town_coords.csv data/outcode_coords.csv data/discovery_links.csv \
     data/title_rules.csv data/search_terms.csv data/employer_boards.csv ./data/
COPY data/processed/skillmatch.db ./data/processed/skillmatch.db
USER app
EXPOSE 8080
# One worker with threads keeps memory low and cold starts quick; --preload loads the taxonomy once.
CMD exec gunicorn wsgi:app --bind 0.0.0.0:${PORT} --workers 1 --threads 8 --timeout 60 --preload --access-logfile -
