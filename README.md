# Python_PBI
 
## Descrição
Este projeto demonstra uma aplicação web construída com Dash e Flask, que inclui autenticação de usuário utilizando Flask-Login e Flask-Bcrypt. Ele fornece páginas de registro, login, um painel interativo protegido, e uma página de erro de acesso. A aplicação também conecta-se a um banco de dados SQLite para armazenar informações dos usuários.

## Estrutura do Projeto
- __init__.py: Inicializa a aplicação Dash e configura o servidor Flask.
- models.py: Define o modelo de usuário e a função de carregamento de usuário.
- views.py: Define os layouts das páginas e callbacks para a navegação e a lógica de autenticação.

## Instalação

1 Crie um ambiente virtual e ative-o:
python -m venv venv
source venv/bin/activate  # No Windows, use `venv\Scripts\activate`

2 Instale as dependências:
pip install -r requirements.txt

3 Execute a aplicação:
python run.py

## Arquivos
__init__.py

from dash import Dash
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

app = Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions = True

server.config.update(
    SQLALCHEMY_DATABASE_URI="sqlite:///bancodedados.db",
    SECRET_KEY="sua_chave_secreta_aqui",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

database = SQLAlchemy(server)
bcrypt = Bcrypt(server)
login_manager = LoginManager(server)
login_manager.login_view = "/login"

from dashapp import views

models.py

from dashapp import database, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_usuario(id_usuario):
    usuario = Usuario.query.get(int(id_usuario))
    return usuario

class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)

views.py

from dash import html, dcc, Input, Output, State
from dashapp import app, server, database, bcrypt
from dashapp.models import Usuario
from flask_login import login_user, logout_user, current_user

opcoes_dropdown = [
    {"label": "Dia 1", "value": "Dia 1"},
    {"label": "Dia 2", "value": "Dia 2"}
]

layout_homepage = html.Div([
    dcc.Location(id="homepage_url", refresh=False),
    html.H2("Criar conta"),
    html.Div([
        dcc.Input(id="email", type="email", placeholder="Seu e-mail"),
        dcc.Input(id="senha", type="password", placeholder="Sua senha"),
        html.Button("Criar conta", id="botao-criarconta"),
        dcc.Link("Já tem uma conta? Faça seu login aqui", "/login")
    ], className="form-column")
])

layout_login = html.Div([
    dcc.Location(id="login_url", refresh=True),
    html.H2("Faça seu Login"),
    html.Div([
        dcc.Input(id="email", type="email", placeholder="Seu e-mail"),
        dcc.Input(id="senha", type="password", placeholder="Sua senha"),
        html.Button("Faça Login", id="botao-login"),
        dcc.Link("Não tem uma conta? Crie aqui", "/")
    ], className="form-column")
])

layout_dashboard = html.Div([
    dcc.Location(id="dashboard_url", refresh=True),
    html.H2("Meu Dashboard"),
    dcc.Dropdown(id="dropdown", options=opcoes_dropdown, value="Dia 1"),
    dcc.Graph(id="grafico"),
])

layout_erro = html.Div([
    dcc.Location(id="erro_url", refresh=True),
    html.H2("Erro de Acesso"),
    html.Div([
        dcc.Link("Clique aqui para criar uma conta", "/"),
        dcc.Link("Clique aqui para fazer login", "/login")
    ], className="form-column")
])

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div([
        html.H1("Dashapp"),
        html.Div(id="navbar"),
    ], className="align-left-right"),
    html.Div(id="conteudo_pagina")
])

# Callbacks
@app.callback(Output("conteudo_pagina", "children"), Input("url", "pathname"))
def carregar_pagina(pathname):
    if pathname == "/":
        return layout_homepage
    elif pathname == "/dashboard":
        if current_user.is_authenticated:
            return layout_dashboard
        else:
            return dcc.Link("Usuario não autenticado, faça login aqui", "/login")
    elif pathname == "/login":
        return layout_login
    elif pathname == "/erro":
        return layout_erro
    elif pathname == "/logout":
        if current_user.is_authenticated:
            logout_user()
        return layout_login
    
@app.callback(Output("navbar", "children"), Input("url", "pathname"))
def exibir_navbar(pathname):
    if pathname != "/logout":
        if current_user.is_authenticated:
            return html.Div([
                dcc.Link("Dashboard", "/dashboard", className="button-link"),
                dcc.Link("Logout", "/logout", className="button-link")
            ])
        else:
            return html.Div([
                dcc.Link("Login", "/login", className="button-link")
            ])

@app.callback(Output("homepage_url", "pathname"), Input("botao-criarconta", "n_clicks"), 
              [State("email", "value"), State("senha", "value")])
def criar_conta(n_clicks, email, senha):
    if n_clicks:
        usuario  = Usuario.query.filter_by(email=email).first()
        if usuario:
            return "/login"
        else:
            senha_criptografada = bcrypt.generate_password_hash(senha).decode("utf-8")
            usuario = Usuario(email=email, senha=senha_criptografada)
            database.session.add(usuario)
            database.session.commit()
            login_user(usuario)
            return "/dashboard"
        
@app.callback(Output("login_url", "pathname"), Input("botao-login", "n_clicks"), 
              [State("email", "value"), State("senha", "value")])
def login_usuario(n_clicks, email, senha):
    if n_clicks:
        usuario  = Usuario.query.filter_by(email=email).first()
        if not usuario:
            return "/"
        else:
            if bcrypt.check_password_hash(usuario.senha.encode("utf-8"), senha):
                login_user(usuario)
                return "/dashboard"
            else:
                return "/erro"

@app.callback(Output("grafico", "figure"), Input("dropdown", "value"))
def atualizar_grafico(valor_dropdown):
    if valor_dropdown == "Dia 1":
        pontos = {"x": [1, 2, 3, 4], "y": [4, 1, 2, 1]}
        titulo = "Gráfico Dia 1"
    else:
        pontos = {"x": [1, 2, 3, 4], "y": [2, 3, 2, 4]}
        titulo = "Gráfico Dia 2"
    return {"layout": {"title": titulo}, "data": [pontos]}

@server.route("/nova_tela")
def nova_tela():
    return "Você está na página criada pelo Flask"

## Funcionalidades

- Registro de Usuário: Permite a criação de uma nova conta.
- Login de Usuário: Permite que um usuário existente faça login.
- Painel Interativo: Disponível apenas para usuários autenticados.
- Página de Erro: Mostra uma mensagem de erro para tentativas de login inválidas.
- Navbar Dinâmico: Atualiza-se com base no estado de autenticação do usuário.

## Rotas e Callbacks

###Callbacks
- carregar_pagina: Carrega a página correta com base no pathname.
- exibir_navbar: Atualiza a barra de navegação com links apropriados.
- criar_conta: Gerencia a criação de novas contas de usuário.
- login_usuario: Gerencia o processo de login.
 -atualizar_grafico: Atualiza o gráfico com base na seleção do dropdown.
