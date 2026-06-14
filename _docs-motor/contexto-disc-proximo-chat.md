# Contexto DISC — retomada (2026-06-13)

> Resumo para retomar o trabalho em outra sessão.
> Fontes de verdade: [ROADMAP.md](ROADMAP.md) | [STATUS.md](STATUS.md) | [DECISOES.md](DECISOES.md)

---

## O que está pronto (F1–F7 concluídas)

| Fase | O que foi feito | Evidência |
|---|---|---|
| **F1** | Supabase Postgres em produção; auth e questionário funcionando end-to-end | `database.py`, `api/index.py`, Vercel deploy |
| **F2** | Suíte 100% verde: 22/22 passed; `httpx>=0.27`; import órfão removido de `main.py` | commit 05c74fa |
| **F3** | Documentação viva: 7 arquivos criados/atualizados, coerentes entre si | commit a353857 |
| **F4** | `NORM_MODE=public` com `norms_ipip_neo.json` (open_psychometrics_2018, N≈603k); `NORM_SOURCE` env; `norm_info` no `/results/me` | commit f850200 |
| **F5** | `GET /admin/export/bigfive` (CSV 13 colunas); `validacao.py` (test_retest_reliability + omega_por_fator); `PROTOCOLO_VALIDACAO.md` | commit f6d98d9 |
| **F6** | Spranger com campo `"aviso"` na API; instrução no prompt Gemini; ADR-05 atualizado | commit df02877 |
| **F7** | `google.genai`; lifespan handler; `datetime.now(timezone.utc)` — zero warnings próprios | commit f6d98d9 (absorvido com F5) |

**Suíte atual:** 25/25 passed, ~2.7s, zero warnings de depreciação próprios.

**Núcleo científico implementado:**
- Big Five IPIP-50 (50 itens + 3 atenção, `reverse_keyed`, escala 1–5)
- Ômega de McDonald, SEM, IC95%
- Jung contínuo derivado (4 eixos + `borderline` + Estabilidade Emocional)
- DISC e Spranger derivados (heurísticos — camadas de apresentação; Spranger marcado como ilustrativo desde F6)
- NORM_MODE=intra (padrão) e NORM_MODE=public (open_psychometrics_2018)
- Laudo anti-Barnum via Gemini 1.5 Flash + fallback local (7 seções obrigatórias)
- Qualidade de resposta (atenção, straight-lining, velocidade, RVI)

**Deploy:** Vercel, branch `main`, auto-deploy ativo. DATABASE_URL + GEMINI_API_KEY setados no Vercel e salvos em `Drive/segredos/disc-env.txt`.

---

## Pendência F5 — validação empírica

A infraestrutura está pronta, mas o teste-reteste real ainda não foi executado.

**O que falta:**
1. Josemar e Esdra respondem o Big Five no sistema em produção (T1).
2. Aguardar 2–4 semanas.
3. Ambos respondem novamente (T2).
4. Exportar os dois CSVs via `GET /admin/export/bigfive`.
5. Rodar `test_retest_reliability()` conforme `_docs-motor/PROTOCOLO_VALIDACAO.md`.
6. Critério: r ≥ 0,80 por fator (Kline, 2000).

CFA exige N ≥ 200 — meta futura, fora do escopo familiar.

---

## Próxima fase

**F8** (opcional) — TIRT: modelo Thurstoniano para blocos ipsativos DISC. Avaliar viabilidade antes de abrir — DISC hoje é camada derivada do Big Five; TIRT só vale se houver decisão de reativar escolha-forçada com escores válidos e amostra suficiente.

**F9** (próximo passo real) — Camada de Autoconhecimento. Depende de:
- (a) Dados reais acumulados via F5 para validação empírica.
- (b) Decisão de trazer pasta `2-perguntas` (1.242 perguntas, 11 blocos, Google Drive).

---

## Regras que não mudam

1. Testes verdes antes de avançar: `pytest backend/app/ -v` deve retornar 25/25.
2. Não mexer no schema/banco sem pause e confirmação.
3. `2-perguntas` fica fora do repo e nunca entra no motor de pontuação (somente F9, via RAG/pgvector, na saída).
4. Segredos em `Drive/segredos/disc-env.txt` — nunca no código.
5. Um prompt por vez.
