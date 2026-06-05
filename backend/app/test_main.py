import unittest
import math
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

if __name__ == "__main__":
    unittest.main()
