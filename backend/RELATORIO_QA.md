# Relatorio de QA - Evolucao Cientifica

Data: 2026-06-05
Branch: evolucao-cientifica

## O que foi testado

1. Teste-reteste simulado usando `score_big_five()`.
2. Validade convergente interna usando `derive_jung_from_big_five()`.
3. Fluxo e2e via HTTP: cadastro, login, busca de itens BIGFIVE, submissao BIGFIVE, `/results/me` e `/results/report`.
4. Suite automatizada completa com `python -m pytest backend/app/ -v`.

## Resultados reais

### 1. Teste-reteste simulado

Foram criadas duas aplicacoes quase identicas para um respondente ficticio, com variacao de +/-1 ponto em 5 itens.

- Fatores avaliados: `["O", "C", "E", "A", "N"]`
- Aplicacao 1, escores brutos: `[38.0, 34.0, 30.0, 28.0, 24.0]`
- Aplicacao 2, escores brutos: `[37.0, 33.0, 30.0, 29.0, 24.0]`
- Itens alterados por indice na lista IPIP-50: `[1, 8, 17, 29, 44]`
- Correlacao de Pearson entre os 5 fatores das duas aplicacoes: `0.992957`
- Criterio `>= 0.90`: atendido.

### 2. Validade convergente interna

Entrada sintetica usada:

```python
{"E": 85.0, "O": 90.0, "A": 20.0, "C": 80.0, "N": 15.0}
```

Saida real de `derive_jung_from_big_five()`:

- `tipo_resumo`: `ENTJ`
- `E_I`: `E=85.0`, `I=15.0`, `borderline=False`
- `S_N`: `N=90.0`, `S=10.0`, `borderline=False`
- `T_F`: `F=20.0`, `T=80.0`, `borderline=False`
- `J_P`: `J=80.0`, `P=20.0`, `borderline=False`
- `estabilidade_emocional`: `85.0`

Alinhamento verificado:

- E/I acompanha Extroversao: `True`
- S/N acompanha Abertura: `True`
- T/F acompanha Amabilidade: `True`
- J/P acompanha Conscienciosidade: `True`

### 3. Teste e2e completo via HTTP

Usuario criado no teste: `qa-final-92e287f491@example.com`

Status HTTP reais:

- `POST /auth/register`: `200`
- `POST /auth/token`: `200`
- `GET /questionnaire/items?test_type=BIGFIVE`: `200`
- `POST /questionnaire/submit`: `200`
- `GET /results/me`: `200`
- `GET /results/report`: `200`

Resumo real do fluxo:

- Itens submetidos: `53` (`50` Big Five + `3` attention_check)
- Resposta de submissao: `{"status": "success", "all_completed": true}`
- `/results/me` retornou fatores: `["A", "C", "E", "N", "O"]`
- Todos os 5 fatores tinham `ci_low` e `ci_high`: `True`
- `jung_continuo` presente: `True`
- `quality_label`: `alta`
- `/results/report` continha `### Limites desta avaliação`: `True`
- Primeiro titulo do laudo: `### Resumo Executivo com Incerteza`

Primeiras linhas retornadas pelo laudo:

```md
### Resumo Executivo com Incerteza
Os dados de **QA Final** indicam um perfil Big Five descrito por escores com incerteza explícita. A leitura tende a ser mais útil quando cada fator é interpretado junto do seu intervalo de confiança e da qualidade da resposta, registrada como **alta**. Quando algum dado estiver ausente, a conclusão correspondente deve ser tratada como sem dados suficientes.
### Big Five medido com intervalos de confiança
- **Abertura (O)**: escore 50.0, IC95% [38.24, 61.76], bruto 34.0.
- **Conscienciosidade (C)**: escore 50.0, IC95% [38.24, 61.76], bruto 34.0.
```

### 4. Suite automatizada

Comando executado:

```powershell
python -m pytest backend/app/ -v
```

Resultado real:

- Testes coletados: `22`
- Passes: `22`
- Falhas: `0`
- Warnings: `117`
- Tempo reportado: `1.36s`

## Pontos que ainda precisam de atencao humana

- Validacao empirica com pessoas reais: teste-reteste real, estabilidade temporal e revisao qualitativa de devolutivas.
- Norma publica: `NORM_MODE=public` permanece bloqueado ate existir fonte publica versionada e documentada.
- Amostra atual: uso familiar / desenvolvimento; ainda nao ha calibracao populacional propria.
- Confiabilidade operacional: o SEM usa confiabilidade provisoria `0.84`; revisar quando houver dados reais suficientes.
- Revisao psicometrica do mapeamento derivado DISC/Spranger: o codigo declara esses pesos como provisórios e ilustrativos.
- Prompt 8 / TIRT: avaliar somente se houver decisao de manter escolha forcada DISC e amostra suficiente para estimacao.
- Warnings tecnicos da suite: migrar `declarative_base()` para API SQLAlchemy 2, substituir `on_event` por lifespan no FastAPI e planejar migracao do pacote Gemini depreciado.

## Conclusao

Os criterios de QA solicitados foram atendidos nesta execucao: teste-reteste simulado com Pearson `0.992957`, convergencia interna alinhada, e2e HTTP completo com todos os endpoints retornando `200`, laudo com secao de limites presente e suite automatizada com `22` passes e `0` falhas.
