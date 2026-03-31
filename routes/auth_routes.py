"""
Authentication routes
Handles login, logout, and registration endpoints
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, current_app

from utils.validators import ValidationError
from utils.logger import get_logger

logger = get_logger(__name__)

auth_bp = Blueprint('auth_routes', __name__)


def init_auth_routes(service):
    """Store service on the blueprint for access via current_app"""
    auth_bp.record(lambda state: state.app.config.update(auth_service=service))


def _get_service():
    return current_app.config['auth_service']


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        email = request.form.get('email', '').strip()

        try:
            _get_service().register_user(username, password, confirm_password, email or None)
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
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            return render_template('login.html', error='Username and password are required')

        user = _get_service().authenticate_user(username, password)

        if user:
            session.clear()
            session['logged_in'] = True
            session['user_id'] = user.id
            session['username'] = user.username
            logger.info(f"User logged in: {username}")
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')

    registered = request.args.get('registered')
    return render_template('login.html', registered=registered)


@auth_bp.route('/logout')
def logout():
    username = session.get('username', 'unknown')
    session.clear()
    logger.info(f"User logged out: {username}")
    return redirect(url_for('index'))
