from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import (StringField, PasswordField, SubmitField, BooleanField,
     SelectField)
from wtforms.validators import (DataRequired, EqualTo, Length,
    Email, ValidationError)
from FlaskApp.models import User, PendingUser


class AddPlayerRequest(FlaskForm):
    name = StringField('Player Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(),
        Email(), Length(min=5, max=100)])
    address_1 = StringField('Address Line 1', validators=[DataRequired()])
    address_2 = StringField('Address Line 2', validators=[DataRequired()])
    postcode = StringField('Postcode', validators=[DataRequired()])
    association_id = StringField('Association ID', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_email(self, email):
        approved_email = User.query.filter_by(email=email.data).first()
        pending_email = PendingUser.query.filter_by(email=email.data).first()
        if approved_email or pending_email:
            raise ValidationError('That email is taken. Please choose a different one')


class AddPlayer(FlaskForm):
    name = StringField('Player Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(),
        Email(), Length(min=5, max=100)])
    team = SelectField(u'Team', validators=[DataRequired()])
    address_1 = StringField('Address Line 1', validators=[DataRequired()])
    address_2 = StringField('Address Line 2', validators=[DataRequired()])
    postcode = StringField('Postcode', validators=[DataRequired()])
    association_id = StringField('Association ID', validators=[DataRequired()])
    player_status = SelectField(u'Player Status', choices=[('Pending', 'Pending'),
        ('Approved Player', 'Approved Player'), ('Captain', 'Captain')], validators=[DataRequired()])
    admin_level = SelectField('Admin Level', choices=[('Admin', 'Admin'),
        ('Rep', 'Rep'), ('User', 'User')], validators=[DataRequired()])
    submit = SubmitField()

    def validate_email(self, email):
        approved_email = User.query.filter_by(email=email.data).first()
        pending_email = PendingUser.query.filter_by(email=email.data).first()
        if approved_email or pending_email:
            raise ValidationError('That email is taken. Please choose a different one')


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(),
        Email(), Length(min=5, max=100)])
    address_1 = StringField('Address Line 1', validators=[DataRequired()])
    address_2 = StringField('Address Line 2', validators=[DataRequired()])
    postcode = StringField('Postcode', validators=[DataRequired()])
    association_id = StringField('Association ID', validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Account')

    def validate_email(self, email):
        if email.data != current_user.email:
            approved_email = User.query.filter_by(email=email.data).first()
            pending_email = PendingUser.query.filter_by(email=email.data).first()
            if approved_email or pending_email:
                raise ValidationError('That email is taken. Please choose a different one')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('''There is no account with that email,
                please try again or speak to your team captain.''')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class ChangePassword(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new = PasswordField('Confirm New Password', validators=[DataRequired(),
        EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Update!')

