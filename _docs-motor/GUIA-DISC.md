# 🧭 Guia Mestre de Implantação — DISC no Padrão Big Five
### Documento único. Siga de cima para baixo. Marque as caixinhas conforme avança.

> **Estratégia em um parágrafo:** o Big Five (5 fatores, com Neuroticismo) é o núcleo medido com itens validados do IPIP. Jung — que você gosta — é mantido, mas medido de forma **contínua** e derivado do Big Five, com o tipo de 4 letras como resumo. DISC e Spranger ficam como camadas de apresentação. Assim você herda décadas de validação científica em vez de tentar recriá-la.

---

## 0. ONDE VOCÊ ESTÁ (status)

| Parte | Status |
|---|---|
| Motor científico (Big Five, Ômega, IC, Jung contínuo, qualidade) | ✅ **Construído e testado** |
| Itens IPIP-50 em PT-BR + itens de atenção | ✅ **Prontos** |
| Encaixe no backend (`models.py`, `seed.py`, `main.py`) | ✅ **Concluído** (Prompts 1–2) |
| Frontend (responder + exibir) | ✅ **Concluído** (Prompt 3) |
| Normas honestas | ✅ **Concluído em modo intra** (Prompt 4; `public` bloqueado até fonte versionada) |
| Laudo anti-Barnum | ✅ **Concluído** (Prompt 5) |
| Manual técnico | ✅ **Concluído** (Prompt 6; `backend/MANUAL_TECNICO.md`) |
| Validação e QA | ✅ **Concluído** (Prompt 7; `backend/RELATORIO_QA.md`) |
| Deploy Vercel | ✅ **Corrigido e validado** (`/` e `/auth/register` em produção) |
| Validação empírica (teste-reteste, AFC) | ⏳ Depende de dados coletados ao longo do tempo |

---

## 1. ARQUIVOS PARA ANEXAR AO PROJETO

Coloque estes três na pasta `backend/app/` do seu projeto:

| Arquivo | Destino | Para quê |
|---|---|---|
| `science_engine.py` | `backend/app/science_engine.py` | Motor científico (núcleo) |
| `seed_big_five_ipip.py` | `backend/app/seed_big_five_ipip.py` | Os 50 itens IPIP em PT-BR |
| `test_science_engine.py` | `backend/app/test_science_engine.py` | Testes do motor |

O `LEIA-ME_INTEGRACAO.md` é só referência — **não precisa ir para o projeto**.

- [ ] Três arquivos `.py` copiados para `backend/app/`

---

## 2. CHECKLIST DE IMPLANTAÇÃO (sequencial)

**Preparação**
- [x] Python 3.9+ e Node.js 18+ instalados (necessário pra rodar)
- [x] `numpy` no `requirements.txt` e `backend/requirements.txt`
- [x] Arquivos do item 1 anexados

**Backend**
- [x] Prompt 0 — branch de segurança
- [x] Prompt 1 — schema + seed dos itens Big Five
- [x] Prompt 2 — processamento + resultados + qualidade

**Frontend**
- [x] Prompt 3 — responder o Big Five e exibir os 5 fatores

**Ciência e qualidade**
- [x] Prompt 4 — normas honestas
- [x] Prompt 5 — laudo anti-Barnum
- [x] Prompt 6 — manual técnico
- [x] Prompt 7 — validação e QA (final)
- [ ] Prompt 8 — TIRT (opcional)

**Pós**
- [x] Testar fluxo completo de ponta a ponta em backend/local e produção Vercel
- [ ] Coletar respostas da família para começar a calibrar normas reais

---

## 3. OS PROMPTS — DO ZERO AO FIM

> Cole **um por vez** num agente de código (Codex, Claude Code ou Cursor). Só avance com os testes verdes. **Não faça merge** até o final.
> Todos pedem: afirmar só o que se verifica no código, não inventar nada, e **parar antes de alterar o schema do banco**.

### ▶️ PROMPT 0 — Rede de segurança
```
Você é um engenheiro sênior. Faça apenas o solicitado.
Contexto: projeto FastAPI em backend/app/ (main.py, models.py, seed.py, science_engine.py recém-anexado). Banco SQLite auto-populado no startup.
Tarefa:
1. Crie e mude para a branch git `evolucao-cientifica`.
2. Rode `pytest backend/app/` e relate quantos testes passam/falham hoje (não altere testes).
3. Confirme que science_engine.py e seed_big_five_ipip.py estão em backend/app/ e importam sem erro (`python -c "from backend.app import science_engine"`).
Critério: branch criada, baseline de testes relatado, imports OK.
Emita ✅ ao final. Pare e pergunte antes de qualquer alteração de schema.
```

### ▶️ PROMPT 1 — Schema + seed dos itens Big Five
```
Você é um engenheiro sênior. Faça apenas o solicitado. NÃO invente itens (os itens já vêm prontos de seed_big_five_ipip.py). Pare e mostre o plano de schema ANTES de aplicar.
Contexto: branch evolucao-cientifica. models.py tem QuestionnaireItem(id, block_number, test_type, dimension, item_text, weight) e PsychometricResult. O banco é recriado no startup via create_all + seed_db.
Tarefa:
1. Em models.py, adicione à QuestionnaireItem a coluna `reverse_keyed = Column(Boolean, default=False)`.
2. Em models.py, adicione à PsychometricResult: `bigfive_O, bigfive_C, bigfive_E, bigfive_A, bigfive_N` (Float, default 0.0) e `bigfive_percentis = Column(JSON, nullable=True)` e `jung_continuo = Column(JSON, nullable=True)` e `quality_label = Column(String, nullable=True)`.
3. MOSTRE o plano de alteração de schema e PARE para minha confirmação. Como é uso familiar sem dados a preservar, a aplicação pode ser feita apagando psicometrico.db para o create_all recriar — confirme isso comigo.
4. Após eu confirmar: em seed.py, ao fim de seed_db, insira os itens BIGFIVE usando `from backend.app.seed_big_five_ipip import construir_itens_bigfive` (mapeie id, block_number, test_type, dimension, item_text, weight, reverse_keyed para QuestionnaireItem).
5. Suba o servidor uma vez e confirme que os itens BIGFIVE foram semeados (consulte /questionnaire/items?test_type=BIGFIVE).
Critério: colunas criadas, 50 itens BIGFIVE + 3 de atenção semeados, servidor sobe sem erro.
Emita ✅ a cada passo. PARE antes de aplicar o schema.
```

### ▶️ PROMPT 2 — Processamento + resultados + qualidade
```
Você é um psicometrista e engenheiro Python sênior. Faça apenas o solicitado. Use as funções já prontas em science_engine.py; não reimplemente a matemática.
Contexto: branch evolucao-cientifica. science_engine.py expõe: score_big_five, percentil_por_norma, percentil_intraindividual, derive_jung_from_big_five, derive_disc_from_big_five, derive_spranger_from_big_five, mcdonald_omega, standard_error_of_measurement, confidence_interval, response_quality_index. Itens de atenção têm dimension="attention_check".
Tarefa:
1. Em main.py /questionnaire/submit: ao receber respostas BIGFIVE (Likert 1–5), persista-as (use o campo value). Separe os itens de atenção.
2. Em process_psychometric_results: monte a lista {dimension, value, reverse_keyed} a partir das respostas BIGFIVE (busque reverse_keyed no QuestionnaireItem), chame score_big_five, depois percentil por fator (use NORM_MODE — ver Prompt 4; por enquanto percentil_por_norma com média=30, sd=6 PROVISÓRIO), e derive_jung_from_big_five(percentis). Persista bigfive_*, bigfive_percentis, jung_continuo em PsychometricResult.
3. Calcule response_quality_index (atenção, straight-lining via variância, irt_avg da TelemetrySession) e persista quality_label. Troque a linguagem de "fraude" para "qualidade" na saída da API.
4. PARE de calcular Alpha de Cronbach sobre o DISC ipsativo. Em /admin/stats, calcule mcdonald_omega sobre a matriz de respostas BIGFIVE por fator.
5. Em /results/me: retorne os 5 fatores com confidence_interval(p, sem, bounds=(0,100)) (use sem de standard_error_of_measurement com confiabilidade 0.84 provisória), o jung_continuo completo, DISC/Spranger derivados e quality_label.
6. Adicione um teste e2e em test_main.py: submissão BIGFIVE → /results/me com 5 fatores + IC + jung.
Critério: fluxo BIGFIVE submit→resultado funciona, omega em /admin/stats, sem Alpha sobre ipsativo, teste e2e passa.
Emita ✅ a cada passo.
```

### ▶️ PROMPT 3 — Frontend (responder e exibir)
```
Você é um engenheiro frontend React/TypeScript sênior. Faça apenas o solicitado. Não altere o backend.
Contexto: branch evolucao-cientifica. Frontend em frontend/ (App.tsx, components/TestRoom.tsx, components/Dashboards.tsx), Vite + Tailwind. A API agora serve itens test_type="BIGFIVE" (Likert 1–5) e /results/me retorna 5 fatores Big Five com ci_low/ci_high, jung_continuo (tipo_resumo, eixos com borderline, estabilidade_emocional) e quality_label.
Tarefa:
1. Em TestRoom.tsx: adicione a fase de responder os itens BIGFIVE numa escala Likert de 5 pontos (1=Muito imprecisa ... 5=Muito precisa). Inclua os itens de atenção no fluxo normal (sem destacá-los).
2. Em Dashboards.tsx: exiba os 5 fatores Big Five como barras com a faixa do intervalo de confiança visível; exiba o tipo Jung como resumo com os 4 eixos contínuos (e um aviso quando borderline=true); exiba a Estabilidade Emocional; mostre um selo de qualidade da resposta (alta/média/baixa).
3. Garanta responsividade mobile (a família vai usar no celular).
Critério: dá pra responder o Big Five e ver os 5 fatores com IC, o Jung contínuo e a qualidade, no desktop e no mobile.
Emita ✅ a cada passo.
```

### ▶️ PROMPT 4 — Normas honestas
```
Você é um psicometrista sênior. Faça apenas o solicitado. Não fabrique normas. Use fonte pública real OU o modo intra-individual.
Contexto: branch evolucao-cientifica. science_engine.py tem percentil_por_norma(raw, mean, sd) e percentil_intraindividual(raw_atual, historico).
Tarefa:
1. Em config.py adicione NORM_MODE lido do .env, valores "intra" (padrão) ou "public".
2. "intra": compare cada pessoa com o próprio histórico de PsychometricResult; rotule a saída como "régua interna (não é percentil populacional)".
3. "public": carregue normas reais de Big Five do IPIP-NEO de um arquivo de dados versionado (ex.: derivadas do dataset aberto https://github.com/automoto/big-five-data ou normas publicadas por Johnson). Cite a fonte no arquivo. Rotule a saída como "comparado à amostra pública IPIP-NEO".
4. Remova/isole a norma provisória (média 30, sd 6) e o rótulo deve deixar claro qual modo está ativo.
Critério: dois modos funcionam, fonte pública citada e versionada, percentil rotulado honestamente, sem norma chutada solta no código.
Emita ✅ a cada passo. Pare antes de baixar arquivos grandes.
```

### ▶️ PROMPT 5 — Laudo anti-Barnum
```
Você é consultor psicométrico e engenheiro de prompts sênior. Faça apenas o solicitado.
Contexto: branch evolucao-cientifica. gemini_service.py tem generate_psychometric_report (Gemini) e generate_mock_report (fallback local). O núcleo agora é Big Five; Jung é contínuo derivado; escores têm intervalos de confiança; há quality_label.
Tarefa:
1. Reescreva o prompt enviado ao Gemini para: usar linguagem de incerteza ("tende a", "indica" — nunca "você é"); citar os intervalos de confiança; PROIBIR frases genéricas que sirvam para qualquer pessoa (anti-Barnum); tratar a pilha de funções junguianas apenas como narrativa, nunca medida; incluir seção fixa "Limites desta avaliação" (não é diagnóstico, não é imutável, rastreios são triagem); e a âncora "use apenas os dados fornecidos; se faltar dado, diga 'sem dados suficientes'".
2. Aplique a mesma estrutura ao generate_mock_report.
3. O laudo deve reportar 5 fatores + Jung contínuo + Estabilidade Emocional + qualidade da resposta.
Critério: prompt e fallback com incerteza, IC citados, anti-Barnum, seção de limites e âncora anti-alucinação.
Emita ✅ a cada passo.
```

### ▶️ PROMPT 6 — Manual técnico
```
Você é um psicometrista documentando o instrumento. Faça apenas o solicitado. Documente só o que está realmente no código.
Contexto: branch evolucao-cientifica. Sistema mede Big Five (IPIP), deriva Jung contínuo/DISC/Spranger, usa Ômega + IC, qualidade de resposta, normas (NORM_MODE) e laudo anti-Barnum.
Tarefa: crie backend/MANUAL_TECNICO.md com: versão e data; construtos e origem dos itens (IPIP, com referência); quais itens são reverse_keyed e de atenção; método de pontuação de cada camada (Big Five medido; Jung/DISC/Spranger derivados com fórmulas); confiabilidade (Ômega, como é calculada) e o SEM dos intervalos; normas (modo e fonte); limites e usos vedados; changelog inicial.
Critério: MANUAL_TECNICO.md reflete o código real, com referências e changelog. Nada inexistente descrito.
Emita ✅ ao final.
```

### ▶️ PROMPT 7 — Validação e QA (FINAL)
```
Você é engenheiro de QA e psicometria sênior. Faça apenas o solicitado. Reporte resultados reais; não declare sucesso sem rodar.
Contexto: branch evolucao-cientifica, todas as etapas anteriores concluídas.
Tarefa:
1. Harness de teste-reteste: simule um respondente preenchendo duas vezes com respostas quase iguais e verifique estabilidade dos 5 fatores (correlação alta).
2. Validade convergente interna: verifique que derive_jung_from_big_five acompanha os fatores de origem (E/I ~ Extroversão etc.).
3. Teste e2e: cadastro → responder Big Five (com atenção) → /results/me (5 fatores + IC + Jung + qualidade) → /results/report (laudo com seção de Limites).
4. Rode `pytest backend/app/` inteiro e relate o número real de passes/falhas.
5. Gere RELATORIO_QA.md curto: o que foi testado, resultados reais, pontos que ainda precisam de atenção humana.
Critério: teste-reteste e convergente passam, e2e passa, suíte inteira roda e o resultado real é relatado, RELATORIO_QA.md gerado.
Emita ✅ e o resumo do RELATORIO_QA.md. NÃO faça merge — deixe para revisão humana.
```

### ▶️ PROMPT 8 — TIRT (OPCIONAL, só se quiser manter a escolha-forçada do DISC)
```
Você é psicometrista especialista em IRT. Faça apenas o solicitado. Use o modelo Thurstoniano (Brown & Maydeu-Olivares). Não improvise a matemática.
Contexto: branch evolucao-cientifica. O DISC tem 24 blocos de escolha-forçada pontuados de forma ipsativa. O núcleo já é Big Five; o DISC é apresentação. Esta etapa é opcional.
Tarefa: avalie a viabilidade de TIRT (pacote thurstonianIRT em R) para o N pequeno de uso familiar. Se inviável (N pequeno limita estimação — cite Bürkner et al., 2019), PARE e documente a recomendação de manter o DISC apenas derivado do Big Five, sem alterar código. Se viável, implemente e substitua a pontuação ipsativa.
Critério: decisão fundamentada — implementado OU recomendação documentada — sem quebrar nada.
PARE e mostre a análise de viabilidade antes de implementar.
```

---

## 4. O QUE ESTÁ PENDENTE (resumo honesto)

1. **Persistência em produção**: trocar `DATABASE_URL` da Vercel para a Transaction Pooler URL do Supabase. Hoje há fallback temporário para SQLite em `/tmp` quando a URL direta do Supabase falha.
2. **Normas públicas**: o modo atual é `intra` (régua interna). Ativar `public` somente com fonte pública versionada.
3. **Validação empírica** (⏳ não é código): teste-reteste com pessoas reais e análise fatorial confirmatória exigem **dados coletados ao longo do tempo**.
4. **Decisão sobre Spranger**: hoje é camada ilustrativa provisória. Decida depois se mede com itens próprios ou mantém só ilustrativo.
5. **Prompt 8 / TIRT**: opcional, apenas se houver decisão de manter escolha-forçada DISC e amostra suficiente.

---

## 5. REGRA DE OURO

Um prompt por vez. Testes verdes antes de avançar. **Pare antes de mexer no schema.** Nada de merge até o Prompt 7. Se um prompt pedir algo que o código não confirma, o agente deve **parar e perguntar** — não inventar.
