# ROADMAP — Fases do projeto DISC (atualizado 2026-06-10)

> Fonte única da verdade: este arquivo. Siga de cima para baixo.

## Status das fases

| Fase | Tema | Status | Prioridade |
|---|---|---|---|
| **F1** | Persistência do banco (Supabase Postgres) | ✅ CONCLUÍDA | — |
| **F2** | Suíte 100% verde + higiene de imports | 🔜 PRÓXIMA | 🟠 Alta |
| **F3** | Documentação viva (auto-documentar a evolução) | 🔲 Pendente | 🟠 Alta |
| **F4** | Normas públicas reais (sair do `intra` quando quiser) | 🔲 Pendente | 🟡 Média |
| **F5** | Validação com dados reais (teste-reteste humano, AFC) | 🔲 Pendente | 🟡 Média |
| **F6** | Decisão sobre Spranger (medir vs. manter ilustrativo) | 🔲 Pendente | 🟢 Baixa |
| **F7** | Higiene técnica (deprecações: genai, on_event, utcnow) | 🔲 Pendente | 🟢 Baixa |
| **F8** | TIRT (escolha-forçada do DISC com escores válidos) | 🔲 Opcional | ⚪ |
| **F9** | Camada de Autoconhecimento (Bloco 2: perguntas + IA) | 🔲 Visão futura | 🔵 |

---

## F1 — Persistência (Supabase Postgres) ✅ CONCLUÍDA

**Critério de pronto:** App sobe contra Postgres; tabelas criadas; dados persistem entre reinícios; seed não duplica; auth funcionando.

**O que foi feito:**
- `database.py`: engine Postgres com `pool_pre_ping`, `pool_recycle=300`, `connect_timeout=5`
- `api/index.py`: proxy ASGI com lazy import, lifespan próprio e error handling JSON
- `main.py`: `@app.exception_handler(Exception)` para capturar erros como JSON (não plain text)
- Supabase: tabelas criadas via `create_all`, seed DISC (24 blocos) carregado
- Vercel: `DATABASE_URL` setada (Transaction pooler, port 6543, sslmode=require)
- Segredos: salvos em `Drive/segredos/disc-env.txt` (REGRA_MESTRE_SYNC)

---

## F2 — Suíte 100% verde + higiene 🔜 PRÓXIMA

**Critério de pronto:** `pytest backend/app/` retorna 22/22 verdes; import órfão removido.

**O que fazer:**
1. `backend/app/conftest.py` — fixture autouse que cria tabelas antes dos testes
2. `test_bigfive_submit_to_results_e2e` — usar `with TestClient(app):` para disparar startup
3. `backend/requirements.txt` — adicionar `httpx>=0.27`
4. `backend/app/main.py:21` — remover import órfão `calculate_cronbach_alpha` (importado, não usado)

Prompt completo: `_docs-motor/PLANO_EVOLUCAO_DISC_v2.md` § 3 (PROMPT F2).

---

## F3 — Documentação viva

**Critério de pronto:** 7 arquivos criados/atualizados pelo prompt-mestre de documentação.

Prompt completo: `_docs-motor/PLANO_EVOLUCAO_DISC_v2.md` § 5 (PROMPT-MESTRE DE DOCUMENTAÇÃO).

---

## F4 — Normas públicas reais

**Critério de pronto:** `NORM_MODE=public` usa normas reais citadas e versionadas.

**Dependência:** fonte pública real (ex: dataset IPIP-NEO) — não fabricar normas.

---

## F5 — Validação com dados reais

**Critério de pronto:** exportação CSV funciona; `validacao.py` testado; protocolo documentado.

**Dependência:** N de respondentes reais suficiente.

---

## F6 — Decisão sobre Spranger

**Critério de pronto:** decisão documentada em `_docs-motor/DECISOES.md` e implementada.

Opções: (a) medir com itens próprios validados; (b) manter ilustrativo com rótulo claro na UI.

---

## F7 — Higiene técnica

**Critério de pronto:** sem avisos de depreciação críticos; suíte verde.

Itens: `google.generativeai` → `google.genai`; `@app.on_event` → lifespan handlers; `datetime.utcnow()` → timezone-aware.

---

## F8 — TIRT (opcional)

**Critério de pronto:** decisão fundamentada sobre viabilidade do modelo Thurstoniano.

---

## F9 — Camada de Autoconhecimento (visão futura)

**Pré-requisitos:** F1 concluída (✅) + extensão `pgvector` ativa no Supabase.

**Material:** pasta `2-perguntas` no Google Drive — 1.242 perguntas, 11 blocos, dois níveis:
- Narrativo (Blocos 01–10, ~1.030 perguntas) → pgvector/RAG
- Rastreio psicométrico (Bloco 11, 212 itens) → pontuação quantitativa

**Arquitetura:** perfil pontuado (DISC) + respostas biográficas → IA de aconselhamento.

**Regra:** as perguntas **nunca** entram no motor de pontuação DISC. A junção é só na camada de saída.

---

## Ordem recomendada

**F2 → F3 → F4/F5** (conforme a família for usando) **→ F6/F7/F8** (quando fizer sentido) **→ F9** (quando DISC estiver redondo e `2-perguntas` for integrada).

**Regra de ouro:** um prompt por vez, testes verdes antes de avançar, **pare antes de mexer no schema/banco**.
