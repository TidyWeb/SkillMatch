"""Gunicorn entry point: `gunicorn wsgi:app`."""

from skillmatch.web import create_app

app = create_app()
