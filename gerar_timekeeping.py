"""Gera a tabela timekeeping com apontamentos de horas por colaborador."""

from __future__ import annotations

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

CAMPOS_TIMEKEEPING = (
    "Data de apontamento",
    "Horas apontadas",
    "Código do colaborador",
    "Card",
)


def ler_hr_base(caminho: Path) -> list[dict[str, str]]:
    with caminho.open("r", newline="", encoding="utf-8-sig") as arquivo:
        return list(csv.DictReader(arquivo))


def ler_cards(caminho: Path) -> list[dict[str, str]]:
    with caminho.open("r", newline="", encoding="utf-8-sig") as arquivo:
        return list(csv.DictReader(arquivo))


def data_entre(inicio: date, fim: date, gerador: random.Random) -> date:
    if fim < inicio:
        return inicio
    delta = (fim - inicio).days
    return inicio + timedelta(days=gerador.randint(0, max(0, delta)))


def gerar_timekeeping(hr_base: list[dict[str, str]], cards: list[dict[str, str]], seed: int = 42) -> list[dict[str, str]]:
    gerador = random.Random(seed)
    cards_ids = [card["ID Card"] for card in cards]
    registros: list[dict[str, str]] = []

    dias_por_mes = {}
    for linha in hr_base:
        codigo = linha["Código do colaborador"]
        data_admissao = date.fromisoformat(linha["Data de Admissão"])
        data_desligamento = (
            date.fromisoformat(linha["Data de desligamento"])
            if linha.get("Data de desligamento")
            else None
        )
        ano_mes = linha["Ano-mês de referência"]
        ano, mes = map(int, ano_mes.split("-"))
        inicio_mes = date(ano, mes, 1)
        fim_mes = date(ano, mes + 1, 1) if mes < 12 else date(ano + 1, 1, 1)
        fim_mes = fim_mes - timedelta(days=1)

        if data_desligamento:
            fim_mes = min(fim_mes, data_desligamento)

        dias = []
        data = inicio_mes
        while data <= fim_mes:
            if data >= data_admissao and (not data_desligamento or data <= data_desligamento):
                dias.append(data)
            data += timedelta(days=1)
        dias_por_mes[(codigo, ano_mes)] = dias

    for linha in hr_base:
        codigo = linha["Código do colaborador"]
        ano_mes = linha["Ano-mês de referência"]
        dias = dias_por_mes.get((codigo, ano_mes), [])
        if not dias:
            continue

        for dia in dias:
            pontos_no_dia = gerador.randint(1, 4)
            for _ in range(pontos_no_dia):
                registros.append(
                    {
                        "Data de apontamento": dia.isoformat(),
                        "Horas apontadas": str(gerador.randint(1, 8)),
                        "Código do colaborador": codigo,
                        "Card": random.choice(cards_ids),
                    }
                )

    return registros


def salvar_timekeeping(registros: list[dict[str, str]], caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_TIMEKEEPING)
        escritor.writeheader()
        escritor.writerows(registros)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hr-base", type=Path, default=Path("hr_base.csv"))
    parser.add_argument("--cards", type=Path, default=Path("base_cards.csv"))
    parser.add_argument("--saida", type=Path, default=Path("timekeeping.csv"))
    parser.add_argument("--seed", type=int, default=42)
    argumentos = parser.parse_args()

    hr_base = ler_hr_base(argumentos.hr_base)
    cards = ler_cards(argumentos.cards)
    if not hr_base:
        raise ValueError(f"Nenhuma linha encontrada em {argumentos.hr_base}")
    if not cards:
        raise ValueError(f"Nenhum card encontrado em {argumentos.cards}")

    registros = gerar_timekeeping(hr_base, cards, argumentos.seed)
    salvar_timekeeping(registros, argumentos.saida)
    print(f"Timekeeping criado: {argumentos.saida} ({len(registros)} registros)")


if __name__ == "__main__":
    main()
