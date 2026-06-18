import unittest
import math
import importlib
from uuid import uuid4
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.math_engine import (
    raw_to_percentile, calculate_euclidean_distance, calculate_cosine_similarity,
    detect_frictions, calculate_cronbach_alpha
)

class TestPsychometricMathEngine(unittest.TestCase):
    
    def test_percentile_conversion(self):
        # A média deve retornar 50% de percentil
        self.assertAlmostEqual(raw_to_percentile(10, 10, 2), 50.0, places=1)
        # Score muito alto deve aproximar de 99.9%
        self.assertGreater(raw_to_percentile(20, 10, 2), 99.0)
        # Score muito baixo deve aproximar de 0.1%
        self.assertLess(raw_to_percentile(0, 10, 2), 1.0)

    def test_euclidean_distance(self):
        v1 = [10, 20, 30, 40]
        v2 = [10, 20, 30, 40]
        self.assertEqual(calculate_euclidean_distance(v1, v2), 0.0)
        
        v3 = [10, 20, 30, 40]
        v4 = [15, 20, 30, 40]
        # Distancia entre 10 e 15 no primeiro item = sqrt(5^2) = 5
        self.assertEqual(calculate_euclidean_distance(v3, v4), 5.0)

    def test_cosine_similarity(self):
        v1 = [1.0, 0.0, 0.0, 0.0]
        v2 = [1.0, 0.0, 0.0, 0.0]
        # Mesmos vetores = similaridade 1.0 (100% de match)
        self.assertAlmostEqual(calculate_cosine_similarity(v1, v2), 1.0, places=4)
        
        v3 = [0.0, 1.0, 0.0, 0.0]
        # Vetores ortogonais = similaridade 0.0 (sem compatibilidade)
        self.assertAlmostEqual(calculate_cosine_similarity(v1, v3), 0.0, places=4)

    def test_cronbach_alpha(self):
        # Matriz simples de respostas idênticas deve ter alta consistência
        import numpy as np
        matrix = np.array([
            [5, 5, 5, 5],
            [4, 4, 4, 4],
            [5, 4, 5, 4],
            [3, 3, 3, 3]
        ])
        alpha = calculate_cronbach_alpha(matrix)
        self.assertGreaterEqual(alpha, 0.0)

    def test_friction_detection(self):
        # Mapeia perfil Comunicador Exaurível
        disc_nat = {"D": 20, "I": 85, "S": 15, "C": 10}
        spranger = {"teorico": 50, "economico": 50, "estetico": 50, "social": 50, "individualista": 10, "regulador": 50}
        jung = {"E": 20.0, "I": 80.0, "S": 50.0, "N": 50.0, "T": 50.0, "F": 50.0, "J": 50.0, "P": 50.0}
        
        frictions = detect_frictions(disc_nat, spranger, jung)
        # Deve ter ativado a fricção de "Comunicador Exaurível" devido ao alto I natural e alta introversão do Jung
        frictions_names = [f["name"] for f in frictions]
        self.assertIn("Fricção de Comunicação (Comunicador Exaurível)", frictions_names)

    def test_bigfive_submit_to_results_e2e(self):
        with TestClient(app) as client:
            email = f"bigfive-{uuid4().hex}@example.com"
            register = client.post("/auth/register", json={
                "email": email,
                "password": "123456",
                "full_name": "Pessoa Big Five"
            })
            self.assertEqual(register.status_code, 200)
            token = register.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            items_response = client.get("/questionnaire/items?test_type=BIGFIVE", headers=headers)
            self.assertEqual(items_response.status_code, 200)
            blocks = items_response.json()
            answers = []
            likert = [1, 2, 3, 4, 5]
            idx = 0
            for block in blocks:
                for item in block["items"]:
                    value = likert[idx % len(likert)]
                    if item["dimension"] == "attention_check":
                        text = item["item_text"]
                        if "Muito imprecisa" in text:
                            value = 1
                        elif "Muito precisa" in text:
                            value = 5
                        else:
                            value = 3
                    answers.append({
                        "item_id": item["id"],
                        "block_number": block["block_number"],
                        "value": value
                    })
                    idx += 1

            submit = client.post("/questionnaire/submit", json={
                "test_type": "BIGFIVE",
                "phase": "natural",
                "answers": answers,
                "ttfc_avg": 1200,
                "irt_avg": 2500,
                "rvi_count": 1,
                "raw_telemetry": []
            }, headers=headers)
            self.assertEqual(submit.status_code, 200)
            self.assertTrue(submit.json()["all_completed"])

            results = client.get("/results/me", headers=headers)
            self.assertEqual(results.status_code, 200)
            data = results.json()
            self.assertEqual(set(data["bigfive"]["factors"].keys()), {"O", "C", "E", "A", "N"})
            self.assertEqual(data["bigfive"]["norm_mode"], "intra")
            self.assertEqual(data["bigfive"]["norm_label"], "primeira aplicação — linha de base interna criada")
            self.assertTrue(data["bigfive"]["is_first_assessment"])
            self.assertEqual(data["metadata"]["interpretation_confidence"], "baseline")
            self.assertEqual(len(data["history"]), 1)
            self.assertEqual(data["history"][0]["sequence"], 1)
            self.assertEqual(data["history"][0]["bigfive_raw"]["O"], data["bigfive"]["factors"]["O"]["raw"])
            self.assertIsNone(data["history"][0]["bigfive_percentiles"]["O"])
            for factor in data["bigfive"]["factors"].values():
                self.assertIsNone(factor["percentile"])
                self.assertIn("mean", factor)
                self.assertIn("ci_low", factor)
                self.assertIn("ci_high", factor)
            self.assertIn("tipo_resumo", data["jung_continuo"])
            self.assertIn("eixos", data["jung_continuo"])

            high_answers = []
            for block in blocks:
                for item in block["items"]:
                    if item["dimension"] == "attention_check":
                        text = item["item_text"]
                        if "Muito imprecisa" in text:
                            value = 1
                        elif "Muito precisa" in text:
                            value = 5
                        else:
                            value = 3
                    else:
                        value = 1 if item["reverse_keyed"] else 5
                    high_answers.append({
                        "item_id": item["id"],
                        "block_number": block["block_number"],
                        "value": value
                    })

            submit_again = client.post("/questionnaire/submit", json={
                "test_type": "BIGFIVE",
                "phase": "natural",
                "answers": high_answers,
                "ttfc_avg": 1200,
                "irt_avg": 2500,
                "rvi_count": 1,
                "raw_telemetry": []
            }, headers=headers)
            self.assertEqual(submit_again.status_code, 200)

            second_results = client.get("/results/me", headers=headers)
            self.assertEqual(second_results.status_code, 200)
            second_data = second_results.json()
            self.assertEqual(len(second_data["history"]), 2)
            self.assertEqual([item["sequence"] for item in second_data["history"]], [1, 2])
            self.assertLessEqual(second_data["history"][0]["created_at"], second_data["history"][1]["created_at"])
            self.assertEqual(second_data["history"][-1]["bigfive_raw"]["O"], second_data["bigfive"]["factors"]["O"]["raw"])
            self.assertTrue(second_data["bigfive"]["has_intraindividual_history"])
            for factor in second_data["bigfive"]["factors"].values():
                self.assertEqual(factor["percentile"], 100.0)

if __name__ == "__main__":
    unittest.main()


def test_test_retest_perfeito():
    from backend.app.validacao import test_retest_reliability
    # 10 itens por fator, valores distintos — correlação perfeita quando A == B
    aplicacao = [
        {"fator": f, "escore_raw": float(i + 1)}
        for f in ["O", "C", "E", "A", "N"]
        for i in range(10)
    ]
    resultado = test_retest_reliability(aplicacao, aplicacao)
    for f in ["O", "C", "E", "A", "N"]:
        assert resultado[f] == 1.0, f"Correlação perfeita esperada para {f}, obteve {resultado[f]}"


def test_omega_por_fator_coerente():
    from backend.app.validacao import omega_por_fator
    # 20 respondentes, 10 itens para fator O com alta consistência interna
    # true_score varia de 2.0 a 5.0; noise determinístico e pequeno
    respostas = []
    for resp_idx in range(20):
        true_score = 2.0 + (resp_idx / 19) * 3.0
        for item_idx in range(10):
            noise = (item_idx % 3 - 1) * 0.05
            respostas.append({
                "item_id": f"O_{item_idx + 1}",
                "fator": "O",
                "escore": true_score + noise
            })
    resultado = omega_por_fator(respostas)
    assert resultado["O"] > 0.7, f"Ômega esperado > 0.7, obteve {resultado['O']}"


def test_bigfive_public_norm(monkeypatch):
    from backend.app.config import settings as _settings
    monkeypatch.setattr(_settings, "NORM_MODE", "public")
    monkeypatch.setattr(_settings, "NORM_SOURCE", "open_psychometrics_2018")

    with TestClient(app) as client:
        email = f"public-norm-{uuid4().hex}@example.com"
        reg = client.post("/auth/register", json={
            "email": email, "password": "123456", "full_name": "Norma Publica"
        })
        assert reg.status_code == 200
        headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

        blocks = client.get("/questionnaire/items?test_type=BIGFIVE", headers=headers).json()
        answers = []
        likert = [1, 2, 3, 4, 5]
        for idx, block in enumerate(blocks):
            for item in block["items"]:
                value = likert[idx % len(likert)]
                if item["dimension"] == "attention_check":
                    text = item["item_text"]
                    value = 1 if "Muito imprecisa" in text else (5 if "Muito precisa" in text else 3)
                answers.append({
                    "item_id": item["id"],
                    "block_number": block["block_number"],
                    "value": value
                })

        submit = client.post("/questionnaire/submit", json={
            "test_type": "BIGFIVE", "phase": "natural", "answers": answers,
            "ttfc_avg": 1200, "irt_avg": 2500, "rvi_count": 1, "raw_telemetry": []
        }, headers=headers)
        assert submit.status_code == 200

        data = client.get("/results/me", headers=headers).json()
        assert "norm_info" in data["bigfive"], "norm_info ausente na resposta"
        assert data["bigfive"]["norm_info"]["mode"] == "public"
        assert data["bigfive"]["norm_label"] == "norma pública: open_psychometrics_2018"
        for factor in data["bigfive"]["factors"].values():
            assert 0.0 <= factor["percentile"] <= 100.0


def _auth_headers(client):
    email = f"api-hardening-{uuid4().hex}@example.com"
    reg = client.post("/auth/register", json={
        "email": email,
        "password": "123456",
        "full_name": "API Hardening"
    })
    assert reg.status_code == 200
    return {"Authorization": f"Bearer {reg.json()['access_token']}"}


def _valid_bigfive_answers(client, headers):
    blocks = client.get("/questionnaire/items?test_type=BIGFIVE", headers=headers).json()
    answers = []
    for block in blocks:
        for item in block["items"]:
            value = 3
            if item["dimension"] == "attention_check":
                text = item["item_text"]
                value = 1 if "Muito imprecisa" in text else (5 if "Muito precisa" in text else 3)
            answers.append({"item_id": item["id"], "block_number": block["block_number"], "value": value})
    return answers


def _submit_payload(answers):
    return {
        "test_type": "BIGFIVE",
        "phase": "natural",
        "answers": answers,
        "ttfc_avg": 1200,
        "irt_avg": 2500,
        "rvi_count": 1,
        "raw_telemetry": []
    }


def test_questionnaire_submit_rejects_missing_duplicate_unknown_and_bad_value():
    with TestClient(app) as client:
        headers = _auth_headers(client)
        answers = _valid_bigfive_answers(client, headers)

        assert client.post("/questionnaire/submit", json=_submit_payload(answers[:-1]), headers=headers).status_code == 422

        duplicate = answers.copy()
        duplicate[-1] = duplicate[0]
        assert client.post("/questionnaire/submit", json=_submit_payload(duplicate), headers=headers).status_code == 422

        unknown = [dict(a) for a in answers]
        unknown[0]["item_id"] = 999999
        assert client.post("/questionnaire/submit", json=_submit_payload(unknown), headers=headers).status_code == 422

        bad_value = [dict(a) for a in answers]
        bad_value[0]["value"] = 9
        assert client.post("/questionnaire/submit", json=_submit_payload(bad_value), headers=headers).status_code == 422


def test_register_with_company_does_not_auto_promote_to_hr():
    with TestClient(app) as client:
        email = f"company-{uuid4().hex}@example.com"
        reg = client.post("/auth/register", json={
            "email": email,
            "password": "123456",
            "full_name": "Pessoa Empresa",
            "company_name": "Empresa Sem Convite"
        })
        assert reg.status_code == 200
        assert reg.json()["user"]["role"] == "respondent"


def test_secret_key_required_in_production(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "")
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://frontend.example")
    import backend.app.config as config_module
    try:
        importlib.reload(config_module)
        assert False, "Settings deveria falhar sem SECRET_KEY segura em produção"
    except RuntimeError as exc:
        assert "SECRET_KEY" in str(exc)
    finally:
        monkeypatch.setenv("ENV", "test")
        monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
        monkeypatch.setenv("ENABLE_DEMO_SEED", "true")
        importlib.reload(config_module)


def test_delete_consolidado_preserva_bigfive():
    """
    Prova a invariante F5: o filtro do delete consolidado (bigfive_percentis IS NULL)
    remove apenas resultados sem Big Five e preserva o histórico Big Five intacto.
    """
    from backend.app.database import SessionLocal
    from backend.app.models import PsychometricResult

    db = SessionLocal()
    try:
        # ID de usuário fictício isolado para este teste
        user_id = 999999

        # Limpa qualquer resíduo de execuções anteriores
        db.query(PsychometricResult).filter(
            PsychometricResult.respondent_id == user_id
        ).delete()
        db.commit()

        # Linha Big Five: bigfive_percentis preenchido com dict (como _process_bigfive_results faz)
        r_bigfive = PsychometricResult(
            respondent_id=user_id,
            bigfive_O=35.0, bigfive_C=40.0, bigfive_E=30.0, bigfive_A=45.0, bigfive_N=25.0,
            bigfive_percentis={"O": 60.0, "C": 70.0, "E": 50.0, "A": 80.0, "N": 40.0},
        )
        # Linha consolidada: bigfive_percentis NÃO setado (SQL NULL), como process_psychometric_results
        # faz no ramo sem-Big-Five (linhas 610-639 de main.py nunca setam bigfive_percentis).
        # Não usar bigfive_percentis=None explícito: o JSON type armazena isso como "null" (string),
        # não como SQL NULL, e IS NULL não o encontraria.
        r_consolidado = PsychometricResult(
            respondent_id=user_id,
        )
        db.add(r_bigfive)
        db.add(r_consolidado)
        db.commit()

        # Executa exatamente o filtro do ramo consolidado em main.py
        db.query(PsychometricResult).filter(
            PsychometricResult.respondent_id == user_id,
            PsychometricResult.bigfive_percentis.is_(None)
        ).delete(synchronize_session=False)
        db.commit()

        restantes = db.query(PsychometricResult).filter(
            PsychometricResult.respondent_id == user_id
        ).all()

        assert len(restantes) == 1, f"Esperava 1 resultado, encontrou {len(restantes)}"
        assert restantes[0].bigfive_percentis is not None, "Resultado Big Five foi removido — invariante violada"
    finally:
        # Limpeza
        db.query(PsychometricResult).filter(
            PsychometricResult.respondent_id == user_id
        ).delete()
        db.commit()
        db.close()
