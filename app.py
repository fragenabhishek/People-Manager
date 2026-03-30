"""
People Manager Application
AI-powered relationship management with clean architecture

Architecture:
- Config: Centralized configuration
- Models: Domain entities (Person, User, Note)
- Repositories: Data access layer (MongoDB/JSON)
- Services: Business logic (Person, Auth, AI, Notes, Import/Export)
- Routes: API endpoints (separated by domain)
- Middleware: Auth, rate limiting
- Utils: Validation, logging, response formatting
"""
from flask import Flask, render_template, session
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient

from config import Config
from utils.logger import setup_logger
from middleware import login_required

from repositories.person_repository import PersonRepository
from repositories.user_repository import UserRepository
from repositories.note_repository import NoteRepository

from services.auth_service import AuthService
from services.person_service import PersonService
from services.ai_service import AIService
from services.note_service import NoteService
from services.import_export_service import ImportExportService

from routes import auth_bp, person_bp, ai_bp, note_bp
from routes.auth_routes import init_auth_routes
from routes.person_routes import init_person_routes
from routes.ai_routes import init_ai_routes
from routes.note_routes import init_note_routes

logger = setup_logger('people_manager')


def create_app() -> Flask:
    """Application factory - creates and configures the Flask app"""
    app = Flask(__name__)

    # Core config
    app.secret_key = Config.SECRET_KEY
    app.config['SESSION_COOKIE_HTTPONLY'] = Config.SESSION_COOKIE_HTTPONLY
    app.config['SESSION_COOKIE_SAMESITE'] = Config.SESSION_COOKIE_SAMESITE

    # Bcrypt
    bcrypt = Bcrypt(app)

    # Rate limiter
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

    Config.validate()

    # Repositories
    people_repo, user_repo, note_repo = initialize_repositories()

    # Services (Dependency Injection)
    auth_service = AuthService(user_repo, bcrypt)
    person_service = PersonService(people_repo, note_repo)
    ai_service = AIService()
    note_service = NoteService(note_repo, people_repo)
    ie_service = ImportExportService(people_repo)

    # Wire routes
    init_auth_routes(auth_service)
    init_person_routes(person_service, ie_service)
    init_ai_routes(ai_service, person_service, note_service)
    init_note_routes(note_service)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(person_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(note_bp)

    register_main_routes(app)

    # Health check
    @app.route('/health')
    def health():
        return {'status': 'ok', 'storage': 'mongodb' if Config.USE_MONGODB else 'json', 'ai': Config.AI_ENABLED}

    logger.info("Application initialized successfully")
    return app


def initialize_repositories():
    """Initialize repositories based on configuration"""
    if Config.USE_MONGODB:
        client = MongoClient(Config.MONGO_URI)
        db = client[Config.DB_NAME]
        people_repo = PersonRepository(people_collection=db[Config.PEOPLE_COLLECTION])
        user_repo = UserRepository(users_collection=db[Config.USERS_COLLECTION])
        note_repo = NoteRepository(notes_collection=db[Config.NOTES_COLLECTION])
    else:
        people_repo = PersonRepository(data_file=Config.DATA_FILE)
        user_repo = UserRepository(data_file=Config.USERS_FILE)
        note_repo = NoteRepository(data_file=Config.NOTES_FILE)
    return people_repo, user_repo, note_repo


def register_main_routes(app: Flask):
    """Register main application routes"""

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
