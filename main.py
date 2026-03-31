"""
People Manager — FastAPI application.
Replaces Flask app.py as the primary entry point.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from config import Config
from repositories.note_repository import NoteRepository
from repositories.person_repository import PersonRepository
from repositories.user_repository import UserRepository
from routers import ai, api_auth, auth, notes, people
from services.ai_service import AIService
from services.auth_service import AuthService
from services.import_export_service import ImportExportService
from services.note_service import NoteService
from services.person_service import PersonService
from services.token_service import TokenService
from utils.hashing import PasswordHasher
from utils.logger import setup_logger
from utils.templating import configure_url_for, templates
from utils.validators import ValidationError

logger = setup_logger("people_manager")


def _init_repositories():
    if Config.USE_SQL:
        from models.database import create_tables, get_session_factory, init_db
        from repositories.sql_note_repository import SqlNoteRepository
        from repositories.sql_person_repository import SqlPersonRepository
        from repositories.sql_user_repository import SqlUserRepository

        init_db(Config.DATABASE_URL, echo=Config.DEBUG)
        create_tables()
        sf = get_session_factory()
        return SqlPersonRepository(sf), SqlUserRepository(sf), SqlNoteRepository(sf)

    if Config.USE_MONGODB:
        from pymongo import MongoClient

        client = MongoClient(Config.MONGO_URI)
        db = client[Config.DB_NAME]
        return (
            PersonRepository(people_collection=db[Config.PEOPLE_COLLECTION]),
            UserRepository(users_collection=db[Config.USERS_COLLECTION]),
            NoteRepository(notes_collection=db[Config.NOTES_COLLECTION]),
        )

    return (
        PersonRepository(data_file=Config.DATA_FILE),
        UserRepository(data_file=Config.USERS_FILE),
        NoteRepository(data_file=Config.NOTES_FILE),
    )


def create_app() -> FastAPI:
    Config.validate()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Application initialized successfully")
        yield

    app = FastAPI(
        title="People Manager",
        description="AI-powered relationship management",
        version="2.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(SessionMiddleware, secret_key=Config.SECRET_KEY)

    people_repo, user_repo, note_repo = _init_repositories()

    hasher = PasswordHasher()
    app.state.token_service = TokenService(
        Config.SECRET_KEY,
        access_ttl_minutes=Config.JWT_ACCESS_TOKEN_MINUTES,
        refresh_ttl_minutes=Config.JWT_REFRESH_TOKEN_MINUTES,
    )
    app.state.auth_service = AuthService(user_repo, hasher)
    app.state.person_service = PersonService(people_repo, note_repo)
    app.state.ai_service = AIService()
    app.state.note_service = NoteService(note_repo, people_repo)
    app.state.import_export_service = ImportExportService(people_repo)
    app.state.testing = False

    app.include_router(auth.router)
    app.include_router(api_auth.router)
    app.include_router(people.router)
    app.include_router(notes.router)
    app.include_router(ai.router)

    app.mount("/static", StaticFiles(directory="static"), name="static")

    _register_error_handlers(app)
    _register_security_headers(app)
    configure_url_for(app)
    _register_main_routes(app)

    return app


def _register_error_handlers(app: FastAPI):

    @app.exception_handler(ValidationError)
    async def handle_validation(request: Request, exc: ValidationError):
        return JSONResponse(
            {"success": False, "error": str(exc), "error_code": "VALIDATION_ERROR"},
            status_code=400,
        )

    @app.exception_handler(ValueError)
    async def handle_value(request: Request, exc: ValueError):
        return JSONResponse(
            {"success": False, "error": str(exc), "error_code": "VALIDATION_ERROR"},
            status_code=400,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception):
        logger.exception("Unhandled exception")
        return JSONResponse(
            {"success": False, "error": "Internal server error", "error_code": "SERVER_ERROR"},
            status_code=500,
        )


def _register_security_headers(app: FastAPI):

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if not Config.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )
        response.headers["Content-Security-Policy"] = csp
        return response


def _register_main_routes(app: FastAPI):

    @app.get("/health")
    def health():
        if Config.USE_SQL:
            storage = "postgresql"
        elif Config.USE_MONGODB:
            storage = "mongodb"
        else:
            storage = "json"
        return {
            "status": "ok",
            "storage": storage,
            "ai": Config.AI_ENABLED,
            "db_connected": True,
        }

    @app.get("/", response_class=HTMLResponse, name="index")
    def index(request: Request):
        if request.session.get("logged_in"):
            return templates.TemplateResponse(request, "dashboard.html", {"session": dict(request.session)})
        return templates.TemplateResponse(request, "landing.html")

    @app.get("/dashboard", response_class=HTMLResponse, name="dashboard")
    def dashboard(request: Request):
        if not request.session.get("logged_in"):
            from fastapi.responses import RedirectResponse
            return RedirectResponse("/login")
        return templates.TemplateResponse(request, "dashboard.html", {"session": dict(request.session)})


app = create_app()

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {Config.HOST}:{Config.PORT}")
    uvicorn.run("main:app", host=Config.HOST, port=Config.PORT, reload=Config.DEBUG)
