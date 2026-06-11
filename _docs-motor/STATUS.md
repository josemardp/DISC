# STATUS — Fotografia do estado atual (2026-06-10)

## Deploy em produção

| Item | Estado | Detalhe |
|---|---|---|
| Plataforma | ✅ Vercel (Serverless) | branch `main`, auto-deploy ativo |
| Banco de dados | ✅ Supabase Postgres | Transaction pooler, `aws-1-sa-east-1`, port 6543 |
| Autenticação | ✅ Funcionando | `/auth/register` e `/auth/token` retornam JWT |
| Questionário | ✅ Funcionando | `/questionnaire/items?test_type=DISC` retorna 24 blocos |
| GEMINI_API_KEY | ✅ Setada no Vercel | duas chaves salvas em `Drive/segredos/disc-env.txt` |
| DATABASE_URL | ✅ Setada no Vercel | salva em `Drive/segredos/disc-env.txt` |

## Suíte de testes

| Item | Estado | Detalhe |
|---|---|---|
| Total de testes | ⚠️ 21/22 passando | 1 falha de harness (não de lógica) |
| Teste falho | `test_bigfive_submit_to_results_e2e` | `TestClient` sem context manager não dispara startup → `no such table: users` |
| Import órfão | ⚠️ `calculate_cronbach_alpha` | importado em `main.py:21`, não usado — remover na F2 |

## Como rodar localmente

```powershell
# 1. Instalar dependências
cd backend
pip install -r requirements.txt

# 2. Criar .env na raiz do backend com:
#    DATABASE_URL=<string do pooler Supabase OU sqlite:///./psicometrico.db para dev>
#    GEMINI_API_KEY=<chave>
#    SECRET_KEY=<qualquer string longa>

# 3. Rodar backend
uvicorn backend.app.main:app --reload

# 4. Rodar frontend (outro terminal)
cd frontend
npm install && npm run dev

# Ou usar o script all-in-one (Windows):
.\run_local.bat
```

## Como rodar os testes

```powershell
cd 1-disc-app
pytest backend/app/ -v
# Esperado: 21/22 — 1 falha em test_bigfive_submit_to_results_e2e (F2 resolve)
```

## Variáveis de ambiente necessárias

| Variável | Onde setar | Descrição |
|---|---|---|
| `DATABASE_URL` | Vercel + `.env` local | Connection string Supabase (pooler Transaction, sslmode=require) |
| `GEMINI_API_KEY` | Vercel + `.env` local | Chave Gemini para geração de laudos |
| `SECRET_KEY` | Vercel + `.env` local | Chave JWT (qualquer string longa aleatória) |
| `NORM_MODE` | `.env` | `intra` (padrão) ou `public` (bloqueado até ter normas versionadas) |

## Estrutura de arquivos chave

```
1-disc-app/
├── api/index.py              # Proxy ASGI para Vercel (lazy import + lifespan)
├── backend/app/
│   ├── main.py               # FastAPI app — rotas, auth, motor de resultados
│   ├── database.py           # Engine SQLAlchemy (Postgres ou SQLite)
│   ├── science_engine.py     # Big Five, Jung, DISC, Spranger, Ômega, IC, qualidade
│   ├── math_engine.py        # Utilitários matemáticos (percentil, distâncias)
│   ├── gemini_service.py     # Laudo narrativo via Gemini + fallback local
│   ├── seed.py               # Seed DISC (24 blocos) + seed_big_five_ipip.py (50 itens IPIP)
│   ├── models.py             # SQLAlchemy models
│   └── config.py             # Pydantic settings (DATABASE_URL, SECRET_KEY, GEMINI_API_KEY)
├── _docs-motor/              # Documentação do projeto
└── vercel.json               # Build config: frontend + rewrite /api/* → api/index.py
```
