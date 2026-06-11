# Sistema Psicométrico DISC — Plataforma Corporativa

Plataforma de avaliação psicométrica baseada em Big Five (IPIP-50) com derivação de DISC, Jung contínuo e Spranger. Backend FastAPI + Frontend React, deployado na Vercel com banco Supabase Postgres.

---

## Stack

- **Backend:** FastAPI (Python), SQLAlchemy, psycopg2-binary, python-jose, Pydantic
- **Frontend:** React, TypeScript, Vite, Tailwind CSS
- **Banco:** Supabase Postgres (produção) / SQLite (dev local)
- **Deploy:** Vercel (Serverless Functions via proxy ASGI em `api/index.py`)
- **IA:** Google Gemini (laudos narrativos) com fallback local

---

## Como rodar localmente

### Pré-requisitos

- Python 3.10+
- Node.js 18+

### Backend

```powershell
cd backend
pip install -r requirements.txt
```

Crie `.env` na raiz do `backend/` (copie `.env.template`):

```env
DATABASE_URL=sqlite:///./psicometrico.db   # dev local
SECRET_KEY=qualquer-string-longa-aleatoria
GEMINI_API_KEY=sua-chave-aqui
NORM_MODE=intra
```

```powershell
uvicorn backend.app.main:app --reload
# API disponível em http://localhost:8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
# UI disponível em http://localhost:5173
```

### Script all-in-one (Windows)

```powershell
.\run_local.bat
```

---

## Configuração para produção (Vercel + Supabase)

### 1. Supabase

1. Crie um projeto em [supabase.com](https://supabase.com)
2. Em *Database → Extensions*, ative **`vector` (pgvector)** (necessário para F9)
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

## Rodar testes

```powershell
pytest backend/app/ -v
# Esperado: 21/22 verdes (F2 resolve o último)
```

---

## Documentação

| Documento | Conteúdo |
|---|---|
| `_docs-motor/ROADMAP.md` | Fases F1–F9 com status e critério de pronto |
| `_docs-motor/STATUS.md` | Estado atual: deploy, testes, variáveis de ambiente |
| `_docs-motor/DECISOES.md` | ADRs: por que cada decisão de arquitetura foi tomada |
| `_docs-motor/PLANO_EVOLUCAO_DISC_v2.md` | Plano completo com prompts prontos para cada fase |
| `backend/MANUAL_TECNICO.md` | Instrumento: construtos, itens, pontuação, confiabilidade |
| `backend/RELATORIO_QA.md` | Resultados da suíte de testes e QA |
| `CHANGELOG.md` | Histórico de versões |

---

## Estrutura

```
1-disc-app/
├── api/
│   └── index.py              # Proxy ASGI (Vercel entrypoint)
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI: rotas de auth, questionário, resultados, RH
│   │   ├── science_engine.py # Big Five, Jung, DISC, Spranger, Ômega, IC, qualidade
│   │   ├── math_engine.py    # Percentil, distâncias, detecção de fricções
│   │   ├── gemini_service.py # Laudo narrativo + fallback local
│   │   ├── database.py       # Engine SQLAlchemy (Postgres / SQLite)
│   │   ├── models.py         # ORM models
│   │   ├── config.py         # Pydantic settings
│   │   ├── seed.py           # Seed DISC (24 blocos)
│   │   └── seed_big_five_ipip.py  # 50 itens IPIP + atenção
│   └── requirements.txt
├── frontend/                 # React + Vite + Tailwind
├── _docs-motor/              # Documentação técnica e roadmap
├── vercel.json               # Build config
├── CHANGELOG.md
└── README.md
```
