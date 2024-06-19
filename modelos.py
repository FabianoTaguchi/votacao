from votar import db
from datetime import datetime
import pytz

tz = pytz.timezone('America/Santiago')

#Definição dos modelos
class Candidato(db.Model):
    __tablename__ = 'candidato'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    tipoCandidato = db.Column(db.String(50), nullable=False) 
    imagem = db.Column(db.String(100), nullable=True)
    criacao = db.Column(db.DateTime, default=datetime.now(tz))
    def __repr__(self):
        return '<Name %r>' % self.name

class Voto(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    candidato_id = db.Column(db.Integer, db.ForeignKey('candidato.id'), nullable=False)
    time = db.Column(db.DateTime, default=datetime.now(tz))

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(20), nullable=False)
    senha = db.Column(db.String(20), nullable=False)
    def __repr__(self):
        return '<Name %r>' % self.name
    
class Eleitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
