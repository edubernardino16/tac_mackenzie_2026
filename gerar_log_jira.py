"""Gera uma tabela de log de alterações do Jira a partir da base de cards."""

from __future__ import annotations

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

from gerar_base_csv import STATUS_BUG, STATUS_INICIATIVE, STATUS_PADRAO

CAMPOS_LOG = (
    "Card",
    "Data da alteração",
    "Objeto alterado",
    "Valor anterior",
    "Valor posterior",
)


def ler_cards(caminho: Path) -> list[dict[str, str]]:
    """Lê a base principal de cards."""
    with caminho.open("r", newline="", encoding="utf-8-sig") as arquivo:
        return list(csv.DictReader(arquivo))


def parse_data(valor: str) -> date | None:
    """Converte string ISO em date, retornando None se vazia."""
    if not valor:
        return None
    return date.fromisoformat(valor)


def data_entre(inicio: date, fim: date, gerador: random.Random) -> date:
    """Retorna uma data aleatória entre inicio e fim, inclusive."""
    delta = (fim - inicio).days
    if delta <= 0:
        return inicio
    return inicio + timedelta(days=gerador.randint(0, delta))


def status_disponiveis_por_tipo(tipo: str) -> list[str]:
    """Retorna a lista de status válida para o tipo do card."""
    if tipo == "INICIATIVE":
        return list(STATUS_INICIATIVE)
    if tipo in {"BUG", "BUG SUBTASK"}:
        return list(STATUS_PADRAO[:-2] + STATUS_BUG)
    return list(STATUS_PADRAO[:-2])


def transicoes_status(card: dict[str, str]) -> list[tuple[str, str]]:
    """Cria a sequência de transições de status a partir do status atual do card."""
    tipo = card.get("Tipo de Card", "")
    status_atual = card.get("Status", "")
    lista_status = status_disponiveis_por_tipo(tipo)

    if not status_atual or status_atual not in lista_status:
        return []

    indice_atual = lista_status.index(status_atual)
    if indice_atual <= 0:
        return []

    return [
        (lista_status[indice - 1], lista_status[indice])
        for indice in range(1, indice_atual + 1)
    ]


def gerar_log_jira(cards: list[dict[str, str]], seed: int = 42) -> list[dict[str, str]]:
    """Cria um histórico de transição de status para cada card."""
    gerador = random.Random(seed)
    logs: list[dict[str, str]] = []

    for card in cards:
        card_id = card["ID Card"]
        data_criacao = parse_data(card["Data de Criação"])
        if data_criacao is None:
            continue

        data_resolucao = parse_data(card["Data de resolução"])
        data_fim = data_resolucao or data_criacao + timedelta(days=gerador.randint(10, 60))
        transicoes = transicoes_status(card)

        if not transicoes:
            continue

        total_transicoes = len(transicoes)
        intervalo_total = max(1, (data_fim - data_criacao).days)

        for indice, (valor_anterior, valor_posterior) in enumerate(transicoes, start=1):
            offset = round((intervalo_total * indice) / (total_transicoes + 1))
            data_alteracao = data_criacao + timedelta(days=offset)
            logs.append(
                {
                    "Card": card_id,
                    "Data da alteração": data_alteracao.isoformat(),
                    "Objeto alterado": "status",
                    "Valor anterior": valor_anterior,
                    "Valor posterior": valor_posterior,
                }
            )

    return logs


def salvar_log(logs: list[dict[str, str]], caminho: Path) -> None:
    """Salva a tabela de log em CSV."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_LOG)
        escritor.writeheader()
        escritor.writerows(logs)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=Path("base_cards.csv"))
    parser.add_argument("--saida", type=Path, default=Path("log_jira.csv"))
    parser.add_argument("--seed", type=int, default=42)
    argumentos = parser.parse_args()

    cards = ler_cards(argumentos.entrada)
    if not cards:
        raise ValueError(f"Nenhum card encontrado em {argumentos.entrada}")

    logs = gerar_log_jira(cards, argumentos.seed)
    salvar_log(logs, argumentos.saida)
    print(f"Log Jira criado: {argumentos.saida} ({len(logs)} registros)")


if __name__ == "__main__":
    main()
