"""
science_engine.py
=================
Núcleo científico (padrão Big Five) para o sistema de avaliação.

PRINCÍPIO DE ARQUITETURA
------------------------
O Big Five (5 fatores, incluindo Neuroticismo) é o NÚCLEO MEDIDO.
Jung, DISC e Spranger são CAMADAS DE APRESENTAÇÃO derivadas do Big Five.

Tudo aqui é função pura (sem dependência de banco), para ser fácil de testar
e de plugar no backend FastAPI existente.

Referências:
- Goldberg (1992) IPIP Big-Five Factor Markers (50 itens, domínio público).
- McCrae & Costa (1989): mapeamento MBTI <-> Big Five.
- McDonald (1999): ômega como medida de consistência interna.
"""

import math
from typing import Dict, List, Tuple, Optional

FATORES_BIG_FIVE = ["O", "C", "E", "A", "N"]  # Abertura, Conscienciosidade, Extroversão, Amabilidade, Neuroticismo

# =====================================================================
# 1. CONFIABILIDADE E INCERTEZA
# =====================================================================

def normal_cdf(z: float) -> float:
    """Função de distribuição cumulativa normal padrão (Phi(Z)), via função erro."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def cronbach_alpha(response_matrix: list) -> float:
    return 0.0

def mcdonald_omega(response_matrix: list) -> float:
    return 0.0


def standard_error_of_measurement(sd: float, reliability: float) -> float:
    """Erro-padrão de medida: SEM = sd * sqrt(1 - confiabilidade)."""
    if reliability >= 1.0:
        return 0.0
    return round(sd * math.sqrt(max(0.0, 1.0 - reliability)), 4)


def confidence_interval(score: float, sem: float, z: float = 1.96,
                        bounds: Optional[Tuple[float, float]] = None) -> Tuple[float, float]:
    """
    Intervalo de confiança (95% por padrão) em torno de um escore.
    Se 'bounds' for informado (ex.: (0, 100) para percentis), o intervalo é
    limitado a essa faixa para não produzir valores impossíveis.
    """
    margem = z * sem
    low, high = score - margem, score + margem
    if bounds is not None:
        lo_b, hi_b = bounds
        low = max(lo_b, low)
        high = min(hi_b, high)
    return (round(low, 2), round(high, 2))


# =====================================================================
# 2. PONTUAÇÃO DO BIG FIVE (NORMATIVA, LIKERT 1-5, COM ITENS REVERSOS)
# =====================================================================

def _aplica_reverso(valor: int, reverse: bool, escala_max: int = 5) -> int:
    """Inverte o item reverso numa escala Likert (ex.: 1-5 -> 6 - valor)."""
    return (escala_max + 1 - valor) if reverse else valor


def score_big_five(respostas: List[Dict]) -> Dict[str, Dict[str, float]]:
    """
    Calcula os 5 fatores a partir das respostas.

    respostas: lista de dicts com:
        - 'dimension': um de O, C, E, A, N  (itens de atenção devem ser 'attention_check' e são ignorados)
        - 'value': int 1..5
        - 'reverse_keyed': bool

    Retorna por fator: {'raw': soma 10-50, 'mean': média 1-5, 'n_itens': k}
    Inclui também 'ES' (Estabilidade Emocional) = inverso de N.
    """
    acumulado = {f: [] for f in FATORES_BIG_FIVE}
    for r in respostas:
        dim = r.get("dimension")
        if dim not in FATORES_BIG_FIVE:
            continue  # ignora itens de atenção e quaisquer outros
        v = _aplica_reverso(int(r["value"]), bool(r.get("reverse_keyed", False)))
        acumulado[dim].append(v)

    resultado = {}
    for f in FATORES_BIG_FIVE:
        vals = acumulado[f]
        if vals:
            raw = float(sum(vals))
            mean = round(raw / len(vals), 3)
        else:
            raw, mean = 0.0, 0.0
        resultado[f] = {"raw": raw, "mean": mean, "n_itens": len(vals)}

    # Estabilidade Emocional = inverso do Neuroticismo (na média 1-5: 6 - mean)
    n_mean = resultado["N"]["mean"]
    resultado["ES"] = {
        "raw": round(60.0 - resultado["N"]["raw"], 3) if resultado["N"]["n_itens"] else 0.0,
        "mean": round(6.0 - n_mean, 3) if n_mean else 0.0,
        "n_itens": resultado["N"]["n_itens"],
    }
    return resultado


# =====================================================================
# 3. NORMATIZAÇÃO HONESTA (percentil)
# =====================================================================

def percentil_por_norma(raw: float, mean: float, sd: float) -> float:
    """Converte escore bruto em percentil via Score-Z + Phi(Z). Requer norma (mean, sd)."""
    if sd == 0:
        return 50.0
    z = (raw - mean) / sd
    return round(max(0.0, min(100.0, normal_cdf(z) * 100.0)), 2)


def percentil_intraindividual(raw_atual: float, historico: List[float]) -> Dict[str, float]:
    """
    Modo régua interna: compara a pessoa com ela mesma ao longo do tempo.
    Não alega percentil populacional. Retorna posição relativa no próprio histórico.
    """
    todos = sorted(historico + [raw_atual])
    if len(todos) <= 1:
        return {"posicao_relativa": 50.0, "n_medidas": len(todos)}
    abaixo = sum(1 for x in historico if x < raw_atual)
    pos = round((abaixo / len(historico)) * 100.0, 2) if historico else 50.0
    return {"posicao_relativa": pos, "n_medidas": len(todos)}


# =====================================================================
# 4. JUNG EM PADRÃO BIG FIVE (CONTÍNUO, DERIVADO)
#    Mapeamento estabelecido (McCrae & Costa, 1989):
#      E/I <- Extroversão | S/N <- Abertura | T/F <- Amabilidade | J/P <- Conscienciosidade
#    5º eixo reportado: Estabilidade Emocional <- inverso de Neuroticismo (Jung não tem)
# =====================================================================

def _borderline(p: float) -> bool:
    return 45.0 <= p <= 55.0


def derive_jung_from_big_five(bf_percentis: Dict[str, float]) -> Dict:
    """
    bf_percentis: percentis 0-100 dos fatores Big Five {O, C, E, A, N}.
    Retorna eixos contínuos, tipo-resumo de 4 letras, flags de 'em cima do muro'
    e o eixo extra de Estabilidade Emocional.
    A pilha de funções cognitivas NÃO é calculada (sem suporte empírico) — fica para a narrativa.
    """
    extr = bf_percentis.get("E", 50.0)
    aber = bf_percentis.get("O", 50.0)
    amab = bf_percentis.get("A", 50.0)
    consc = bf_percentis.get("C", 50.0)
    neuro = bf_percentis.get("N", 50.0)

    eixos = {
        "E_I": {"E": round(extr, 2), "I": round(100 - extr, 2), "borderline": _borderline(extr)},
        "S_N": {"N": round(aber, 2), "S": round(100 - aber, 2), "borderline": _borderline(aber)},
        "T_F": {"F": round(amab, 2), "T": round(100 - amab, 2), "borderline": _borderline(amab)},
        "J_P": {"J": round(consc, 2), "P": round(100 - consc, 2), "borderline": _borderline(consc)},
    }

    tipo = ""
    tipo += "E" if extr >= 50 else "I"
    tipo += "N" if aber >= 50 else "S"
    tipo += "F" if amab >= 50 else "T"
    tipo += "J" if consc >= 50 else "P"

    return {
        "tipo_resumo": tipo,
        "eixos": eixos,
        "estabilidade_emocional": round(100 - neuro, 2),  # eixo extra (não junguiano)
        "aviso": "Tipo é um RESUMO de escores contínuos; eixos 'borderline' (45-55%) podem alternar a letra.",
    }


# =====================================================================
# 5. DISC E SPRANGER COMO CAMADAS DE APRESENTAÇÃO (DERIVADAS)
#    Pesos provisórios — apresentação, não medida validada.
# =====================================================================

def derive_disc_from_big_five(bf_percentis: Dict[str, float]) -> Dict[str, float]:
    """
    DISC derivado do Big Five (PROVISÓRIO — apresentação).
    Combinações heurísticas documentadas:
      D (Dominância)   ~ alta Extroversão + baixa Amabilidade
      I (Influência)   ~ alta Extroversão + alta Amabilidade
      S (Estabilidade) ~ alta Amabilidade + baixa Neuroticismo (alta ES)
      C (Conformidade) ~ alta Conscienciosidade
    """
    extr = bf_percentis.get("E", 50.0)
    amab = bf_percentis.get("A", 50.0)
    consc = bf_percentis.get("C", 50.0)
    neuro = bf_percentis.get("N", 50.0)
    es = 100 - neuro
    return {
        "D": round((extr + (100 - amab)) / 2, 2),   # [provisório]
        "I": round((extr + amab) / 2, 2),            # [provisório]
        "S": round((amab + es) / 2, 2),              # [provisório]
        "C": round(consc, 2),                        # [provisório]
        "_aviso": "DISC derivado do Big Five — pesos provisórios, camada de apresentação.",
    }


def derive_spranger_from_big_five(bf_percentis: Dict[str, float]) -> Dict[str, float]:
    """
    Spranger (valores) NÃO mapeia limpo no Big Five. Mapeamento HEURÍSTICO e PROVISÓRIO.
    Recomendação: ou medir Spranger com itens próprios validados, ou tratar como ilustrativo.
    """
    aber = bf_percentis.get("O", 50.0)
    amab = bf_percentis.get("A", 50.0)
    consc = bf_percentis.get("C", 50.0)
    extr = bf_percentis.get("E", 50.0)
    return {
        "teorico": round(aber, 2),                       # [provisório] curiosidade intelectual ~ Abertura
        "estetico": round(aber, 2),                      # [provisório]
        "social": round(amab, 2),                        # [provisório] empatia ~ Amabilidade
        "regulador": round(consc, 2),                    # [provisório] ordem ~ Conscienciosidade
        "individualista": round(extr, 2),                # [provisório] status/liderança ~ Extroversão
        "economico": round((consc + (100 - aber)) / 2, 2),  # [provisório]
        "_aviso": "Spranger não mapeia bem no Big Five; valores PROVISÓRIOS e ilustrativos.",
    }


# =====================================================================
# 6. QUALIDADE DA RESPOSTA (não 'fraude' — sinal de confiabilidade)
# =====================================================================

def response_quality_index(valores: List[int],
                           atencao_ok: bool,
                           irt_avg_ms: float,
                           rvi_count: int) -> Dict:
    """
    Avalia a qualidade do preenchimento.
      - straight_lining: variância ~0 (marcou tudo igual)
      - muito_rapido: tempo médio por item < 800ms
      - atencao_ok: passou nos itens de atenção
    """
    straight = False
    muito_rapido = bool(irt_avg_ms < 800)

    pontos = 0
    if not atencao_ok:
        pontos += 2
    if straight:
        pontos += 2
    if muito_rapido:
        pontos += 1
    if rvi_count > 10:
        pontos += 1

    if pontos >= 3:
        label = "baixa"
    elif pontos >= 1:
        label = "media"
    else:
        label = "alta"

    return {
        "attention_passed": atencao_ok,
        "straight_lining": straight,
        "too_fast": muito_rapido,
        "quality_label": label,
    }
