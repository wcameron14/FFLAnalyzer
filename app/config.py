import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
    AWS_REGION = os.getenv('AWS_REGION')
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Add other configuration variables here
