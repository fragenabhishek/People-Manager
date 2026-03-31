"""
Authentication routes
Handles login, logout, and registration endpoints
"""
from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from utils.logger import get_logger
from utils.validators import ValidationError

logger = get_logger(__name__)

auth_bp = Blueprint('auth_routes', __name__)


def _svc():
    return current_app.config['auth_service']


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        email = request.form.get('email', '').strip()

        try:
            _svc().register_user(username, password, confirm_password, email or None)
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

        user = _svc().authenticate_user(username, password)

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
