from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import (StringField, PasswordField, SubmitField, BooleanField,
     TimeField)
from wtforms.fields.html5 import DateField
from wtforms.validators import (DataRequired, EqualTo, Length,
    Email, ValidationError)
from netballleague.models import User, PendingUser


player_statuses = ['Pending', 'Approved Player', 'Captain']
admin_levels = ['Admin', 'Rep', 'User']


class AddPlayerRequest(FlaskForm):
    name = StringField('Player Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(),
        Email(), Length(min=5, max=100)])
    submit = SubmitField('Submit')

    def validate_email(self, email):
        approved_email = User.query.filter_by(email=email.data).first()
        pending_email = PendingUser.query.filter_by(email=email.data).first()
        if approved_email or pending_email:
            raise ValidationError('That email is taken. Please choose a different one')


class AddPlayer(FlaskForm):
    name = StringField('Player Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(min=5, max=100)])
    password = PasswordField('Password', validators=[DataRequired()])
    team = StringField('Team', validators=[DataRequired()])
    player_status = StringField('Player Status. Accepted options: Pending, Approved Player, Captain',
        validators=[DataRequired()])
    admin_level = StringField('Admin Level. Accepted options are: Admin, Rep or User',
        validators=[DataRequired()])
    submit = SubmitField()

    def validate_admin_level(self, admin_level):
        if admin_level.data not in admin_levels:
            raise ValidationError('Not a valid Admin level. Accepted options are: Admin, Rep or User')

    def validate_player_status(self, player_status):
        if player_status.data not in player_statuses:
            raise ValidationError('Not a valid Player Status. Accepted options: Pending, Approved Player, Captain')

    def validate_email(self, email):
        approved_email = User.query.filter_by(email=email.data).first()
        pending_email = PendingUser.query.filter_by(email=email.data).first()
        if approved_email or pending_email:
            raise ValidationError('That email is taken. Please choose a different one')


class AddMatch(FlaskForm):
    home_team = StringField('Home Team', validators=[DataRequired()])
    away_team = StringField('Away Team', validators=[DataRequired()])
    location = StringField('Match Location', validators=[DataRequired()])
    date = DateField('Match Date', format='%Y-%m-%d',
        validators=[DataRequired(message='Enter as format YYYY/MM/DD')])
    time = TimeField('Match Time', validators=[DataRequired(message='Enter as format HH:MM')])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(),
        Email(), Length(min=5, max=100)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Account')

    def validate_email(self, email):
        if email.data != current_user.email:
            approved_email = User.query.filter_by(email=email.data).first()
            pending_email = PendingUser.query.filter_by(email=email.data).first()
            if approved_email or pending_email:
                raise ValidationError('That email is taken. Please choose a different one')
