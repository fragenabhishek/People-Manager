"""
Authentication routes
Handles login, logout, and registration endpoints
"""
from flask import Blueprint, render_template, request, session, redirect, url_for

from services.auth_service import AuthService
from utils.validators import ValidationError
from utils.logger import get_logger

logger = get_logger(__name__)

# Create blueprint
auth_bp = Blueprint('auth_routes', __name__)

# Service will be injected
auth_service: AuthService = None


def init_auth_routes(service: AuthService):
    """Initialize routes with service dependency"""
    global auth_service
    auth_service = service


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration endpoint"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        email = request.form.get('email', '').strip()
        
        try:
            # Register user through service
            auth_service.register_user(username, password, confirm_password, email or None)
            logger.info(f"User registered: {username}")
            return redirect(url_for('auth_routes.login', registered='true'))
        
        except ValidationError as e:
            return render_template('register.html', error=str(e))
        
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return render_template('register.html', error='Failed to create account. Please try again.')
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login endpoint"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template('login.html', error='Username and password are required')
        
        # Authenticate user through service
        user = auth_service.authenticate_user(username, password)
        
        if user:
            session['logged_in'] = True
            session['user_id'] = user.id
            session['username'] = user.username
            logger.info(f"User logged in: {username}")
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    # Check if just registered
    registered = request.args.get('registered')
    return render_template('login.html', registered=registered)


@auth_bp.route('/logout')
def logout():
    """User logout endpoint"""
    username = session.get('username', 'unknown')
    session.clear()
    logger.info(f"User logged out: {username}")
    return redirect(url_for('auth_routes.login'))

