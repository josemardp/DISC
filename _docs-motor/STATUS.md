# STATUS — Fotografia do estado atual

> Última atualização: 2026-06-19 (Sprint 14: perguntas reflexivas F9; 32/32 verdes).
> Para o roadmap e próximas fases, ver [ROADMAP.md](ROADMAP.md).

---

## Deploy em produção

| Item | Estado | Detalhe |
|---|---|---|
| Plataforma | ✅ Vercel (Serverless) | branch `main`, auto-deploy ativo |
| Banco de dados | ✅ Supabase Postgres | Transaction pooler, `aws-1-sa-east-1`, port 6543 |
| Autenticação | ✅ Funcionando | `/auth/register` e `/auth/token` retornam JWT |
| Questionário Big Five | ✅ Funcionando | `/questionnaire/items?test_type=BIGFIVE` retorna 53 itens (50 IPIP + 3 atenção) |
| GEMINI_API_KEY | ✅ Setada no Vercel | salva em `Drive/segredos/disc-env.txt` |
| DATABASE_URL | ✅ Setada no Vercel | salva em `Drive/segredos/disc-env.txt` |

---

## Suíte de testes

| Item | Estado | Detalhe |
|---|---|---|
| Total de testes | ✅ **32/32 passando** | baseline intra, public norm, API hardening, reflexões F9 e segurança |
| Tempo de execução | ✅ ~2.7s | `pytest backend/app/ -v` |
| test_bigfive_submit_to_results_e2e | ✅ Passando | usa `with TestClient(app) as client:` |
| test_delete_consolidado_preserva_bigfive | ✅ Passando | prova a invariante de preservação Big Five (DELETE IS NULL não remove histórico) |
| conftest.py | ✅ Fixture autouse | cria tabelas + seed antes de qualquer teste |
| Warnings | ✅ Zero | Pytest final sem warnings |

---

## O que está implementado e funcionando

| Funcionalidade | Arquivo | Observação |
|---|---|---|
| Auth JWT (register/login/token) | `main.py` | Multi-tenant; roles: admin, hr, respondent |
| Big Five IPIP-50 + atenção | `seed_big_five_ipip.py` | 50 itens + 3 atenção; Likert 1-5; `reverse_keyed` |
| Pontuação Big Five | `science_engine.py` | `score_big_five()`: soma com reversão, ignora atenção |
| Estabilidade Emocional | `science_engine.py` | `ES = 6.0 - mean_N` (inverso de Neuroticismo) |
| Percentil régua interna | `science_engine.py` | `percentil_intraindividual()` — NORM_MODE=intra |
| Jung contínuo derivado | `science_engine.py` | `derive_jung_from_big_five()` — 4 eixos + borderline |
| DISC derivado (provisório) | `science_engine.py` | `derive_disc_from_big_five()` — heurístico |
| Spranger derivado (ilustrativo) | `science_engine.py` | `derive_spranger_from_big_five()` — heurístico; campo `"aviso"` na resposta da API (F6) |
| NORM_MODE=public com normas reais | `main.py`, `norms_ipip_neo.json` | fonte `open_psychometrics_2018` (N≈603k); `NORM_SOURCE` configurável por env (F4) |
| Exportação CSV Big Five | `main.py` | `GET /admin/export/bigfive` — 13 colunas, role admin (F5) |
| Infraestrutura de validação | `validacao.py` | `test_retest_reliability()` e `omega_por_fator()` — usa `mcdonald_omega` do science_engine (F5) |
| Refazer teste (nova rodada) | `App.tsx`, `Dashboards.tsx` | botão na aba "Meu Perfil"; sessão-only; reabre TestRoom no Big Five; histórico preservado no DB |
| Histórico visual entre aplicações | `main.py`, `Dashboards.tsx` | `/results/me` retorna `history`; UI lista aplicações e compara a mais recente com a anterior |
| Relatório pessoal em PDF | `Dashboards.tsx`, `index.css` | versão imprimível/salvável pelo navegador; usa dados já carregados no Dashboard |
| Polimento mobile/print | `index.css` | QA desktop/mobile; ajuste de impressão para reduzir espaço da capa e evitar cortes ruins de cards |
| Perguntas reflexivas F9 | `TestRoom.tsx`, `models.py`, `main.py`, `Dashboards.tsx` | duas respostas opcionais por aplicação; fora do motor; Dashboard e PDF |
| Invariante de preservação Big Five | `main.py` | DELETE consolidado restrito a `bigfive_percentis IS NULL`; ADR-11; teste dedicado |
| Ômega de McDonald | `science_engine.py` | `mcdonald_omega()` — via PCA unifatorial aproximado |
| SEM e IC95% | `science_engine.py` | `standard_error_of_measurement()` + `confidence_interval()` |
| Qualidade de resposta | `science_engine.py` | `response_quality_index()` — atenção, straight-lining, velocidade |
| Detecção de fricções | `math_engine.py` | `detect_frictions()` — 3 fricções implementadas |
| Relatório narrativo anti-Barnum | `gemini_service.py` | Gemini 1.5 Flash + fallback local; 7 seções; limites obrigatórios |
| Motor de resultados | `main.py` | `/results/me` retorna bigfive + jung_continuo + disc + spranger + qualidade |
| Devolutiva pessoal | `Dashboards.tsx`, `gemini_service.py` | resumo, traços marcantes, forças prováveis, pontos de atenção, sugestões práticas, uso no dia a dia e limites |
| Admin stats | `main.py` | `/admin/stats` — omega_bigfive por fator |
| Proxy ASGI Vercel | `api/index.py` | lazy import + lifespan próprio + error JSON |

---

## Escopo atual

Este projeto está no estágio de **aplicativo pessoal de autoconhecimento**.

Não é, nesta fase:

- produto comercial;
- sistema RH/corporativo em produção;
- teste psicológico validado pelo CFP/SATEPSI;
- diagnóstico;
- laudo psicológico;
- avaliação psicológica profissional;
- ferramenta de seleção profissional.

LGPD completa não é requisito obrigatório nesta fase. Mantêm-se apenas cuidados mínimos: aviso de não diagnóstico, não versionar segredos, não vazar traceback em produção, `SECRET_KEY` segura, CORS restrito em produção, sem seed demo em produção e logs sem dados sensíveis.

---

## Como rodar localmente

### Pré-requisitos

- Python 3.10+
- Node.js 18+

### Script all-in-one (Windows)

```bat
.\run_local.bat
```

O script: instala dependências do backend (`pip install -r backend/requirements.txt`), instala dependências do frontend (`npm install`), e abre duas janelas CMD separadas — backend na porta 8000, frontend na porta padrão do Vite.

### Passo a passo manual

```powershell
# 1. Variáveis de ambiente — crie .env na raiz do projeto:
#    DATABASE_URL=sqlite:///./psicometrico.db   (dev local)
#    SECRET_KEY=qualquer-string-longa-aleatoria
#    GEMINI_API_KEY=sua-chave-aqui              (opcional — usa fallback se ausente)
#    NORM_MODE=intra

# 2. Backend
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
# API disponível em http://localhost:8000
# Docs interativos em http://localhost:8000/docs

# 3. Frontend (outro terminal)
cd frontend
npm install
npm run dev
# UI disponível na porta padrão do Vite (ver frontend/vite.config.ts)
```

---

## Como rodar os testes

```powershell
# Na raiz do projeto 1-disc-app:
pytest backend/app/ -v
# Resultado esperado: 32 passed, 0 failed, 0 warnings
```

**Nota:** a fixture autouse em `backend/app/conftest.py` garante criação de tabelas e seed antes de qualquer teste. O banco de teste usa SQLite local (`psicometrico.db` ou o DATABASE_URL do `.env`).

---

## Variáveis de ambiente

| Variável | Valor local | Valor produção | Descrição |
|---|---|---|---|
| `DATABASE_URL` | `sqlite:///./psicometrico.db` | pooler Transaction Supabase, port 6543, sslmode=require | Motor do banco |
| `GEMINI_API_KEY` | opcional (usa fallback) | obrigatória | Geração de laudos |
| `SECRET_KEY` | qualquer string | string aleatória longa | Assina tokens JWT |
| `NORM_MODE` | `intra` | `intra` | Modo de normatização; `public` disponível desde F4 |
| `NORM_SOURCE` | `open_psychometrics_2018` | `open_psychometrics_2018` | Fonte de normas para `NORM_MODE=public` |

---

## Estrutura de arquivos chave

```
1-disc-app/
├── api/
│   └── index.py              # Proxy ASGI para Vercel (lazy import + lifespan + error JSON)
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI: auth, questionário, resultados e área administrativa
│   │   ├── science_engine.py # Big Five, Jung, DISC, Spranger, Ômega, IC, qualidade
│   │   ├── math_engine.py    # Percentil, distâncias, detecção de fricções, Alpha (legacy)
│   │   ├── gemini_service.py # Relatório narrativo via Gemini 1.5 Flash + fallback local
│   │   ├── database.py       # Engine SQLAlchemy (Postgres ou SQLite)
│   │   ├── models.py         # ORM: Tenant, User, QuestionnaireItem, Response, PsychometricResult, Report, Job
│   │   ├── config.py         # Settings: DATABASE_URL, SECRET_KEY, GEMINI_API_KEY, NORM_MODE
│   │   ├── seed.py           # Seed: Tenant demo, usuários demo, DISC (24 blocos), Spranger (24), Jung (24)
│   │   ├── seed_big_five_ipip.py  # 50 itens IPIP Big-Five + 3 itens de atenção
│   │   ├── conftest.py       # Fixture autouse: cria tabelas + seed antes dos testes
│   │   ├── test_main.py      # 6 testes de math_engine + e2e Big Five completo
│   │   └── test_science_engine.py  # 16 testes do science_engine
│   └── requirements.txt      # FastAPI, SQLAlchemy, psycopg2, httpx, jose, numpy, etc.
├── frontend/                 # React + TypeScript + Vite + Tailwind CSS
├── _docs-motor/              # Documentação técnica e roadmap
├── vercel.json               # Build config: frontend + rewrite /api/* → api/index.py
├── run_local.bat             # Inicializador Windows (backend + frontend em janelas separadas)
├── CHANGELOG.md              # Histórico de versões semânticas
└── README.md                 # Porta de entrada do projeto
```

---

## Próxima fase

**Próxima evolução recomendada — edição posterior das reflexões.**

Ordem recomendada:

1. Permitir editar as reflexões da aplicação atual sem refazer o teste.
2. Manter versionamento por aplicação e sem qualquer efeito sobre pontuação.
3. Prosseguir com validação empírica pessoal T1/T2 quando houver dados reais suficientes.

**Não priorizar agora:** TIRT/F8, RH corporativo, dashboard de equipe, ranking de pessoas, seleção profissional, LGPD completa, produto comercial, alteração profunda do motor, promessa CFP/SATEPSI, laudo psicológico ou diagnóstico.

**Pendência F5 empírica:** infraestrutura pronta; teste-reteste real (Josemar + Esdra, intervalo 2–4 semanas) ainda não executado. A rodada 2 agora é feita pelo botão "Refazer teste" na aba "Meu Perfil". Quando tiver os dois snapshots, rodar `test_retest_reliability()` conforme `PROTOCOLO_VALIDACAO.md`.
