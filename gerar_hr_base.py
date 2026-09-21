"""Gera a tabela hr_base com histórico mensal de colaboradores."""

from __future__ import annotations

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

CAMPOS_HR_BASE = (
    "Código do colaborador",
    "Data de Admissão",
    "Data de desligamento",
    "Ano-mês de referência",
    "Equipe",
)


def ler_primeira_base(caminho: Path) -> list[dict[str, str]]:
    with caminho.open("r", newline="", encoding="utf-8-sig") as arquivo:
        return list(csv.DictReader(arquivo))


def gerar_codigos_colaboradores(total: int) -> list[str]:
    usados: set[str] = set()
    codigos: list[str] = []
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    while len(codigos) < total:
        codigo = "".join(random.choice(letras) for _ in range(4))
        if codigo not in usados:
            usados.add(codigo)
            codigos.append(codigo)
    return codigos


def data_maxima_cards(cards: list[dict[str, str]]) -> date:
    datas = []
    for card in cards:
        valor = card.get("Data da carga", "")
        if valor:
            datas.append(date.fromisoformat(valor))
    if not datas:
        return date(2025, 12, 31)
    return max(datas)


def montar_equipes(cards: list[dict[str, str]]) -> list[str]:
    equipes = sorted({card["Equipe"] for card in cards if card.get("Equipe")})
    return equipes


def gerar_hr_base(cards: list[dict[str, str]], seed: int = 42) -> list[dict[str, str]]:
    random.seed(seed)
    equipes = montar_equipes(cards)
    data_maxima = data_maxima_cards(cards)

    colaboradores_total = 600
    codigos = gerar_codigos_colaboradores(colaboradores_total)
    registros: list[dict[str, str]] = []

    meses = [date(2025, mes, 1) for mes in range(1, 13)]
    admissoes: dict[str, date] = {}
    desligamentos: dict[str, date | None] = {}
    equipe_por_colaborador: dict[str, str] = {}

    for codigo in codigos:
        equipe = random.choice(equipes)
        equipe_por_colaborador[codigo] = equipe
        mes_admissao = random.randint(1, 12)
        dia_admissao = random.randint(1, 28)
        admissao = date(2025, mes_admissao, dia_admissao)
        if admissao > data_maxima:
            admissao = data_maxima
        admissoes[codigo] = admissao

        if random.random() < 0.20:
            mes_desligamento = random.randint(admissao.month, 12)
            dia_desligamento = random.randint(1, 28)
            desligamento = date(2025, mes_desligamento, dia_desligamento)
            if desligamento <= admissao:
                desligamento = admissao + timedelta(days=1)
            if desligamento > data_maxima:
                desligamento = data_maxima
            desligamentos[codigo] = desligamento
        else:
            desligamentos[codigo] = None

    for codigo in codigos:
        data_admissao = admissoes[codigo]
        data_desligamento = desligamentos[codigo]
        equipe_atual = equipe_por_colaborador[codigo]
        for mes in meses:
            if data_admissao > mes:
                continue
            if data_desligamento and mes > data_desligamento.replace(day=1):
                continue

            if random.random() < 0.05:
                equipe_atual = random.choice(equipes)

            registros.append(
                {
                    "Código do colaborador": codigo,
                    "Data de Admissão": data_admissao.isoformat(),
                    "Data de desligamento": data_desligamento.isoformat() if data_desligamento else "",
                    "Ano-mês de referência": mes.strftime("%Y-%m"),
                    "Equipe": equipe_atual,
                }
            )

    return registros[:7200]


def salvar_hr_base(registros: list[dict[str, str]], caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_HR_BASE)
        escritor.writeheader()
        escritor.writerows(registros)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=Path("base_cards.csv"))
    parser.add_argument("--saida", type=Path, default=Path("hr_base.csv"))
    parser.add_argument("--seed", type=int, default=42)
    argumentos = parser.parse_args()

    cards = ler_primeira_base(argumentos.entrada)
    if not cards:
        raise ValueError(f"Nenhum card encontrado em {argumentos.entrada}")

    registros = gerar_hr_base(cards, argumentos.seed)
    salvar_hr_base(registros, argumentos.saida)
    print(f"HR Base criada: {argumentos.saida} ({len(registros)} registros)")


if __name__ == "__main__":
    main()
