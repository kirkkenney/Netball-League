from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt  # pip install flask-bcrypt
from flask_login import LoginManager  # pip install flask-login
from flask_mail import Mail
from FlaskApp.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
# below defines set up for 'login required' pages
# it tells flask what route to load when a user is trying to access a
# restricted page
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from FlaskApp.users.routes import users
    from FlaskApp.teams.routes import teams
    from FlaskApp.posts.routes import posts
    from FlaskApp.matches.routes import matches
    from FlaskApp.main.routes import main
    from FlaskApp.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(teams)
    app.register_blueprint(posts)
    app.register_blueprint(matches)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
