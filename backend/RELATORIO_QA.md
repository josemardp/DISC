# Relatorio de QA - Evolucao Cientifica

Data inicial: 2026-06-05
Branch: evolucao-cientifica

> Nota de sincronização: as seções antigas abaixo ficam como histórico. O estado atual oficial, pós-commit `7bc0094`, é: backend 30 testes passando, 0 warnings no pytest, frontend build OK, `NORM_MODE=public` funcional e pendência menor no chunk `charts`/Recharts.

## Atualizacao QA - Sprint 11 - 2026-06-18

- `/results/me` agora expõe `history` com aplicações Big Five em ordem cronológica.
- A primeira aplicação permanece como linha de base interna quando `NORM_MODE=intra`, sem percentil interpretável.
- A tela de resultados exibe histórico de aplicações e comparação simples com a aplicação anterior.
- A comparação usa resultados brutos Big Five e avisa que pequenas mudanças podem refletir contexto, humor, cansaço ou forma de responder.
- Motor psicométrico, cálculos, normas, autenticação e segurança não foram alterados nesta sprint.

## Atualizacao QA - Sprint 10 - 2026-06-18

- Devolutiva de resultados reorganizada para uso pessoal: resumo geral, tracos marcantes, pontos fortes provaveis, pontos de atencao, sugestoes praticas, uso no dia a dia e limites.
- Big Five ganhou explicacoes simples por fator na UI.
- Jung, DISC e Spranger continuam rotulados como derivados/exploratorios.
- Aviso de nao diagnostico, nao laudo e nao avaliacao psicologica profissional preservado.
- Motor psicometrico, calculos, normas, autenticacao e seguranca nao foram alterados nesta sprint.

## Atualizacao QA - 2026-06-17

### Estado inicial medido nesta rodada

- Repositorio real: `C:\projetos\autoconhecimento\1-disc-app` (o diretorio pai nao e repo Git).
- Build frontend inicial: passou, mas com aviso de bundle `assets/index-*.js` maior que 500 kB.
- Pytest inicial: 26 testes coletados, 0 passando, 26 erros de setup, 2 warnings. Causa: banco SQLite local antigo sem a coluna `questionnaire_items.reverse_keyed`.
- `NORM_MODE` atual: `intra`.
- Arquivo normativo existente: `backend/app/norms_ipip_neo.json`, com `_meta` e fonte `open_psychometrics_2018`, escala bruta 10-50 por fator.
- Big Five calculado em `backend/app/science_engine.py::score_big_five()` e escalado em `backend/app/main.py::_bigfive_scaled_scores()`.
- Big Five renderizado em `frontend/src/components/Dashboards.tsx`.
- Jung/DISC/Spranger derivados em `backend/app/science_engine.py`.
- Relatorio narrativo gerado em `backend/app/gemini_service.py::generate_psychometric_report()`.

### Correcoes implementadas

- Testes agora usam SQLite em memoria (`sqlite:///:memory:`), isolado do banco local antigo.
- SQLAlchemy migrou de `declarative_base()` para `DeclarativeBase`.
- Google GenAI passou a ser importado sob demanda, evitando warning de SDK durante testes sem chave.
- Primeira aplicacao em `NORM_MODE=intra` retorna baseline interna, sem percentil interpretavel (`percentile: null`) e com metadados `is_first_assessment`, `has_intraindividual_history`, `interpretation_confidence`, `warnings` e `norm_label`.
- `NORM_MODE=public` usa `backend/app/norms_ipip_neo.json`, fonte `open_psychometrics_2018`, com `raw_to_percentile()` na escala bruta 10-50.
- Jung borderline majoritario retorna `tipo_resumo="indefinido"` e `tipo_fechado=false`.
- DISC e Spranger aparecem como derivados heurísticos, nao instrumentos independentes.
- Endpoint `/questionnaire/submit` valida `test_type`, `phase`, escala de `value`, `item_id`, duplicidade, itens ausentes, bloco incompatível e campos extras.
- Campo opcional de perfil nao promove usuario para `hr`; fica como `respondent`.
- Producao exige `SECRET_KEY` segura e `ALLOWED_ORIGINS`; wildcard CORS, seed demo e criacao automatica de schema ficam restritos fora de producao.
- Layout Big Five separa nome/score, barra e metadados em linhas proprias.
- Code splitting com `React.lazy()` para `Dashboards` e `TestRoom`; chunk grande restante fica isolado em `recharts`.

### Historico append-only

O delete em `process_psychometric_results()` continua restrito a `PsychometricResult.bigfive_percentis.is_(None)`. Ele remove apenas registros consolidados/legados sem Big Five, e preserva historico Big Five valido. O teste `test_delete_consolidado_preserva_bigfive` protege esse comportamento.

### Estado final medido

- Backend: `python -m pytest backend/app/ -v` -> 30 passed, 0 failed, 0 warnings.
- Frontend: `npm run build` -> build OK. Aviso residual: chunk `charts-*.js` maior que 500 kB, isolado em carregamento de Dashboard/Recharts.

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
- Resolvido em `7bc0094`: `NORM_MODE=public` está funcional com a fonte pública exploratória `open_psychometrics_2018` em `backend/app/norms_ipip_neo.json`.
- Amostra atual: uso familiar / desenvolvimento; ainda nao ha calibracao populacional propria.
- Confiabilidade operacional: o SEM usa confiabilidade provisoria `0.84`; revisar quando houver dados reais suficientes.
- Revisao psicometrica do mapeamento derivado DISC/Spranger: o codigo declara esses pesos como provisórios e ilustrativos.
- TIRT/F8: não priorizar agora. Só reavaliar se houver decisão futura de reativar escolha forçada DISC e amostra suficiente.
- Warnings tecnicos da suite: migrar `declarative_base()` para API SQLAlchemy 2, substituir `on_event` por lifespan no FastAPI e planejar migracao do pacote Gemini depreciado.

## Conclusao

Os criterios de QA solicitados foram atendidos nesta execucao: teste-reteste simulado com Pearson `0.992957`, convergencia interna alinhada, e2e HTTP completo com todos os endpoints retornando `200`, laudo com secao de limites presente e suite automatizada com `22` passes e `0` falhas.
