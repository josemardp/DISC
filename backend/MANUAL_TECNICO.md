# Manual Técnico do Instrumento

> Ver também: [ROADMAP](_docs-motor/ROADMAP.md) | [DECISOES](_docs-motor/DECISOES.md) | [STATUS](_docs-motor/STATUS.md)

## 1. Versão e data

- Versão: v0.6
- Data: 2026-06-19
- Branch de trabalho: main (Sprint 15, 33/33 testes passando, 0 warnings no pytest)

---

## 2. Construtos e origem dos itens

### Big Five — núcleo medido

O único construto medido diretamente por itens é o Big Five, com 50 itens em PT-BR carregados por `backend/app/seed_big_five_ipip.py`.

**Origem:** IPIP Big-Five Factor Markers, 50 itens, Goldberg (1992), domínio público (`https://ipip.ori.org`). Tradução PT-BR versionada no código. Escala de resposta: 1 = Muito imprecisa, 5 = Muito precisa.

**Fatores medidos (5):**

| Sigla | Nome |
|---|---|
| O | Abertura / Intelecto |
| C | Conscienciosidade |
| E | Extroversão |
| A | Amabilidade |
| N | Neuroticismo |

### Itens de atenção

3 itens com `dimension="attention_check"` e `weight=0.0`. Não entram no escore Big Five. Usados em `response_quality_index()`.

| Item | Resposta esperada |
|---|---|
| "Para esta questão, marque 'Muito imprecisa' (1)." | 1 |
| "Por favor, selecione 'Muito precisa' (5) nesta frase." | 5 |
| "Marque a opção do meio (3) para confirmar que está atento." | 3 |

### Camadas derivadas (não medidas por itens)

| Camada | Função | Observação |
|---|---|---|
| Jung contínuo | `derive_jung_from_big_five()` | 4 eixos + borderline + Estabilidade Emocional |
| DISC | `derive_disc_from_big_five()` | heurístico, provisório |
| Spranger | `derive_spranger_from_big_five()` | heurístico, provisório |

Ver [ADR-01](../&#95;docs-motor/DECISOES.md#adr-01), [ADR-02](../&#95;docs-motor/DECISOES.md#adr-02), [ADR-05](../&#95;docs-motor/DECISOES.md#adr-05).

---

## 3. Itens reverse_keyed

`reverse_keyed=True` significa que o item é invertido por `6 − valor` (em escala 1–5) antes da soma, via `_aplica_reverso()` em `science_engine.py`.

### E — Extroversão (5 itens invertidos)

- "Não falo muito."
- "Fico em segundo plano."
- "Tenho pouco a dizer."
- "Não gosto de chamar atenção para mim."
- "Sou quieto perto de estranhos."

### A — Amabilidade (4 itens invertidos)

- "Sinto pouca preocupação com os outros."
- "Insulto as pessoas."
- "Não me interesso pelos problemas dos outros."
- "Não tenho muito interesse pelos outros."

### C — Conscienciosidade (4 itens invertidos)

- "Deixo minhas coisas espalhadas."
- "Faço uma bagunça das coisas."
- "Costumo esquecer de colocar as coisas de volta no lugar."
- "Fujo das minhas obrigações."

### N — Neuroticismo (2 itens invertidos)

- "Fico relaxado na maior parte do tempo."
- "Raramente fico para baixo."

### O — Abertura / Intelecto (3 itens invertidos)

- "Tenho dificuldade em entender ideias abstratas."
- "Não me interesso por ideias abstratas."
- "Não tenho boa imaginação."

---

## 4. Método de pontuação

### Big Five — `score_big_five()` em `science_engine.py`

- Ignora itens com `dimension` fora de `["O", "C", "E", "A", "N"]` (inclui `attention_check`).
- Aplica reversão quando `reverse_keyed=True`: `valor_final = 6 − valor`.
- Retorna por fator: `{"raw": soma, "mean": média, "n_itens": k}`.
- Calcula também `ES` (Estabilidade Emocional) como `raw = 60.0 − raw_N`, `mean = 6.0 − mean_N`.

### Percentis e normas

Modo padrão: `NORM_MODE=intra`. A régua interna compara cada fator do respondente com seus próprios históricos anteriores.

Na primeira aplicação, o sistema cria uma linha de base interna e não retorna percentil interpretável. Isso evita apresentar 50 como se fosse resultado populacional real. A partir da segunda aplicação, o histórico intraindividual passa a sustentar a comparação.

Modo `public`: funcional com `backend/app/norms_ipip_neo.json`, fonte `open_psychometrics_2018`, escala bruta 10-50 por fator. É norma pública exploratória, não representativa da população brasileira.

### Jung contínuo — `derive_jung_from_big_five()` em `science_engine.py`

Mapeamento (McCrae & Costa, 1989):

| Eixo Jung | Fator Big Five |
|---|---|
| E/I | Extroversão (E) |
| S/N | Abertura (O) |
| T/F | Amabilidade (A) |
| J/P | Conscienciosidade (C) |
| Estabilidade Emocional* | 100 − Neuroticismo (N) |

*Não é eixo Junguiano — reportado como "eixo extra".

Eixos marcados como `borderline` quando percentil está entre 45 e 55. Quando a maioria dos eixos está borderline, `tipo_resumo` retorna `indefinido`. Quando há tipo de 4 letras, ele é apenas resumo exploratório dos escores contínuos, não tipo fixo.

### DISC derivado — `derive_disc_from_big_five()` em `science_engine.py`

| Dimensão | Fórmula (provisória) |
|---|---|
| D | (E + (100 − A)) / 2 |
| I | (E + A) / 2 |
| S | (A + ES) / 2 |
| C | C (Conscienciosidade) |

Todos marcados como `[provisório]` no código.

### Spranger derivado — `derive_spranger_from_big_five()` em `science_engine.py`

| Dimensão | Fórmula (provisória) |
|---|---|
| teorico | O (Abertura) |
| estetico | O (Abertura) |
| social | A (Amabilidade) |
| regulador | C (Conscienciosidade) |
| individualista | E (Extroversão) |
| economico | (C + (100 − O)) / 2 |

Todos marcados como `[provisório]` no código. Mapeamento heurístico e ilustrativo.

---

## 5. Confiabilidade e intervalos de confiança

### Ômega de McDonald — `mcdonald_omega()` em `science_engine.py`

Estima ômega total por modelo unifatorial aproximado via primeira componente principal sobre a matriz de correlações dos itens. Remove colunas com variância zero. Retorna valor entre 0.0 e 1.0.

Em `/admin/stats`, o sistema calcula `omega_bigfive` por fator Big Five quando há dados suficientes.

### SEM — `standard_error_of_measurement()` em `science_engine.py`

```
SEM = sd × √(1 − confiabilidade)
```

No motor de resultados: `sd=15.0`, `reliability=0.84` (provisório — revisar quando houver dados reais).

### IC95% — `confidence_interval()` em `science_engine.py`

- `z=1.96` por padrão.
- `bounds=(0, 100)` para percentis.
- Retorna `ci_low` e `ci_high`.

### Alpha de Cronbach — `calculate_cronbach_alpha()` em `math_engine.py`

Disponível para uso avulso (usado nos testes automatizados). **Não é usado nas rotas de produção** — substituído pelo Ômega de McDonald. Ver [ADR-04](../&#95;docs-motor/DECISOES.md#adr-04).

---

## 6. Qualidade de resposta — `response_quality_index()` em `science_engine.py`

| Critério | Condição | Pontos |
|---|---|---|
| Atenção | item `attention_check` com valor errado | +2 |
| Straight-lining | variância dos valores < 0.01 | +2 |
| Muito rápido | `irt_avg` < 800 ms | +1 |
| RVI excessivo | `rvi_count` > 10 | +1 |

| Total de pontos | Label |
|---|---|
| 0 | `alta` |
| 1–2 | `media` |
| ≥3 | `baixa` |

Retorna também `attention_passed`, `straight_lining` e `too_fast`.

---

## 7. Normas

| Modo | Função | Estado |
|---|---|---|
| `intra` (padrão) | `percentil_intraindividual()` | Ativo — régua interna honesta |
| `public` | `raw_to_percentile()` via norma pública versionada | Ativo — `open_psychometrics_2018`, exploratório |

Lido de `.env` por `backend/app/config.py`: `NORM_MODE=intra`.

`NORM_MODE=public` usa `NORM_SOURCE=open_psychometrics_2018` por padrão. Não interpretar como norma brasileira validada.

---

## 8. Devolutiva pessoal narrativa — `gemini_service.py`

**Modelo:** Gemini 1.5 Flash (`gemini-1.5-flash`), temperatura 0.3. Fallback local quando `GEMINI_API_KEY` ausente ou API indisponível.

**Seções obrigatórias (7):**
1. Resumo geral do perfil
2. Traços mais marcantes
3. Pontos fortes prováveis
4. Pontos de atenção
5. Sugestões práticas
6. Como usar esse resultado no dia a dia
7. Limites desta avaliação

**Regras anti-Barnum no prompt:**
- Linguagem de incerteza obrigatória: "suas respostas sugerem", "nesta aplicação apareceu", "pode indicar", "é possível que".
- Proibição de frases genéricas sem vínculo com dados numéricos.
- Cada interpretação deve citar pelo menos um escore ou IC95%.
- Jung é narrativa derivada — nunca tratado como medida independente.
- Seção de limites obrigatória.

**Dados passados ao prompt:**
- Nome da pessoa
- Big Five: escore, IC95%, bruto por fator
- Jung contínuo: tipo_resumo, eixos
- Estabilidade Emocional
- Qualidade da resposta (label)
- DISC e Spranger derivados
- Fricções de construtos detectadas
- Alertas telemétricos

---

## 9. Reflexões pessoais F9

A Sprint 14 adiciona duas respostas abertas opcionais, com no máximo 1000 caracteres cada: objetivo de autocompreensão e comportamento ou padrão que a pessoa quer observar nas próximas semanas.

Os campos são recebidos por `ReflectionSubmission`, persistidos em `personal_reflections` e vinculados ao `PsychometricResult` da aplicação. O endpoint `/results/me` os retorna em `reflections`.

Essas respostas são qualitativas e escritas pela própria pessoa. Não são enviadas ao `science_engine`, não geram classificação ou inferência clínica e não alteram Big Five, DISC, Jung, Spranger, percentis, normas ou histórico. O Dashboard e o relatório imprimível as apresentam em seção separada com aviso explícito.

Em produção, criar a tabela com `backend/schema/2026-06-19_personal_reflections.sql` antes de publicar a API correspondente, seguindo `backend/schema/README.md`. A migração usa `ON DELETE CASCADE`, checks de 1000 caracteres e transação explícita. `updated_at` foi omitido porque ainda não existe edição.

RLS não é habilitado atualmente. A aplicação não usa Supabase Auth nem acesso direto do frontend; a API FastAPI autentica com JWT próprio e consulta pelo usuário corrente. A migração revoga privilégios de `anon` e `authenticated`. Se essa arquitetura mudar, criar policies de leitura, inserção e atualização baseadas na propriedade de `psychometric_results` antes de expor a tabela.

---

## 10. Limites e usos vedados

**Limites documentados conforme o código:**

- Não é diagnóstico clínico, psiquiátrico ou médico.
- Não descreve características imutáveis.
- Jung, DISC e Spranger são camadas derivadas do Big Five — não são medidas independentes no fluxo atual.
- O modo atual de norma (`intra`) é régua interna, não percentil populacional.
- SEM usa confiabilidade provisória (0.84) — revisar quando houver dados reais suficientes.
- Mapeamentos DISC e Spranger têm pesos provisórios documentados como heurísticos.

**Usos vedados ou que exigem validação adicional:**

- Não usar isoladamente para decisões de admissão, desligamento, promoção ou outras decisões de alto impacto.
- Não usar como diagnóstico clínico.
- Não interpretar resultados como traços fixos.

**Amostra atual:** uso pessoal / desenvolvimento. Checagem empírica pessoal T1/T2 ainda pendente; isso não equivale a validação científica formal.

---

## 11. Changelog interno

- v0.4 — 2026-06-17 — Pós-commit `7bc0094`: baseline intra corrigido, `NORM_MODE=public` funcional, Jung borderline indefinido, DISC/Spranger derivados explicitados, suite 30/30 e 0 warnings.
- v0.4 — 2026-06-18 — Sprint 10: devolutiva pessoal narrativa reorganizada em sete seções humanas, sem alterar o motor psicométrico.
- v0.5 — 2026-06-19 — Sprint 14: perguntas reflexivas F9 por aplicação, separadas do motor; suíte 32/32 e build frontend OK.
- v0.6 — 2026-06-19 — Sprint 15: migração Supabase revisada, SQL/ORM alinhados, guia operacional e teste de contrato.
- v0.3 — 2026-06-13 — F3: documentação viva concluída. Referências cruzadas adicionadas. Seções de Alpha e relatório narrativo expandidas. Tabelas de DISC/Spranger/Jung com fórmulas reais do código.
- v0.2 — 2026-06-10 — F1 + F2 concluídas: Supabase Postgres em produção; 22/22 testes passando; conftest.py com fixture autouse; import órfão `calculate_cronbach_alpha` removido de `main.py`.
- v0.1 — 2026-06-05 — versão inicial: Big Five IPIP-50, itens de atenção, camadas derivadas, régua interna, confiabilidade, IC95%, qualidade de resposta, laudo anti-Barnum.
