from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, send_from_directory,session
from werkzeug.security import generate_password_hash
from app.database.models import db, User
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from app.services.email_services import send_email, get_email_content
from app.auth.forms import AccountSetupForm, LoginForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
import os
from app import login_manager
from .forms import LoginForm, AccountSetupForm, SleeperSetupForm
import subprocess
from app.sleeperAPI.main import get_all_data

auth = Blueprint('auth', __name__)
main = Blueprint('main', __name__)

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

        # Check if a user with the provided email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('An account with that email already exists. Please login or use another email address.')
            return redirect(url_for('auth.login'))

        # Generate a token using the SECRET_KEY
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = s.dumps(email, salt='email-confirmation-salt')

        new_user = User(email=email, first_name=first_name, last_name=last_name, password_hash=hashed_password)
        current_app.logger.debug(f"Adding new user {email} to database session")
        db.session.add(new_user)
        db.session.commit()
        current_app.logger.info(f"Committed new user {email} to database")

        # Generate confirmation link
        confirm_link = url_for('auth.confirm_email', token=token, _external=True)
        # Include the confirmation link in the email
        body_html, body_text = get_email_content(confirm_link)  # Modify get_email_content to accept and include the link

        # Send welcome email
        subject = 'Welcome to FFLAnalyzer!'
        send_email(email, subject, body_html, body_text)

        return redirect(url_for('auth.confirm_email', token=token))

    return render_template('account_setup.html', form=form) # Adjust the template path as needed

@auth.route('/confirm_email/<token>', methods=['GET'])
def confirm_email(token):
    try:
        # Decode the token to get the email
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = s.loads(token, salt='email-confirmation-salt', max_age=600) # 10 minute expiration
    except SignatureExpired:
        # If the token has expired
        return render_template('expired_token.html'), 400 # You can create a custom page for expired tokens

    # Fetch the user by email
    user = User.query.filter_by(email=email).first()

    if user:
        # Update the user's email confirmation status
        user.email_confirmed = True
        user.is_active = True
        db.session.commit()
        form = LoginForm()
        return redirect(url_for('auth.login'))
    else:
        return "User not found", 404

@auth.app_errorhandler(404)
def page_not_found(e):
    current_app.logger.info("Received request for non-existent route")
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@auth.route('/login', methods=['GET', 'POST'])
def login():
    current_app.logger.debug(f"Login route hit. Session: {session.items()}")
    # If the user is already logged in, redirect to the main index
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    # If the form is submitted and valid
    if form.validate_on_submit():
        # Get the user by email
        user = User.query.filter_by(email=form.email.data).first()

        # If the user doesn't exist or the password is incorrect, redirect to login
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        # If the user hasn't confirmed their email, redirect to login
        if not user.email_confirmed:
            flash('Please confirm your email before logging in.')
            return redirect(url_for('auth.login'))

        # Log the user in
        user.is_logged_in = True  # Set is_logged_in to True
        db.session.commit()
        login_user(user, remember=form.remember_me.data)    

        # If the user hasn't set their Sleeper ID, redirect to the setup page
        if not user.sleeper_id:
            return redirect(url_for('auth.setup_sleeper'))

        # Get the next URL from the request arguments
        next_url = request.args.get('next')
        current_app.logger.debug(f"Next URL: {next_url}")

        # If the next URL is not set or is external, redirect to the main index
        if not next_url or url_parse(next_url).netloc != '':
            next_url = url_for('main.index')
        current_app.logger.debug(f"Redirecting to: {next_url}")

        # Redirect to the next URL
        return redirect(next_url)

    # Render the login form
    return render_template('login.html', title='Sign In', form=form)

@main.route('/index')
@login_required
def index():
    current_app.logger.debug(f"Index route accessed by user {current_user.email}")
    current_app.logger.debug(f"Current user authenticated: {current_user.is_active}")
    return render_template('index.html', username=current_user.first_name)

@auth.route('/setup_sleeper', methods=['GET', 'POST'])
@login_required
def setup_sleeper():
    form = SleeperSetupForm()
    if form.validate_on_submit():
        current_user.sleeper_id = form.sleeper_id.data
        db.session.commit()
        flash('Your Sleeper ID has been set!')
        
        # Call get_all_data function
        get_all_data(2018, current_user.sleeper_id)

        return redirect(url_for('main.index'))
    return render_template('setup_sleeper.html', title='Set Sleeper ID', form=form)

@auth.route('/logout')
@login_required
def logout():
    current_user.is_logged_in = False  # Set is_logged_in to False
    db.session.commit()
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(main.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@main.route('/leagues')
def leagues():
    return render_template('leagues.html')

@main.route('/players')
def players():
    return render_template('players.html')

@main.route('/trades')
def trades():
    return render_template('trades.html')

@main.route('/account')
def account():
    return render_template('account.html')

