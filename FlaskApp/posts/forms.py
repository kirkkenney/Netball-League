from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Message Content', validators=[DataRequired()])
    send_email = BooleanField('Send As An Email?')
    submit = SubmitField('Post!')
