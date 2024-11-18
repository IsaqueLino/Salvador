import os
import re
from backend.dao.persistence import Banco
from dotenv import load_dotenv
load_dotenv()

'''
' OR '1'='1
'''

class Controle:

    def __init__(self):
        dbsenha = os.getenv("SENHA_DB_GOSTOS")
        dbusuario = os.getenv("USUARIO_DB_GOSTOS")
        dbbanco = os.getenv("BANCO_DB_GOSTOS")
        dbhost = os.getenv("HOST_DB_GOSTOS")
        self.ob = Banco()
        self.ob.configura(ho=dbhost, db=dbbanco, us=dbusuario, se=dbsenha)

    def verificar_login(self, email):
        mail = re.sub(r'[^a-zA-Z0-9@._-]', '', email)
        mail = mail.replace("'", "''")

        self.ob.abrirConexao()
        sql = f"select * from usuario where email = '{mail}'"
        resultado = []
        resultado = self.ob.selectQuery(sql)

        if resultado:
            return resultado
        else:
            return None

    def verificar_email(self, email):
        email = re.sub(r'[^a-zA-Z0-9@._-]', '', email)

        email = email.replace("'", "''")
        self.ob.abrirConexao()
        sql = f"select email from usuario where email = '{email}'"
        resultado = self.ob.selectQuery(sql)
        if resultado:
            email = resultado[0][0]
            return email
        else:
            return None

    def inserir_usuario(self):
        self.ob.abrirConexao()
        sql = f"select count(*)+1 from usuario"
        resultado = self.ob.selectQuery(sql)
        quantidade = resultado
        if resultado:
            return quantidade
        else:
            return None

    def inserir_chat(self):
        self.ob.abrirConexao()
        sql = f"select count(*)+1 from chat"
        resultado = self.ob.selectQuery(sql)
        quantidade = resultado[0][0]
        if resultado:
            return quantidade
        else:
            return None

    def inserir_mensagem(self):
        self.ob.abrirConexao()
        sql = f"select count(*)+1 from mensagem"
        resultado = self.ob.selectQuery(sql)
        quantidade = resultado[0][0]
        if resultado:
            return quantidade
        else:
            return None

    def buscar_usuario(self):
        self.ob.abrirConexao()
        sql = f"select * from usuario"
        resultado = []
        resultado = self.ob.selectQuery(sql)
        if resultado:
            return resultado
        else:
            return None

    def buscar_chats(self, idusuario):
        self.ob.abrirConexao()
        sql = f"select * from chat where idusuario= '{idusuario}'"
        resultado = self.ob.selectQuery(sql)
        if resultado:
            print(resultado)
            return resultado
        else:
            return None

    def checar_chats(self, idchat):
        self.ob.abrirConexao()
        sql = f"select * from chat where idchat= '{idchat}'"
        resultado = self.ob.selectQuery(sql)
        if resultado:
            print(resultado)
            return resultado
        else:
            return None

    def buscar_msg(self, idchat):
        self.ob.abrirConexao()
        sql = f"select * from mensagem where idchat= '{idchat}'"
        resultado = self.ob.selectQuery(sql)
        if resultado:
            return resultado
        else:
            return None

    def buscar_ultima_msg(self, idchat):
        self.ob.abrirConexao()
        sql = f"select conteudo from mensagem where idchat = '{idchat}' and origem = 1 order by idmensagem desc limit 1"
        resultado = self.ob.selectQuery(sql)
        if resultado:
            return resultado
        else:
            return None
    def incluir(self, info):
        self.ob.abrirConexao()

        sql = info

        try:
            self.ob.execute(sql)
            self.ob.gravar()
        except:
            print("Houve um erro")
            self.ob.descarte()

    def pesquisar(self, info):
        self.ob.abrirConexao()
        dados = self.ob.selectQuery(info)
        dados = dados[0]
        return dados

    def excluir(self, info):
        self.ob.abrirConexao()
        sql = info
        try:
            self.ob.execute(sql)
            self.ob.gravar()
        except:
            print("Houve um erro ao excluir o registro")
            self.ob.descarte()

    def alterar(self, info):
        self.ob.abrirConexao()
        sql = info
        try:
            self.ob.execute(sql)
            self.ob.gravar()
        except:
            print("Houve um erro ao alterar o registro")
            self.ob.descarte()
