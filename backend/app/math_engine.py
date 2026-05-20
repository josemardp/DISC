import math
import numpy as np
from typing import Dict, List, Tuple

def normal_cdf(z: float) -> float:
    """
    Função de Distribuição Cumulativa de uma distribuição normal padrão (Phi(Z)).
    Utiliza uma aproximação de erro de função de alta precisão (equivalente a scipy.stats.norm.cdf).
    Retorna um valor entre 0.0 e 1.0.
    """
    try:
        return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
    except Exception:
        # Fallback de segurança para valores extremos
        if z < -6:
            return 0.0
        if z > 6:
            return 1.0
        return 0.5

def calculate_z_score(raw_score: float, mean: float, std_dev: float) -> float:
    """
    Calcula o Score-Z de uma nota bruta.
    Previne divisão por zero se o desvio padrão for nulo.
    """
    if std_dev == 0:
        return 0.0
    return (raw_score - mean) / std_dev

def raw_to_percentile(raw_score: float, mean: float, std_dev: float) -> float:
    """
    Normaliza a nota bruta (X) contra a média e desvio padrão populacional e converte para Percentil (0 a 100).
    """
    z = calculate_z_score(raw_score, mean, std_dev)
    percentile = normal_cdf(z) * 100.0
    return round(max(0.0, min(100.0, percentile)), 2)

def calculate_euclidean_distance(v1: List[float], v2: List[float]) -> float:
    """
    Calcula a distância euclidiana entre dois vetores numéricos de mesma dimensão.
    Fórmula: Raiz_Quadrada(Soma((v1_i - v2_i)^2))
    """
    if len(v1) != len(v2) or not v1:
        return 0.0
    squared_diffs = [(a - b) ** 2 for a, b in zip(v1, v2)]
    return round(math.sqrt(sum(squared_diffs)), 4)

def calculate_cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """
    Calcula a Similaridade de Cossenos entre dois vetores (Candidato vs Cargo).
    Fórmula: (v1 . v2) / (||v1|| * ||v2||)
    Retorna um valor entre 0.0 e 1.0.
    """
    if len(v1) != len(v2) or not v1:
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a ** 2 for a in v1))
    norm_v2 = math.sqrt(sum(b ** 2 for b in v2))
    
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
        
    similarity = dot_product / (norm_v1 * norm_v2)
    return round(max(0.0, min(1.0, similarity)), 4)

def detect_frictions(disc_percentiles: Dict[str, float], 
                      spranger_percentiles: Dict[str, float], 
                      jung_scores: Dict[str, float]) -> List[Dict[str, str]]:
    """
    Calcula as fricções psicológicas ativas com base nas regras de interferência de construtos.
    Retorna uma lista de fricções detectadas com títulos e descrições detalhadas.
    """
    frictions = []
    
    # 1. Fricção de Execução (Regulador Baixo vs Conformidade Alta)
    # DISC.C >= 70% e Spranger.Regulador <= 35%
    c_score = disc_percentiles.get("C", 0.0) / 100.0
    regulador = spranger_percentiles.get("regulador", 0.0) / 100.0
    if c_score >= 0.70 and regulador <= 0.35:
        frictions.append({
            "id": "friccao_execucao",
            "name": "Fricção de Execução (Alinhamento de Valor)",
            "severity": "Médio",
            "description": (
                "O indivíduo segue regras e padrões operacionais à perfeição (Conformidade Alta), "
                "porém não possui conexão interna de valores com o arcabouço regulatório da empresa (Baixo Regulador). "
                "Gera conformismo formal com propensão à desmotivação crônica por sentir que as regras são burocráticas."
            )
        })
        
    # 2. Fricção de Comunicação (Comunicador Exaurível)
    # DISC.I >= 68% e Jung.Introversion >= 60%
    i_score = disc_percentiles.get("I", 0.0) / 100.0
    introversion = jung_scores.get("I", 0.0) / (jung_scores.get("I", 1.0) + jung_scores.get("E", 1.0) or 1.0)
    if i_score >= 0.68 and introversion >= 0.60:
        frictions.append({
            "id": "friccao_comunicacao",
            "name": "Fricção de Comunicação (Comunicador Exaurível)",
            "severity": "Alto",
            "description": (
                "O indivíduo possui alta competência verbal, carisma e poder persuasivo (Alto I), "
                "porém sua bateria energética cognitiva é recarregada pelo isolamento e reflexão (Introvertido). "
                "Gera um esgotamento rápido de energia após reuniões e interações sociais intensivas. "
                "Demanda tempos de bloqueio pós-reunião para manter a produtividade estável."
            )
        })

    # 3. Fricção de Decisão (Decisor Conflituoso)
    # DISC.D >= 65% e Jung.F (Sentimento) >= 65%
    d_score = disc_percentiles.get("D", 0.0) / 100.0
    feeling = jung_scores.get("F", 0.0) / (jung_scores.get("F", 1.0) + jung_scores.get("T", 1.0) or 1.0)
    if d_score >= 0.65 and feeling >= 0.65:
        frictions.append({
            "id": "friccao_decisao",
            "name": "Fricção de Decisão (Decisor Conflituoso)",
            "severity": "Médio",
            "description": (
                "O indivíduo sente forte impulso interno para comandar, tomar decisões rápidas e ser assertivo (Alto D), "
                "mas seu critério interno de julgamento é fortemente guiado pela empatia, harmonia e impacto nas pessoas (Alto Sentimento). "
                "Gera hesitação interna e estresse emocional ao tomar decisões duras de demissões ou cortes organizacionais."
            )
        })

    return frictions

def calculate_cronbach_alpha(response_matrix: np.ndarray) -> float:
    """
    Calcula o Alpha de Cronbach de uma matriz de respostas (amostras x itens).
    Fórmula: (k / (k-1)) * (1 - soma(var_itens) / var_total)
    """
    k = response_matrix.shape[1]
    if k <= 1:
        return 0.0
    
    item_vars = np.var(response_matrix, axis=0, ddof=1)
    total_scores = np.sum(response_matrix, axis=1)
    total_var = np.var(total_scores, ddof=1)
    
    if total_var == 0:
        return 0.0
        
    alpha = (k / (k - 1)) * (1.0 - (np.sum(item_vars) / total_var))
    return round(float(alpha), 4)
