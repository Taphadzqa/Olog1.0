from flask_wtf import FlaskForm
from wtforms import Form, StringField, DateField, SubmitField, TimeField, SelectField, TextAreaField, FileField
from wtforms.validators import DataRequired
from blank.routes.helpers import NonValidatingSelectField
from datetime import date


class SearchLoadForm(FlaskForm):
    pickup = NonValidatingSelectField('Loading from', choices=[])
    drop = NonValidatingSelectField('Loading to', choices=[])
    loading_date = DateField('Loading Date', validators=[DataRequired()], default=date.today, render_kw={"type": "date"})
    submit = SubmitField('Search')


class AssignDetailsForm(FlaskForm):
    load_id = StringField(validators=[DataRequired()])
    driver = StringField(validators=[DataRequired()])
    cell = StringField(validators=[DataRequired()])
    id = StringField(validators=[DataRequired()])
    reg = StringField(validators=[DataRequired()])
    submit = SubmitField('Generate Load con')


class UpdateStatusForm(FlaskForm):
    load_id = StringField(validators=[DataRequired()])
    eta = TimeField('ETA')
    status = SelectField('Status',choices=[('Awaiting dispatch','Awaiting dispatch'),('Enroute to loading point', 'Enroute to loading point'), ('Waiting to load','Waiting to load'), ('Enroute to offloading point','Enroute to offloading point'), ('Offloaded','Offloaded')])
    comments = TextAreaField('Comments')
    submit = SubmitField('Save')
