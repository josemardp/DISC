# Protocolo de Validação — Big Five IPIP-50

> Documento criado na F5 e atualizado na Sprint 9. Ver [ROADMAP.md](ROADMAP.md) | [DECISOES.md](DECISOES.md)

---

## 1. Objetivo

Estimar, de forma exploratória e pessoal, a estabilidade teste-reteste do Big Five IPIP-50 com os dois respondentes disponíveis: **Josemar** e **Esdra**.

A confiabilidade teste-reteste mede a estabilidade dos escores ao longo do tempo. Nesta fase, isso **não** constitui validação científica formal nem transforma o sistema em teste psicológico validado; serve apenas como checagem de estabilidade para uso pessoal.

---

## 2. Participantes

| Respondente | Papel | Conta no sistema |
|---|---|---|
| Josemar | Respondente 1 | cadastrado em produção |
| Esdra | Respondente 2 | cadastrar antes da 1ª aplicação |

**Tamanho de amostra:** N = 2. Este tamanho não é adequado para análise estatística formal — o objetivo desta fase é validar o funcionamento do instrumento e da infraestrutura, e coletar os primeiros dados reais. Ver Seção 5 sobre CFA.

---

## 3. Intervalo entre aplicações

**Recomendado: 2 a 4 semanas.**

- Intervalo menor: aumenta risco de efeito de memória (o respondente lembra das respostas anteriores e as repete, inflando a correlação artificialmente).
- Intervalo maior: aumenta risco de mudança real no construto (a pessoa mudou de fato, e não o instrumento que falhou).

Registre a data exata de cada aplicação para calcular o intervalo real.

---

## 4. Procedimento passo a passo

### 4.1 Aplicação 1 (T1)

1. Cada respondente acessa o sistema em produção (Vercel) e faz login.
2. Responde o questionário Big Five completo (50 itens IPIP + 3 itens de atenção).
3. Registre a data da aplicação.

### 4.2 Exportação dos dados de T1

Execute o endpoint de exportação via `curl` ou cliente HTTP autenticado com role `admin`:

```bash
curl -H "Authorization: Bearer <token_admin>" \
     https://<seu-dominio-vercel>/admin/export/bigfive \
     -o bigfive_T1.csv
```

O CSV contém: `respondent_id`, `applied_at`, `O_raw`, `C_raw`, `E_raw`, `A_raw`, `N_raw`, `O_pct`, `C_pct`, `E_pct`, `A_pct`, `N_pct`, `quality_label`.

### 4.3 Aplicação 2 (T2) — após 2–4 semanas

Repita o procedimento da Aplicação 1. O endpoint `/questionnaire/submit` substitui as respostas atuais do mesmo teste/fase, mas o resultado Big Five processado é preservado em histórico append-only para permitir comparação entre aplicações.

### 4.4 Exportação dos dados de T2

```bash
curl -H "Authorization: Bearer <token_admin>" \
     https://<seu-dominio-vercel>/admin/export/bigfive \
     -o bigfive_T2.csv
```

### 4.5 Cálculo da confiabilidade teste-reteste

Carregue os dois CSVs e monte as listas de entrada para `test_retest_reliability()`:

```python
import csv
from backend.app.validacao import test_retest_reliability

def carregar_escores_raw(caminho_csv):
    """Converte o CSV exportado para lista de dicts por fator."""
    entradas = []
    with open(caminho_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            for fator in ["O", "C", "E", "A", "N"]:
                entradas.append({
                    "fator": fator,
                    "escore_raw": float(row[f"{fator}_raw"])
                })
    return entradas

aplicacao_t1 = carregar_escores_raw("bigfive_T1.csv")
aplicacao_t2 = carregar_escores_raw("bigfive_T2.csv")

resultado = test_retest_reliability(aplicacao_t1, aplicacao_t2)
print(resultado)
# {"O": 0.95, "C": 0.88, "E": 0.91, "A": 0.87, "N": 0.82}  # exemplo fictício
```

**Nota:** `test_retest_reliability()` recebe listas de escores item-a-item por fator. Como o CSV exporta apenas escores brutos por fator (não item-a-item), a correlação acima é calculada fator-a-fator entre as duas aplicações dos respondentes. Com N=2, o resultado é indicativo, não conclusivo.

---

## 5. Critério de confiabilidade aceitável

**r ≥ 0,80 por fator** (Kline, 2000).

| Valor de r | Interpretação |
|---|---|
| r ≥ 0,90 | Excelente |
| 0,80 ≤ r < 0,90 | Adequado (mínimo aceitável) |
| 0,70 ≤ r < 0,80 | Moderado — interpretar com cautela |
| r < 0,70 | Insuficiente — revisar o instrumento ou o protocolo |

> **Referência:** Kline, R. B. (2000). *Principles and practice of structural equation modeling*. Guilford Press.

Com N = 2 respondentes, o coeficiente de Pearson não tem poder estatístico adequado para inferência formal. Os valores devem ser interpretados como indicadores exploratórios, não como evidência de validação.

---

## 6. Nota sobre Análise Fatorial Confirmatória (CFA)

A Análise Fatorial Confirmatória (CFA) é o método padrão para verificar se os 50 itens IPIP realmente se organizam nos 5 fatores esperados (O, C, E, A, N). No entanto:

- **Tamanho de amostra mínimo recomendado:** N ≥ 200 (Hu & Bentler, 1999).
- **Com N = 2:** inviável. O modelo não converge e os índices de ajuste não são interpretáveis.

A CFA fica registrada como **meta futura distante**, apenas se o projeto deixar de ser app pessoal e houver dados de pelo menos 200 respondentes.

> **Referência:** Hu, L., & Bentler, P. M. (1999). Cutoff criteria for fit indexes in covariance structure analysis. *Structural Equation Modeling*, 6(1), 1–55.

Para implementação de CFA quando houver N suficiente, ver `PLANO_EVOLUCAO_DISC_v2.md` § 4 (PROMPT F5 — validação com dados reais).

---

## 7. Aviso — dados psicológicos sensíveis

- Os dados exportados contêm escores psicométricos individuais — **informação sensível**.
- Armazene os arquivos CSV apenas localmente ou em locais seguros sob controle do responsável.
- **Nunca compartilhe ou publique** os arquivos exportados sem consentimento explícito dos respondentes.
- O banco de dados de produção (Supabase) já é privado por configuração — não altere as permissões de acesso.
- Credenciais de acesso (`DATABASE_URL`, tokens) devem permanecer apenas em `Drive/segredos/disc-env.txt` e nas variáveis de ambiente do Vercel (ver `REGRA_MESTRE_SYNC.md`).
