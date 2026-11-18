"""
Módulo main.py
Ponto de entrada do Sistema de Reservas de Hotel (Interface CLI e subprogramas de menu).
Autor: Rodrigo Henry Dortha Manancas (Matrícula: 202503754306)
"""

from typing import List, Optional
from models import (
    Cliente,
    Quarto,
    QuartoSolteiro,
    QuartoCasal,
    QuartoSuite,
    Reserva,
    ReservaException,
    QuartoIndisponivelError,
    DataInvalidaError,
)
from storage import carregar_dados, salvar_dados


def buscar_cliente_por_documento(clientes: List[Cliente], documento: str) -> Optional[Cliente]:
    """Busca sequencialmente um cliente pelo CPF/documento."""
    doc_limpo = documento.strip()
    for cliente in clientes:
        if cliente.documento == doc_limpo:
            return cliente
    return None


def buscar_quarto_por_numero(quartos: List[Quarto], numero: int) -> Optional[Quarto]:
    """Busca um quarto pelo seu número."""
    for quarto in quartos:
        if quarto.numero == numero:
            return quarto
    return None


def verificar_disponibilidade(
    reservas: List[Reserva], numero_quarto: int, data_checkin: str, data_checkout: str
) -> bool:
    """Verifica se o quarto está livre no período informado."""
    dt_in = Reserva.validar_formato_data(data_checkin)
    dt_out = Reserva.validar_formato_data(data_checkout)
    if dt_out <= dt_in:
        raise DataInvalidaError("A data de check-out deve ser posterior à data de check-in.")

    for res in reservas:
        if res.quarto.numero == numero_quarto and res.conflita_com(dt_in, dt_out):
            return False
    return True


def cadastrar_cliente(clientes: List[Cliente]) -> None:
    print("\n--- CADASTRO DE CLIENTE ---")
    nome = input("Nome completo: ").strip()
    documento = input("CPF / Documento: ").strip()
    if not nome or not documento:
        print("[ERRO] Nome e documento são obrigatórios.")
        return
    if buscar_cliente_por_documento(clientes, documento):
        print("[ERRO] Já existe um cliente cadastrado com este documento.")
        return
    telefone = input("Telefone: ").strip()
    email = input("E-mail (opcional): ").strip()
    novo = Cliente(nome, documento, telefone, email)
    clientes.append(novo)
    print(f"[SUCESSO] Cliente cadastrado: {novo}")


def cadastrar_quarto(quartos: List[Quarto]) -> None:
    print("\n--- CADASTRO DE QUARTO ---")
    try:
        numero = int(input("Número do quarto: ").strip())
        if buscar_quarto_por_numero(quartos, numero):
            print("[ERRO] Já existe um quarto com esse número.")
            return
        print("Tipos: [1] Solteiro (R$ 150) | [2] Casal (R$ 240) | [3] Suíte (R$ 420)")
        opcao_tipo = input("Escolha o tipo (1-3): ").strip()
        diaria_str = input("Valor da diária base (Enter para valor padrão): ").strip()

        if opcao_tipo == "1":
            quarto = QuartoSolteiro(numero, float(diaria_str) if diaria_str else 150.0)
        elif opcao_tipo == "2":
            quarto = QuartoCasal(numero, float(diaria_str) if diaria_str else 240.0)
        elif opcao_tipo == "3":
            quarto = QuartoSuite(numero, float(diaria_str) if diaria_str else 420.0)
        else:
            print("[ERRO] Tipo de quarto inválido.")
            return

        quartos.append(quarto)
        print(f"[SUCESSO] Quarto adicionado: {quarto}")
    except ValueError:
        print("[ERRO] Entrada numérica inválida para número do quarto ou valor da diária.")


def realizar_reserva(clientes: List[Cliente], quartos: List[Quarto], reservas: List[Reserva]) -> None:
    print("\n--- NOVA RESERVA ---")
    doc = input("Informe o CPF/Documento do cliente: ").strip()
    cliente = buscar_cliente_por_documento(clientes, doc)
    if not cliente:
        print("[ERRO] Cliente não encontrado. Cadastre o cliente primeiro.")
        return

    try:
        num_quarto = int(input("Número do quarto desejado: ").strip())
        quarto = buscar_quarto_por_numero(quartos, num_quarto)
        if not quarto:
            print("[ERRO] Quarto não encontrado.")
            return

        checkin = input("Data de check-in (DD/MM/AAAA): ").strip()
        checkout = input("Data de check-out (DD/MM/AAAA): ").strip()

        if not verificar_disponibilidade(reservas, num_quarto, checkin, checkout):
            raise QuartoIndisponivelError(
                f"O Quarto {num_quarto} já está reservado no período de {checkin} a {checkout}."
            )

        novo_id = len(reservas) + 1
        nova_reserva = Reserva(novo_id, cliente, quarto, checkin, checkout)
        reservas.append(nova_reserva)
        print(f"[SUCESSO] Reserva confirmada!\n{nova_reserva}")

    except ValueError:
        print("[ERRO] O número do quarto deve ser um valor inteiro.")
    except ReservaException as erro_negocio:
        print(f"[ERRO DE RESERVA] {erro_negocio}")


def cancelar_reserva(reservas: List[Reserva]) -> None:
    print("\n--- CANCELAMENTO DE RESERVA ---")
    try:
        id_busca = int(input("Informe o ID da reserva a cancelar: ").strip())
        for res in reservas:
            if res.id_reserva == id_busca:
                if res.status == "Cancelada":
                    print("[AVISO] Esta reserva já se encontra cancelada.")
                    return
                res.status = "Cancelada"
                print(f"[SUCESSO] Reserva #{id_busca:03d} cancelada com sucesso.")
                return
        print("[ERRO] Reserva não localizada.")
    except ValueError:
        print("[ERRO] Digite um número de ID válido.")


def listar_dados(clientes: List[Cliente], quartos: List[Quarto], reservas: List[Reserva]) -> None:
    print("\n================ QUARTOS CADASTRADOS ================")
    for q in quartos:
        print(" •", q)
    print("\n================ CLIENTES CADASTRADOS ===============")
    if not clientes:
        print(" (Nenhum cliente cadastrado)")
    for c in clientes:
        print(" •", c)
    print("\n================ HISTÓRICO DE RESERVAS ==============")
    if not reservas:
        print(" (Nenhuma reserva registrada)")
    for r in reservas:
        print(" •", r)


def exibir_menu() -> None:
    print("\n=====================================================")
    print("        SISTEMA DE RESERVAS DE HOTEL - BELÉM         ")
    print("=====================================================")
    print(" [1] Cadastrar Cliente")
    print(" [2] Cadastrar Quarto")
    print(" [3] Realizar Reserva")
    print(" [4] Cancelar Reserva")
    print(" [5] Listar Quartos, Clientes e Reservas")
    print(" [0] Salvar e Sair")
    print("=====================================================")


def main() -> None:
    clientes, quartos, reservas = carregar_dados()
    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "1":
            cadastrar_cliente(clientes)
            salvar_dados(clientes, quartos, reservas)
        elif opcao == "2":
            cadastrar_quarto(quartos)
            salvar_dados(clientes, quartos, reservas)
        elif opcao == "3":
            realizar_reserva(clientes, quartos, reservas)
            salvar_dados(clientes, quartos, reservas)
        elif opcao == "4":
            cancelar_reserva(reservas)
            salvar_dados(clientes, quartos, reservas)
        elif opcao == "5":
            listar_dados(clientes, quartos, reservas)
        elif opcao == "0":
            salvar_dados(clientes, quartos, reservas)
            print("Dados salvos em 'dados_hotel.json'. Encerrando o sistema...")
            break
        else:
            print("[ERRO] Opção inválida! Escolha entre 0 e 5.")


if __name__ == "__main__":
    main()
