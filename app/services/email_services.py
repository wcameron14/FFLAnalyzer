from flask import current_app, url_for, render_template
from itsdangerous import URLSafeTimedSerializer
from email.mime.text import MIMEText
import boto3
from botocore.exceptions import ClientError

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def send_email(to_email, subject, body_html, body_text):
    # Create a new SES resource and specify a region
    client = boto3.client('ses', region_name=current_app.config['AWS_REGION'])

    # Create a MIME-formatted email (optional)
    msg = MIMEText(body_html, 'html')
    msg['Subject'] = subject
    msg['From'] = current_app.config['SENDER_EMAIL']
    msg['To'] = to_email
    msg_as_string = msg.as_string()

    # Try to send the email
    try:
        response = client.send_raw_email(
            Source=current_app.config['SENDER_EMAIL'],
            Destinations=[to_email],
            RawMessage={'Data': msg_as_string}
        )
    except ClientError as e:
        current_app.logger.error(e.response['Error']['Message'])
    else:
        current_app.logger.info('Email sent! Message ID: ' + response['MessageId'])
    
def get_email_content():
    login_url = url_for('auth.login', _external=True)  # Generate the login URL dynamically
    body_html = render_template('confirm_email.html', login_url=login_url)
    body_text = f"Welcome to FFLAnalyzer! This email confirms that your account was set-up correctly. To log in, click on the following link: {login_url}"
    return body_html, body_text
