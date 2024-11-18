from backend.model.usuario import Usuario
class Chat:

    def __init__(self):
        self.__idchat = ''
        self.__titulo = ''
        self.__idusuario = Usuario()
        self.__data = ''

    @property
    def idchat(self):
        return self.__idchat

    @property
    def titulo(self):
        return self.__titulo

    @property
    def idusuario(self):
        return self.__idusuario

    @property
    def data(self):
        return self.__data

    @idchat.setter
    def idchat(self, entrada):
        self.__idchat = entrada

    @titulo.setter
    def titulo(self, entrada):
        self.__titulo = entrada

    @idusuario.setter
    def idusuario(self, entrada):
        self.__idusuario = entrada

    @data.setter
    def data(self, entrada):
        self.__data = entrada

    def setChat(self, idchat, titulo, idusuario, data):
        self.__idchat = idchat
        self.__titulo = titulo
        self.__idusuario = idusuario
        self.__data = data

    def inserirDados(self):
        sql = ("insert into chat values ('{}','{}','{}','{}')".format(
            self.idchat,
            self.titulo,
            self.idusuario,
            self.data
        ))
        print(sql)
        return sql

    def alterar(self):
        sql = ("update chat set titulo = '{}' where idchat = '{}' and idusuario = '{}'".format(
            self.titulo,
            self.idchat,
            self.idusuario
        ))
        print(sql)
        return sql

    def deletar(self):
        sql = ("delete from chat where idchat = '{}' and idusuario = '{}'".format(
            self.idchat,
            self.idusuario
        ))
        print(sql)
        return sql

    def buscar(self):
        sql = "select count(*)+1 from chat"
        return sql