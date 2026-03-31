"""
Browser auth routes — HTML form login/register/logout.
"""
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from utils.logger import get_logger
from utils.templating import templates
from utils.validators import ValidationError

logger = get_logger(__name__)
router = APIRouter(tags=["Auth (Browser)"])


@router.get("/register", response_class=HTMLResponse, name="auth_routes.register")
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")


@router.post("/register", response_class=HTMLResponse)
def register_submit(
    request: Request,
    username: str = Form(""),
    password: str = Form(""),
    confirm_password: str = Form(""),
    email: str = Form(""),
):
    auth_svc = request.app.state.auth_service
    try:
        auth_svc.register_user(username, password, confirm_password, email or None)
        return RedirectResponse("/login?registered=true", status_code=303)
    except ValidationError as e:
        return templates.TemplateResponse(request, "register.html", {"error": str(e)})
    except Exception:
        return templates.TemplateResponse(request, "register.html", {"error": "Failed to create account. Please try again."})


@router.get("/login", response_class=HTMLResponse, name="auth_routes.login")
def login_page(request: Request, registered: str = None):
    return templates.TemplateResponse(request, "login.html", {"registered": registered})


@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    username: str = Form(""),
    password: str = Form(""),
):
    if not username or not password:
        return templates.TemplateResponse(request, "login.html", {"error": "Username and password are required"})

    auth_svc = request.app.state.auth_service
    user = auth_svc.authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse(request, "login.html", {"error": "Invalid username or password"})

    request.session.clear()
    request.session["logged_in"] = True
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    return RedirectResponse("/dashboard", status_code=303)


@router.get("/logout", name="auth_routes.logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)
