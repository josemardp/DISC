# ROADMAP — Fases do projeto DISC

> Fonte única da verdade: este arquivo. Siga de cima para baixo.
> Última atualização: 2026-06-13 (F6 — Spranger ilustrativo concluída; F1–F7 fechadas).

---

## Visão geral de status

| Fase | Tema | Status | Prioridade |
|---|---|---|---|
| **F1** | Persistência do banco (Supabase Postgres) | ✅ CONCLUÍDA | — |
| **F2** | Suíte 100% verde + higiene de imports | ✅ CONCLUÍDA | — |
| **F3** | Documentação viva (auto-documentar a evolução) | ✅ CONCLUÍDA | — |
| **F4** | Normas públicas reais (sair do `intra`) | ✅ CONCLUÍDA | — |
| **F5** | Validação com dados reais (infraestrutura; teste-reteste empírico pendente) | ✅ CONCLUÍDA | — |
| **F6** | Decisão sobre Spranger (mantido como ilustrativo — opção b) | ✅ CONCLUÍDA | — |
| **F7** | Higiene técnica (deprecações: genai, on_event, utcnow) | ✅ CONCLUÍDA | — |
| **F8** | TIRT (escolha-forçada do DISC com escores válidos) | 🔲 Opcional | ⚪ |
| **F9** | Camada de Autoconhecimento (2-perguntas + IA) | 🔲 Visão futura | 🔵 |

---

## F1 — Persistência (Supabase Postgres) ✅ CONCLUÍDA

**Critério de pronto:** app sobe contra Postgres; tabelas criadas; dados persistem entre reinícios; seed não duplica; auth funcionando.

**O que foi feito:**
- `database.py`: engine Postgres com `pool_pre_ping`, `pool_recycle=300`, `connect_timeout=5`; normalização `postgres://` → `postgresql+psycopg2://`; fallback SQLite `/tmp` apenas quando DATABASE_URL já é sqlite
- `api/index.py`: proxy ASGI com lazy import, lifespan próprio e error handling JSON
- `main.py`: `@app.exception_handler(Exception)` — erros viram JSON (não plain text)
- Supabase: tabelas criadas via `create_all`; seed DISC (24 blocos) e Big Five (50 itens IPIP) carregados
- Vercel: `DATABASE_URL` setada (Transaction pooler, port 6543, sslmode=require)
- Segredos: salvos em `Drive/segredos/disc-env.txt` (ver REGRA_MESTRE_SYNC.md)
- Endpoints temporários de debug removidos: `/api/db-info`, `/api/ping`, `/api/simple`

---

## F2 — Suíte 100% verde + higiene ✅ CONCLUÍDA

**Critério de pronto:** `pytest backend/app/` retorna 22/22 verdes; `httpx>=0.27` no requirements; import órfão removido de `main.py`.

**O que foi feito (commit 05c74fa):**
- `backend/app/conftest.py`: fixture `session`-scoped `autouse` que cria tabelas + roda seed antes dos testes — testes independentes do ciclo de startup
- `backend/app/test_main.py`: `test_bigfive_submit_to_results_e2e` usa `with TestClient(app) as client:` — startup dispara, tabelas existem
- `backend/requirements.txt`: `httpx>=0.27` adicionado (dependência do TestClient do FastAPI)
- `backend/app/main.py`: import órfão `calculate_cronbach_alpha` removido (função permanece em `math_engine.py`, usada em `test_main.py:50`)
- Resultado confirmado: **22/22 passed** em 5.29s

---

## F3 — Documentação viva ✅ CONCLUÍDA

**Critério de pronto:** 7 arquivos criados/atualizados, coerentes entre si, refletindo o código real, com referências cruzadas.

**O que foi feito:**
- `_docs-motor/ROADMAP.md` (este arquivo) — fases F1–F9 com status e critério de pronto
- `_docs-motor/STATUS.md` — fotografia do estado atual
- `_docs-motor/DECISOES.md` — 10 ADRs completos
- `CHANGELOG.md` — v1.0.0 → v1.2.0
- `backend/MANUAL_TECNICO.md` — instrumento psicométrico atualizado para v0.3
- `README.md` — visão geral, stack, rodar local, configurar Supabase/Vercel
- `_docs-motor/contexto-disc-proximo-chat.md` — resumo para retomada

---

## F4 — Normas públicas reais ✅ CONCLUÍDA

**Commit:** f850200

**O que foi feito:**
- `config.py`: `NORM_SOURCE` (env; default `open_psychometrics_2018`)
- `main.py`: `load_norm_source()`, `_bigfive_scaled_scores()` usa `percentil_por_norma` do science_engine; `norm_info` no `/results/me` quando `NORM_MODE=public`
- `backend/app/norms_ipip_neo.json`: fonte `open_psychometrics_2018` (N≈603k, 2016–2018, online sample) com `mean` e `sd` por fator (escala 10–50)
- `test_main.py`: `test_bigfive_public_norm` — monkeypatch, e2e, percentis 0–100
- Resultado: **25/25 passed**

---

## F5 — Validação com dados reais ✅ CONCLUÍDA (infraestrutura)

**Commit:** f6d98d9 (absorveu F7 — ver nota)

**O que foi feito:**
- `main.py`: `GET /admin/export/bigfive` — CSV 13 colunas, `Content-Type: text/csv`, role admin
- `backend/app/validacao.py`: `test_retest_reliability()` (Pearson por fator) e `omega_por_fator()` (chama `mcdonald_omega` do science_engine)
- `test_main.py`: `test_test_retest_perfeito` (r=1.0 quando A==B) e `test_omega_por_fator_coerente` (omega>0.7 com dados sintéticos)
- `_docs-motor/PROTOCOLO_VALIDACAO.md`: protocolo Josemar + Esdra, intervalo 2–4 semanas, r≥0,80 (Kline 2000), CFA N≥200 (Hu & Bentler 1999), aviso de dados sensíveis
- Resultado: **25/25 passed**

**⚠️ Pendência empírica:** a infraestrutura está pronta, mas o teste-reteste real (Josemar + Esdra com 2–4 semanas de intervalo) ainda não foi executado. Ver `PROTOCOLO_VALIDACAO.md`.

---

## F6 — Decisão sobre Spranger ✅ CONCLUÍDA

**Commit:** df02877

**Decisão tomada:** opção (b) — manter Spranger como estimativa ilustrativa derivada do Big Five. Opção (a) descartada: exigiria ~30 itens próprios e N ≥ 200 para validação.

**O que foi feito:**
- `science_engine.py`: campo `"aviso"` no retorno de `derive_spranger_from_big_five()`
- `main.py`: `"aviso"` repassado nas 2 ocorrências do dict `"spranger"` em `/results/me`
- `gemini_service.py`: instrução de rótulo adicionada ao prompt (seção Spranger)
- `DECISOES.md`: ADR-05 atualizado com decisão F6 (2026-06-13)
- Resultado: **25/25 passed**

---

## F7 — Higiene técnica ✅ CONCLUÍDA

**Commit:** f6d98d9 (absorvido junto com F5 — todos os arquivos commitados de uma vez)

**O que foi feito:**
- `requirements.txt`: `google-genai>=0.8` adicionado
- `gemini_service.py`: `import google.generativeai as genai` → `from google import genai`; chamada API atualizada para `genai.Client` + `client.models.generate_content`
- `main.py`: `@app.on_event("startup")` → `@asynccontextmanager async def lifespan`; `datetime.utcnow()` → `datetime.now(timezone.utc)`
- `models.py`: 7× `default=datetime.utcnow` → `default=lambda: datetime.now(timezone.utc)`
- Resultado: **25/25 passed**, zero warnings de depreciação próprios

---

## F8 — TIRT (opcional)

**Critério de pronto:** decisão fundamentada sobre viabilidade do modelo Thurstoniano para blocos ipsativos DISC.

**Observação:** DISC hoje é camada derivada do Big Five. TIRT só vale se houver decisão de reativar escolha-forçada com escores válidos e amostra suficiente.

**Prompt pronto em:** `_docs-motor/PLANO_EVOLUCAO_DISC_v2.md` § 4 (PROMPT F8).

---

## F9 — Camada de Autoconhecimento (visão futura)

**Pré-requisitos:** F1 concluída (✅) + extensão `pgvector` ativa no Supabase.

**Material disponível:** pasta `2-perguntas` no Google Drive — 1.242 perguntas, 11 blocos, dois níveis:
- **Narrativo** (Blocos 01–10, ~1.030 perguntas) → embeddings no pgvector (RAG); respostas em texto livre; não pré-codificar
- **Rastreio psicométrico** (Bloco 11, 212 itens) → pontuação quantitativa contra pontos de corte do `schema-bloco-11.json`; derivado de instrumentos clínicos validados

**Arquitetura (três camadas):**
- Base: Supabase Postgres + pgvector
- Fontes: perfil pontuado (DISC) + respostas biográficas (Perguntas Mestres)
- Topo: IA de aconselhamento — lê as duas fontes, condicionada ao perfil

**Regra que não muda:** as perguntas **nunca** entram no motor de pontuação DISC. A integração acontece apenas na camada de saída (aconselhamento).

**Sincronização:** `2-perguntas` fica fora do repo git (`1-disc-app`) — pasta irmã no Google Drive (ver `REGRA_MESTRE_SYNC.md`).

---

## Ordem recomendada

**F1–F7** concluídas → **F8** (opcional — avaliar viabilidade TIRT antes de abrir) → **F9** (próximo passo real — depende de dados reais acumulados via F5 e de trazer `2-perguntas`).

**Regra de ouro:** um prompt por vez, testes verdes antes de avançar, **pare antes de mexer no schema/banco**.
