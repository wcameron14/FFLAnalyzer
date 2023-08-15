import logging
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, send_from_directory
from werkzeug.security import generate_password_hash
from app.database.models import db, User
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from app.services.email_services import send_email, get_email_content
from app.auth.forms import AccountSetupForm, LoginForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
import os
from app import login_manager
auth = Blueprint('auth', __name__)
main = Blueprint('main', __name__)


@auth.route('/test', methods=['GET'])
def test():
    return 'Test route working!'

@auth.route('/')
def landing_page():
    print(f"App root path: {current_app.root_path}")
    print(f"App templates path: {current_app.template_folder}")
    return render_template('landing_page.html')

@auth.route('/account_setup', methods=['GET', 'POST'])
def account_setup():
    form = AccountSetupForm()
    current_app.logger.info("Received request for /account_setup")
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='scrypt')

        # Generate a token using the SECRET_KEY
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = s.dumps(email, salt='account-setup')

        new_user = User(email=email, first_name=first_name, last_name=last_name, password_hash=hashed_password)
        current_app.logger.debug(f"Adding new user {email} to database session")
        db.session.add(new_user)
        db.session.commit()
        current_app.logger.info(f"Committed new user {email} to database")

        # Get email content
        body_html, body_text = get_email_content()

        # Send welcome email
        subject = 'Welcome to FFLAnalyzer!'
        send_email(email, subject, body_html, body_text)

        return redirect(url_for('auth.login'))

    return render_template('account_setup.html', form=form) # Adjust the template path as needed

@auth.route('/confirm_email/<token>', methods=['GET'])
def confirm_email(token):
    # Create a serializer to decode the token
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    try:
        # Decode the token to get the email
        email = s.loads(token, salt='email-confirm', max_age=3600) # 1 hour expiration
    except SignatureExpired:
        # If the token has expired
        return render_template('expired_token.html'), 400 # You can create a custom page for expired tokens

    # Fetch the user by email
    user = User.query.filter_by(email=email).first()

    if user:
        # Update the user's email confirmation status
        user.email_confirmed = True
        db.session.commit()
        return render_template('confirm_email.html')
    else:
        return "User not found", 404

@auth.app_errorhandler(404)
def page_not_found(e):
    current_app.logger.info("Received request for non-existent route")
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # if the current user is authenticated, redirect them to the index page
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.password_hash(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@main.route('/index')
@login_required
def index():
    return "Main Page"

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(main.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')