# Contexto DISC — retomada (2026-06-10)

## O que está pronto

- **Núcleo científico Big Five** integrado e testado (Prompts 0–7 concluídos): 50 itens IPIP, Ômega de McDonald, intervalos de confiança, Jung contínuo derivado, qualidade de resposta, laudo anti-Barnum, NORM_MODE intra/public.
- **F1 CONCLUÍDA — Supabase Postgres + Vercel deploy:** banco de dados persistente em produção, autenticação (register/login) e questionário DISC funcionando end-to-end.
  - DATABASE_URL: pooler de transações Supabase `aws-1-sa-east-1` (salvo no Vercel + `Drive/segredos/disc-env.txt`)
  - Deploy: Vercel, branch `main`, proxy ASGI em `api/index.py`
- **Sincronização resolvida:** app (`1-disc-app`) no GitHub; conteúdo pessoal (`2-perguntas`, `3-terapia`) no Google Drive.
  - Segredos: `Drive/segredos/disc-env.txt` (REGRA_MESTRE_SYNC)

## Próximo passo

**F2 — Suíte 100% verde + higiene de imports.**

Prompt pronto em `_docs-motor/PLANO_EVOLUCAO_DISC_v2.md` § 3 (PROMPT F2).

Tarefas concretas:
1. `conftest.py` com fixture autouse que garante tabelas antes dos testes.
2. Ajustar `test_bigfive_submit_to_results_e2e` (usar `with TestClient(app)` para disparar startup).
3. Adicionar `httpx>=0.27` em `backend/requirements.txt`.
4. Verificar e remover import órfão de `calculate_cronbach_alpha` em `backend/app/main.py` linha 21 (importado mas não usado no arquivo).
5. Rodar `pytest backend/app/` e confirmar 22/22 verdes.

## Fonte única da verdade

- Roadmap: `_docs-motor/ROADMAP.md`
- Estado atual: `_docs-motor/STATUS.md`
- Decisões de arquitetura: `_docs-motor/DECISOES.md`
- Plano completo com prompts: `_docs-motor/PLANO_EVOLUCAO_DISC_v2.md`
