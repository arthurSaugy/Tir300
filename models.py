from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time

db = SQLAlchemy()

class Resultat(db.Model):
    __tablename__ = "resultats"
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    fichier_pdf = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Resultat {self.titre} - {self.date}>"

class AgendaEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)

    def __repr__(self):
        return f"<Agenda {self.date} - {self.description}>"

class EventFlyer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.String(10))  # "box1" ou "box2"
    filename = db.Column(db.String(255), nullable=False)  # nom du fichier stocké

class GaleriePhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
