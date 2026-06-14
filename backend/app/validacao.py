"""
validacao.py
============
Funções de validação psicométrica para o instrumento Big Five IPIP-50.
Usa mcdonald_omega() de science_engine — não reimplementa a matemática.
"""

from collections import defaultdict

import numpy as np

from backend.app.science_engine import mcdonald_omega

FATORES = ["O", "C", "E", "A", "N"]


def test_retest_reliability(
    aplicacao_a: list,
    aplicacao_b: list,
) -> dict:
    """
    Calcula correlação de Pearson por fator Big Five entre duas aplicações
    do mesmo respondente.

    Parâmetros
    ----------
    aplicacao_a : list[dict]
        Lista de respostas item-a-item da 1ª aplicação.
        Cada dict: {"fator": str, "escore_raw": float}.
        Um entry por item — para 10 itens por fator, 50 entries no total.
    aplicacao_b : list[dict]
        Lista equivalente da 2ª aplicação (mesmo respondente, mesma ordem).

    Retorna
    -------
    dict
        {"O": r, "C": r, "E": r, "A": r, "N": r}
        onde r é a correlação de Pearson (float, -1 a 1).
        Retorna 0.0 para fatores com menos de 2 pares ou variância zero.

    Restrições
    ----------
    - len(aplicacao_a) deve ser igual a len(aplicacao_b).
    - Os entries de cada fator devem estar na mesma ordem nas duas listas
      (item 1 de O em A corresponde ao item 1 de O em B).
    """
    resultado = {}
    for fator in FATORES:
        a_vals = [float(r["escore_raw"]) for r in aplicacao_a if r["fator"] == fator]
        b_vals = [float(r["escore_raw"]) for r in aplicacao_b if r["fator"] == fator]
        if len(a_vals) < 2 or len(a_vals) != len(b_vals):
            resultado[fator] = 0.0
            continue
        corr_matrix = np.corrcoef(a_vals, b_vals)
        r = float(corr_matrix[0, 1])
        resultado[fator] = round(r if not np.isnan(r) else 0.0, 4)
    return resultado


def omega_por_fator(respostas_item: list) -> dict:
    """
    Calcula Ômega de McDonald por fator Big Five a partir de respostas
    item-a-item de múltiplos respondentes.

    Usa mcdonald_omega() de science_engine — não reimplementa a matemática.

    Parâmetros
    ----------
    respostas_item : list[dict]
        Lista plana de respostas. Cada dict:
            {"item_id": str, "fator": str, "escore": float}
        Cada item_id pode aparecer várias vezes (uma por respondente).
        A ordem das entradas de cada item_id deve ser consistente entre itens
        (ou seja, o k-ésimo entry de cada item_id corresponde ao mesmo respondente).

    Retorna
    -------
    dict
        {"O": omega, "C": omega, "E": omega, "A": omega, "N": omega}
        Retorna 0.0 para fatores com dados insuficientes (< 2 respondentes
        ou < 2 itens).
    """
    resultado = {}
    for fator in FATORES:
        entradas = [r for r in respostas_item if r["fator"] == fator]
        if not entradas:
            resultado[fator] = 0.0
            continue

        # Agrupa escores por item_id; a ordem de aparição identifica o respondente
        colunas: dict = defaultdict(list)
        for r in entradas:
            colunas[r["item_id"]].append(float(r["escore"]))

        # Verifica uniformidade: todos os itens devem ter o mesmo número de respondentes
        tamanhos = {len(v) for v in colunas.values()}
        if len(tamanhos) != 1 or min(tamanhos) < 2:
            resultado[fator] = 0.0
            continue

        n_respondentes = min(tamanhos)
        lista_colunas = list(colunas.values())

        # Matrix: linhas = respondentes, colunas = itens
        matrix = [
            [lista_colunas[col_idx][resp_idx] for col_idx in range(len(lista_colunas))]
            for resp_idx in range(n_respondentes)
        ]

        resultado[fator] = mcdonald_omega(matrix)
    return resultado
