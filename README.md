# Geracao das bases de dados

Este diretorio contem scripts Python para gerar bases CSV sinteticas usadas no TAC Mackenzie. Os dados sao gerados de forma deterministica quando os scripts sao executados com a mesma `seed`.

## Arquivos Python

### `gerar_base_csv.py`

Gera a base principal de cards do Jira.

- Saida padrao: `base_cards.csv`
- Quantidade padrao: 25.000 registros
- Seed padrao: `42`
- Principais dados: ID do card, tipo, status, equipe, datas de criacao, resolucao, reabertura, entrega prevista, replanejamento, horas estimadas e data da carga.
- Regras simuladas: tipos de card com proporcoes definidas, cards resolvidos ou abertos, duplicidade controlada de IDs, SLAs para bugs e distribuicao de equipes.

Opcoes principais:

```text
python gerar_base_csv.py --saida base_cards.csv --seed 42 --quantidade 25000
```

### `gerar_hr_base.py`

Gera um historico mensal de colaboradores a partir das equipes presentes em `base_cards.csv`.

- Entrada padrao: `base_cards.csv`
- Saida padrao: `hr_base.csv`
- Seed padrao: `42`
- Base simulada: ate 600 colaboradores, com admissao, desligamento, equipe e referencia mensal de 2025.

Opcoes principais:

```text
python gerar_hr_base.py --entrada base_cards.csv --saida hr_base.csv --seed 42
```

### `gerar_log_jira.py`

Gera o historico de alteracoes de status dos cards, usando a sequencia de status permitida para cada tipo de card.

- Entrada padrao: `base_cards.csv`
- Saida padrao: `log_jira.csv`
- Seed padrao: `42`
- Dados gerados: card, data da alteracao, objeto alterado, valor anterior e valor posterior.

Opcoes principais:

```text
python gerar_log_jira.py --entrada base_cards.csv --saida log_jira.csv --seed 42
```

### `gerar_timekeeping.py`

Gera apontamentos diarios de horas por colaborador, considerando os periodos de atividade registrados na base de RH e associando cada apontamento a um card.

- Entradas padrao: `hr_base.csv` e `base_cards.csv`
- Saida padrao: `timekeeping.csv`
- Seed padrao: `42`
- Dados gerados: data de apontamento, horas apontadas, codigo do colaborador e card.

Opcoes principais:

```text
python gerar_timekeeping.py --hr-base hr_base.csv --cards base_cards.csv --saida timekeeping.csv --seed 42
```

## Ordem de execucao

A ordem recomendada e:

1. `gerar_base_csv.py` -> `base_cards.csv`
2. `gerar_hr_base.py` -> `hr_base.csv`
3. `gerar_log_jira.py` -> `log_jira.csv`
4. `gerar_timekeeping.py` -> `timekeeping.csv`

Os nomes dos arquivos podem ser alterados pelas opcoes de entrada e saida, desde que os caminhos informados na etapa seguinte correspondam aos arquivos gerados.

## Execucao completa

No PowerShell, a partir deste diretorio:

```powershell
python gerar_base_csv.py
python gerar_hr_base.py
python gerar_log_jira.py
python gerar_timekeeping.py
```

Todos os CSVs sao gravados em UTF-8 com BOM (`utf-8-sig`), com cabecalho e separador virgula. Para reproduzir os mesmos dados, mantenha a mesma seed e os mesmos parametros.

## Dependencias

Os scripts utilizam apenas a biblioteca padrao do Python. Recomenda-se Python 3.10 ou superior, pois o codigo utiliza anotacoes de tipo com `list[...]`, `dict[...]` e `date | None`.
