"""
People Manager Application
Refactored with SOLID principles and clean architecture

Architecture:
- Config: Centralized configuration management
- Models: Domain entities (Person, User)
- Repositories: Data access layer with abstraction
- Services: Business logic layer
- Routes: API endpoints (separated by domain)
- Middleware: Cross-cutting concerns (auth)
- Utils: Validation, logging, response formatting
"""
from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from pymongo import MongoClient

from config import Config
from utils.logger import setup_logger
from middleware import login_required

# Import repositories
from repositories.person_repository import PersonRepository
from repositories.user_repository import UserRepository

# Import services
from services.auth_service import AuthService
from services.person_service import PersonService
from services.ai_service import AIService

# Import routes
from routes import auth_bp, person_bp, ai_bp
from routes.auth_routes import init_auth_routes
from routes.person_routes import init_person_routes
from routes.ai_routes import init_ai_routes

# Initialize logger
logger = setup_logger('people_manager')


def create_app() -> Flask:
    """
    Application factory pattern
    Creates and configures the Flask application
    
    Returns:
        Configured Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY
    
    # Initialize Bcrypt
    bcrypt = Bcrypt(app)
    
    # Validate configuration
    Config.validate()
    
    # Initialize database connections and repositories
    people_repo, user_repo = initialize_repositories()
    
    # Initialize services (Dependency Injection)
    auth_service = AuthService(user_repo, bcrypt)
    person_service = PersonService(people_repo)
    ai_service = AIService()
    
    # Initialize routes with their dependencies
    init_auth_routes(auth_service)
    init_person_routes(person_service)
    init_ai_routes(ai_service, person_service)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(person_bp)
    app.register_blueprint(ai_bp)
    
    # Register main routes
    register_main_routes(app)
    
    logger.info("Application initialized successfully")
    
    return app


def initialize_repositories():
    """
    Initialize repositories based on configuration
    Implements Dependency Inversion: depends on abstractions
    
    Returns:
        Tuple of (PersonRepository, UserRepository)
    """
    if Config.USE_MONGODB:
        # MongoDB setup
        client = MongoClient(Config.MONGO_URI)
        db = client[Config.DB_NAME]
        people_collection = db[Config.PEOPLE_COLLECTION]
        users_collection = db[Config.USERS_COLLECTION]
        
        people_repo = PersonRepository(people_collection=people_collection)
        user_repo = UserRepository(users_collection=users_collection)
    else:
        # JSON file setup
        people_repo = PersonRepository(data_file=Config.DATA_FILE)
        user_repo = UserRepository(data_file=Config.USERS_FILE)
    
    return people_repo, user_repo


def register_main_routes(app: Flask):
    """Register main application routes"""
    
    @app.route('/')
    @login_required
    def index():
        """Render main page"""
        from flask import session
        return render_template('index.html', session=session)


# Create application instance
app = create_app()


if __name__ == '__main__':
    """Run the application"""
    logger.info(f"Starting server on {Config.HOST}:{Config.PORT}")
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
