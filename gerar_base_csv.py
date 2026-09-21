from __future__ import annotations

import argparse
import csv
import random
from calendar import monthrange
from datetime import date, timedelta
from pathlib import Path


TOTAL_REGISTROS = 25_000
TIPOS = (
    ("TASK", 0.20),
    ("SUBTASK", 0.40),
    ("BUG", 0.15),
    ("BUG SUBTASK", 0.15),
    ("EPIC", 0.05),
    ("INICIATIVE", 0.05),
)
STATUS_INICIATIVE = (
    "Lista de desejos",
    "Backlog",
    "Triage",
    "For Refinement",
    "In Refinement",
    "In Progress",
    "Done",
    "Canceled",
)
STATUS_PADRAO = (
    "Backlog",
    "Triage",
    "For Refinement",
    "In Refinement",
    "For Technical Analysis",
    "In Technical Analysis",
    "Ready for Development",
    "In Development",
    "For Release",
    "Done",
    "Canceled",
)
STATUS_BUG = ("Waiting Information", "Information Sent")
CAMPOS = (
    "ID Card",
    "Tipo de Card",
    "Status",
    "SLA Resposta",
    "SLA Resolução",
    "Equipe",
    "Data de Criação",
    "Data de resolução",
    "Data de reabertura",
    "Data prevista para entrega",
    "Data replanejada para entrega",
    "Horas estimadas do projeto",
    "Data da carga",
)

VALORES_SLA = ("MET", "EXCEEDED")


def quantidade(percentual: float, total: int = TOTAL_REGISTROS) -> int:
    """Converte um percentual em quantidade, arredondando para o inteiro mais próximo."""
    return int(total * percentual + 0.5)


def datas_de_criacao(total: int, gerador: random.Random) -> list[date]:
    """Cria datas de 2025 com meses concentrados ao redor do meio do ano."""
    resultado = []
    for _ in range(total):
        mes = min(12, max(1, int(round(gerador.gauss(6.5, 3.0)))))
        dia = gerador.randint(1, monthrange(2025, mes)[1])
        resultado.append(date(2025, mes, dia))
    return resultado


def tipos_de_card(total: int, gerador: random.Random) -> list[str]:
    """Gera as categorias na proporção solicitada e embaralha sua ordem."""
    tipos = []
    restante = total
    for indice, (tipo, percentual) in enumerate(TIPOS):
        quantidade_tipo = (
            restante if indice == len(TIPOS) - 1 else quantidade(percentual, total)
        )
        tipos.extend([tipo] * quantidade_tipo)
        restante -= quantidade_tipo
    gerador.shuffle(tipos)
    return tipos


def equipes(total: int, gerador: random.Random) -> list[str]:
    """Distribui equipes usando uma amostra de Pareto, favorecendo equipes menores."""
    resultado = []
    for _ in range(total):
        valor_pareto = gerador.paretovariate(1.8)
        indice = min(20, max(1, int(valor_pareto)))
        resultado.append(f"Equipe {indice}")
    return resultado


def status_do_card(tipo: str, resolucao: date | None, gerador: random.Random) -> str:
    """Escolhe um status válido, relacionando cards resolvidos à sua resolução."""
    if resolucao:
        return "Done" if gerador.random() < 0.90 else "Canceled"

    if tipo == "INICIATIVE":
        status_disponiveis = STATUS_INICIATIVE[:-2]
    elif tipo in {"BUG", "BUG SUBTASK"}:
        status_disponiveis = STATUS_PADRAO[:-2] + STATUS_BUG
    else:
        status_disponiveis = STATUS_PADRAO[:-2]
    return gerador.choice(status_disponiveis)


def sla_do_bug(resolucao: date | None, gerador: random.Random) -> tuple[str, str]:
    """Define os status de SLA para bug aberto ou encerrado."""
    if not resolucao:
        return ("IN PROGRESS", "IN PROGRESS")
    return (
        gerador.choices(("MET", "EXCEEDED"), weights=[90, 10], k=1)[0],
        gerador.choices(("MET", "EXCEEDED"), weights=[90, 10], k=1)[0],
    )


def gerar_registros(total: int, seed: int) -> list[dict[str, str]]:
    gerador = random.Random(seed)
    tipos = tipos_de_card(total, gerador)
    datas_criacao = datas_de_criacao(total, gerador)

    # 0,1% das linhas reutilizam IDs já gerados; as demais permanecem únicas.
    quantidade_repetidos = quantidade(0.001, total)
    ids = list(range(100_000, 100_000 + total - quantidade_repetidos))
    ids.extend(gerador.choices(ids, k=quantidade_repetidos))
    gerador.shuffle(ids)

    resolucoes: list[date | None] = []
    for criacao in datas_criacao:
        resolucoes.append(
            None
            if gerador.random() < 0.03
            else criacao + timedelta(days=gerador.randint(10, 30))
        )

    datas_reabertura: list[date | None] = [None] * total
    candidatos_reabertura = [i for i, resolucao in enumerate(resolucoes) if resolucao]
    gerador.shuffle(candidatos_reabertura)
    for indice in candidatos_reabertura[: quantidade(0.005, total)]:
        datas_reabertura[indice] = resolucoes[indice] + timedelta(
            days=gerador.randint(1, 60)
        )

    datas_previstas = [
        criacao + timedelta(days=gerador.randint(10, 30))
        for criacao in datas_criacao
    ]
    datas_replanejadas: list[date | None] = [None] * total
    indices_replanejados = list(range(total))
    gerador.shuffle(indices_replanejados)
    quantidade_replanejados = quantidade(0.05, total)
    quantidade_antes = quantidade(0.01, quantidade_replanejados)
    for posicao, indice in enumerate(indices_replanejados[:quantidade_replanejados]):
        if posicao < quantidade_antes:
            datas_replanejadas[indice] = datas_previstas[indice] - timedelta(
                days=gerador.randint(1, 5)
            )
        else:
            datas_replanejadas[indice] = datas_previstas[indice] + timedelta(
                days=gerador.randint(5, 30)
            )

    registros = []
    for indice in range(total):
        tipo = tipos[indice]
        resolucao = resolucoes[indice]
        status = status_do_card(tipo, resolucao, gerador)
        sla_resposta, sla_resolucao = ("", "")
        if tipo == "BUG":
            sla_resposta, sla_resolucao = sla_do_bug(resolucao, gerador)
        registros.append(
            {
                "ID Card": str(ids[indice]),
                "Tipo de Card": tipo,
                "Status": status,
                "SLA Resposta": sla_resposta,
                "SLA Resolução": sla_resolucao,
                "Equipe": equipes(1, gerador)[0],
                "Data de Criação": datas_criacao[indice].isoformat(),
                "Data de resolução": resolucao.isoformat() if resolucao else "",
                "Data de reabertura": (
                    datas_reabertura[indice].isoformat()
                    if datas_reabertura[indice]
                    else ""
                ),
                "Data prevista para entrega": datas_previstas[indice].isoformat(),
                "Data replanejada para entrega": (
                    datas_replanejadas[indice].isoformat()
                    if datas_replanejadas[indice]
                    else ""
                ),
                "Horas estimadas do projeto": (
                    str(gerador.randrange(8, 161, 4))
                    if tipo in {"BUG", "TASK"}
                    else ""
                ),
                "Data da carga": max(datas_criacao[indice], resolucao or datas_criacao[indice]).isoformat(),
            }
        )
    return registros


def salvar_csv(registros: list[dict[str, str]], caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(registros)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", type=Path, default=Path("base_cards.csv"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--quantidade", type=int, default=TOTAL_REGISTROS)
    argumentos = parser.parse_args()

    if argumentos.quantidade <= 0:
        parser.error("--quantidade deve ser maior que zero")

    registros = gerar_registros(argumentos.quantidade, argumentos.seed)
    salvar_csv(registros, argumentos.saida)
    print(f"CSV criado: {argumentos.saida} ({len(registros)} registros)")


if __name__ == "__main__":
    main()
