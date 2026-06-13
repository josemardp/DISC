import unittest
import math
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
            self.assertEqual(data["bigfive"]["norm_label"], "régua interna (não é percentil populacional)")
            for factor in data["bigfive"]["factors"].values():
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
            for factor in second_data["bigfive"]["factors"].values():
                self.assertEqual(factor["percentile"], 100.0)

if __name__ == "__main__":
    unittest.main()
