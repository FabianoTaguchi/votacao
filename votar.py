from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_pyfile('configuracao.py')
csrf = CSRFProtect(app)

db = SQLAlchemy(app)

from rotas import *

if __name__ == '__main__':
    app.run(debug=True)


    
    