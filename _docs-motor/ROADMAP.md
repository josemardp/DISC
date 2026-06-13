# ROADMAP — Fases do projeto DISC

> Fonte única da verdade: este arquivo. Siga de cima para baixo.
> Última atualização: 2026-06-13 (F3 — documentação viva concluída).

---

## Visão geral de status

| Fase | Tema | Status | Prioridade |
|---|---|---|---|
| **F1** | Persistência do banco (Supabase Postgres) | ✅ CONCLUÍDA | — |
| **F2** | Suíte 100% verde + higiene de imports | ✅ CONCLUÍDA | — |
| **F3** | Documentação viva (auto-documentar a evolução) | ✅ CONCLUÍDA | — |
| **F4** | Normas públicas reais (sair do `intra`) | 🔲 Pendente | 🟡 Média |
| **F5** | Validação com dados reais (teste-reteste humano, AFC) | 🔲 Pendente | 🟡 Média |
| **F6** | Decisão sobre Spranger (medir vs. manter ilustrativo) | 🔲 Pendente | 🟢 Baixa |
| **F7** | Higiene técnica (deprecações: genai, on_event, utcnow) | 🔲 Pendente | 🟢 Baixa |
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

## F4 — Normas públicas reais

**Critério de pronto:** `NORM_MODE=public` usa normas reais citadas e versionadas em `backend/app/norms_ipip_neo.json`.

**Dependência:** fonte pública real (ex: dataset IPIP-NEO aberto) — não fabricar normas.

**Prompt pronto em:** `_docs-motor/PLANO_EVOLUCAO_DISC_v2.md` § 4 (PROMPT F4).

---

## F5 — Validação com dados reais

**Critério de pronto:** exportação CSV funciona; `validacao.py` testado; `_docs-motor/PROTOCOLO_VALIDACAO.md` documentado.

**Dependência:** N de respondentes reais suficiente (CFA exige amostra grande).

**Prompt pronto em:** `_docs-motor/PLANO_EVOLUCAO_DISC_v2.md` § 4 (PROMPT F5).

---

## F6 — Decisão sobre Spranger

**Critério de pronto:** decisão documentada em `_docs-motor/DECISOES.md` (ADR-05 atualizado) e implementada.

Opções: (a) medir com itens próprios validados; (b) manter ilustrativo com rótulo claro na UI e no laudo.

**Prompt pronto em:** `_docs-motor/PLANO_EVOLUCAO_DISC_v2.md` § 4 (PROMPT F6).

---

## F7 — Higiene técnica

**Critério de pronto:** sem avisos de depreciação críticos; suíte 22/22 verde após cada migração.

Itens pendentes (confirmados nos warnings da suíte):
- `google.generativeai` → `google.genai`
- `@app.on_event("startup")` → lifespan handlers (FastAPI)
- `datetime.utcnow()` → timezone-aware (`datetime.now(datetime.UTC)`)

**Prompt pronto em:** `_docs-motor/PLANO_EVOLUCAO_DISC_v2.md` § 4 (PROMPT F7).

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

**F4/F5** (conforme a família for usando os dados) → **F6/F7** (quando fizer sentido técnico) → **F8** (opcional) → **F9** (quando DISC estiver redondo e `2-perguntas` for integrada).

**Regra de ouro:** um prompt por vez, testes verdes antes de avançar, **pare antes de mexer no schema/banco**.
