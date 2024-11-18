from backend.model.chat import Chat
class Mensagem:

    def __init__(self):
        self.__idmensagem = ''
        self.__conteudo = ''
        self.__origem = ''
        self.__idchat = Chat()
        self.__data = ''

    @property
    def idmensagem(self):
        return self.__idmensagem

    @property
    def conteudo(self):
        return self.__conteudo

    @property
    def origem(self):
        return self.__origem

    @property
    def idchat(self):
        return self.__idchat

    @property
    def data(self):
        return self.__data

    @idmensagem.setter
    def idmensagem(self, entrada):
        self.__idmensagem = entrada

    @conteudo.setter
    def conteudo(self, entrada):
        self.__conteudo = entrada

    @origem.setter
    def origem(self, entrada):
        self.__origem = entrada

    @idchat.setter
    def idchat(self, entrada):
        self.__idchat = entrada

    @data.setter
    def data(self, entrada):
        self.__data = entrada

    def setMensagem(self, idmensagem, conteudo, origem, idchat, data):
        self.__idmensagem = idmensagem
        self.__conteudo = conteudo
        self.__origem = origem
        self.__idchat = idchat
        self.__data = data

    def inserirDados(self):
        sql = ("insert into mensagem values ('{}','{}','{}','{}','{}')".format(
            self.idmensagem,
            self.conteudo,
            self.origem,
            self.idchat,
            self.data
        ))
        print(sql)
        return sql

    def deletar(self):
        sql = ("delete from mensagem where idchat = '{}'".format(
            self.idchat
        ))
        print(sql)
        return sql


    def buscar(self):
        sql = "select count(*)+1 from mensagem"
        return sql