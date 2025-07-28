import textwrap
from abc import ABC, abstractmethod
from datetime import datetime


class Usuario:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_operacao(self, conta, operacao):
        operacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Usuario):
    def __init__(self, nome, nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.nascimento = nascimento
        self.cpf = cpf


class ContaBancaria:
    def __init__(self, numero, usuario):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._usuario = usuario
        self._historico = Historico()

    @classmethod
    def criar_conta(cls, usuario, numero):
        return cls(numero, usuario)

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
    def usuario(self):
        return self._usuario

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor > self._saldo:
            print("\n@@@ Saldo insuficiente. @@@")
        elif valor > 0:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Valor inválido para saque. @@@")
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Valor inválido para depósito. @@@")
            return False


class ContaCorrente(ContaBancaria):
    def __init__(self, numero, usuario, limite=500, max_saques=3):
        super().__init__(numero, usuario)
        self._limite = limite
        self._max_saques = max_saques

    def sacar(self, valor):
        saques_realizados = len([
            operacao for operacao in self.historico.transacoes
            if operacao["tipo"] == Saque.__name__
        ])

        if valor > self._limite:
            print("\n@@@ Valor do saque excede o limite. @@@")
        elif saques_realizados >= self._max_saques:
            print("\n@@@ Limite de saques diários excedido. @@@")
        else:
            return super().sacar(valor)
        return False

    def __str__(self):
        return f"""
        Agência:	{self.agencia}
        Conta:		{self.numero}
        Titular:	{self.usuario.nome}
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


class Operacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Operacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


class Deposito(Operacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)


def exibir_menu():
    menu = """
    ================ MENU ================
    [d] Depositar
    [s] Sacar
    [e] Extrato
    [nc] Nova conta
    [lc] Listar contas
    [nu] Novo usuário
    [q] Sair
    => """
    return input(textwrap.dedent(menu))


def localizar_usuario(cpf, usuarios):
    return next((u for u in usuarios if u.cpf == cpf), None)


def recuperar_conta(usuario):
    if not usuario.contas:
        print("\n@@@ Usuário não possui conta. @@@")
        return
    return usuario.contas[0]


def fazer_deposito(usuarios):
    cpf = input("CPF do usuário: ")
    usuario = localizar_usuario(cpf, usuarios)

    if not usuario:
        print("\n@@@ Usuário não encontrado. @@@")
        return

    valor = float(input("Valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta(usuario)
    if conta:
        usuario.realizar_operacao(conta, transacao)


def fazer_saque(usuarios):
    cpf = input("CPF do usuário: ")
    usuario = localizar_usuario(cpf, usuarios)

    if not usuario:
        print("\n@@@ Usuário não encontrado. @@@")
        return

    valor = float(input("Valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta(usuario)
    if conta:
        usuario.realizar_operacao(conta, transacao)


def mostrar_extrato(usuarios):
    cpf = input("CPF do usuário: ")
    usuario = localizar_usuario(cpf, usuarios)

    if not usuario:
        print("\n@@@ Usuário não encontrado. @@@")
        return

    conta = recuperar_conta(usuario)
    if not conta:
        return

    print("\n============= EXTRATO =============")
    transacoes = conta.historico.transacoes
    if not transacoes:
        print("Nenhuma movimentação registrada.")
    else:
        for t in transacoes:
            print(f"{t['tipo']}: R$ {t['valor']:.2f} em {t['data']}")

    print(f"\nSaldo atual: R$ {conta.saldo:.2f}")
    print("==================================")


def cadastrar_usuario(usuarios):
    cpf = input("CPF (apenas números): ")
    if localizar_usuario(cpf, usuarios):
        print("\n@@@ CPF já cadastrado. @@@")
        return

    nome = input("Nome completo: ")
    nascimento = input("Data de nascimento (dd-mm-aaaa): ")
    endereco = input("Endereço (logradouro, nro - bairro - cidade/UF): ")

    usuario = PessoaFisica(nome, nascimento, cpf, endereco)
    usuarios.append(usuario)
    print("\n=== Usuário criado com sucesso! ===")


def criar_nova_conta(numero, usuarios, contas):
    cpf = input("CPF do usuário: ")
    usuario = localizar_usuario(cpf, usuarios)

    if not usuario:
        print("\n@@@ Usuário não encontrado. @@@")
        return

    conta = ContaCorrente.criar_conta(usuario, numero)
    contas.append(conta)
    usuario.adicionar_conta(conta)
    print("\n=== Conta criada com sucesso! ===")


def listar_todas_contas(contas):
    for conta in contas:
        print("=" * 50)
        print(conta)


def main():
    usuarios = []
    contas = []

    while True:
        opcao = exibir_menu()

        if opcao == "d":
            fazer_deposito(usuarios)
        elif opcao == "s":
            fazer_saque(usuarios)
        elif opcao == "e":
            mostrar_extrato(usuarios)
        elif opcao == "nu":
            cadastrar_usuario(usuarios)
        elif opcao == "nc":
            numero = len(contas) + 1
            criar_nova_conta(numero, usuarios, contas)
        elif opcao == "lc":
            listar_todas_contas(contas)
        elif opcao == "q":
            break
        else:
            print("\n@@@ Opção inválida. Tente novamente. @@@")


main()
