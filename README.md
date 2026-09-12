# Antigravity Psico — Autoconhecimento

Aplicativo pessoal de autoconhecimento baseado em Big Five (IPIP-50), com leituras derivadas/exploratórias de Jung contínuo, DISC e Spranger. Backend FastAPI + Frontend React, deployado na Vercel com banco Supabase Postgres.

## O que este repositório demonstra

- **Psicometria implementada de verdade, não simulada.** O núcleo é o Big Five com
  o banco de itens IPIP, normas aplicadas a partir de `norms_ipip_neo.json`, e as
  leituras DISC, Jung e Spranger são derivadas dele e rotuladas como exploratórias.
  A separação entre o que é psicometricamente sustentado e o que é leitura
  interpretativa está explícita no código e na interface.
- **LLM com rédea curta.** O Gemini gera o relatório narrativo a partir de escores já
  calculados, nunca os calcula. Há fallback local para quando a API falha, então o
  produto não deixa de funcionar por indisponibilidade de terceiro.
- **Anti-Barnum como requisito de produto.** O gerador de texto é avaliado contra
  descrições genéricas que serviriam para qualquer pessoa, que é a falha clássica de
  instrumento de perfil.
- **Testes onde o risco mora:** a bateria cobre o motor de cálculo, não só as rotas.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | FastAPI (Python), SQLAlchemy, psycopg2-binary, python-jose, Pydantic, NumPy |
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Banco | Supabase Postgres (produção) / SQLite (dev local) |
| Deploy | Vercel — Serverless Functions via proxy ASGI em `api/index.py` |
| IA | Google Gemini 1.5 Flash (relatórios narrativos) com fallback local |
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
# Resultado atual: 35 passed, 0 failed, 0 warnings
```

Build frontend:

```powershell
cd frontend
npm run build
# Resultado atual: build OK; chunk grande restante isolado em Recharts/Dashboard.
```

> **Estado atual:** backend com 35 testes passando, frontend com build OK. **Sprint 17 em curso** — fase de uso pessoal real e observação T1/T2, sem mudanças no motor nem no produto funcional.
> Pendência conhecida: chunk `charts`/Recharts >500 kB, isolado no Dashboard.
> Log das sprints 11 a 16: [`docs/HISTORICO.md`](docs/HISTORICO.md)

---

## Limites éticos e psicométricos

Este sistema é uma ferramenta de autoconhecimento e devolutiva comportamental exploratória. Ele não constitui diagnóstico psicológico, laudo psicológico, avaliação psicológica profissional, teste psicológico validado pelo CFP/SATEPSI, avaliação clínica ou instrumento definitivo de personalidade.

- Big Five/IPIP-50 é o núcleo medido diretamente.
- Jung contínuo, DISC e Spranger são leituras derivadas e heurísticas a partir do Big Five.
- A primeira aplicação em `NORM_MODE=intra` cria uma linha de base interna; não exibe percentis interpretáveis.
- `NORM_MODE=public` usa a fonte pública exploratória `open_psychometrics_2018` em `backend/app/norms_ipip_neo.json`, na escala bruta 10-50 por fator. Essa norma não é representativa da população brasileira.

Diferenças importantes:

- Escore bruto: soma dos 10 itens do fator, de 10 a 50.
- Média por item: escore bruto dividido por 10, de 1 a 5.
- Percentil intraindividual: comparação contra histórico do próprio respondente, não populacional.
- Percentil público exploratório: cálculo contra norma pública versionada, com limitações de amostra.

## Devolutiva pessoal

A tela de resultados prioriza linguagem de autoconhecimento:

- resumo geral do perfil;
- traços mais marcantes;
- pontos fortes prováveis;
- pontos de atenção;
- sugestões práticas;
- como usar o resultado no dia a dia;
- limites da avaliação.

O Big Five permanece como núcleo medido. Jung, DISC e Spranger aparecem apenas como leituras derivadas/exploratórias. A primeira aplicação em `NORM_MODE=intra` cria uma linha de base interna; a comparação intraindividual fica mais útil a partir do reteste.

O histórico visual entre aplicações mostra:

- aplicações Big Five salvas em ordem cronológica;
- data de cada aplicação;
- linha de base interna na primeira aplicação;
- comparação simples com a aplicação anterior usando resultados brutos;
- aviso de que pequenas mudanças podem refletir contexto, cansaço, humor ou forma de responder.

A tela também permite baixar/salvar um relatório pessoal em PDF pelo navegador. O relatório inclui capa, data, aviso de não diagnóstico/laudo, Big Five medido, pontos fortes prováveis, pontos de atenção, sugestões práticas, leituras derivadas, reflexões pessoais e histórico/comparação quando houver reteste.

As respostas reflexivas são opcionais, têm até 1000 caracteres por campo e ficam em `personal_reflections`, vinculadas ao resultado da aplicação. A pessoa pode editar as reflexões da aplicação atual no card "Minhas reflexões"; o Dashboard e o conteúdo imprimível/PDF são atualizados após o salvamento. Elas não entram no `science_engine` e não alteram Big Five, DISC, Jung, Spranger, normas, percentis ou histórico.

## Sprint 17 — uso pessoal e observação T1/T2

Checklist para cada participante real:

- [ ] Fazer a primeira aplicação (T1) e registrar a data.
- [ ] Responder às reflexões pessoais com contexto suficiente para uma releitura futura.
- [ ] Salvar o relatório/PDF de T1 em local privado.
- [ ] Aguardar de 2 a 4 semanas, sem tentar reproduzir respostas anteriores.
- [ ] Fazer a segunda aplicação (T2) pelo fluxo de reteste.
- [ ] Salvar o relatório/PDF de T2 e comparar o histórico com T1.
- [ ] Avaliar quais partes da devolutiva fazem sentido, quais não fazem e quais ficaram pouco claras.
- [ ] Registrar separadamente os ajustes de texto, experiência ou interpretação desejados, sem alterar respostas ou resultados já salvos.

Esta etapa é uma observação pessoal de uso e estabilidade ao longo do tempo. Não constitui validação científica formal, estudo normativo, validação para uso profissional, aprovação do CFP ou avaliação pelo SATEPSI.

## Produção e cuidados mínimos

Em produção:

- `SECRET_KEY` deve vir de variável de ambiente, ser longa e segura.
- `ALLOWED_ORIGINS` é obrigatório; CORS wildcard só é permitido fora de produção.
- `ENABLE_DEMO_SEED` não deve ficar ativo.
- `AUTO_CREATE_SCHEMA` não deve substituir migrações em produção.
- Campo opcional de perfil não muda permissões automaticamente; área administrativa exige aprovação/flag futura.

Cuidados mínimos mantidos nesta sprint:

- Aviso claro de que o resultado não é diagnóstico, laudo ou avaliação psicológica profissional.
- Não expor dados sensíveis em logs.
- Não vazar traceback ou erros internos para o usuário em produção.
- Não versionar segredos, chaves ou `.env` real.
- Manter `SECRET_KEY` segura em produção.
- Manter CORS restrito em produção.
- Não criar seed demo ou usuário de teste em produção.

LGPD completa fica como pendência futura caso o aplicativo pessoal evolua para produto comercial, corporativo ou de RH.

---

## Configuração para produção (Vercel + Supabase)

### 1. Supabase

1. Crie um projeto em [supabase.com](https://supabase.com)
2. Em *Database → Extensions*, ative **`vector` (pgvector)** somente se uma evolução futura realmente usar embeddings; a F9 atual não depende dessa extensão
3. Em *Project Settings → Database*, copie a **connection string do pooler Transaction** (port 6543)
4. Antes de publicar a API com reflexões, siga [o guia de migração](backend/schema/README.md) e execute `backend/schema/2026-06-19_personal_reflections.sql` no SQL Editor do Supabase

Não execute a migração em um banco com dados relevantes sem backup atualizado. A tabela não habilita RLS: o projeto usa autenticação e autorização próprias no backend, sem Supabase Auth ou acesso direto do frontend ao banco. O SQL revoga privilégios de `anon` e `authenticated`; se essa arquitetura mudar, RLS passa a ser requisito antes de expor a tabela ao cliente.

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
| [`CHANGELOG.md`](CHANGELOG.md) | Histórico de versões (v1.0.0 → v1.7.x) |

---

## Estrutura

```
1-disc-app/
├── api/
│   └── index.py              # Proxy ASGI (Vercel entrypoint)
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI: auth, questionário, resultados e área administrativa
│   │   ├── science_engine.py # Big Five, Jung, DISC, Spranger, Ômega, IC, qualidade
│   │   ├── math_engine.py    # Percentil, distâncias, detecção de fricções
│   │   ├── gemini_service.py # Relatório narrativo + fallback local
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
