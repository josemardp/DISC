# DECISOES — Registro de Decisões de Arquitetura (ADR)

> Cada decisão tem: contexto / decisão / consequências. Atualizado em 2026-06-10.

---

## ADR-01 — Big Five como núcleo medido

**Contexto:** o projeto iniciou medindo DISC e Spranger com itens próprios. Esses instrumentos têm problemas psicométricos conhecidos (ipsatividade no DISC, normas não publicadas).

**Decisão:** o núcleo medido é o Big Five (IPIP-50), com itens de domínio público, validados internacionalmente. DISC e Spranger são camadas de apresentação derivadas matematicamente do Big Five.

**Consequências:** escores Big Five são os únicos com confiabilidade calculável (Ômega de McDonald). DISC e Spranger têm validade construtal limitada enquanto forem derivados — documentar isso claramente nos laudos.

---

## ADR-02 — Jung contínuo derivado do Big Five + Estabilidade Emocional

**Contexto:** tipos Jungnianos (MBTI-like) são categorias discretas com baixa validade psicométrica.

**Decisão:** Jung é derivado do Big Five como escala contínua: E/I ← Extroversão; S/N ← Abertura; T/F ← Amabilidade; J/P ← Conscienciosidade; Estabilidade Emocional ← inverso de Neuroticismo. Eixos marcados como `borderline` quando percentil está entre 45 e 55.

**Consequências:** sem dicotomias artificiais; representa incerteza honestamente. Mapeamento é heurístico — documentar nos laudos.

---

## ADR-03 — Funções cognitivas Jungnianas como narrativa apenas

**Contexto:** funções cognitivas (Ti, Fe, Ni etc.) não têm itens próprios no sistema.

**Decisão:** não medir funções cognitivas por itens. Usar apenas como narrativa opcional nos laudos, condicionada ao tipo dominante derivado.

**Consequências:** nenhuma pontuação de função cognitiva no motor. Qualquer menção nos laudos deve ser marcada como inferência narrativa.

---

## ADR-04 — Ômega de McDonald no lugar do Alpha de Cronbach

**Contexto:** Alpha de Cronbach assume tau-equivalência (cargas iguais) e subestima a confiabilidade com itens de pesos diferentes.

**Decisão:** usar Ômega total de McDonald (via PCA unifatorial aproximado) como medida de confiabilidade. Alpha permanece disponível em `math_engine.py` mas não é usado na rota principal.

**Consequências:** confiabilidade mais precisa para instrumentos heterogêneos. Import de `calculate_cronbach_alpha` em `main.py` é órfão — remover na F2.

---

## ADR-05 — DISC e Spranger como camadas de apresentação

**Contexto:** RH e empresas reconhecem DISC e Spranger como linguagem. Big Five é mais preciso mas menos reconhecido no contexto corporativo.

**Decisão:** DISC e Spranger são derivados do Big Five via mapeamento heurístico (pesos provisórios no código) e apresentados como "estilo de ação" e "motivadores", respectivamente. Os próprios docstrings no código marcam esses mapeamentos como provisórios.

**Consequências:** facilita adoção corporativa sem abrir mão do núcleo científico. A validade do mapeamento é limitada e deve ser explicitada nos laudos e na UI.

---

## ADR-06 — NORM_MODE=intra como padrão

**Contexto:** usar percentis populacionais exige normas publicadas e versionadas. O sistema ainda não tem base de dados suficiente nem fonte pública versionada.

**Decisão:** padrão é `NORM_MODE=intra` — régua interna do próprio respondente (comparação entre fatores do mesmo indivíduo). O modo `public` está bloqueado no código com mensagem explicativa até existir uma fonte pública versionada.

**Consequências:** resultados são honestos sobre o que medem. Não é possível afirmar "você está no percentil 80 da população". Documentar isso nos laudos.

---

## ADR-07 — Itens IPIP de domínio público

**Contexto:** instrumentos comerciais (NEO PI-R, 16PF etc.) têm licenças restritivas e custo por aplicação.

**Decisão:** usar IPIP Big-Five Factor Markers (Goldberg, 1992), 50 itens, domínio público (`https://ipip.ori.org`). Tradução PT-BR versionada no código.

**Consequências:** sem custo por aplicação. Citação da fonte obrigatória em qualquer publicação derivada.

---

## ADR-08 — Perguntas Mestres em pasta separada, integração apenas na F9

**Contexto:** o projeto tem 1.242 perguntas biográficas (`2-perguntas`) que poderiam ser integradas ao questionário.

**Decisão:** `2-perguntas` fica em pasta irmã fora do repo (`Drive/Arquivos Josemar/...`). As perguntas **nunca entram no motor de pontuação**. A integração acontece na F9, via pgvector/RAG, apenas na camada de saída (aconselhamento).

**Consequências:** núcleo DISC permanece limpo e psicometricamente justificável. Misturar as perguntas narrativas com itens psicométricos invalidaria a medição.

---

## ADR-09 — Supabase Postgres para persistência em produção

**Contexto:** SQLite em `/tmp` na Vercel é efêmero e por instância — dados da família não persistiam entre cold starts.

**Decisão:** usar Supabase Postgres com Transaction pooler (port 6543, `sslmode=require`). `database.py` normaliza `postgres://` → `postgresql+psycopg2://` e configura `pool_pre_ping`, `pool_recycle=300`, `connect_timeout=5`.

**Consequências:** dados persistem. Cada cold start da Vercel abre conexão nova — o pooler de transações é o modo correto para serverless (não o pooler de sessão).

---

## ADR-10 — Proxy ASGI em `api/index.py` para Vercel Serverless

**Contexto:** Vercel Serverless Functions não suportam ASGI diretamente de forma confiável com lifespan.

**Decisão:** `api/index.py` é um proxy ASGI leve que: (a) faz lazy import do backend; (b) gerencia o lifespan próprio (não delega ao backend) para evitar conflito com `ServerErrorMiddleware`; (c) chama `_init_db()` na primeira request; (d) captura erros de runtime e retorna JSON.

**`main.py`** tem `@app.exception_handler(Exception)` para garantir que erros virem JSON antes de chegar ao `ServerErrorMiddleware` (que enviaria plain text e re-raise).

**Consequências:** deploy serverless estável. Qualquer erro em produção retorna `{"detail": "..."}` em vez de "Internal Server Error" em plain text.
