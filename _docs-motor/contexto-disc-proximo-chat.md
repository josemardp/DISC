# Contexto DISC — retomada (2026-06-13)

> Resumo para retomar o trabalho em outra sessão.
> Fontes de verdade: [ROADMAP.md](ROADMAP.md) | [STATUS.md](STATUS.md) | [DECISOES.md](DECISOES.md)

---

## O que está pronto (F1 + F2 + F3 concluídas)

| Fase | O que foi feito | Evidência |
|---|---|---|
| **F1** | Supabase Postgres em produção; auth e questionário funcionando end-to-end | `database.py`, `api/index.py`, Vercel deploy |
| **F2** | Suíte 100% verde: 22/22 passed; `httpx>=0.27`; import órfão removido de `main.py` | commit 05c74fa |
| **F3** | Documentação viva: 7 arquivos criados/atualizados, coerentes entre si | este commit |

**Núcleo científico implementado:**
- Big Five IPIP-50 (50 itens + 3 atenção, `reverse_keyed`, escala 1–5)
- Ômega de McDonald, SEM, IC95%
- Jung contínuo derivado (4 eixos + `borderline` + Estabilidade Emocional)
- DISC e Spranger derivados (heurísticos, provisórios — camadas de apresentação)
- NORM_MODE=intra (régua interna honesta; modo `public` bloqueado até F4)
- Laudo anti-Barnum via Gemini 1.5 Flash + fallback local (7 seções obrigatórias)
- Qualidade de resposta (atenção, straight-lining, velocidade, RVI)

**Deploy:** Vercel, branch `main`, auto-deploy ativo. DATABASE_URL + GEMINI_API_KEY setados no Vercel e salvos em `Drive/segredos/disc-env.txt`.

---

## Próxima fase

**F4 — Normas públicas reais**

Objetivo: desbloquear `NORM_MODE=public` com normas reais, citadas e versionadas em `backend/app/norms_ipip_neo.json`.

Prompt pronto em `PLANO_EVOLUCAO_DISC_v2.md` § 4 (PROMPT F4).

---

## Pendências técnicas (não bloqueantes)

Estes warnings existem na suíte (F7 resolve):
- `google.generativeai` depreciado → migrar para `google.genai`
- `@app.on_event("startup")` depreciado → migrar para lifespan handlers
- `datetime.utcnow()` depreciado → usar `datetime.now(datetime.UTC)`
- SEM usa confiabilidade provisória `0.84` → revisar quando houver dados reais (F5)

---

## Regras que não mudam

1. Testes verdes antes de avançar: `pytest backend/app/ -v` deve retornar 22/22.
2. Não mexer no schema/banco sem pause e confirmação.
3. `2-perguntas` fica fora do repo e nunca entra no motor de pontuação (somente F9, via RAG/pgvector, na saída).
4. Segredos em `Drive/segredos/disc-env.txt` — nunca no código.
5. Um prompt por vez.
