# Changelog

Formato: [Versão Semântica](https://semver.org/) — `[MAJOR.MINOR.PATCH] — data — título`

---

## [1.7.6] — 2026-06-18 — Polimento mobile e impressão

### Alterado
- QA manual de desktop, mobile e relatório imprimível reforçou a estabilidade da devolutiva pessoal.
- CSS de impressão ajustado para reduzir espaço da capa e evitar que cards do relatório quebrem de forma ruim entre páginas.
- Fluxo mobile em viewport aproximado de 390px conferido sem overflow horizontal.

### Mantido
- Sem alteração no motor psicométrico, fórmulas, normas, banco, autenticação, segurança ou endpoints.
- Chunk `charts`/Recharts permanece como pendência conhecida de performance leve.

---

## [1.7.5] — 2026-06-18 — Relatório pessoal em PDF

### Adicionado
- Tela de resultados ganhou a ação "Baixar relatório em PDF".
- Relatório imprimível/salvável pelo navegador com capa, data, aviso de não diagnóstico, Big Five medido, devolutiva pessoal, leituras derivadas e histórico entre aplicações.
- Comparação com a aplicação anterior incluída no relatório quando houver reteste.

### Mantido
- Sem dependência nova e sem endpoint novo.
- Motor psicométrico, normas, autenticação, segurança e histórico Big Five sem alteração de cálculo.
- DISC, Jung e Spranger continuam descritos como leituras derivadas/exploratórias.

---

## [1.7.4] — 2026-06-18 — Histórico visual entre aplicações

### Adicionado
- `/results/me` passou a retornar `history` com as aplicações Big Five salvas em ordem cronológica, preservando a linha de base interna da primeira aplicação.
- Tela de resultados ganhou os cards "Histórico de aplicações" e "Comparação com a aplicação anterior".
- Comparação visual mostra variações simples dos cinco fatores Big Five entre as duas aplicações mais recentes.

### Mantido
- Motor psicométrico, normas, pontuação, autenticação, segurança e rotas principais sem alteração de cálculo.
- DISC, Jung e Spranger continuam derivados/exploratórios, com Big Five como núcleo medido.
- Backend validado com **30 testes passando** e frontend com **build OK**. Pendência conhecida: chunk `charts`/Recharts >500 kB.

---

## [1.7.3] — 2026-06-18 — Devolutiva pessoal dos resultados

### Alterado
- Tela de resultados reorganizada para uma devolutiva pessoal com resumo, traços marcantes, forças prováveis, pontos de atenção, sugestões práticas, uso no dia a dia e limites.
- Big Five ganhou explicações simples por fator, com separação mais clara entre núcleo medido e leituras derivadas.
- Relatório narrativo por IA/fallback passou a usar linguagem mais humana, cautelosa e orientada a autoconhecimento.

### Mantido
- Motor psicométrico, pontuação, normas, autenticação, segurança e estrutura de endpoints sem alteração de cálculo.
- Aviso de não diagnóstico, não laudo e não avaliação psicológica profissional preservado.

---

## [1.7.2] — 2026-06-18 — Linguagem de app pessoal

### Alterado
- UX copy do frontend ajustada para comunicar app pessoal de autoconhecimento.
- Textos visíveis de login, cadastro, instruções, resultados e área administrativa suavizados para reduzir linguagem corporativa/RH.
- README reposicionado de "plataforma de avaliação" para aplicativo pessoal de autoconhecimento.

### Mantido
- Motor psicométrico, pontuação, normas, segurança, backend e rotas técnicas sem alteração funcional.
- Avisos de não diagnóstico, não laudo e leituras derivadas/exploratórias preservados.

---

## [1.7.1] — 2026-06-17 — Sincronização documental e preparação da Sprint 9

### Alterado
- Documentação sincronizada com o estado pós-commit `7bc0094`.
- Próxima fase registrada como **Sprint 9 — Sincronização documental, QA manual e preparação da experiência pessoal**.
- F8/TIRT, RH corporativo, seleção profissional, LGPD completa e produto comercial marcados como fora de prioridade atual.
- Contexto de retomada atualizado em `_docs-motor/contexto-disc-proximo-chat.md`.

### Resultado esperado
- Backend permanece documentado como **30/30 passed**, 0 warnings.
- Frontend permanece documentado como build OK, com pendência menor no chunk `charts`/Recharts >500 kB.

---

## [1.7.0] — 2026-06-17 — Baseline intra, normas públicas, segurança e devolutiva ética

Status: estável após o commit `7bc0094` (`fix(psychometrics): corrige normas e resultados derivados`).

### Corrigido
- `NORM_MODE=intra`: primeira aplicação agora cria linha de base interna e não exibe 50 como percentil interpretável.
- `NORM_MODE=public`: percentis calculados pela fonte `open_psychometrics_2018` em escala bruta 10-50.
- Jung borderline: maioria de eixos entre 45-55 retorna `indefinido`, sem tipo fechado.
- Layout Big Five: score bruto/média e barra separados para evitar encavalamento.
- SQLAlchemy: `DeclarativeBase` no lugar de `declarative_base()`.
- Google GenAI: import sob demanda para evitar warning em ambiente sem chave.

### Segurança
- `SECRET_KEY` segura obrigatória em produção.
- CORS restrito por `ALLOWED_ORIGINS` em produção.
- Seed demo e criação automática de schema bloqueados em produção.
- Cadastro com empresa não autoeleva usuário para RH.
- `/questionnaire/submit` valida payload de forma estrita.

### Documentação e testes
- README, `.env.template` e `backend/RELATORIO_QA.md` atualizados.
- Suíte final: **30/30 passed**, **0 warnings**.
- Build frontend: passou; pendência conhecida: chunk `charts`/Recharts >500 kB, isolado no Dashboard.

---

## [1.6.0] — 2026-06-14 — Refazer teste + invariante de preservação Big Five

### Adicionado
- Frontend: botão "Refazer teste" na aba "Meu Perfil" — `App.tsx` (estado `forceRetake` + gate de render) e `Dashboards.tsx` (prop `onRetake` + botão com `window.confirm`). Reabre o TestRoom no Big Five; sessão-only (não persiste em reload); histórico preservado no banco. (commit d9482e2)
- `test_main.py`: `test_delete_consolidado_preserva_bigfive` — prova que o DELETE consolidado não remove resultados Big Five. (commit 16c656c)
- `DECISOES.md`: ADR-11 — invariante de preservação do histórico Big Five (caminho Big Five é append-only). (commit 16c656c)

### Corrigido
- `main.py`: DELETE do ramo consolidado restrito a `bigfive_percentis IS NULL` — nunca remove histórico Big Five (base do teste-reteste F5 e do NORM_MODE=intra). (commit 16c656c)

### Resultado
- Suíte: **26/26 passed**

---

## [1.5.0] — 2026-06-13 — F6: Spranger rotulado como ilustrativo

### Alterado
- `science_engine.py`: campo `"aviso"` adicionado ao retorno de `derive_spranger_from_big_five()` com texto padronizado
- `main.py`: campo `"aviso"` repassado nas 2 ocorrências do dict `"spranger"` em `/results/me`
- `gemini_service.py`: instrução explícita de rótulo adicionada ao prompt na seção Spranger
- `DECISOES.md`: ADR-05 atualizado com decisão F6 (2026-06-13) — opção (b) escolhida

### Resultado
- Suíte: **25/25 passed** (commit df02877)

---

## [1.4.0] — 2026-06-13 — F5+F7: infraestrutura de validação + higiene técnica

### Adicionado
- `backend/app/validacao.py`: `test_retest_reliability()` (Pearson por fator) e `omega_por_fator()` (usa `mcdonald_omega` do science_engine)
- `GET /admin/export/bigfive`: CSV 13 colunas (`respondent_id`, `applied_at`, `O/C/E/A/N_raw`, `O/C/E/A/N_pct`, `quality_label`), role admin
- `_docs-motor/PROTOCOLO_VALIDACAO.md`: protocolo teste-reteste Josemar + Esdra, r≥0,80 (Kline 2000), CFA N≥200 (Hu & Bentler 1999)
- `requirements.txt`: `google-genai>=0.8`
- `test_main.py`: `test_test_retest_perfeito`, `test_omega_por_fator_coerente`, `test_bigfive_public_norm`

### Alterado
- `gemini_service.py`: `import google.generativeai as genai` → `from google import genai`; chamada API → `genai.Client` + `client.models.generate_content`
- `main.py`: `@app.on_event("startup")` → `@asynccontextmanager async def lifespan`; `datetime.utcnow()` → `datetime.now(timezone.utc)`
- `models.py`: 7× `default=datetime.utcnow` → `default=lambda: datetime.now(timezone.utc)`

### Resultado
- Suíte: **25/25 passed**, zero warnings de depreciação próprios (commit f6d98d9)

---

## [1.3.0] — 2026-06-13 — F4: NORM_MODE=public com normas reais versionadas

### Adicionado
- `config.py`: `NORM_SOURCE` (env; default `open_psychometrics_2018`)
- `main.py`: `load_norm_source()`, `_bigfive_scaled_scores()` com suporte a `NORM_MODE=public`; campo `norm_info` em `/results/me`
- `test_main.py`: `test_bigfive_public_norm` — monkeypatch, e2e, percentis 0–100

### Alterado
- `norms_ipip_neo.json`: fonte `open_psychometrics_2018` (N≈603k) com `mean` e `sd` por fator

### Resultado
- Suíte: **25/25 passed**; modo `intra` inalterado (commit f850200)

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
