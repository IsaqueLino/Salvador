class Usuario:

    def __init__(self):
        self.__idusuario = ''
        self.__nome = ''
        self.__email = ''
        self.__senha = ''

    @property
    def idusuario(self):
        return self.__idusuario

    @property
    def nome(self):
        return self.__nome

    @property
    def email(self):
        return self.__email

    @property
    def senha(self):
        return self.__senha

    @idusuario.setter
    def idusuario(self, entrada):
        self.__idusuario = entrada

    @nome.setter
    def nome(self, entrada):
        self.__nome = entrada

    @email.setter
    def email(self, entrada):
        self.__email = entrada

    @senha.setter
    def senha(self, entrada):
        self.__senha = entrada

    def setUsuario(self, idusuario, nome, email, senha):
        self.__idusuario = idusuario
        self.__nome = nome
        self.__email = email
        self.__senha = senha

    def inserirDados(self):
        sql = ("insert into usuario values ('{}','{}','{}','{}')".format(
            self.idusuario,
            self.nome,
            self.email,
            self.senha,
        ))
        print(sql)
        return sql

    def buscar(self):
        sql = "select count(*)+1 from usuario"
        return sql