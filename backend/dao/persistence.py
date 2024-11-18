import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
class Banco:

    def __init__(self):
        dbsenha = os.getenv("SENHA_DB_GOSTOS")
        dbusuario = os.getenv("USUARIO_DB_GOSTOS")
        dbbanco = os.getenv("BANCO_DB_GOSTOS")
        dbhost = os.getenv("HOST_DB_GOSTOS")

        self.servidor = dbhost
        self.usuario = dbusuario
        self.senha = dbsenha
        self.banco = dbbanco
        self.ponteiro = None
        self.con = None

    def abrirConexao(self):
        try:
            self.con = psycopg2.connect(
                host=self.servidor,
                database=self.banco,
                user=self.usuario,
                password=self.senha,
                port='6543',
                options='-c client_encoding=UTF8'
            )
            self.ponteiro = self.con.cursor()
        except UnicodeDecodeError as e:
            print(f"Erro de decodificação: {e}")
        except Exception as e:
            print(f"Erro ao conectar ao banco: {e}")

    def selectQuery(self, entrada):
        if self.ponteiro is None:
            print("Erro: Conexão não estabelecida.")
            return None
        self.ponteiro.execute(entrada)
        resposta = self.ponteiro.fetchall()
        return resposta

    def executeQuery(self, entrada, dados):
        if self.ponteiro is None:
            print("Erro: Conexão não estabelecida.")
            return
        self.ponteiro.execute(entrada, dados)

    def execute(self, entrada):
        if self.ponteiro is None:
            print("Erro: Conexão não estabelecida.")
            return
        self.ponteiro.execute(entrada)

    def gravar(self):
        if self.con:
            self.con.commit()

    def descarte(self):
        if self.con:
            self.con.rollback()

    def configura(self, ho, db, se=os.getenv("SENHA_DB_GOSTOS"), us=os.getenv("USUARIO_DB_GOSTOS")):
        self.servidor = ho
        self.usuario = us
        self.senha = se
        self.banco = db

    def mostraResultado(self, entrada):
        for i in entrada:
            print(i)
