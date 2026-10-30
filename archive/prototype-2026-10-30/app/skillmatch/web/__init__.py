"""Flask application factory."""

from flask import Flask

from skillmatch import config


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(DB_PATH=None, TAILOR_PAGE_URL=config.TAILOR_PAGE_URL)
    if test_config:
        app.config.update(test_config)

    from skillmatch.web.format import FILTERS
    from skillmatch.web.routes import bp

    app.jinja_env.filters.update(FILTERS)
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024  # a profile is a few KB
    app.register_blueprint(bp)
    return app
