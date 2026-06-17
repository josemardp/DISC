# 🧭 Plano de Evolução DISC — v2 (atualizado pós-integração)
### Fonte única da verdade. Substitui o guia anterior. Siga de cima para baixo.

> Atualização 2026-06-17: após o commit `7bc0094`, o estado técnico está estável para uso pessoal (backend 30/30, frontend build OK). A próxima fase oficial não é F8/TIRT; é a **Sprint 9 — sincronização documental, QA manual e preparação da experiência pessoal**. Ver `ROADMAP.md` e `contexto-disc-proximo-chat.md`.

> **Onde chegamos:** o núcleo científico Big Five está integrado e funcionando. Jung é medido de forma contínua e derivado do Big Five (com Estabilidade Emocional). Os Prompts 0–7 do roteiro original estão concluídos. Este v2 registra o estado real e delineia o caminho futuro.

---

## 1. STATUS ATUAL (verificado no código)

| Etapa | Status | Evidência |
|---|---|---|
| Branch `evolucao-cientifica` | ✅ | em uso |
| Schema novo (`reverse_keyed`, `bigfive_*`, `jung_continuo`, `quality_label`) | ✅ | models.py |
| Seed dos 50 itens IPIP + atenção | ✅ | seed.py importa `construir_itens_bigfive` |
| Motor fiado no backend (Big Five, Jung, Ômega, IC, qualidade, modo `intra`) | ✅ | main.py |
| Frontend exibindo 5 fatores + faixa de IC + Jung contínuo + qualidade | ✅ | Dashboards.tsx |
| Laudo anti-Barnum + "sem dados suficientes" | ✅ | gemini_service.py |
| Manual técnico | ✅ | backend/MANUAL_TECNICO.md |
| QA (teste-reteste r=0,993; convergente OK; e2e HTTP 200) | ✅ | backend/RELATORIO_QA.md |
| Suíte de testes | ⚠️ | 21/22 — 1 falha de harness (não de lógica) |
| Deploy Vercel + Supabase Postgres | ✅ | F1 concluída — banco persiste, auth e questionário funcionando |

**Conclusão:** o produto funciona de ponta a ponta. Faltam dois ajustes para uso real e a maturação científica que depende de dados.

---

## 2. ROADMAP FUTURO (fases e prioridade)

| Fase | Tema | Prioridade | Tipo |
|---|---|---|---|
| **F1** | Persistência do banco (Supabase Postgres) | ✅ CONCLUÍDA | — |
| **F2** | Suíte 100% verde + higiene de imports | 🔜 PRÓXIMA | Prompt pronto |
| **F3** | Documentação viva (auto-documentar a evolução) | 🟠 Alta | Prompt-mestre |
| **F4** | Normas públicas reais (sair do `intra` quando quiser) | 🟡 Média | Delineado |
| **F5** | Validação com dados reais (teste-reteste humano, AFC) | 🟡 Média | Depende de dados |
| **F6** | Decisão sobre Spranger | 🟢 Baixa | Delineado |
| **F7** | Higiene técnica (deprecações) | 🟢 Baixa | Delineado |
| **F8** | TIRT (escolha-forçada do DISC) | ⚪ Opcional | Delineado |
| **F9** | Camada de Autoconhecimento (Bloco 2: perguntas + IA) | 🔵 Visão futura | Delineado (material ✅; depende de F1 + pgvector) |

> **Onde entram as Perguntas Mestres:** a pasta `2-perguntas` é **irmã** do app (`1-disc-app`), nunca dentro dele. As perguntas **não entram no motor de pontuação**. Elas só "entram" na **F9**, numa camada de IA que lê o *perfil pontuado* (do DISC) + as *respostas biográficas* (das perguntas). A integração acontece na **saída/aconselhamento**, não na medição.
>
> **⚠️ Sincronização (importante):** o repositório git é o **`1-disc-app`** — o `.git` mora lá dentro. Logo, `2-perguntas` e `3-terapia` estão **fora do repo** e NÃO entram no `git push` (ficam "soltas"). Cada uma precisa de uma casa que sincronize (REGRA_MESTRE_SYNC). Recomendado: **`2-perguntas` no Google Drive sincronizado** (conteúdo pessoal e sensível — Blocos 05 e 11), privado nas duas máquinas. Alternativa: repositório git privado próprio só para `2-perguntas`. Não misturar com o repo do app.

---

## 3. PROMPTS PRONTOS — FAZER AGORA

> **Antes da F1:** crie um projeto Postgres no Supabase (você já usa Supabase) e copie a **connection string do pooler** (modo *Transaction*, recomendado para serverless) em *Project Settings → Database*. Guarde-a — ela vira a variável `DATABASE_URL`. Não cole a string aqui no prompt; o Codex usa a variável de ambiente.
>
> **Já habilite o pgvector agora:** no mesmo Supabase, em *Database → Extensions*, ative a extensão **`vector` (pgvector)**. É um clique e não atrapalha o DISC — mas é a base obrigatória da F9 (camada de autoconhecimento). Deixar pronto agora evita retrabalho depois.

### ▶️ PROMPT F1 — Persistência (Supabase Postgres)
```
Você é um engenheiro backend sênior. Faça apenas o solicitado. Não exponha segredos no código (use variável de ambiente). Mudança ADITIVA: não apague dados existentes.

## Contexto (manter adiante)
- Branch evolucao-cientifica. FastAPI em backend/app/. database.py já converte "postgres://" -> "postgresql://" e tem um fallback que joga SQLite para /tmp quando roda na Vercel. config.py: DATABASE_URL default = sqlite:///./psicometrico.db.
- PROBLEMA: na Vercel, SQLite em /tmp é efêmero e por instância — os dados da família NÃO persistem. Solução: usar Postgres do Supabase via DATABASE_URL.
- O startup roda create_all + seed_db; o seed já é idempotente para BIGFIVE.

## Tarefa
1. Em backend/requirements.txt, adicione o driver: `psycopg2-binary>=2.9`.
2. Em database.py: quando DATABASE_URL for Postgres, monte a URL SQLAlchemy como `postgresql+psycopg2://...`; crie o engine com `pool_pre_ping=True` e `pool_recycle=300`; NÃO aplique os connect_args de SQLite nesse caso; e DESATIVE o fallback "/tmp SQLite" quando houver uma URL Postgres definida (o fallback só vale para SQLite local).
3. Garanta idempotência no startup com Postgres: create_all deve ser no-op se as tabelas existem; verifique que o seed de tenant/usuários demo também checa existência antes de inserir (evite duplicar em cold starts). Se faltar essa checagem, adicione.
4. Atualize .env.template documentando: `DATABASE_URL` (string do pooler do Supabase, modo transaction, com sslmode=require) e que na Vercel ela deve ser definida em Settings → Environment Variables.
5. Teste local: rode com `DATABASE_URL` apontando para um Postgres e execute o fluxo e2e (cadastro → submit BIGFIVE → /results/me) confirmando persistência após reiniciar o processo.

## Critérios de sucesso (binário)
- App sobe contra Postgres; tabelas criadas; dados persistem entre reinícios; seed não duplica; SQLite continua funcionando para dev local. Nenhum segredo hardcoded.

Emita ✅ a cada passo. PARE e pergunte antes de qualquer operação destrutiva no banco.
```

### ▶️ PROMPT F2 — Suíte 100% verde + higiene
```
Você é um engenheiro sênior. Faça apenas o solicitado. Verifique antes de remover (confirme que o símbolo não é usado).

## Contexto (manter adiante)
- Branch evolucao-cientifica. O teste test_bigfive_submit_to_results_e2e em backend/app/test_main.py instancia `client = TestClient(app)` sem context manager, então o evento de startup (que cria as tabelas e semeia) NÃO dispara, causando "no such table: users". Os outros 21 testes passam.
- main.py linha ~18 ainda importa `calculate_cronbach_alpha` (provável import órfão — o Ômega é a confiabilidade agora).

## Tarefa
1. Em conftest.py (backend/app/), adicione uma fixture autouse que, antes dos testes, garanta as tabelas: `from backend.app.database import Base, engine; Base.metadata.create_all(bind=engine)`. Isso torna os testes independentes do ciclo de startup.
2. Ajuste o teste e2e para funcionar com as tabelas criadas (ou use `with TestClient(app) as client:` para disparar o startup). O teste deve passar.
3. Em backend/requirements.txt, adicione `httpx>=0.27` (dependência do TestClient do FastAPI), para a suíte rodar em qualquer máquina.
4. Confirme que `calculate_cronbach_alpha` não é mais chamado em lugar nenhum; se for órfão, remova o import da linha 18 e a função de math_engine.py se não houver mais uso. NÃO remova se ainda estiver em uso.
5. Rode `pytest backend/app/` e relate o número real de testes passando — alvo: todos verdes.

## Critérios de sucesso (binário)
- Suíte 100% verde relatada com número real. httpx no requirements. Alpha removido apenas se órfão.

Emita ✅ a cada passo.
```

---

## 4. PROMPTS FUTUROS (já delineados)

### ▶️ PROMPT F4 — Normas públicas reais
```
Você é psicometrista sênior. Não fabrique normas; use fonte pública real e cite-a.
Contexto: NORM_MODE="intra" é o padrão (régua interna, honesto para família). Para ativar "public", falta uma fonte real.
Tarefa: versione um arquivo backend/app/norms_ipip_neo.json com médias/desvios por fator Big Five derivados de fonte pública (ex.: dataset aberto IPIP-NEO https://github.com/automoto/big-five-data ou normas publicadas por Johnson), citando a fonte e a data no arquivo. Faça percentil_por_norma ler desse arquivo quando NORM_MODE="public". Rotule a saída como "comparado à amostra pública IPIP-NEO (fonte X)".
Critério: modo "public" usa normas reais citadas e versionadas; "intra" segue padrão. Pare antes de baixar arquivos grandes.
```

### ▶️ PROMPT F5 — Validação com dados reais (protocolo + ferramenta)
```
Você é psicometrista e engenheiro sênior. Não invente dados; crie a infraestrutura para coletar e analisar dados reais.
Contexto: o teste-reteste atual é simulado. A validação "padrão ouro" exige dados reais ao longo do tempo.
Tarefa:
1. Crie um endpoint/admin que exporte (CSV) as respostas item-a-item e os escores por respondente/aplicação, para análise externa.
2. Crie backend/app/validacao.py com funções: test_retest_real(aplicacao_a, aplicacao_b) (correlação por fator), e alpha_omega_por_fator(matriz) reaproveitando mcdonald_omega.
3. Crie _docs-motor/PROTOCOLO_VALIDACAO.md descrevendo como conduzir o teste-reteste com a família (intervalo 2–4 semanas), e quando há N suficiente para análise fatorial confirmatória (citar que CFA exige amostra grande).
Critério: exportação funciona; validacao.py testado; protocolo documentado.
```

### ▶️ PROMPT F6 — Decisão sobre Spranger
```
Contexto: Spranger é hoje camada ilustrativa provisória derivada do Big Five (mapeamento heurístico).
Tarefa: implemente UMA das opções e documente a escolha em _docs-motor/DECISOES.md:
(a) medir Spranger com itens próprios validados (criar bloco de itens, citar fonte); ou
(b) manter ilustrativo, mas rotular claramente na UI e no laudo como "estimativa ilustrativa, não medida".
Critério: opção escolhida implementada e registrada.
```

### ▶️ PROMPT F7 — Higiene técnica (deprecações)
```
Contexto: avisos de depreciação — `google.generativeai` (migrar p/ `google.genai`), `@app.on_event` (migrar p/ lifespan handlers), `datetime.utcnow()` (usar timezone-aware).
Tarefa: migre os três, mantendo o comportamento idêntico, com testes verdes. Faça um de cada vez.
Critério: sem avisos de depreciação críticos; suíte verde.
```

### ▶️ PROMPT F8 — TIRT (opcional)
```
Contexto: o DISC tem blocos de escolha-forçada pontuados de forma ipsativa; hoje o DISC é camada derivada do Big Five. TIRT só vale se quiser reativar a escolha-forçada com escores válidos.
Tarefa: avalie viabilidade do modelo Thurstoniano (pacote thurstonianIRT em R) para N pequeno (cite Bürkner et al., 2019). Se inviável, PARE e documente a recomendação de manter o DISC só derivado. Se viável, implemente.
Critério: decisão fundamentada, sem quebrar nada.
```

### ▶️ FASE F9 — Camada de Autoconhecimento (Bloco 2) — *visão futura, delineada*

> Esta é a fase que junta o DISC com as Perguntas Mestres — **na ponta**, não fundindo questionários. Depende de (a) a F1 concluída (Postgres) com **pgvector ativo**, e (b) a pasta `2-perguntas` (✅ **já disponível** — 1.242 perguntas em 11 blocos, com versões bruta e parametrizada). Quando a F1 estiver de pé, montamos os prompts de P1/P2/P3.

**Pré-requisitos:** F1 concluída + extensão pgvector ativa no Supabase. (Material `2-perguntas` ✅ pronto.)

**Arquitetura (três camadas):**
- Base: Supabase Postgres + pgvector (guarda e busca as respostas por similaridade).
- Fontes: o **perfil pontuado** (do DISC) + as **respostas biográficas** (das Perguntas Mestres).
- Topo: a IA de aconselhamento, que lê as duas fontes já *condicionada* ao perfil.

**O material `2-perguntas` tem DOIS níveis (descoberto ao inspecionar a pasta) — e isso divide o P1:**
- **Nível 1 — Narrativo (Blocos 01–10, ~1.030 perguntas).** Respostas em texto livre. Vão para o **pgvector/RAG** (embeddings + busca por similaridade). Analisadas depois por 9 lentes clínicas. NÃO pré-codificar — pré-codificar mata a riqueza narrativa.
- **Nível 2 — Rastreio psicométrico (Bloco 11, 212 itens).** Derivado de instrumentos clínicos validados (ASRS-1.1, WURS-25, DIVA-5, AQ, RAADS-R, CAT-Q, OEQ-II, HSP, GAD-7, OCI-R, CBI, PCL-5). É **quantitativo**: pontua contra os pontos de corte do `schema-bloco-11.json`. Tratar separado da narrativa, e **com o aviso clínico que já existe: rastreio NÃO é diagnóstico.**

**Partes:**
- **P1 — Banco de perguntas (dois fluxos).** (a) Narrativa (Blocos 01–10) → embeddings no pgvector (RAG). (b) Bloco 11 → pontuação quantitativa contra os cortes do schema. As perguntas vivem **separadas** do DISC; só os dados entram no banco.
- **P2 — Contrato de laudo (report contract).** Formato de saída do aconselhamento: o que a IA recebe (perfil + trechos narrativos recuperados + escores do rastreio), o que pode e não pode afirmar (mesmas regras anti-Barnum/incerteza do DISC), e a seção de limites.
- **P3 — MVP de Terapia/Aconselhamento.** A IA gera o aconselhamento condicionado ao perfil, citando apenas o que veio dos dados (âncora anti-alucinação). Temas de risco tratados com cuidado, direcionando a ajuda real.

**Regra que não muda:** as perguntas **nunca** entram no motor de pontuação do DISC. A junção é só nesta camada de saída.

---

## 5. PROMPT-MESTRE DE DOCUMENTAÇÃO (para o Codex deixar a evolução auto-documentada)

> Este é o prompt que você pediu: faz o Codex criar/atualizar **todos os documentos de referência** com base no código real, para a evolução ficar clara hoje e no futuro.

```
Você é um engenheiro de documentação técnica sênior. Documente APENAS o que existe de fato no código (leia os arquivos antes de escrever). Não descreva funcionalidades inexistentes. Cruze referências entre os documentos. Use Português do Brasil.

## Contexto (manter adiante)
- Projeto DISC, branch evolucao-cientifica. Núcleo Big Five (IPIP) com Jung contínuo derivado, Ômega, intervalos de confiança, qualidade de resposta, NORM_MODE intra/public, laudo anti-Barnum. Backend FastAPI em backend/app/; frontend React em frontend/. Já existem: backend/MANUAL_TECNICO.md, backend/RELATORIO_QA.md, _docs-motor/GUIA-DISC.md, _docs-motor/contexto-disc-proximo-chat.md.

## Tarefa — crie/atualize os seguintes arquivos, todos coerentes entre si:
1. `_docs-motor/ROADMAP.md` — roadmap vivo: fases F1–F9 com status (feito/em andamento/pendente), prioridade e critério de "pronto". Marque claramente o que já está concluído (núcleo Big Five, Jung contínuo, Ômega, IC, qualidade, modo intra, laudo anti-Barnum) e registre a F9 (camada de autoconhecimento) como visão futura dependente de pgvector.
2. `_docs-motor/STATUS.md` — fotografia do estado atual: o que roda, como rodar local (run_local.bat), como rodar testes, estado do deploy (Vercel + persistência), resultado real da suíte de testes.
3. `_docs-motor/DECISOES.md` — registro de decisões de arquitetura (ADR), uma por seção, com contexto/decisão/consequência: (a) Big Five como núcleo medido; (b) Jung contínuo derivado do Big Five + Estabilidade Emocional; (c) funções cognitivas só como narrativa; (d) Ômega de McDonald no lugar do Alpha; (e) DISC/Spranger como camadas de apresentação; (f) NORM_MODE intra como padrão honesto; (g) itens IPIP de domínio público; (h) Perguntas Mestres (`2-perguntas`) ficam em projeto/pasta separada e só se integram na camada de autoconhecimento (F9), via RAG/pgvector, na saída — nunca no motor de pontuação.
4. `CHANGELOG.md` (raiz) — versão semântica, começando em v1.0.0 (núcleo científico integrado), com as mudanças desta branch.
5. Atualize `backend/MANUAL_TECNICO.md` — garanta que reflete o código atual (construtos, itens, reverse_keyed, atenção, pontuação, Ômega/SEM, NORM_MODE, limites) e adicione/atualize o changelog interno.
6. Atualize `README.md` — visão geral, stack, como rodar local, como configurar Supabase/Vercel (DATABASE_URL), e links para os docs acima.
7. Consolide `_docs-motor/contexto-disc-proximo-chat.md` — um resumo curto e atual para retomar o trabalho em outra sessão, apontando para ROADMAP/STATUS/DECISOES.

## Critérios de sucesso (binário)
- Os 7 itens criados/atualizados, consistentes entre si, refletindo o código real, com referências cruzadas. Nenhuma funcionalidade inexistente descrita.

Emita ✅ a cada arquivo. Não faça merge — deixe para revisão.
```

---

## 6. MAPA DOS DOCUMENTOS DE REFERÊNCIA (para não se perder)

| Documento | Papel | Quem mantém |
|---|---|---|
| `_docs-motor/ROADMAP.md` | O futuro: fases e status | Codex (prompt §5) |
| `_docs-motor/STATUS.md` | O presente: o que roda agora | Codex (prompt §5) |
| `_docs-motor/DECISOES.md` | O porquê: decisões de arquitetura | Codex (prompt §5) |
| `CHANGELOG.md` | O histórico: versões | Codex (prompt §5) |
| `backend/MANUAL_TECNICO.md` | O instrumento: psicometria | Codex (prompt §5) |
| `backend/RELATORIO_QA.md` | A prova: resultados de teste | gerado no QA |
| `README.md` | A porta de entrada | Codex (prompt §5) |
| **Este arquivo (v2)** | O plano humano de evolução | você |

---

## 7. ORDEM RECOMENDADA E REGRA DE OURO

**Ordem atual (pós-7bc0094):** **Sprint 9** → QA manual → devolutiva textual → histórico visual → PDF → T1/T2 pessoal → F9 com perguntas abertas como apoio reflexivo. F8/TIRT fica apenas como opção futura distante, não como próximo passo.

**Regra de ouro:** um prompt por vez, testes verdes antes de avançar, **pare antes de mexer no schema/banco**, e nada de merge até revisão. Se um prompt pedir algo que o código não confirma, o agente **para e pergunta** — não inventa.
```
