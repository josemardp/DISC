"""
seed_big_five_ipip.py
=====================
Banco de itens do NÚCLEO Big Five.

Fonte: IPIP Big-Five Factor Markers, 50 itens (Goldberg, 1992) — DOMÍNIO PÚBLICO
(https://ipip.ori.org). Tradução para PT-BR feita aqui, preservando o sentido.
Cada item mantém sua chave (+ ou -) original do IPIP.

Convenção de chave:
- Itens O, C, E, A são keyed para o próprio fator (+ aumenta o fator).
- Itens N (Neuroticismo) são keyed para Neuroticismo (+ aumenta neuroticismo).
- reverse_keyed=True significa que o item é negativamente keyed e deve ser
  invertido (6 - valor numa escala 1-5) antes de somar.

Escala de resposta: 1=Muito imprecisa ... 5=Muito precisa.
"""

# Cada tupla: (dimension, texto_ptbr, reverse_keyed)
ITENS_IPIP_50 = [
    # ---------------- EXTROVERSÃO (E) ----------------
    ("E", "Sou a alma da festa.", False),
    ("E", "Não falo muito.", True),
    ("E", "Sinto-me à vontade perto das pessoas.", False),
    ("E", "Fico em segundo plano.", True),
    ("E", "Inicio conversas.", False),
    ("E", "Tenho pouco a dizer.", True),
    ("E", "Converso com muitas pessoas diferentes em festas.", False),
    ("E", "Não gosto de chamar atenção para mim.", True),
    ("E", "Não me importo de ser o centro das atenções.", False),
    ("E", "Sou quieto perto de estranhos.", True),

    # ---------------- AMABILIDADE (A) ----------------
    ("A", "Sinto pouca preocupação com os outros.", True),
    ("A", "Tenho interesse pelas pessoas.", False),
    ("A", "Insulto as pessoas.", True),
    ("A", "Compreendo os sentimentos dos outros.", False),
    ("A", "Não me interesso pelos problemas dos outros.", True),
    ("A", "Tenho um coração mole.", False),
    ("A", "Não tenho muito interesse pelos outros.", True),
    ("A", "Reservo tempo para os outros.", False),
    ("A", "Percebo as emoções dos outros.", False),
    ("A", "Faço as pessoas se sentirem à vontade.", False),

    # ---------------- CONSCIENCIOSIDADE (C) ----------------
    ("C", "Estou sempre preparado.", False),
    ("C", "Deixo minhas coisas espalhadas.", True),
    ("C", "Presto atenção aos detalhes.", False),
    ("C", "Faço uma bagunça das coisas.", True),
    ("C", "Realizo as tarefas imediatamente.", False),
    ("C", "Costumo esquecer de colocar as coisas de volta no lugar.", True),
    ("C", "Gosto de ordem.", False),
    ("C", "Fujo das minhas obrigações.", True),
    ("C", "Sigo um cronograma.", False),
    ("C", "Sou rigoroso no meu trabalho.", False),

    # ---------------- NEUROTICISMO (N) ----------------
    ("N", "Fico estressado com facilidade.", False),
    ("N", "Fico relaxado na maior parte do tempo.", True),
    ("N", "Preocupo-me com as coisas.", False),
    ("N", "Raramente fico para baixo.", True),
    ("N", "Sou facilmente perturbado.", False),
    ("N", "Fico chateado com facilidade.", False),
    ("N", "Mudo muito de humor.", False),
    ("N", "Tenho oscilações de humor frequentes.", False),
    ("N", "Irrito-me com facilidade.", False),
    ("N", "Sinto-me triste com frequência.", False),

    # ---------------- ABERTURA / INTELECTO (O) ----------------
    ("O", "Tenho um vocabulário rico.", False),
    ("O", "Tenho dificuldade em entender ideias abstratas.", True),
    ("O", "Tenho uma imaginação vívida.", False),
    ("O", "Não me interesso por ideias abstratas.", True),
    ("O", "Tenho excelentes ideias.", False),
    ("O", "Não tenho boa imaginação.", True),
    ("O", "Compreendo as coisas rapidamente.", False),
    ("O", "Uso palavras difíceis.", False),
    ("O", "Dedico tempo a refletir sobre as coisas.", False),
    ("O", "Sou cheio de ideias.", False),
]

# Itens de atenção (NÃO entram no escore). 'expected' = resposta correta esperada.
ITENS_ATENCAO = [
    {"dimension": "attention_check", "item_text": "Para esta questão, marque 'Muito imprecisa' (1).", "expected": 1},
    {"dimension": "attention_check", "item_text": "Por favor, selecione 'Muito precisa' (5) nesta frase.", "expected": 5},
    {"dimension": "attention_check", "item_text": "Marque a opção do meio (3) para confirmar que está atento.", "expected": 3},
]


def construir_itens_bigfive(start_id: int = 1000, intercalar_atencao: bool = True) -> list:
    """
    Gera a lista de itens prontos para inserir no banco (formato compatível com
    QuestionnaireItem: id, block_number, test_type, dimension, item_text, weight,
    reverse_keyed). Intercala os itens de atenção ao longo do questionário.

    block_number aqui agrupa por fator (1=E, 2=A, 3=C, 4=N, 5=O, 9=atenção),
    apenas para organização de renderização.
    """
    bloco_por_fator = {"E": 1, "A": 2, "C": 3, "N": 4, "O": 5}
    itens = []
    item_id = start_id
    for dim, texto, rev in ITENS_IPIP_50:
        item_id += 1
        itens.append({
            "id": item_id,
            "block_number": bloco_por_fator[dim],
            "test_type": "BIGFIVE",
            "dimension": dim,
            "item_text": texto,
            "reverse_keyed": rev,
            "weight": 1.0,
        })

    if intercalar_atencao:
        for ac in ITENS_ATENCAO:
            item_id += 1
            itens.append({
                "id": item_id,
                "block_number": 9,
                "test_type": "BIGFIVE",
                "dimension": "attention_check",
                "item_text": ac["item_text"],
                "reverse_keyed": False,
                "weight": 0.0,
                "expected": ac["expected"],
            })
    return itens


if __name__ == "__main__":
    itens = construir_itens_bigfive()
    by_dim = {}
    for it in itens:
        by_dim[it["dimension"]] = by_dim.get(it["dimension"], 0) + 1
    print(f"Total de itens: {len(itens)}")
    print("Itens por dimensão:", by_dim)
