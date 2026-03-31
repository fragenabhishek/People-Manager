"""
Shared Jinja2 templates instance and url_for helper.
"""
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


def configure_url_for(app):
    """Register a Flask-compatible url_for as a Jinja2 global."""

    def url_for(name: str, **kwargs):
        if name == "static":
            path = kwargs.get("filename") or kwargs.get("path", "")
            return f"/static/{path}"
        try:
            return app.url_path_for(name, **kwargs)
        except Exception:
            return f"/{name}"

    templates.env.globals["url_for"] = url_for
