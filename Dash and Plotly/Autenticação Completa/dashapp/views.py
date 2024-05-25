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

# pathname
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
        # vou criar a conta
        # verificar se já existe um usuário com essa conta
        usuario  = Usuario.query.filter_by(email=email).first() # finalizar
        if usuario:
            return "/login"
        else:
            # criar o usuario
            senha_criptografada = bcrypt.generate_password_hash(senha).decode("utf-8")
            usuario = Usuario(email=email, senha=senha_criptografada) # 123456
            database.session.add(usuario)
            database.session.commit()
            login_user(usuario)
            return "/dashboard"
        
@app.callback(Output("login_url", "pathname"), Input("botao-login", "n_clicks"), 
              [State("email", "value"), State("senha", "value")])
def criar_conta(n_clicks, email, senha):
    if n_clicks:
        # vou criar a conta
        # verificar se já existe um usuário com essa conta
        usuario  = Usuario.query.filter_by(email=email).first() # finalizar
        if not usuario:
            return "/"
        else:
            # criar o usuario
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
