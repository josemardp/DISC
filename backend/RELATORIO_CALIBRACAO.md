# Relatório de Calibração — ENTREGA 1

**Data:** 2026-06-21  
**Script:** `backend/qa_calibracao.py` (somente leitura — nenhum arquivo de produção alterado)  
**Versão do app:** v1.6.0  
**Grade varrida:** 11^5 = 161.051 pontos (cada fator Big Five de 0 a 100 em passos de 10)

---

## 1. Achados da Grade (i–iv)

### (i) Pares com correlação estrutural = 1,0 na grade

O script detectou **8 pares** com |corr| ≥ 0,999. Todos com corr = +1,000000 exato.

| Par | Fator Big Five comum | Explicação estrutural |
|-----|---------------------|----------------------|
| `DISC.C` ↔ `SPR.regulador` | C | Ambos mapeiam diretamente `bf["C"]` |
| `DISC.C` ↔ `JUNG.JP_J` | C | Ambos mapeiam diretamente `bf["C"]` |
| `SPR.teorico` ↔ `SPR.estetico` | O | Ambos mapeiam `aber = bf["O"]` — **valor idêntico** |
| `SPR.teorico` ↔ `JUNG.SN_N` | O | Ambos mapeiam `aber = bf["O"]` |
| `SPR.estetico` ↔ `JUNG.SN_N` | O | Ambos mapeiam `aber = bf["O"]` |
| `SPR.social` ↔ `JUNG.TF_F` | A | Ambos mapeiam `amab = bf["A"]` |
| `SPR.regulador` ↔ `JUNG.JP_J` | C | Ambos mapeiam `consc = bf["C"]` |
| `SPR.individualista` ↔ `JUNG.EI_E` | E | Ambos mapeiam `extr = bf["E"]` |

> **NOTA OBRIGATÓRIA — Natureza da correlação detectada:**  
> Esta correlação é **ESTRUTURAL da fórmula**, não correlação empírica entre pessoas.  
> A grade é uniforme (cada fator varia de 0 a 100 independentemente); não representa
> nenhuma amostra humana. O que o código faz é literalmente atribuir o **mesmo valor
> numérico** de um fator Big Five a duas dimensões diferentes de instrumentos distintos.
> Por exemplo, `SPR.teorico = round(aber, 2)` e `SPR.estetico = round(aber, 2)` — são
> a mesma expressão. A correlação = 1,0 é uma consequência algébrica, não um achado
> psicométrico sobre como pessoas reais se comportam. **Não interpretar como "essas
> dimensões andam juntas nas pessoas".**

### (ii) Casos contraintuitivos — Top-5 (E alto, D baixo)

A dimensão D (Dominância) é calculada como `D = (E + (100 − A)) / 2`. Quando Amabilidade
é alta, A eleva o denominador e reduz D, mesmo com Extroversão alta. Resultado: uma pessoa
com E=70 (alta Extroversão) e A=100 (máxima Amabilidade) recebe **D=35**, que é baixo.

| E | A | D derivado | Fórmula |
|---|---|------------|---------|
| 70 | 100 | **35,0** | (70 + 0) / 2 |
| 70 | 90  | **40,0** | (70 + 10) / 2 |
| 80 | 100 | **40,0** | (80 + 0) / 2 |
| 70 | 80  | **45,0** | (70 + 20) / 2 |
| 80 | 90  | **45,0** | (80 + 10) / 2 |

**Interpretação:** Esta é uma propriedade esperada do modelo heurístico (D reflete assertividade
sem empatia). Não é um bug, mas é um ponto de atenção ao comunicar resultados: um perfil
altamente extrovertido e altamente amável receberá D moderado-baixo, o que pode parecer
contraintuitivo a quem espera que "extroversão = dominância".

### (iii) Fração da grade em zona borderline Jung (≥ 1 eixo em 45–55)

```
Borderline Jung: 51.051 / 161.051 = 31,70%
```

Interpretação: a função `_borderline` (science_engine.py) define a zona indefinida
como 45 ≤ valor ≤ 55. Na grade uniforme em passos de 10, apenas o valor **50** cai nessa
faixa. A probabilidade de que **pelo menos 1** dos 4 eixos Jung (O, C, E, A) assuma o
valor 50 numa amostra uniforme discreta é 1 − (10/11)^4 ≈ 31,64%, condizente com o
resultado numérico de 31,70%. Em dados reais (distribuição contínua), a fração pode ser
diferente, dependendo de quão concentrada a população é próximo de cada centro.

> **Para um usuário real com apenas 2 respondentes (contexto do app),** é comum que
> eixos fiquem próximos do centro em medidas sucessivas — a zona borderline é um indicador
> de ausência de tendência definida, não de "erro" de medida.

### (iv) Escores fora de [0, 100] ou NaN/erro

```
Out-of-range : 0 eventos
NaN/Erros    : 0 eventos
```

**Todas as 161.051 combinações** produziram escores dentro do intervalo [0, 100] sem
exceções ou erros de runtime. As funções `derive_disc_from_big_five`,
`derive_jung_from_big_five` e `derive_spranger_from_big_five` são numericamente estáveis
para todos os inputs 0–100.

---

## 2. Sanity-check de Percentil (1.d)

Fonte testada: `open_psychometrics_2018` (n = 603.322).  
Função testada: `percentil_por_norma(raw, mean, sd)` de `science_engine.py`.

| Fator | µ | σ | pct(µ) esperado ~50 | pct(µ+σ) esperado ~84 | pct(µ−σ) esperado ~16 | OK? |
|-------|---|---|---------------------|----------------------|----------------------|-----|
| O | 39,3888 | 6,1826 | 50,00 | 84,13 | 15,87 | SIM |
| C | 33,4256 | 7,3905 | 50,00 | 84,13 | 15,87 | SIM |
| E | 29,1382 | 9,1123 | 50,00 | 84,13 | 15,87 | SIM |
| A | 37,5891 | 7,3633 | 50,00 | 84,13 | 15,87 | SIM |
| N | 30,8132 | 8,6068 | 50,00 | 84,13 | 15,87 | SIM |

**Resultado: SIM — `percentil_por_norma` reproduz os pontos esperados da norma com
precisão de ≥ 2 casas decimais.** A implementação via z-score + Phi(Z) está correta;
a média da norma retorna exatamente percentil 50, e ±1 DP retorna 84,13/15,87
(valores teóricos da distribuição normal padrão).

---

## 3. Status dos Bugs Conhecidos

### Bug A — Ômega sem recodificar reversos

**Status: CONFIRMADO**

**Localização:** `backend/app/main.py`, rota `/admin/stats`, linhas 1243–1248:

```python
# main.py  linhas 1243-1248
for r in factor_rows:
    matrix[user_to_idx[r.respondent_id]][item_to_idx[r.item_id]] = r.value
omega_value = mcdonald_omega(matrix)
```

**Problema:** A variável `r.value` contém o valor Likert bruto (1–5) tal como gravado
no banco, sem aplicar a inversão dos itens reversos (`reverse_keyed = True`). A função
`score_big_five` em `science_engine.py` aplica `_aplica_reverso` antes de computar
os escores, mas a rota `/admin/stats` não o faz antes de montar a matriz de correlações.

**Impacto:** A matriz de correlações passada para `mcdonald_omega` inclui itens misturados
em direções opostas (alguns keyed +, outros keyed −). Isso infla a variância de erro e
**subestima sistematicamente** o ômega de cada fator. Com 18 itens reversos nos 50 itens
IPIP-50 (5 em E, 4 em A, 4 em C, 2 em N, 3 em O), o efeito pode ser substancial.

**Prova estrutural:**
```python
# seed_big_five_ipip.py — contagem de reverse_keyed=True por fator
# E: 5 reversos  (itens "Não falo muito", "Fico em segundo plano", ...)
# A: 4 reversos  (itens "Sinto pouca preocupação", "Insulto as pessoas", ...)
# C: 4 reversos  (itens "Deixo minhas coisas espalhadas", ...)
# N: 2 reversos  (itens "Fico relaxado", "Raramente fico para baixo")
# O: 3 reversos  (itens "Dificuldade em entender ideias abstratas", ...)
# Total: 18 itens reversos de 50
```

---

### Bug B — IC95% usando reliability=0,84 fixo

**Status: CONFIRMADO**

**Localização 1:** `backend/app/main.py`, rota `/results/me`, linha 860:

```python
# main.py  linha 860  (rota GET /results/me)
sem = standard_error_of_measurement(sd=15.0, reliability=0.84)
```

**Localização 2:** `backend/app/main.py`, rota `/results/report`, linha 1022:

```python
# main.py  linha 1022  (rota GET /results/report)
sem = standard_error_of_measurement(sd=15.0, reliability=0.84)
```

**Problema:** Ambas as rotas usam `reliability=0.84` fixo, ignorando o ômega medido
(calculado em `/admin/stats`). O valor 0,84 é um parâmetro arbitrário não derivado dos
dados reais. Além disso, a resposta da API não inclui um campo `reliability_source`
indicando qual confiabilidade foi usada para calcular o SEM — o usuário não tem como
saber se o IC95% usa o ômega real ou um default fixo.

**Nota sobre `sd=15.0`:** O escore sendo estimado é um percentil (0–100). O parâmetro
`sd=15.0` trata percentis como se fossem escores numa escala com DP ≈ 15 (similar a
T-scores ou QI). Para N pequeno (2 usuários) no modo `intra`, percentis são posições
relativas ao próprio histórico — usar `sd=15` como proxy é razoável como default, mas
a `reliability` deveria refletir os dados reais de consistência interna.

---

### Bug C — Semântica do irt_avg: bloco vs. item

**Status: CONFIRMADO**

**O que o front envia (bloco):**

`frontend/src/utils/telemetry.ts`, linhas 47–60:
```typescript
// telemetry.ts  linhas 47-60
endBlock(blockNumber: number) {
    if (this.activeBlock !== blockNumber) return;
    const now = Date.now();
    this.blocksData[blockNumber] = {
      blockNumber,
      startTime: this.blockStartTime,
      firstClickTime: this.firstClickTime,
      endTime: now - this.blockStartTime,   // <-- duração TOTAL do bloco em ms
      rviCount: this.rviCount,
      clicks: [...this.clicks]
    };
```

`telemetry.ts`, linhas 78–81 (`getSummary`):
```typescript
// telemetry.ts  linhas 78-81
if (b.endTime !== null) {
    totalIrt += b.endTime;   // soma de durações de BLOCOs
}
// ...
irtAvg: Math.round(totalIrt / list.length),  // média por BLOCO, não por item
```

**O que o back testa (como se fosse por item):**

`backend/app/main.py`, linhas 409–411:
```python
# main.py  linhas 409-411
if submission.irt_avg < 800:
    is_fraud = True
    reasons.append("LinearResponsePattern: Velocidade de clique excessiva (< 800ms por item).")
```

**O mesmo threshold em `science_engine.py`, linha 317:**
```python
# science_engine.py  linha 317
muito_rapido = bool(irt_avg_ms < 800)
```

**Inconsistência:** O campo `irt_avg` contém a duração média por **BLOCO** (do início
do bloco até o respondente finalizar todas as escolhas daquele bloco), mas o comentário
e o limiar dizem "< 800ms **por item**". Para o Big Five IPIP-50 (cada bloco tem
exatamente 1 item Likert), bloco ≈ item e o efeito prático é pequeno. Para testes
com blocos multi-item (ex.: DISC no formato forçado-escolha, onde cada bloco tem 4
adjetivos), o `irt_avg` seria a média de tempo por bloco de 4 itens — comparar com
800ms "por item" seria absurdo. A variável está bem nomeada em outros contextos
mas o comentário e a semântica do limiar estão errados.

---

## 4. Recomendações por Categoria

### "Bug objetivo → corrigir na Entrega 2"

| # | Bug | Ação |
|---|-----|------|
| A | Ômega sem reversos | Na rota `/admin/stats`, fazer JOIN com `QuestionnaireItem` para ler `reverse_keyed`, e aplicar a mesma lógica de `_aplica_reverso` de `score_big_five` antes de montar a matriz para `mcdonald_omega`. |
| B | IC95% com reliability fixo | Usar o ômega por fator quando disponível (calculado em `/admin/stats`). Adicionar campo `reliability_source` na resposta para indicar se usou o ômega medido ou o default 0,84. Mantendo `sd=15.0` como aproximação razoável. |
| C | irt_avg: bloco vs. item | **Descrição da mudança proposta (requer aprovação antes de implementar):** ver seção 4.1 abaixo. |

#### 4.1 Bug C — Descrição da mudança proposta (AGUARDANDO OK antes de implementar)

**O que o front envia hoje:**
- Campo: `irt_avg` (float, ms)
- Unidade: milissegundos médios por **bloco** (soma das `endTime` dos blocos ÷ número de blocos)
- Cálculo: `irtAvg = Math.round(totalIrt / list.length)` em `getSummary()`

**O que o back espera hoje:**
- Campo: `irt_avg` (float, ms)
- O código testa `irt_avg < 800` e chama de "velocidade por item"
- O comentário diz "< 800ms por item", mas o valor é por bloco

**Mudança proposta:**
- **Opção 1 (mudança só no back):** Corrigir o limiar e o comentário para refletir que
  é por bloco. Para Big Five (1 item/bloco) o limiar 800 ms é razoável. Renomear o campo
  no comentário para deixar claro que é por bloco. Ajustar o limiar para ≥ 800 ms × N_itens_por_bloco
  se no futuro houver blocos multi-item.
- **Opção 2 (mudança no front + back):** O front passa dois campos separados:
  `irt_avg_per_block` (atual) e `irt_avg_per_item` (calculado dividindo por número de
  itens do bloco). O back usa `irt_avg_per_item` para o limiar de "velocidade por item".

Para o caso atual (Big Five com 1 item/bloco), ambas as opções produzem o mesmo resultado
prático. A Opção 1 tem escopo mínimo e menor risco. **PARE — aguardando aprovação do
Josemar antes de implementar.**

### "Decisão de modelagem → Josemar decide"

| Achado | Descrição |
|--------|-----------|
| SPR.teorico = SPR.estetico | As duas dimensões Spranger usam `aber = bf["O"]` (o fator O), produzindo valores sempre idênticos. O `estetico` está marcado como `[provisório]` sem fórmula própria. Redefinir o fator mapeado para `estetico` (ex.: poderia ser N invertido = Estabilidade Emocional, ou uma combinação) é uma decisão de modelagem, não um bug de código. |
| DISC.C = SPR.regulador = JUNG.JP_J | Três dimensões de três instrumentos distintos mapeiam para o mesmo fator `bf["C"]`. Isto está documentado como `[provisório]` mas pode ser confuso em relatórios se o usuário vê três "leituras independentes" que são numericamente idênticas. Josemar decide se prefere diferenciá-los ou documentar explicitamente que são leituras do mesmo construto. |
| D = f(E, A) sem peso de N | Dominância não usa Neuroticismo; uma pessoa com alto estresse (N=100) pode receber D alto se E e A o justificarem. Isto é uma escolha heurística explicitada como `[provisório]`. |

---

## 5. Resumo Executivo

```
Grade: 161.051 pontos varridos (11^5)
Out-of-range / NaN: NENHUM — funções numericamente estáveis
Pares corr ≥ 0.999 : 8 (todos estruturais, ver nota acima)
Borderline Jung    : 31,70% da grade (esperado analiticamente: 31,64%)
Sanity percentil   : OK — pct(µ) = 50,00; pct(µ+σ) = 84,13; pct(µ-σ) = 15,87

Bug A (Omega sem reversos) : CONFIRMADO — main.py:1247
Bug B (IC95% reliability fixo): CONFIRMADO — main.py:860 e main.py:1022
Bug C (irt_avg bloco vs item) : CONFIRMADO — telemetry.ts:55 + main.py:409
```

---

*Gerado por `backend/qa_calibracao.py` — leitura do código + varredura de grade.*  
*Nenhum arquivo de produção foi alterado. Suíte de testes não foi executada aqui.*
