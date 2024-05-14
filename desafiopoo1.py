from abc import ABC, abstractmethod
from datetime import datetime
import textwrap  # Adicionando a importação necessária


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_trans(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nasci, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nasci = data_nasci
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
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
        saldo = self._saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n ---- Operacao falhou! Você não possui saldo suficiente.---")

        elif valor > 0:
            self._saldo -= valor
            print("\n --- Saque realizado com sucesso! ----")
            return True

        else:
            print("\n--- Operacao falhou! o valor informado é invalido ----")
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n --- Deposito realizado com sucesso! ---")
            return True

        else:
            print("\n --- Operacao falhou! o valor informado é invalido! ---")
            return False


class ContaCorrente(Conta):  # Corrigindo a herança
    def __init__(self, numero, cliente, limite=500, limite_saque=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saque = limite_saque

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacao
             if transacao[1] == "Saque"]
        )

        excedeu_limite = valor > self.limite
        excedeu_numero_saques = numero_saques >= self.limite_saque

        if excedeu_limite:
            print("\n --- Operacao falhou! Valor do saque excedeu o limite. ---")

        elif excedeu_numero_saques:
            print("\n --- Operacao falhou! Numero maximo de saques excedeu o limite. ---")

        else:
            return super().sacar(valor)
        return False

    def __str__(self):
        return f"""\
            Agencia: \t{self.agencia}
            C/C: \t\t{self.numero}
            Titular:\t{self.cliente.nome}
            """


class Historico:
    def __init__(self):
        self._transacao = []

    @property
    def transacao(self):
        return self._transacao

    def adicionar_transacao(self, transacao):
        self._transacao.append((
            "Tipo:", transacao.__class__.__name__,
            "Valor:", transacao.valor,
            "Data:", datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        ))


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
        sucesso_trans = conta.sacar(self.valor)

        if sucesso_trans:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_trans = conta.depositar(self.valor)

        if sucesso_trans:
            conta.historico.adicionar_transacao(self)


def menu():
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [
        cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n--- Cliente não possui conta! ---")
        return None

    print("\n=== Contas do cliente ===")
    for i, conta in enumerate(cliente.contas, 1):
        print(f"{i}. {conta}")

    escolha = int(input("Escolha o número da conta: "))
    return cliente.contas[escolha - 1]


def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n--- Cliente não encontrado!---")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_trans(conta, transacao)


def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n--- Cliente não encontrado! ---")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_trans(conta, transacao)


def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n--- Cliente não encontrado! ---")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacao

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")


def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n---Já existe cliente com esse CPF! ---")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input(
        "Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(
        nome=nome, data_nasci=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n--- Cliente não encontrado, fluxo de criação de conta encerrado! ---")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print(
                "\n---Operação inválida, por favor selecione novamente a operação desejada.---")


main()
