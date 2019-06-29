import os


class Config:
    SECRET_KEY = os.environ.get('NETBALL_KEY')
    # SQLALCHEMY_DATABASE_URI = os.environ.get('NETBALL_DB')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///netball.db'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
