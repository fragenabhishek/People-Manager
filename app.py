"""
People Manager Application
AI-powered relationship management with clean architecture
"""
from datetime import timedelta

from flask import Flask, render_template, session
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient

from config import Config
from middleware import login_required
from repositories.note_repository import NoteRepository
from repositories.person_repository import PersonRepository
from repositories.user_repository import UserRepository
from routes import ai_bp, api_auth_bp, auth_bp, note_bp, person_bp
from services.ai_service import AIService
from services.auth_service import AuthService
from services.import_export_service import ImportExportService
from services.note_service import NoteService
from services.person_service import PersonService
from services.token_service import TokenService
from utils.logger import setup_logger
from utils.response import APIResponse
from utils.validators import ValidationError

logger = setup_logger('people_manager')


def create_app() -> Flask:
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)

    _configure_app(app)
    Config.validate()

    bcrypt = Bcrypt(app)
    _configure_rate_limiter(app)

    people_repo, user_repo, note_repo = _init_repositories()

    app.config['token_service'] = TokenService(
        Config.SECRET_KEY,
        access_ttl_minutes=Config.JWT_ACCESS_TOKEN_MINUTES,
        refresh_ttl_minutes=Config.JWT_REFRESH_TOKEN_MINUTES,
    )
    app.config['auth_service'] = AuthService(user_repo, bcrypt)
    app.config['person_service'] = PersonService(people_repo, note_repo)
    app.config['ai_service'] = AIService()
    app.config['note_service'] = NoteService(note_repo, people_repo)
    app.config['import_export_service'] = ImportExportService(people_repo)

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_auth_bp)
    app.register_blueprint(person_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(note_bp)

    _register_error_handlers(app)
    _register_security_headers(app)
    _register_main_routes(app)

    logger.info("Application initialized successfully")
    return app


def _configure_app(app: Flask):
    app.secret_key = Config.SECRET_KEY
    app.config['SESSION_COOKIE_HTTPONLY'] = Config.SESSION_COOKIE_HTTPONLY
    app.config['SESSION_COOKIE_SAMESITE'] = Config.SESSION_COOKIE_SAMESITE
    app.config['SESSION_COOKIE_SECURE'] = not Config.DEBUG
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)


def _configure_rate_limiter(app: Flask):
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[Config.RATE_LIMIT_DEFAULT],
        storage_uri="memory://",
    )
    limiter.limit(Config.RATE_LIMIT_LOGIN)(auth_bp)
    limiter.limit(Config.RATE_LIMIT_API)(person_bp)
    limiter.limit(Config.RATE_LIMIT_API)(note_bp)
    limiter.limit(Config.RATE_LIMIT_AI)(ai_bp)


def _init_repositories():
    if Config.USE_SQL:
        from models.database import create_tables, init_db
        from repositories.sql_note_repository import SqlNoteRepository
        from repositories.sql_person_repository import SqlPersonRepository
        from repositories.sql_user_repository import SqlUserRepository

        init_db(Config.DATABASE_URL, echo=Config.DEBUG)
        create_tables()
        from models.database import get_session_factory
        sf = get_session_factory()
        return (
            SqlPersonRepository(sf),
            SqlUserRepository(sf),
            SqlNoteRepository(sf),
        )
    if Config.USE_MONGODB:
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


def _register_error_handlers(app: Flask):
    """Central error handlers — routes no longer need individual try/catch."""

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return APIResponse.validation_error(str(e))

    @app.errorhandler(ValueError)
    def handle_value_error(e):
        return APIResponse.validation_error(str(e))

    @app.errorhandler(404)
    def handle_not_found(e):
        return APIResponse.not_found()

    @app.errorhandler(429)
    def handle_rate_limit(e):
        return APIResponse.error("Rate limit exceeded. Please try again later.", 429, "RATE_LIMITED")

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        logger.exception("Unhandled exception")
        return APIResponse.server_error()

    @app.route('/health')
    def health():
        db_ok = True
        if Config.USE_SQL:
            storage = 'postgresql'
        elif Config.USE_MONGODB:
            storage = 'mongodb'
            try:
                client = app.config.get('_mongo_client')
                if client:
                    client.admin.command('ping')
            except Exception:
                db_ok = False
        else:
            storage = 'json'
        return {
            'status': 'ok' if db_ok else 'degraded',
            'storage': storage,
            'ai': Config.AI_ENABLED,
            'db_connected': db_ok,
        }


def _register_security_headers(app: Flask):
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        if not Config.DEBUG:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )
        response.headers['Content-Security-Policy'] = csp
        return response


def _register_main_routes(app: Flask):

    @app.route('/')
    def index():
        if session.get('logged_in'):
            return render_template('dashboard.html', session=session)
        return render_template('landing.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html', session=session)


app = create_app()

if __name__ == '__main__':
    logger.info(f"Starting server on {Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
