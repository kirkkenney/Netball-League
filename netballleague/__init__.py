from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt  # pip install flask-bcrypt
from flask_login import LoginManager  # pip install flask-login
import os

app = Flask(__name__)

# app.config['SECRET_KEY'] = '_Ex9aFfOiewV953Q6K3SsChJXRW3xLUt0fIUPHOY4zE'
app.config['SECRET_KEY'] = os.environ.get('NETBALL_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///netball.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
# below defines set up for 'login required' pages
# it tells flask what route to load when a user is trying to access a
# restricted page
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from netballleague import routes
