from flask import render_template, request, redirect, url_for, session, flash, send_from_directory
from modelos import Candidato, Usuario, Voto, Eleitor
from votar import app, db
from funcoes import FormularioCandidato, FormularioUsuario, recuperaImagem, deletaArquivo, VotacaoForm, CadastroEleitorForm
import time
import os


#Rotas para o eleitor
@app.route('/')
def index():
    form = VotacaoForm()
    listaCandidatos = Candidato.query.all()
    candidatos = []
    for candidato in listaCandidatos:
        candidato.imagemCaminho = url_for('imagem', nomeArquivo=candidato.imagem) if candidato.imagem else url_for('static', filename='default.png')
        candidatos.append((str(candidato.id), candidato.nome))
    form.candidato_id.choices = candidatos
    return render_template('votar.html', titulo='Painel de votação', candidatos=listaCandidatos, form=form)

   
@app.route('/confirmar', methods=['POST'])
def confirmar():
    form = VotacaoForm()
    candidato_id = form.candidato_id.data
    candidato = Candidato.query.get(candidato_id)
    if candidato:
        candidato.imagemCaminho = url_for('imagem', nomeArquivo=candidato.imagem) if candidato.imagem else url_for('static', filename='default.png')
        session['candidato_id'] = candidato_id
        return render_template('confirmar.html', candidato=candidato, form=form)
    else:
        flash('Candidato não encontrado!', 'danger')
        return redirect(url_for('index'))
    

@app.route('/votar', methods=['POST'])
def registrarVoto():
    candidato_id = session.get('candidato_id')
    if candidato_id:
        voto = Voto(candidato_id=candidato_id)
        db.session.add(voto)
        db.session.commit()
        session.pop('candidato_id', None)  # Remove o dado da sessão após o registro
        flash('Voto registrado com sucesso!', 'success')
        return redirect(url_for('index'))
    else:
        flash('Erro ao registrar voto. Tente novamente.', 'danger')
        return redirect(url_for('index'))


# Rota para cadastrar eleitor
@app.route('/eleitor', methods=['GET', 'POST'])
def eleitor():
    form = CadastroEleitorForm()
    if form.validate_on_submit():
        cpf = form.cpf.data
        eleitorExistente = Eleitor.query.filter_by(cpf=cpf).first()
        if eleitorExistente:
            return render_template('mensagem.html', mensagem='Este CPF já está cadastrado.')

        novoEleitor = Eleitor(cpf=cpf)
        db.session.add(novoEleitor)
        db.session.commit()
        return render_template('mensagem.html', mensagem=f'Eleitor cadastrado com sucesso: {cpf}')
    return render_template('eleitor.html', form=form)

#Rotas para o painel administrativo
@app.route('/candidatos')
def candidatos():
    listaCandidatos = Candidato.query.order_by(Candidato.id)
    return render_template('lista.html', titulo='Listagem dos candidatos', candidatos=listaCandidatos)

@app.route('/login')
def login():
    form = FormularioUsuario()
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima, form=form)

@app.route('/logout')
def logout():
    session['usuarioLogado'] = None
    flash('Logout efetuado com sucesso!')
    return redirect(url_for('candidatos'))

@app.route('/autenticar', methods=['POST', ])
def autenticar():
    form = FormularioUsuario(request.form)
    usuario = Usuario.query.filter_by(login=form.login.data).first()
    if usuario:
        if form.senha.data == usuario.senha:
            session['usuarioLogado'] = usuario.login
            flash(usuario.login + ' logado com sucesso!')
            return redirect(url_for('candidatos'))
        else:
            flash('Usuário não logado.')
            return redirect(url_for('login'))
    else:
        flash('Usuário não logado.')
        return redirect(url_for('login'))
    
@app.route('/novo')
def novo():
    if 'usuarioLogado' not in session or session['usuarioLogado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    form = FormularioCandidato()
    return render_template('novo.html', titulo='Cadastro de um novo candidato', form=form)

@app.route('/criar', methods=['POST',])
def criar():
    form = FormularioCandidato(request.form)
    if not form.validate_on_submit():
        return redirect(url_for('novo'))
    nome = form.nome.data
    descricao = form.descricao.data
    tipoCandidato = form.tipoCandidato.data

    candidato = Candidato.query.filter_by(nome=nome).first()
    if candidato:
        flash('Candidato já cadastrado')
        return redirect(url_for('novo'))
    
    novoCandidato = Candidato(nome=nome, descricao=descricao, tipoCandidato=tipoCandidato)
    db.session.add(novoCandidato)
    db.session.commit()
    arquivo = request.files['arquivo']
    
    if arquivo and allowedFile(arquivo.filename):
        upload_path = app.config['UPLOAD_PATH']
        filename = f'foto{novoCandidato.id}-{int(time.time())}.png'
        arquivo.save(os.path.join(upload_path, filename))
        novoCandidato.imagem = filename
        db.session.commit()
    return redirect(url_for('candidatos'))

def allowedFile(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


@app.route('/editar/<int:id>')
def editar(id):
    if 'usuarioLogado' not in session or session['usuarioLogado'] is None:
        return redirect(url_for('login', proxima=url_for('editar', id=id)))
    
    consultaCandidato = Candidato.query.filter_by(id=id).first()
    form = FormularioCandidato(request.form)
    form.nome.data = consultaCandidato.nome
    form.descricao.data = consultaCandidato.descricao
    form.tipoCandidato.data = consultaCandidato.tipoCandidato
    imagemAluno = recuperaImagem(id)
    return render_template('editar.html', titulo='Edição de dados do candidato', candidato=consultaCandidato, imagemAluno=imagemAluno , form=form)

@app.route('/uploads/<nomeArquivo>')
def imagem(nomeArquivo):
    try:
        return send_from_directory(app.config['UPLOAD_PATH'], nomeArquivo)
    except FileNotFoundError:
        flash('Imagem não encontrada.')
        return redirect(url_for('candidatos'))

@app.route('/atualizar', methods=['POST'])
def atualizar():
    form = FormularioCandidato(request.form)
    if form.validate_on_submit():
        candidatoConsulta = Candidato.query.filter_by(id=request.form['id']).first()
        candidatoConsulta.nome = form.nome.data
        candidatoConsulta.descricao = form.descricao.data
        candidatoConsulta.tipoCandidato = form.tipoCandidato.data

        db.session.add(candidatoConsulta)
        db.session.commit()
        arquivo = request.files['arquivo']
        if arquivo and allowedFile(arquivo.filename):
            upload_path = app.config['UPLOAD_PATH']
            deletaArquivo(candidatoConsulta.id)  
            filename = f'foto{candidatoConsulta.id}-{int(time.time())}.png'
            arquivo.save(os.path.join(upload_path, filename))
            candidatoConsulta.imagem = filename
            db.session.commit()
    return redirect(url_for('candidatos'))

@app.route('/deletar/<int:id>')
def deletar(id):
    if 'usuarioLogado' not in session or session['usuarioLogado'] == None:
        return redirect(url_for('login'))
    candidatoConsulta = Candidato.query.filter_by(id=id).first()
    Candidato.query.filter_by(id=id).delete()
    db.session.commit()
    deletaArquivo(candidatoConsulta.id)
    flash('Candidato excluído com sucesso!')
    return redirect(url_for('candidatos'))


#Relatórios
@app.route('/contagem')
def votos():
    if 'usuarioLogado' not in session or session['usuarioLogado'] is None:
        return redirect(url_for('login', proxima=url_for('novo')))
    
    totalVotos = db.session.query(db.func.count(Voto.id)).scalar()
    categorias = ['Técnico', 'Discente', 'Docente']
    resultados = {}

    for categoria in categorias:
        votosCategoria = (
            db.session.query(Candidato, db.func.count(Voto.id))
            .outerjoin(Voto)
            .filter(Candidato.tipoCandidato == categoria)
            .group_by(Candidato)
            .all()
        )
        totalVotosCategoria = (
            db.session.query(db.func.count(Voto.id))
            .join(Candidato, Voto.candidato_id == Candidato.id)
            .filter(Candidato.tipoCandidato == categoria)
            .scalar()
        )
        
        percentuaisCategoria = [
            (candidato.nome, votos / totalVotosCategoria * 100) 
            for candidato, votos in votosCategoria
        ] if totalVotosCategoria > 0 else []

        candidatoEleitoCategoria = max(votosCategoria, key=lambda x: x[1])[0] if votosCategoria else None

        resultados[categoria] = {
            'total_votos': totalVotosCategoria,
            'resultados': votosCategoria,
            'percentuais': percentuaisCategoria,
            'candidatoEleito': candidatoEleitoCategoria
        }
    
    return render_template(
        'contagem.html', 
        resultados=resultados, 
        total_votos=totalVotos
    )


@app.route('/acompanhar')
def acompanhar():
    if 'usuarioLogado' not in session or session['usuarioLogado'] is None:
        return redirect(url_for('login', proxima=url_for('novo')))
    
    totalVotos = db.session.query(db.func.count(Voto.id)).scalar()
    categorias = ['Técnico', 'Discente', 'Docente']
    resultados = {}

    for categoria in categorias:
        totalVotosCategoria = (
            db.session.query(db.func.count(Voto.id))
            .join(Candidato, Voto.candidato_id == Candidato.id)
            .filter(Candidato.tipoCandidato == categoria)
            .scalar()
        )
        
        resultados[categoria] = {
            'total_votos': totalVotosCategoria
        }
    
    return render_template('acompanhar.html', resultados=resultados, total_votos=totalVotos)
