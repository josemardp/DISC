# Manual Técnico do Instrumento

## 1. Versão e data

- Versão: v0.2
- Data: 2026-06-10
- Branch de trabalho: main (F1 concluída — Supabase Postgres em produção)

## 2. Construtos e origem dos itens

### Big Five medido

O núcleo medido do sistema é o Big Five, com 50 itens em PT-BR carregados por `backend/app/seed_big_five_ipip.py`.

Origem documentada no código: IPIP Big-Five Factor Markers, 50 itens, Goldberg (1992), domínio público IPIP (`https://ipip.ori.org`). A tradução PT-BR está no arquivo `seed_big_five_ipip.py`.

Fatores medidos:

- O: Abertura / Intelecto
- C: Conscienciosidade
- E: Extroversão
- A: Amabilidade
- N: Neuroticismo

Escala de resposta documentada no código: 1 = Muito imprecisa até 5 = Muito precisa.

### Itens de atenção

O sistema inclui 3 itens com `dimension="attention_check"`. Eles não entram no escore Big Five (`weight=0.0`) e são usados na qualidade de resposta.

Itens de atenção definidos no código:

- "Para esta questão, marque 'Muito imprecisa' (1)." Resposta esperada: 1.
- "Por favor, selecione 'Muito precisa' (5) nesta frase." Resposta esperada: 5.
- "Marque a opção do meio (3) para confirmar que está atento." Resposta esperada: 3.

### Camadas derivadas

Jung contínuo, DISC e Spranger são derivados do Big Five no código. Eles não são medidos diretamente por itens próprios no fluxo atual Big Five.

- Jung contínuo: derivado por `derive_jung_from_big_five()`.
- DISC: derivado por `derive_disc_from_big_five()`.
- Spranger: derivado por `derive_spranger_from_big_five()`.

## 3. Itens reverse_keyed

No código, `reverse_keyed=True` significa que o item é invertido por `6 - valor` em escala 1-5 antes da soma.

Dimensões com itens invertidos:

- E: Extroversão
- A: Amabilidade
- C: Conscienciosidade
- N: Neuroticismo
- O: Abertura / Intelecto

Itens invertidos reais definidos em `seed_big_five_ipip.py`:

### E - Extroversão

- "Não falo muito."
- "Fico em segundo plano."
- "Tenho pouco a dizer."
- "Não gosto de chamar atenção para mim."
- "Sou quieto perto de estranhos."

### A - Amabilidade

- "Sinto pouca preocupação com os outros."
- "Insulto as pessoas."
- "Não me interesso pelos problemas dos outros."
- "Não tenho muito interesse pelos outros."

### C - Conscienciosidade

- "Deixo minhas coisas espalhadas."
- "Faço uma bagunça das coisas."
- "Costumo esquecer de colocar as coisas de volta no lugar."
- "Fujo das minhas obrigações."

### N - Neuroticismo

- "Fico relaxado na maior parte do tempo."
- "Raramente fico para baixo."

### O - Abertura / Intelecto

- "Tenho dificuldade em entender ideias abstratas."
- "Não me interesso por ideias abstratas."
- "Não tenho boa imaginação."

## 4. Método de pontuação de cada camada

### Big Five

A pontuação é feita por `score_big_five()` em `backend/app/science_engine.py`.

Comportamento documentado no código:

- Ignora itens cuja dimensão não está em `["O", "C", "E", "A", "N"]`, incluindo `attention_check`.
- Aplica reversão quando `reverse_keyed=True`.
- Retorna por fator: escore bruto (`raw`), média (`mean`) e número de itens (`n_itens`).
- Calcula também `ES` (Estabilidade Emocional) como inverso de N.

### Percentis / régua interna

O modo atual é `NORM_MODE=intra`, lido de `.env` por `backend/app/config.py`.

No modo atual, o sistema usa régua interna do próprio respondente por `percentil_intraindividual()`. O rótulo retornado pela API é: "régua interna (não é percentil populacional)".

O modo `public` está bloqueado no código até existir fonte pública versionada.

### Jung contínuo

O Jung contínuo é derivado por `derive_jung_from_big_five()` em `science_engine.py`.

Mapeamento implementado:

- E/I deriva de Extroversão.
- S/N deriva de Abertura.
- T/F deriva de Amabilidade.
- J/P deriva de Conscienciosidade.
- Estabilidade Emocional deriva do inverso de Neuroticismo.

O código também marca eixos `borderline` quando o percentil está entre 45 e 55.

### DISC derivado

DISC é derivado por `derive_disc_from_big_five()` em `science_engine.py`.

Mapeamento implementado no código:

- D: média de Extroversão e baixa Amabilidade.
- I: média de Extroversão e Amabilidade.
- S: média de Amabilidade e Estabilidade Emocional.
- C: Conscienciosidade.

O próprio código rotula esses pesos como provisórios e como camada de apresentação.

### Spranger derivado

Spranger é derivado por `derive_spranger_from_big_five()` em `science_engine.py`.

Mapeamento implementado no código:

- teorico: Abertura
- estetico: Abertura
- social: Amabilidade
- regulador: Conscienciosidade
- individualista: Extroversão
- economico: média de Conscienciosidade e baixa Abertura

O próprio código informa que esse mapeamento é heurístico, provisório e ilustrativo.

## 5. Confiabilidade e intervalos de confiança

### Ômega de McDonald

A função `mcdonald_omega()` está em `science_engine.py`.

Implementação atual:

- Estima ômega total por modelo unifatorial aproximado via primeira componente principal sobre matriz de correlações dos itens.
- Remove colunas com variância zero.
- Retorna valor limitado entre 0.0 e 1.0.

Em `/admin/stats`, o sistema calcula `omega_bigfive` por fator Big Five quando há dados suficientes.

### SEM

A função `standard_error_of_measurement()` está em `science_engine.py`.

Fórmula implementada:

- `SEM = sd * sqrt(1 - reliability)`

No endpoint de resultados e relatório, o código usa `sd=15.0` e confiabilidade provisória `reliability=0.84`.

### IC95%

A função `confidence_interval()` está em `science_engine.py`.

Implementação atual:

- Usa `z=1.96` por padrão.
- Aplica limites opcionais; para percentis, o código usa `bounds=(0, 100)`.
- Retorna `ci_low` e `ci_high`.

## 6. Qualidade de resposta

A qualidade de resposta é calculada por `response_quality_index()` em `science_engine.py`.

Critérios implementados:

- Atenção: verifica se os itens `attention_check` foram respondidos com os valores esperados.
- Straight-lining: detecta variância menor que `0.01` nos valores respondidos.
- `irt_avg`: marca `too_fast` quando o tempo médio por item é menor que 800 ms.

O código também considera `rvi_count > 10` na pontuação de qualidade.

Labels possíveis:

- `alta`
- `media`
- `baixa`

Pontuação implementada:

- Falha em atenção: +2 pontos.
- Straight-lining: +2 pontos.
- Muito rápido: +1 ponto.
- `rvi_count > 10`: +1 ponto.
- 0 pontos: `alta`.
- 1 a 2 pontos: `media`.
- 3 ou mais pontos: `baixa`.

## 7. Normas

Modo atual:

- `NORM_MODE=intra`
- Usa régua interna do próprio respondente.
- A saída é rotulada como "régua interna (não é percentil populacional)".

Modo `public`:

- Bloqueado no código.
- Mensagem implementada: `NORM_MODE=public requer arquivo de normas públicas versionado. Use NORM_MODE=intra por enquanto.`
- Fonte pública versionada: a verificar.

## 8. Limites e usos vedados

Limites documentados conforme o comportamento atual do código:

- Não é diagnóstico clínico.
- Não descreve características imutáveis.
- Jung, DISC e Spranger são camadas derivadas do Big Five, não medidas independentes no fluxo atual.
- O modo atual de norma é uma régua interna, não percentil populacional.
- O laudo gerado via Gemini e fallback local usa linguagem de incerteza e seção de limites, mas deve ser lido como apoio interpretativo.

Usos vedados ou que exigem validação adicional:

- Não usar isoladamente para decisões de admissão, desligamento, promoção ou outras decisões de alto impacto sem validação adicional.
- Não usar como diagnóstico clínico, psiquiátrico ou médico.
- Não interpretar resultados como traços fixos ou imutáveis.

Amostra atual:

- Uso familiar / desenvolvimento.
- Validação empírica com amostra própria: a verificar.

## 9. Changelog

- v0.2 — 2026-06-10 — atualizado para refletir F1 concluída (Supabase Postgres em produção, Vercel deploy estável).
- v0.1 — 2026-06-05 — versão inicial do manual técnico, refletindo Big Five IPIP-50, itens de atenção, camadas derivadas, régua interna, confiabilidade, IC95%, qualidade de resposta e laudo anti-Barnum conforme código atual.
