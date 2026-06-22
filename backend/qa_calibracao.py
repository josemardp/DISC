#!/usr/bin/env python
"""
qa_calibracao.py — DIAGNÓSTICO, SOMENTE LEITURA
================================================
Varre grade 11^5 = 161.051 combinações Big Five (0..100 em passos de 10)
chamando AS FUNÇÕES REAIS de backend/app/science_engine.py.

NÃO altera nenhum arquivo de produção. NÃO persiste dados.
Execute a partir da raiz do repo: python backend/qa_calibracao.py
"""

import json
import math
import itertools
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np
import io

# Forcar UTF-8 no stdout do Windows para evitar UnicodeEncodeError com caracteres especiais
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ---------------------------------------------------------------------------
# Path: adiciona raiz do repo para importar backend.app.*
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.app.science_engine import (
    derive_disc_from_big_five,
    derive_jung_from_big_five,
    derive_spranger_from_big_five,
    standard_error_of_measurement,
    confidence_interval,
    mcdonald_omega,
    percentil_por_norma,
)

FATORES = ["O", "C", "E", "A", "N"]
STEPS   = list(range(0, 101, 10))   # 0, 10, 20, ..., 100  (11 valores)
TOTAL   = 11 ** 5                    # 161.051

print("[OK] Funcoes importadas de backend.app.science_engine.", flush=True)
print(f"[1] Varrendo grade {TOTAL:,} pontos (11^5 = {11}^5)...", flush=True)

# ---------------------------------------------------------------------------
# Coleta por série (para correlações)
# ---------------------------------------------------------------------------
DISC_KEYS = ["D", "I", "S", "C"]
SPR_KEYS  = ["teorico", "estetico", "social", "regulador", "individualista", "economico"]
JUNG_KEYS = ["EI_E", "SN_N", "TF_F", "JP_J", "ES"]

disc_ser: Dict[str, List[float]] = {k: [] for k in DISC_KEYS}
spr_ser:  Dict[str, List[float]] = {k: [] for k in SPR_KEYS}
jung_ser: Dict[str, List[float]] = {k: [] for k in JUNG_KEYS}

out_of_range: List[str] = []
nan_errors:   List[str] = []

borderline_count = 0  # combinações com ≥1 eixo Jung em 45–55

# Registros para casos contraintuitivos: (E, A, D_disc)
contraint_records: List[Tuple[int, int, float]] = []

for combo in itertools.product(STEPS, repeat=5):
    O, C, E, A, N = combo
    bf = {"O": float(O), "C": float(C), "E": float(E), "A": float(A), "N": float(N)}

    # --- DISC ---
    try:
        disc = derive_disc_from_big_five(bf)
        for key in DISC_KEYS:
            v = disc[key]
            disc_ser[key].append(v)
            if not math.isfinite(v) or not (0.0 <= v <= 100.0):
                out_of_range.append(f"DISC.{key}={v!r} @ O={O} C={C} E={E} A={A} N={N}")
        contraint_records.append((E, A, disc["D"]))
    except Exception as exc:
        nan_errors.append(f"DISC @ O={O} C={C} E={E} A={A} N={N}: {exc}")
        contraint_records.append((E, A, float("nan")))

    # --- Spranger ---
    try:
        spr = derive_spranger_from_big_five(bf)
        for key in SPR_KEYS:
            v = spr[key]
            spr_ser[key].append(v)
            if not math.isfinite(v) or not (0.0 <= v <= 100.0):
                out_of_range.append(f"SPR.{key}={v!r} @ O={O} C={C} E={E} A={A} N={N}")
    except Exception as exc:
        nan_errors.append(f"SPR @ O={O} C={C} E={E} A={A} N={N}: {exc}")

    # --- Jung ---
    try:
        jung = derive_jung_from_big_five(bf)
        eixos = jung["eixos"]
        vals = {
            "EI_E": eixos["E_I"]["E"],
            "SN_N": eixos["S_N"]["N"],
            "TF_F": eixos["T_F"]["F"],
            "JP_J": eixos["J_P"]["J"],
            "ES":   jung["estabilidade_emocional"],
        }
        for key, v in vals.items():
            jung_ser[key].append(v)
            if not math.isfinite(v) or not (0.0 <= v <= 100.0):
                out_of_range.append(f"JUNG.{key}={v!r} @ O={O} C={C} E={E} A={A} N={N}")
        if jung["borderline_count"] > 0:
            borderline_count += 1
    except Exception as exc:
        nan_errors.append(f"JUNG @ O={O} C={C} E={E} A={A} N={N}: {exc}")

print(f"  → out-of-range: {len(out_of_range)} | NaN/erros: {len(nan_errors)}", flush=True)

# ---------------------------------------------------------------------------
# (i) Correlações entre todas as dimensões derivadas
# ---------------------------------------------------------------------------
print("\n[2] Calculando correlações entre dimensões derivadas...", flush=True)

all_series: Dict[str, np.ndarray] = {}
for k in DISC_KEYS: all_series[f"DISC.{k}"] = np.array(disc_ser[k])
for k in SPR_KEYS:  all_series[f"SPR.{k}"]  = np.array(spr_ser[k])
for k in JUNG_KEYS: all_series[f"JUNG.{k}"] = np.array(jung_ser[k])

keys = list(all_series.keys())
high_corr_pairs: List[Tuple[str, str, float]] = []

for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        ki, kj = keys[i], keys[j]
        c = float(np.corrcoef(all_series[ki], all_series[kj])[0, 1])
        if abs(c) >= 0.999:
            high_corr_pairs.append((ki, kj, round(c, 6)))

print(f"  Pares com |corr| ≥ 0.999: {len(high_corr_pairs)}", flush=True)
for a, b, c in sorted(high_corr_pairs, key=lambda x: -abs(x[2])):
    print(f"    {a} ↔ {b}  corr = {c:+.6f}", flush=True)

# ---------------------------------------------------------------------------
# (ii) Casos contraintuitivos: E alto mas D baixo — top-5 mais extremos
# ---------------------------------------------------------------------------
print("\n[3] Casos contraintuitivos (E ≥ 70 mas D baixo)...", flush=True)

valid_cases = [(E, A, D) for E, A, D in contraint_records
               if E >= 70 and math.isfinite(D)]
# Deduplica por (E, A) — o D é determinístico dado E e A
seen_ea: set = set()
unique_cases: List[Tuple[int, int, float]] = []
for E, A, D in valid_cases:
    if (E, A) not in seen_ea:
        seen_ea.add((E, A))
        unique_cases.append((E, A, D))
# ordenar por D crescente (D mais baixo = mais contraintuitivo)
unique_cases.sort(key=lambda x: x[2])
top5_high_e_low_d = unique_cases[:5]

print("  Top-5 pares distintos (E alto, D mais baixo):", flush=True)
for E, A, D in top5_high_e_low_d:
    print(f"    E={E:3d}, A={A:3d}  ->  D={D:.1f}  "
          f"(formula: ({E} + {100-A}) / 2 = {D:.1f})", flush=True)

# ---------------------------------------------------------------------------
# (iii) Fração borderline Jung (≥1 eixo em 45–55)
# ---------------------------------------------------------------------------
frac_bl = borderline_count / TOTAL
print(f"\n[4] Fração borderline Jung (≥1 eixo em 45–55): "
      f"{borderline_count}/{TOTAL} = {frac_bl:.4%}", flush=True)

# ---------------------------------------------------------------------------
# (iv) NaN / out-of-range / erro
# ---------------------------------------------------------------------------
print(f"\n[5] Out-of-range: {len(out_of_range)} | Erros: {len(nan_errors)}", flush=True)
if out_of_range:
    print("  Exemplos (primeiros 5):", flush=True)
    for ev in out_of_range[:5]:
        print(f"    {ev}", flush=True)

# ---------------------------------------------------------------------------
# (d) Sanity-check da função percentil_por_norma vs norms_ipip_neo.json
# ---------------------------------------------------------------------------
print("\n[6] Sanity-check percentil_por_norma vs norms_ipip_neo.json...", flush=True)

norm_path = Path(__file__).parent / "app" / "norms_ipip_neo.json"
with open(norm_path, "r", encoding="utf-8") as f:
    norms_data = json.load(f)

fonte = "open_psychometrics_2018"
src = norms_data["sources"][fonte]
print(f"  Fonte: {fonte} (n={src['n']:,})", flush=True)

sanity_all_ok = True
sanity_table: List[dict] = []

for fator in FATORES:
    m  = src[fator]["mean"]
    sd = src[fator]["sd"]
    if m is None or sd is None:
        print(f"  [x] {fator}: norma ausente nesta fonte", flush=True)
        sanity_all_ok = False
        continue

    p_mean    = percentil_por_norma(m,      m, sd)   # esperado ~50.00
    p_plus1   = percentil_por_norma(m + sd, m, sd)   # esperado ~84.13
    p_minus1  = percentil_por_norma(m - sd, m, sd)   # esperado ~15.87

    ok_mean  = abs(p_mean   - 50.00)  < 0.5
    ok_plus  = abs(p_plus1  - 84.13)  < 0.5
    ok_minus = abs(p_minus1 - 15.87)  < 0.5
    row_ok   = ok_mean and ok_plus and ok_minus

    if not row_ok:
        sanity_all_ok = False

    mark = "[v]" if row_ok else "[x]"
    print(
        f"  {mark} {fator}  µ={m:.4f} σ={sd:.4f}  |  "
        f"pct(µ)={p_mean:.2f}  pct(µ+σ)={p_plus1:.2f}  pct(µ-σ)={p_minus1:.2f}",
        flush=True,
    )
    sanity_table.append({
        "fator": fator, "mean": m, "sd": sd,
        "p_mean": p_mean, "p_plus1sd": p_plus1, "p_minus1sd": p_minus1,
        "ok": row_ok,
    })

print(f"\n  Sanity-check OK: {'SIM — percentil_por_norma reproduz norma corretamente.' if sanity_all_ok else 'NÃO — verificar função.'}", flush=True)

# ---------------------------------------------------------------------------
# Resumo final para uso no relatório
# ---------------------------------------------------------------------------
print("\n" + "=" * 70, flush=True)
print("RESUMO PARA RELATÓRIO", flush=True)
print("=" * 70, flush=True)
print(f"  Grade: {TOTAL:,} pontos | 5 fatores × 11 valores (0..100, passo 10)", flush=True)
print(f"  Pares com |corr| ≥ 0.999 : {len(high_corr_pairs)}", flush=True)
print(f"  Borderline Jung (≥1 eixo): {frac_bl:.2%}", flush=True)
print(f"  Out-of-range              : {len(out_of_range)}", flush=True)
print(f"  NaN/Erros                 : {len(nan_errors)}", flush=True)
print(f"  Sanity percentil          : {'OK' if sanity_all_ok else 'FALHOU'}", flush=True)
print("=" * 70, flush=True)
print("\n[OK] qa_calibracao.py concluído — nenhum arquivo de produção alterado.", flush=True)
