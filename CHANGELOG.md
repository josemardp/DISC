# Changelog

Formato: [Versão Semântica](https://semver.org/) — `[MAJOR.MINOR.PATCH] — data — título`

---

## [1.2.0] — 2026-06-13 — F2: Suíte 100% verde + higiene de imports

### Adicionado
- `backend/app/conftest.py`: fixture `session`-scoped `autouse` que cria tabelas (`Base.metadata.create_all`) e roda `seed_db` antes de qualquer teste — torna os testes independentes do ciclo de startup da aplicação
- `backend/requirements.txt`: `httpx>=0.27` (dependência do `TestClient` do FastAPI)

### Alterado
- `backend/app/test_main.py`: `test_bigfive_submit_to_results_e2e` passou de `client = TestClient(app)` para `with TestClient(app) as client:` — startup event dispara, tabelas existem na hora certa

### Removido
- `backend/app/main.py`: import órfão `calculate_cronbach_alpha` removido da linha 20 (função permanece em `math_engine.py`, usada em `test_main.py`)

### Resultado
- Suíte: **22/22 passed**, 0 failed, 5.29s (commit 05c74fa)

---

## [1.1.0] — 2026-06-10 — F1: Supabase Postgres + Vercel deploy estável

### Adicionado
- `api/index.py`: proxy ASGI para Vercel com lazy import, lifespan próprio, `_init_db()` na primeira request e error response JSON
- `main.py`: `@app.exception_handler(Exception)` — captura todos os erros como JSON (evita plain text "Internal Server Error")
- `backend/requirements.txt`: `psycopg2-binary>=2.9`

### Alterado
- `database.py`: engine Postgres com `pool_pre_ping=True`, `pool_recycle=300`, `connect_args={"connect_timeout": 5}`; normalização `postgres://` → `postgresql+psycopg2://`; fallback SQLite `/tmp` só ativo quando `DATABASE_URL` já é sqlite

### Removido
- Endpoints de debug temporários: `/api/db-info`, `/api/ping`, `/api/simple`

### Infraestrutura
- Supabase Postgres provisionado (Transaction pooler, `aws-1-sa-east-1`, port 6543, `sslmode=require`)
- `DATABASE_URL` e `GEMINI_API_KEY` setados no Vercel e salvos em `Drive/segredos/disc-env.txt`
- Tabelas criadas via `create_all`; seed DISC (24 blocos), Spranger (24 itens), Jung (24 itens) e Big Five (50 itens IPIP + 3 atenção) carregados

---

## [1.0.0] — 2026-06-05 — Núcleo científico Big Five integrado

### Adicionado
- `seed_big_five_ipip.py`: 50 itens IPIP Big-Five Factor Markers (Goldberg, 1992), PT-BR, domínio público
- 3 itens de atenção (`attention_check`, `weight=0.0`) integrados ao fluxo Big Five
- `science_engine.py` — funções puras, sem dependência de banco:
  - `score_big_five()`: pontuação com reversão de itens e cálculo de Estabilidade Emocional
  - `percentil_intraindividual()`: régua interna honesta (NORM_MODE=intra)
  - `derive_jung_from_big_five()`: Jung contínuo com detecção de eixos `borderline`
  - `derive_disc_from_big_five()`: DISC derivado (heurístico, provisório)
  - `derive_spranger_from_big_five()`: Spranger derivado (heurístico, provisório)
  - `mcdonald_omega()`: Ômega total via PCA unifatorial aproximado
  - `standard_error_of_measurement()`: SEM = sd × √(1 − confiabilidade)
  - `confidence_interval()`: IC95% com limites opcionais
  - `response_quality_index()`: atenção, straight-lining, velocidade, RVI
- `math_engine.py`: `raw_to_percentile`, `calculate_euclidean_distance`, `calculate_cosine_similarity`, `detect_frictions`, `calculate_cronbach_alpha`
- `gemini_service.py`: laudo narrativo anti-Barnum via Gemini 1.5 Flash; 7 seções obrigatórias; regras anti-Barnum no prompt; fallback local completo quando `GEMINI_API_KEY` ausente
- `NORM_MODE=intra` como régua interna honesta; modo `public` bloqueado no código
- `backend/MANUAL_TECNICO.md`: instrumento, construtos, reverse_keyed, pontuação, Ômega, IC, qualidade, limites
- `backend/RELATORIO_QA.md`: teste-reteste simulado (r=0.993), convergência interna, e2e HTTP 200, 21/22 testes

### Esquema de banco
- `QuestionnaireItem`: campo `reverse_keyed` (Boolean)
- `PsychometricResult`: campos `bigfive_O/C/E/A/N`, `bigfive_percentis` (JSON), `jung_continuo` (JSON), `quality_label`

### Frontend
- React + TypeScript + Vite + Tailwind CSS
- Dashboards: Big Five (5 fatores com IC), Jung contínuo (eixos), DISC derivado, qualidade de resposta
