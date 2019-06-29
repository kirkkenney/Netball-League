from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TimeField, SelectField,
    IntegerField)
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired


class AddMatch(FlaskForm):
    home_team = SelectField(u'Home Team', validators=[DataRequired()])
    away_team = SelectField(u'Away Team', validators=[DataRequired()])
    location = StringField('Match Location', validators=[DataRequired()])
    date = DateField('Match Date', format='%Y-%m-%d', validators=[DataRequired()])
    time = TimeField('Match Time', validators=[DataRequired(message='Enter as format HH:MM')])
    submit = SubmitField('Submit')


class UpdateMatch(FlaskForm):
    home_team = SelectField(u'Home Team', validators=[DataRequired()])
    away_team = SelectField(u'Away Team', validators=[DataRequired()])
    location = StringField('Match Location', validators=[DataRequired()])
    date = DateField('Match Date', format='%Y-%m-%d',
        validators=[DataRequired()])
    time = TimeField('Match Time', validators=[DataRequired(message='Enter as format HH:MM')])
    submit = SubmitField('Submit')


class UpdateScore(FlaskForm):
    score = IntegerField('Score')
    submit = SubmitField('Update!')
