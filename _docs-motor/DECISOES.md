# DECISOES — Registro de Decisões de Arquitetura (ADR)

> Cada decisão: contexto / decisão / consequências.
> Última atualização: 2026-06-17 (pós-commit `7bc0094`; escopo pessoal e Sprint 9).
> Ver também: [ROADMAP.md](ROADMAP.md) | [STATUS.md](STATUS.md)

---

## ADR-01 — Big Five como núcleo medido

**Contexto:** o projeto iniciou medindo DISC e Spranger com itens próprios. Esses instrumentos têm problemas psicométricos conhecidos: DISC usa escolha-forçada ipsativa (escores interdependentes), Spranger não tem normas publicadas amplamente.

**Decisão:** o núcleo medido é o Big Five (IPIP-50), com itens de domínio público, validados internacionalmente. DISC e Spranger são camadas de apresentação derivadas matematicamente do Big Five — não têm itens próprios no fluxo atual.

**Consequências:** escores Big Five são os únicos com confiabilidade calculável (Ômega de McDonald). DISC e Spranger têm validade construtal limitada enquanto forem derivados — os docstrings do código marcam explicitamente os pesos como `[provisório]`. Documentar nos laudos.

---

## ADR-02 — Jung contínuo derivado do Big Five + Estabilidade Emocional

**Contexto:** tipos Jungnianos (MBTI-like) são categorias discretas com baixa validade psicométrica. A literatura (McCrae & Costa, 1989) documenta correlações entre os polos MBTI e os fatores Big Five.

**Decisão:** Jung é derivado do Big Five como escala contínua em `derive_jung_from_big_five()`:
- E/I ← Extroversão (E)
- S/N ← Abertura (O)
- T/F ← Amabilidade (A)
- J/P ← Conscienciosidade (C)
- Estabilidade Emocional ← inverso de Neuroticismo (não é eixo Junguiano — reportado como "eixo extra")

Eixos são marcados como `borderline` quando o percentil está entre 45 e 55.

**Consequências:** sem dicotomias artificiais; incerteza representada explicitamente. Mapeamento é heurístico — documentar nos laudos e na UI. O `tipo_resumo` de 4 letras é um resumo de escores contínuos, não um tipo fixo.

---

## ADR-03 — Funções cognitivas Jungnianas como narrativa apenas

**Contexto:** funções cognitivas (Ti, Fe, Ni, Se etc.) do modelo Junguiano não têm itens próprios no sistema e não são derivadas pelos algoritmos atuais.

**Decisão:** não medir funções cognitivas por itens nem derivá-las numericamente. Usar apenas como narrativa opcional nos laudos, condicionada ao tipo-resumo derivado.

**Consequências:** nenhuma pontuação de função cognitiva no motor (`science_engine.py`). O docstring de `derive_jung_from_big_five()` registra explicitamente: "A pilha de funções cognitivas NÃO é calculada (sem suporte empírico) — fica para a narrativa."

---

## ADR-04 — Ômega de McDonald no lugar do Alpha de Cronbach

**Contexto:** Alpha de Cronbach assume tau-equivalência (cargas fatoriais iguais entre itens) — suposição frequentemente violada. O Ômega total de McDonald é mais apropriado para instrumentos com itens de pesos diferentes.

**Decisão:** usar Ômega total de McDonald (`mcdonald_omega()` em `science_engine.py`) via modelo unifatorial aproximado (primeira componente principal sobre matriz de correlações). Alpha permanece disponível em `math_engine.py:calculate_cronbach_alpha()` mas não é usado em nenhuma rota de produção.

**Consequências:** confiabilidade mais precisa. Import de `calculate_cronbach_alpha` foi removido de `main.py` em F2 (commit 05c74fa) — a função permanece em `math_engine.py` pois é usada em `test_main.py`.

---

## ADR-05 — DISC e Spranger como camadas de apresentação

**Contexto:** RH e empresas reconhecem DISC e Spranger como linguagem. Big Five é mais preciso mas menos reconhecido no contexto corporativo.

**Decisão:** DISC e Spranger são derivados do Big Five via mapeamento heurístico e apresentados como "estilo de ação" e "motivadores", respectivamente. Os docstrings em `derive_disc_from_big_five()` e `derive_spranger_from_big_five()` marcam todos os pesos como `[provisório]`. A F6 decidirá se Spranger passa a ter itens próprios ou se mantém o rótulo ilustrativo.

**Consequências:** facilita adoção corporativa sem abrir mão do núcleo científico. A validade do mapeamento é limitada e deve ser explicitada nos laudos (o prompt do Gemini já inclui essa ressalva) e na UI.

Decisão F6 (2026-06-13): opção (b) escolhida — manter ilustrativo. Opção (a) descartada: exigiria ~30 itens próprios e N ≥ 200 para validação, incompatível com escopo familiar. Rótulo "estimativa ilustrativa" adicionado à saída da API e ao prompt do laudo.

---

## ADR-06 — NORM_MODE=intra como padrão honesto

**Contexto:** usar percentis populacionais exige normas publicadas e versionadas para a população-alvo. O sistema não tem base própria suficiente nem norma brasileira validada, mas possui uma fonte pública exploratória versionada.

**Decisão:** padrão é `NORM_MODE=intra` — régua interna do próprio respondente. A primeira aplicação cria baseline interna e não retorna percentil interpretável. O modo `public` está funcional com `backend/app/norms_ipip_neo.json`, fonte `open_psychometrics_2018`, em escala bruta 10-50.

**Consequências:** resultados são honestos sobre o que medem. No modo intra, a primeira aplicação não deve ser lida como percentil populacional. No modo public, os percentis são exploratórios e não representam norma brasileira validada. Documentar nos laudos e na UI.

---

## ADR-07 — Itens IPIP de domínio público

**Contexto:** instrumentos comerciais (NEO PI-R, 16PF, MBTI etc.) têm licenças restritivas e custo por aplicação.

**Decisão:** usar IPIP Big-Five Factor Markers (Goldberg, 1992), 50 itens, domínio público (`https://ipip.ori.org`). Tradução PT-BR versionada em `seed_big_five_ipip.py`. Origem documentada no código com citação da fonte.

**Consequências:** sem custo por aplicação. Citação da fonte obrigatória em qualquer publicação derivada. A tradução PT-BR não foi validada por linguistas — revisar antes de uso em publicações.

---

## ADR-08 — Perguntas Mestres em pasta separada; integração apenas na F9

**Contexto:** o projeto tem 1.242 perguntas biográficas (`2-perguntas`, 11 blocos) que poderiam ser integradas ao questionário DISC. Misturá-las com itens psicométricos invalidaria a medição do Big Five.

**Decisão:** `2-perguntas` fica em pasta irmã fora do repo git (`1-disc-app`), sincronizada via Google Drive (ver `REGRA_MESTRE_SYNC.md`). As perguntas **nunca entram no motor de pontuação**. A integração acontece na F9, via pgvector/RAG, apenas na camada de saída (aconselhamento condicionado ao perfil pontuado).

**Consequências:** núcleo DISC permanece limpo e psicometricamente justificável. A F9 requer pgvector ativo no Supabase (já habilitado) e material `2-perguntas` disponível (já existe). Os dois níveis de material têm tratamentos distintos: narrativo (Blocos 01–10) vai para embeddings; rastreio psicométrico (Bloco 11) tem pontuação quantitativa contra pontos de corte do `schema-bloco-11.json`.

---

## ADR-09 — Supabase Postgres para persistência em produção

**Contexto:** SQLite em `/tmp` na Vercel é efêmero e por instância — dados não persistem entre cold starts.

**Decisão:** usar Supabase Postgres com Transaction pooler (port 6543, `sslmode=require`). `database.py` normaliza `postgres://` → `postgresql+psycopg2://` e configura `pool_pre_ping=True`, `pool_recycle=300`, `connect_timeout=5`. O fallback SQLite `/tmp` só é ativado quando `DATABASE_URL` já aponta para sqlite.

**Consequências:** dados persistem entre cold starts. Transaction pooler é o modo correto para Vercel Serverless (não session pooler). Segredos guardados em `Drive/segredos/disc-env.txt` e setados no Vercel.

---

## ADR-10 — Proxy ASGI em `api/index.py` para Vercel Serverless

**Contexto:** Vercel Serverless Functions não suportam ASGI diretamente com lifespan de forma confiável. Conflito entre `ServerErrorMiddleware` do Starlette e o exception handler do FastAPI resultava em erros em plain text.

**Decisão:** `api/index.py` é um proxy ASGI leve que: (a) faz lazy import do backend para evitar timeout de cold start; (b) gerencia lifespan próprio (não delega ao backend); (c) chama `_init_db()` na primeira requisição; (d) captura erros de runtime e retorna JSON. O `main.py` mantém `@app.exception_handler(Exception)` como segunda linha de defesa.

**Consequências:** deploy serverless estável. Qualquer erro em produção retorna `{"detail": "..."}` em vez de "Internal Server Error" em plain text. O lifespan separado é necessário porque o `ServerErrorMiddleware` re-raise exceções do lifespan do app, quebrando o deploy.

---

## ADR-11 — Invariante de preservação do histórico Big Five (2026-06-14)

**Contexto:** `process_psychometric_results()` tem dois caminhos: (a) se há respostas Big Five, faz early return para `_process_bigfive_results()`, que é append-only (cria novo `PsychometricResult` sem deletar os anteriores); (b) se não há Big Five, cai no ramo consolidado (DISC+Spranger+Jung), que continha um `DELETE` em massa de todos os `PsychometricResult` do usuário. Esse delete-all era um landmine: se o gate `has_bigfive` mudasse ou o fluxo DISC/Spranger/Jung fosse revivido, uma nova submissão apagaria todo o histórico Big Five, quebrando o teste-reteste (F5) e o NORM_MODE=intra.

**Decisão:** o delete do ramo consolidado foi estreitado para remover apenas linhas com `bigfive_percentis IS NULL` (resultados consolidados/legados). Resultados Big Five, identificados por `bigfive_percentis IS NOT NULL`, nunca são removidos por esse caminho. O caminho Big Five permanece append-only. Um comentário de invariante foi adicionado acima do delete em `main.py`.

**Motivo:** sustentar o teste-reteste da F5 (Josemar + Esdra, dois snapshots com 2–4 semanas de intervalo) e o `_bigfive_raw_history()` que alimenta o `NORM_MODE=intra`. Remover o landmine antes que o fluxo seja alterado.

**Consequências:** o histórico de `PsychometricResult` Big Five é imutável por código de aplicação. O delete consolidado continua funcionando para seu propósito original (substituir resultado consolidado antes de criar novo). Um teste unitário (`test_delete_consolidado_preserva_bigfive`) prova o invariante diretamente no filtro.

---

## ADR-12 — Escopo pessoal e Sprint 9 (2026-06-17)

**Contexto:** após a sprint técnica `7bc0094`, o núcleo psicométrico está suficientemente estável para uso pessoal: Big Five medido, baseline intra corrigido, norma pública exploratória funcional, Jung borderline indefinido, DISC/Spranger derivados com avisos, backend 30/30 e frontend build OK.

**Decisão:** o projeto, por enquanto, é aplicativo pessoal de autoconhecimento. A próxima fase oficial é a Sprint 9: sincronização documental, QA manual, melhoria da devolutiva, histórico visual, relatório PDF, validação pessoal T1/T2 e F9 com perguntas abertas apenas como apoio reflexivo.

**Consequências:** não priorizar TIRT/F8, RH corporativo, dashboard de equipe, ranking, seleção profissional, LGPD completa, produto comercial, alteração profunda do motor, promessa CFP/SATEPSI, laudo psicológico ou diagnóstico. LGPD completa volta ao roadmap apenas se o app virar produto comercial/corporativo/RH.
