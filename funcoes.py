import os
from modelos import Candidato
from votar import app
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, RadioField, validators, SelectField
from wtforms.validators import InputRequired, DataRequired, Length, Regexp

class FormularioCandidato(FlaskForm):
    nome = StringField('Nome do Candidato:', [validators.DataRequired(), validators.Length(min=1, max=50)])
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=30)])
    tipoCandidato = SelectField('Tipo de Candidato', choices=[('Técnico', 'Técnico'), ('Docente', 'Docente'), ('Discente', 'Discente')], validators=[DataRequired()])
    salvar = SubmitField('Cadastrar')

class FormularioUsuario(FlaskForm):
    login = StringField('Login:', [validators.DataRequired(), validators.Length(min=1, max=30)])
    senha = PasswordField('Senha', [validators.DataRequired(), validators.Length(min=1, max=20)])
    logar = SubmitField('Login')

class CadastroEleitorForm(FlaskForm):
    cpf = StringField('CPF do Eleitor', validators=[
        DataRequired(message='O CPF é obrigatório.'),
        Length(min=11, max=11, message='O CPF deve ter exatamente 11 dígitos.'),
        Regexp('^\d+$', message='O CPF deve conter apenas números.')
    ])
    submit = SubmitField('Cadastrar')

class VotacaoForm(FlaskForm):
    candidato_id = RadioField('Candidato', choices=[], validators=[InputRequired(message='Selecione um candidato.')])

def recuperaImagem(id):
    for nomeArquivo in os.listdir(app.config['UPLOAD_PATH']):
        if f'foto{id}-' in nomeArquivo:
            return nomeArquivo
    return 'padrao.jpeg'

def deletaArquivo(id):
    arquivo = recuperaImagem(id)
    upload_path = app.config['UPLOAD_PATH']
    candidato = Candidato.query.get(id)
    if arquivo != 'padrao.jpeg':
        os.remove(os.path.join(app.config['UPLOAD_PATH'], arquivo))
    if candidato and candidato.imagem:
        arquivo_path = os.path.join(upload_path, candidato.imagem)
        if os.path.exists(arquivo_path):
            os.remove(arquivo_path)



