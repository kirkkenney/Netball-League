from netballleague import db, login_manager
from flask_login import UserMixin


# decorator function for user sessions, from flask_login > LoginManager
# (login_manager)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(db.String)
    away_team = db.Column(db.String)
    location = db.Column(db.String)
    time = db.Column(db.Time)
    date = db.Column(db.Date)
    umpire = db.Column(db.String)
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    home_approved = db.Column(db.Boolean)
    away_approved = db.Column(db.Boolean)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    profile_pic = db.Column(db.String, nullable=False, default='default.jpg')
    team = db.Column(db.String, nullable=False)
    player_status = db.Column(db.String, nullable=False)
    admin_level = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.team}', '{self.player_status}', '{self.admin_level}')"


class PendingUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    profile_pic = db.Column(db.String, nullable=False, default='default.jpg')
    team = db.Column(db.String, nullable=False)
    player_status = db.Column(db.String, nullable=False, default='Pending')
    admin_level = db.Column(db.String, nullable=False, default='User')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.team}', '{self.player_status}', '{self.admin_level}')"


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    points = db.Column(db.Integer, nullable=False, default=0)
    matches_won = db.Column(db.Integer, nullable=False, default=0)
    matches_lose = db.Column(db.Integer, nullable=False, default=0)
    matches_drawn = db.Column(db.Integer, nullable=False, default=0)
