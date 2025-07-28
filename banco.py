import textwrap
from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.nascimento = nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def criar_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor <= 0:
            print("\n@@@ Valor inválido para saque. @@@")
            return False

        if valor > self._saldo:
            print("\n@@@ Saldo insuficiente. @@@")
            return False

        self._saldo -= valor
        print("\n=== Saque efetuado com sucesso! ===")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("\n@@@ Valor inválido para depósito. @@@")
            return False

        self._saldo += valor
        print("\n=== Depósito efetuado com sucesso! ===")
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, max_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._max_saques = max_saques

    def sacar(self, valor):
        saques_efetuados = [t for t in self.historico.transacoes if t["tipo"] == "Saque"]

        if len(saques_efetuados) >= self._max_saques:
            print("\n@@@ Limite de saques excedido. @@@")
            return False

        if valor > self._limite:
            print("\n@@@ Valor excede o limite permitido. @@@")
            return False

        return super().sacar(valor)

    def __str__(self):
        return f"""
        Agência:	{self.agencia}
        Número:	{self.numero}
        Cliente:	{self.cliente.nome}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        })


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)
