"""
test_science_engine.py — prova que o núcleo científico funciona.
Rodar:  python3 -m pytest test_science_engine.py -v
"""
import numpy as np
import science_engine as se
from seed_big_five_ipip import construir_itens_bigfive, ITENS_IPIP_50


# ---------- Big Five: pontuação e itens reversos ----------

def test_reverso_inverte_na_escala_1_5():
    assert se._aplica_reverso(1, True) == 5
    assert se._aplica_reverso(5, True) == 1
    assert se._aplica_reverso(3, True) == 3
    assert se._aplica_reverso(2, False) == 2


def test_score_big_five_respeita_reverso():
    # Pessoa que marca 5 em todos os itens de Extroversão.
    # Itens positivos contam 5; reversos viram 1 -> isso é o comportamento correto.
    respostas = []
    for dim, texto, rev in ITENS_IPIP_50:
        if dim == "E":
            respostas.append({"dimension": "E", "value": 5, "reverse_keyed": rev})
    res = se.score_big_five(respostas)
    # 5 itens positivos (valem 5) + 5 reversos (viram 1) = 25 + 5 = 30, em 10 itens
    assert res["E"]["n_itens"] == 10
    assert res["E"]["raw"] == 30.0


def test_estabilidade_emocional_inverte_neuroticismo():
    respostas = [{"dimension": "N", "value": 5, "reverse_keyed": False} for _ in range(10)]
    res = se.score_big_five(respostas)
    assert res["N"]["mean"] == 5.0
    # ES = 6 - 5 = 1.0 (baixa estabilidade quando neuroticismo é máximo)
    assert res["ES"]["mean"] == 1.0


def test_itens_atencao_sao_ignorados_no_escore():
    respostas = [
        {"dimension": "E", "value": 4, "reverse_keyed": False},
        {"dimension": "attention_check", "value": 1, "reverse_keyed": False},
    ]
    res = se.score_big_five(respostas)
    assert res["E"]["n_itens"] == 1  # o item de atenção não entrou


# ---------- Confiabilidade ----------

def test_omega_alto_para_itens_coerentes():
    # Dados em que todos os itens correlacionam forte -> omega alto
    rng = np.random.default_rng(42)
    fator = rng.normal(0, 1, 200)
    matriz = np.column_stack([fator + rng.normal(0, 0.3, 200) for _ in range(8)])
    omega = se.mcdonald_omega(matriz)
    assert omega > 0.80


def test_omega_baixo_para_itens_aleatorios():
    rng = np.random.default_rng(7)
    matriz = rng.normal(0, 1, (200, 8))  # itens independentes
    omega = se.mcdonald_omega(matriz)
    assert omega < 0.50


def test_sem_e_intervalo_de_confianca():
    sem = se.standard_error_of_measurement(sd=15.0, reliability=0.84)
    assert sem > 0
    low, high = se.confidence_interval(70.0, sem)
    assert low < 70.0 < high


# ---------- Normatização ----------

def test_percentil_na_media_da_60():
    # escore igual à média -> percentil 50
    assert se.percentil_por_norma(raw=30, mean=30, sd=5) == 50.0


def test_percentil_intraindividual():
    out = se.percentil_intraindividual(raw_atual=40, historico=[10, 20, 30])
    assert out["posicao_relativa"] == 100.0  # 40 é maior que todos os anteriores
    assert out["n_medidas"] == 4


# ---------- Jung derivado do Big Five ----------

def test_jung_deriva_tipo_de_quatro_letras():
    bf = {"E": 70, "O": 80, "A": 75, "C": 65, "N": 40}
    jung = se.derive_jung_from_big_five(bf)
    assert jung["tipo_resumo"] == "ENFJ"
    # Estabilidade emocional = 100 - 40 = 60
    assert jung["estabilidade_emocional"] == 60.0


def test_jung_marca_borderline():
    bf = {"E": 50, "O": 52, "A": 80, "C": 80, "N": 30}
    jung = se.derive_jung_from_big_five(bf)
    assert jung["eixos"]["E_I"]["borderline"] is True   # 50 está em 45-55
    assert jung["eixos"]["T_F"]["borderline"] is False  # 80 não é borderline


def test_jung_borderline_majoritario_retorna_indefinido():
    bf = {"E": 50, "O": 50, "A": 50, "C": 50, "N": 50}
    jung = se.derive_jung_from_big_five(bf)
    assert jung["tipo_resumo"] == "indefinido"
    assert jung["tipo_fechado"] is False
    assert jung["borderline_count"] == 4


def test_jung_eixos_contínuos_somam_100():
    bf = {"E": 73, "O": 41, "A": 60, "C": 55, "N": 50}
    jung = se.derive_jung_from_big_five(bf)
    e = jung["eixos"]["E_I"]
    assert abs((e["E"] + e["I"]) - 100.0) < 0.01


# ---------- Camadas derivadas e qualidade ----------

def test_disc_derivado_retorna_quatro_eixos():
    bf = {"E": 60, "O": 50, "A": 40, "C": 70, "N": 30}
    disc = se.derive_disc_from_big_five(bf)
    for k in ["D", "I", "S", "C"]:
        assert 0 <= disc[k] <= 100


def test_qualidade_detecta_straight_lining():
    q = se.response_quality_index(valores=[3, 3, 3, 3, 3], atencao_ok=True, irt_avg_ms=2000, rvi_count=0)
    assert q["straight_lining"] is True
    assert q["quality_label"] in ("media", "baixa")


def test_qualidade_alta_resposta_normal():
    q = se.response_quality_index(valores=[1, 4, 2, 5, 3], atencao_ok=True, irt_avg_ms=3000, rvi_count=1)
    assert q["quality_label"] == "alta"


# ---------- Seed IPIP ----------

def test_seed_tem_50_itens_mais_atencao():
    itens = construir_itens_bigfive()
    bigfive = [i for i in itens if i["dimension"] in se.FATORES_BIG_FIVE]
    atencao = [i for i in itens if i["dimension"] == "attention_check"]
    assert len(bigfive) == 50
    assert len(atencao) == 3
    # 10 itens por fator
    for f in se.FATORES_BIG_FIVE:
        assert sum(1 for i in bigfive if i["dimension"] == f) == 10
