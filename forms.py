from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FileField, TimeField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed, FileRequired

class ResultatForm(FlaskForm):
    titre = StringField("Titre", validators=[DataRequired(), Length(min=1, max=100)])
    date = DateField("Date", validators=[DataRequired()])
    fichier_pdf = FileField("Fichier PDF", validators=[
        FileRequired(),
        FileAllowed(["pdf"], "Seuls les fichiers PDF sont autorisés !")
    ])

class DummyForm(FlaskForm):
    pass

class RdvForm(FlaskForm):
    id = HiddenField() 
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    debut = TimeField('Heure début', format='%H:%M', validators=[DataRequired()])
    fin = TimeField('Heure fin', format='%H:%M', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Enregistrer')
