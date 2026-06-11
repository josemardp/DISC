# Changelog

## [1.1.0] — 2026-06-10 — F1: Supabase Postgres + Vercel deploy estável

### Adicionado
- `api/index.py`: proxy ASGI para Vercel com lazy import, lifespan próprio, init_db não-fatal e error response JSON
- `main.py`: `@app.exception_handler(Exception)` para capturar todos os erros como JSON (evita "Internal Server Error" em plain text)
- `backend/requirements.txt`: `psycopg2-binary>=2.9`

### Alterado
- `database.py`: engine Postgres com `pool_pre_ping=True`, `pool_recycle=300`, `connect_args={"connect_timeout": 5}`; normalização `postgres://` → `postgresql+psycopg2://`; fallback SQLite `/tmp` só ativo quando DATABASE_URL já é sqlite

### Removido
- Endpoints de debug temporários: `/api/db-info`, `/api/ping`, `/api/simple`

### Infraestrutura
- Supabase Postgres provisionado (Transaction pooler, `aws-1-sa-east-1`, port 6543)
- `DATABASE_URL` e `GEMINI_API_KEY` setados no Vercel e salvos em `Drive/segredos/disc-env.txt`
- Tabelas criadas via `create_all`; seed DISC (24 blocos) e Big Five (50 itens IPIP) carregados

---

## [1.0.0] — 2026-06-05 — Núcleo científico Big Five integrado

### Adicionado
- 50 itens IPIP Big-Five Factor Markers (Goldberg, 1992), PT-BR, em `seed_big_five_ipip.py`
- 3 itens de atenção (`attention_check`) integrados ao fluxo Big Five
- `science_engine.py`: `score_big_five`, `percentil_intraindividual`, `derive_jung_from_big_five`, `derive_disc_from_big_five`, `derive_spranger_from_big_five`, `mcdonald_omega`, `standard_error_of_measurement`, `confidence_interval`, `response_quality_index`
- Jung contínuo derivado do Big Five com detecção de eixos `borderline`
- DISC e Spranger como camadas derivadas do Big Five
- NORM_MODE=intra como régua interna honesta (modo `public` bloqueado)
- Laudo narrativo anti-Barnum via Gemini com fallback local
- Suíte de testes: 21/22 passando (1 falha de harness — F2 resolve)
- `backend/MANUAL_TECNICO.md` e `backend/RELATORIO_QA.md`
- Frontend React: dashboards Big Five, Jung contínuo, DISC derivado, qualidade de resposta
