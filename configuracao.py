import os
from votar import app

SECRET_KEY = 'teste123'
#Configuração da conexão com o banco de dados
SQLALCHEMY_DATABASE_URI = \
    '{SGBD}://{usuario}:{senha}@{servidor}/{database}'.format(
        SGBD = 'mysql+mysqlconnector',
        usuario = 'root',
        senha = 'root',
        servidor = '10.0.0.107',
        database = 'votacao'
    )

app.config['UPLOAD_PATH'] = 'uploads'

