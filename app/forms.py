from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

class EssayForm(FlaskForm):
    essay = TextAreaField('Enter your essay:', validators=[DataRequired()])
    submit = SubmitField('Analyze Essay')
