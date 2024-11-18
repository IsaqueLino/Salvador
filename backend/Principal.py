import datetime
import bcrypt

import requests
from bs4 import BeautifulSoup
from backend.db import get_db

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from sqlalchemy.orm import sessionmaker

from backend.controller.controle import Controle
from backend.model.usuario import Usuario
from backend.model.chat import Chat
from backend.model.mensagem import Mensagem

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine

import secrets
import os

from backend.tools import *
from langchain.agents import create_tool_calling_agent
from langchain.tools import StructuredTool
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from werkzeug.security import generate_password_hash

app = Flask(__name__, static_folder='../static', template_folder='../templates')
app.secret_key = secrets.token_urlsafe(32)

controle = Controle()
usuario = Usuario()
chat = Chat()
mensagem = Mensagem()

load_dotenv()

def get_engine_for_db():
    user = os.getenv("USUARIO_DB_GOSTOS")
    password = os.getenv("SENHA_DB_GOSTOS")
    host = os.getenv("HOST_DB_GOSTOS")
    database = os.getenv("BANCO_DB_GOSTOS")
    db = next(get_db())

    try:
        engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}/{database}")
        session_local_read_only = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        read_only_db = session_local_read_only()
        yield read_only_db

    finally:
        db.close()

def get_engine_db():
    user = os.getenv("USUARIO_DB_GOSTOS")
    password = os.getenv("SENHA_DB_GOSTOS")
    host = os.getenv("HOST_DB_GOSTOS")
    database = os.getenv("BANCO_DB_GOSTOS")

    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}/{database}")

    return engine

engine = get_engine_db()

db = SQLDatabase(engine)

class FunctionsTools:
    def __init__(self, assistantPrompt, llmModel):
        self.llm = llmModel

        #showTablesFunction = ShowTablesTool()
        consultDatabaseFunction = ConsultDatabaseTool()
        #deleteDatabaseFunction = DeleteDatabaseTool()
        updateDatabaseFunction = UpdateDatabaseTool()
        insertDatabaseFunction = InsertDatabaseTool()

        # Lista de ferramentas disponíveis
        self.tools = [
            StructuredTool(
                name=consultDatabaseFunction.name,
                func=consultDatabaseFunction.run,
                description=consultDatabaseFunction.description,
                return_direct=False,
                args_schema=ArgsConsultDatabase
            ),
            StructuredTool(
                name=updateDatabaseFunction.name,
                func=updateDatabaseFunction.run,
                description=updateDatabaseFunction.description,
                return_direct=False,
                args_schema=ArgsUpdateDatabase
            ),
            StructuredTool(
                name=insertDatabaseFunction.name,
                func=insertDatabaseFunction.run,
                description=insertDatabaseFunction.description,
                return_direct=False,
                args_schema=ArgsInsertDatabase
            )
        ]
        self.agent = create_tool_calling_agent(llm=self.llm, prompt=assistantPrompt, tools=self.tools)

def get_complete_agent(prompt, llm):
    return FunctionsTools(prompt, llm)

def get_model():
    return ChatGoogleGenerativeAI(
        api_key=os.getenv("GEMINI_KEY_API"),
        model="gemini-1.5-flash",
        temperature=0.6,
        max_tokens=None,
        timeout=None,
        streaming=False
    )

def get_prompt(systemPrompt, question: str, file: str):
    return ChatPromptTemplate.from_messages(
        [
            ("system", systemPrompt.format(
                file=file,
            )),
            MessagesPlaceholder("history"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ]
    )

def invoke(chatHistory, pergunta, file_content, memory_type):
    prompt_text = rf"""Você irá receber uma informação contendo título, capítulo/episódio, site e gênero (manga, anime ou dorama). Sua tarefa é separar esses dados e, em seguida, realizar a inserção na base de dados. Dependendo do gênero, os dados devem ser inseridos na tabela correspondente:

- Se for **anime**, insira na tabela **animes**.
- Se for **manga**, **manhwa** ou outro gênero relacionado, insira na tabela **mangas**.
- Se for **dorama**, insira na tabela **doramas**.

Caso o título JÁ EXISTA na base de dados, realize um **update** nas informações correspondentes.

A resposta deve ser estruturada da seguinte forma **IMPORTANTE** USE \\n:
1. Título: [Título encontrado]
2. Capítulo/Episódio: [Capítulo ou Episódio encontrado ou 'Na lista' caso não haja informação para indicar que não teve inicio]
3. Site: [Site encontrado]
4. Gênero: [Gênero encontrado - pode ser manga, anime ou dorama]

Essa é as informações do banco de dados: {db.get_table_info()} insira o idusuario também
    """

    try:
        chainModel = get_model()
        print("ChainModel criado")
    except Exception as e:
        print(e)
        return f"Ocorreu um erro ao obter o modelo selecionado: {e}"

    if memory_type == "kMessages":
        prompt = get_prompt(prompt_text, pergunta, file_content)

        try:
            agente = get_complete_agent(prompt, chainModel)
            print("Agente criado")
        except Exception as e:
            print(e)
            return f"Ocorreu um erro ao obter o agente: {e}"

        try:
            executor = AgentExecutor(agent=agente.agent, tools=agente.tools, verbose=True)
            print("Executor criado")
        except Exception as e:
            print(e)
            return f"Ocorreu um erro ao criar o executor do agente: {e}"

        try:
            return executor.invoke({"input": pergunta, 'history': chatHistory})
        except Exception as e:
            print(e)
            return f"Ocorreu um erro ao executar o agente: {e}"

def separar_texto_url(mensagem):
    match = re.search(r"(.*?)(https?://\S+)", mensagem)
    if match:
        texto = match.group(1).strip()
        url = match.group(2).strip()
        return texto, url
    else:
        return mensagem, None

def get_page_title(msg, historico, idusuario):
    try:
        texto, url = separar_texto_url(msg)
        title = ""
        if url:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Verifica se houve algum erro na requisição
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "Título não encontrado"

        chatHistory = []
        file_content = []
        res = invoke(pergunta=f"Instrução: {texto}, dados: {title}, idusuario: {idusuario}", file_content=file_content, memory_type="kMessages", chatHistory=chatHistory)
        return res
    except requests.RequestException as e:
        return f"Erro ao acessar a URL: {e}"

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario_logado' in session:
        return redirect(url_for('chatbot'))

    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        resultado = controle.verificar_login(email)

        if not bcrypt.checkpw(
                senha.encode("utf-8"), resultado[0][3].encode("utf-8")
        ):
            print("Tente novamente")
            return render_template('login.html')

        if resultado:
            usuariologado = resultado
            session['usuario_logado'] = usuariologado

            usuario.idusuario = resultado[0][0]
            usuario.nome = resultado[0][1]
            usuario.email = resultado[0][2]
            usuario.senha = resultado[0][3]

            return redirect(url_for('chatbot'))

    return render_template('login.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        hashed_password = hash_password(senha)

        novocadastro = Usuario()

        resut = controle.inserir_usuario()
        novocadastro.idusuario = resut[0][0]
        novocadastro.nome = nome
        novocadastro.email = email
        novocadastro.senha = hashed_password

        alu = novocadastro.inserirDados()
        controle.incluir(alu)
        return render_template('login.html')

    return render_template('cadastro.html')


@app.route('/chatbot')
def chatbot():
    if 'usuario_logado' in session:
        usuariologado = session['usuario_logado']
        quantidadechat = controle.inserir_chat()
        chats = controle.buscar_chats(usuario.idusuario)
        if chats is None:
            chats = []

        return render_template('chatbot.html', usuario=usuariologado, chats=chats,
                               quantidade=quantidadechat, chat_id=0)
    else:
        return render_template('login.html')


@app.route('/excluir_chat', methods=['POST'])
def excluir_chat():
    data = request.get_json()
    chat_id = data.get('chatId')

    msgs = Mensagem()
    chatt = Chat()

    msgs.idchat = chat_id
    dmsg = msgs.deletar()
    controle.excluir(dmsg)

    chatt.idchat = chat_id
    chatt.idusuario = usuario.idusuario
    dchat = chatt.deletar()
    controle.excluir(dchat)

    return jsonify({'status': 'success', 'message': 'Chat excluído com sucesso'})


@app.route('/chatbot/<int:chat_id>', methods=['GET', 'POST'])
def chatbotMSG(chat_id):
    checagem = controle.checar_chats(chat_id)
    quantidadechat = controle.inserir_chat()
    if checagem is None or chat_id == 0:
        chat.idchat = quantidadechat
        chat.titulo = 'Nova conversa'
        chat.idusuario = usuario.idusuario
        chat.data = datetime.now().date()

        '''talvez de erro'''
        chat_id = quantidadechat

        newchat = chat.inserirDados()
        controle.incluir(newchat)

    messages = controle.buscar_msg(chat_id)
    if messages is None:
        messages = []

    if 'usuario_logado' in session:
        usuariologado = session['usuario_logado']
        chats = controle.buscar_chats(usuario.idusuario)
        if chats is None:
            chats = []

        return render_template('chatbot.html', usuario=usuariologado, chats=chats, mensagens=messages,
                               quantidade=quantidadechat, chat_id=chat_id)
    else:
        return render_template('login.html')


@app.route('/retornar_msgGEMINI', methods=['GET'])
def retornar_msgGEMINI():
    chat_id = request.args.get('chat_id', type=int)
    if not chat_id:
        return jsonify({"error": "chat_id não fornecido"}), 400

    ultimaMsgG = controle.buscar_ultima_msg(chat_id)

    if ultimaMsgG is None:
        return jsonify({"error": "Nenhuma mensagem encontrada para o chat_id fornecido"}), 404

    return jsonify({"ultimaMsgG": ultimaMsgG}), 200


@app.route('/save_message', methods=['POST'])
def save_message():
    data = request.get_json()
    content = data.get('content')
    chat_id = data.get('chatId')
    origin = data.get('origin')
    originbot = data.get('originbot')

    if not 'usuario_logado' in session or usuario.idusuario == 0:
        return render_template('login.html')

    if chat_id == 0:
        quantidadechat = controle.inserir_chat()
        chat.idchat = quantidadechat
        chat.titulo = 'Nova conversa'
        chat.idusuario = usuario.idusuario
        chat.data = datetime.now().date()
        newchat = chat.inserirDados()
        controle.incluir(newchat)
        chat_id = quantidadechat

    try:
        historico = controle.buscar_msg(chat_id)

        mensagem.idmensagem = controle.inserir_mensagem()
        mensagem.conteudo = content.replace("'", "''")
        mensagem.origem = origin
        mensagem.idchat = chat_id
        mensagem.data = datetime.now().date()
        newmsg = mensagem.inserirDados()
        controle.incluir(newmsg)

        content_agent = get_page_title(content, historico, usuario.idusuario)

        if isinstance(content_agent, dict):
            content_agent = content_agent.get('output', '')
        mensagem.conteudo = content_agent.replace("'", "''")

        mensagem.idmensagem = controle.inserir_mensagem()
        mensagem.origem = originbot
        mensagem.idchat = chat_id
        mensagem.data = datetime.now().date()
        newmsg = mensagem.inserirDados()
        controle.incluir(newmsg)

    except Exception as e:
        print(f"Erro no save_message: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({'status': 'success'}), 200


@app.route('/rename_chat', methods=['POST'])
def rename_chat():
    data = request.get_json()
    new_name = data.get('newName')
    chat_id = data.get('chatId')

    if not data or 'newName' not in data or 'chatId' not in data:
        return jsonify({'error': 'Dados inválidos'}), 400

    newNameChat = Chat()
    newNameChat.idchat = chat_id
    newNameChat.titulo = new_name
    newNameChat.idusuario = usuario.idusuario

    newnc = newNameChat.alterar()

    try:
        controle.alterar(newnc)
    except Exception as e:
        print(f"Erro ao alterar o chat: {e}")
        return jsonify({"error": "Failed to update chat"}), 500

    return jsonify({"success": "Chat updated successfully"})


@app.route('/sair', methods=['GET', 'POST'])
def sair():
    session.pop('usuario_logado', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
