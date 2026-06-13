# Sistema Psicométrico — Antigravity Psico

Plataforma de avaliação psicométrica baseada em Big Five (IPIP-50) com derivação de Jung contínuo, DISC e Spranger. Backend FastAPI + Frontend React, deployado na Vercel com banco Supabase Postgres.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | FastAPI (Python), SQLAlchemy, psycopg2-binary, python-jose, Pydantic, NumPy |
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Banco | Supabase Postgres (produção) / SQLite (dev local) |
| Deploy | Vercel — Serverless Functions via proxy ASGI em `api/index.py` |
| IA | Google Gemini 1.5 Flash (laudos narrativos) com fallback local |
| Testes | pytest, httpx, FastAPI TestClient |

---

## Como rodar localmente

### Pré-requisitos

- Python 3.10+
- Node.js 18+

### Script all-in-one (Windows)

```bat
.\run_local.bat
```

Instala dependências, abre o backend na porta 8000 e o frontend na porta padrão do Vite em janelas separadas.

### Passo a passo manual

**1. Variáveis de ambiente** — crie `.env` na raiz do projeto:

```env
DATABASE_URL=sqlite:///./psicometrico.db
SECRET_KEY=qualquer-string-longa-aleatoria
GEMINI_API_KEY=sua-chave-aqui
NORM_MODE=intra
```

**2. Backend:**

```powershell
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

**3. Frontend (outro terminal):**

```powershell
cd frontend
npm install
npm run dev
```

---

## Rodar testes

```powershell
pytest backend/app/ -v
# Resultado: 22 passed, 0 failed
```

---

## Configuração para produção (Vercel + Supabase)

### 1. Supabase

1. Crie um projeto em [supabase.com](https://supabase.com)
2. Em *Database → Extensions*, ative **`vector` (pgvector)** — obrigatório para a F9 (camada de autoconhecimento)
3. Em *Project Settings → Database*, copie a **connection string do pooler Transaction** (port 6543)

### 2. Vercel

Em *Settings → Environment Variables*, adicione:

| Variável | Valor |
|---|---|
| `DATABASE_URL` | `postgresql://postgres.<ref>:<senha>@aws-1-<região>.pooler.supabase.com:6543/postgres?sslmode=require` |
| `GEMINI_API_KEY` | sua chave Gemini |
| `SECRET_KEY` | string longa aleatória |
| `NORM_MODE` | `intra` |

O deploy é automático via push na branch `main`.

---

## Documentação

| Documento | Conteúdo |
|---|---|
| [`_docs-motor/ROADMAP.md`](_docs-motor/ROADMAP.md) | Fases F1–F9 com status e critério de pronto |
| [`_docs-motor/STATUS.md`](_docs-motor/STATUS.md) | Estado atual: deploy, testes, variáveis de ambiente |
| [`_docs-motor/DECISOES.md`](_docs-motor/DECISOES.md) | 10 ADRs: por que cada decisão de arquitetura foi tomada |
| [`_docs-motor/PLANO_EVOLUCAO_DISC_v2.md`](_docs-motor/PLANO_EVOLUCAO_DISC_v2.md) | Plano completo com prompts prontos para cada fase |
| [`backend/MANUAL_TECNICO.md`](backend/MANUAL_TECNICO.md) | Instrumento: construtos, itens, pontuação, confiabilidade, limites |
| [`backend/RELATORIO_QA.md`](backend/RELATORIO_QA.md) | Resultados de QA: teste-reteste, convergência, e2e HTTP |
| [`CHANGELOG.md`](CHANGELOG.md) | Histórico de versões (v1.0.0 → v1.2.0) |

---

## Estrutura

```
1-disc-app/
├── api/
│   └── index.py              # Proxy ASGI (Vercel entrypoint)
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI: auth, questionário, resultados, RH, admin
│   │   ├── science_engine.py # Big Five, Jung, DISC, Spranger, Ômega, IC, qualidade
│   │   ├── math_engine.py    # Percentil, distâncias, detecção de fricções
│   │   ├── gemini_service.py # Laudo narrativo + fallback local
│   │   ├── database.py       # Engine SQLAlchemy (Postgres / SQLite)
│   │   ├── models.py         # ORM models (Tenant, User, QuestionnaireItem, ...)
│   │   ├── config.py         # Settings (DATABASE_URL, SECRET_KEY, NORM_MODE, ...)
│   │   ├── seed.py           # Seed: DISC (24 blocos), Spranger (24), Jung (24)
│   │   ├── seed_big_five_ipip.py  # 50 itens IPIP + 3 atenção
│   │   ├── conftest.py       # Fixture autouse para testes
│   │   ├── test_main.py      # Testes de math_engine + e2e Big Five
│   │   └── test_science_engine.py  # Testes do science_engine
│   └── requirements.txt
├── frontend/                 # React + Vite + Tailwind
├── _docs-motor/              # Roadmap, status, decisões, plano
├── vercel.json               # Build config
├── run_local.bat             # Inicializador Windows
├── CHANGELOG.md
└── README.md
```
