"""
Módulo storage.py
Responsável pela persistência de dados em arquivo JSON e operações procedurais auxiliares.
Autor: Rodrigo Henry Dortha Manancas (Matrícula: 202503754306)
"""

import json
import os
from typing import List, Tuple
from models import Cliente, Quarto, QuartoSolteiro, QuartoCasal, QuartoSuite, Reserva

ARQUIVO_DADOS = "dados_hotel.json"


def carregar_dados(caminho: str = ARQUIVO_DADOS) -> Tuple[List[Cliente], List[Quarto], List[Reserva]]:
    """Carrega clientes, quartos e reservas do arquivo JSON ou inicializa quartos padrão."""
    if not os.path.exists(caminho):
        quartos_iniciais = [
            QuartoSolteiro(101, 150.0),
            QuartoSolteiro(102, 150.0),
            QuartoCasal(201, 240.0),
            QuartoCasal(202, 240.0),
            QuartoSuite(301, 420.0),
        ]
        salvar_dados([], quartos_iniciais, [], caminho)
        return [], quartos_iniciais, []

    try:
        with open(caminho, "r", encoding="utf-8") as arq:
            conteudo = json.load(arq)
        clientes = [Cliente.from_dict(c) for c in conteudo.get("clientes", [])]
        quartos = [Quarto.from_dict(q) for q in conteudo.get("quartos", [])]
        reservas = [Reserva.from_dict(r) for r in conteudo.get("reservas", [])]
        return clientes, quartos, reservas
    except (json.JSONDecodeError, OSError, KeyError) as erro:
        print(f"[AVISO] Erro ao ler '{caminho}': {erro}. Inicializando base vazia.")
        return [], [], []


def salvar_dados(
    clientes: List[Cliente],
    quartos: List[Quarto],
    reservas: List[Reserva],
    caminho: str = ARQUIVO_DADOS,
) -> None:
    """Salva o estado atual do sistema em formato JSON."""
    dados = {
        "clientes": [c.to_dict() for c in clientes],
        "quartos": [q.to_dict() for q in quartos],
        "reservas": [r.to_dict() for r in reservas],
    }
    with open(caminho, "w", encoding="utf-8") as arq:
        json.dump(dados, arq, ensure_ascii=False, indent=4)
