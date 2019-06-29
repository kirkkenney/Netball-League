from flask import current_app
from FlaskApp import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime


# decorator function for user sessions, from flask_login > LoginManager
# (login_manager)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Match(db.Model):
    __tablename__ = 'match'
    id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(db.String)
    away_team = db.Column(db.String)
    location = db.Column(db.String)
    time = db.Column(db.Time)
    date = db.Column(db.Date)
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    home_approved = db.Column(db.Boolean)
    away_approved = db.Column(db.Boolean)
    home_approved_by = db.Column(db.String)
    away_approved_by = db.Column(db.String)
    home_players = db.Column(db.PickleType)
    away_players = db.Column(db.PickleType)
    home_approved_time = db.Column(db.DateTime)
    away_approved_time = db.Column(db.DateTime)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    address_1 = db.Column(db.String, nullable=False)
    address_2 = db.Column(db.String, nullable=False)
    postcode = db.Column(db.String, nullable=False)
    association_id = db.Column(db.String, nullable=False)
    profile_pic = db.Column(db.String, nullable=False, default='default.jpg')
    team = db.Column(db.String, nullable=False)
    player_status = db.Column(db.String, nullable=False)
    admin_level = db.Column(db.String, nullable=False)
    approved_by = db.Column(db.String)
    approved_time = db.Column(db.DateTime, default=datetime.now)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.team}', '{self.player_status}', '{self.admin_level}')"

    def get_reset_token(self, expires_sec=86400):
        # set up token with app's key and expiration time (86400 secs = 24hours)
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    # below decorator tells Python not to expect 'self' parameter as an arg
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.profile_pic}')"


class PendingUser(db.Model):
    __tablename__ = 'pending_user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    address_1 = db.Column(db.String, nullable=False)
    address_2 = db.Column(db.String, nullable=False)
    postcode = db.Column(db.String, nullable=False)
    association_id = db.Column(db.String, nullable=False)
    profile_pic = db.Column(db.String, nullable=False, default='default.jpg')
    team = db.Column(db.String, nullable=False)
    player_status = db.Column(db.String, nullable=False, default='Pending')
    admin_level = db.Column(db.String, nullable=False, default='User')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.team}', '{self.player_status}', '{self.admin_level}')"


class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    points = db.Column(db.Integer, nullable=False, default=0)
    matches_won = db.Column(db.Integer, nullable=False, default=0)
    matches_lose = db.Column(db.Integer, nullable=False, default=0)
    matches_drawn = db.Column(db.Integer, nullable=False, default=0)


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    team = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
