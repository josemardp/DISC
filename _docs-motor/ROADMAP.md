# ROADMAP - Fases do projeto DISC

> Fonte de orientacao do ciclo atual. Ultima atualizacao: 2026-06-17, pos-commit `7bc0094`.
> Direcao atual: sair da correcao tecnica do motor e entrar na fase de experiencia pessoal.

---

## Estado atual oficial

| Area | Estado |
|---|---|
| Backend | 30 testes passando, 0 warnings no pytest |
| Frontend | build OK |
| Pendencia tecnica menor | chunk `charts`/Recharts > 500 kB, isolado no Dashboard |
| Escopo | aplicativo pessoal de autoconhecimento |
| Uso vedado | diagnostico, laudo psicologico, avaliacao psicologica profissional, selecao profissional |

Nucleo psicometrico estabilizado para uso pessoal:
- Big Five/IPIP-50 medido diretamente.
- `NORM_MODE=intra` cria baseline na primeira aplicacao e nao mostra percentil 50 enganoso.
- `NORM_MODE=public` funcional com norma publica exploratoria `open_psychometrics_2018`.
- Jung e derivado exploratorio e pode retornar `indefinido` em zona borderline.
- DISC e Spranger sao derivados heuristicos/ilustrativos.

---

## Fases concluidas

| Fase | Tema | Status |
|---|---|---|
| F1 | Persistencia Postgres/Supabase e deploy Vercel | Concluida |
| F2 | Suite verde e higiene inicial | Concluida historicamente |
| F3 | Documentacao viva inicial | Concluida historicamente |
| F4 | Norma publica versionada | Concluida e revisada em `7bc0094` |
| F5 | Infraestrutura de validacao/exportacao | Concluida; T1/T2 real pendente |
| F6 | Spranger como camada ilustrativa | Concluida |
| F7 | Higiene tecnica de deprecacoes | Concluida e revisada em `7bc0094` |
| Sprint tecnica 2026-06-17 | Baseline intra, Jung indefinido, API hardening, seguranca e layout | Concluida em `7bc0094` |

Historicos como 22/22, 25/25 ou 26/26 pertencem a fases antigas. O estado atual e 30/30 testes passando.

---

## Proxima fase oficial

## Sprint 9 - Sincronizacao documental, QA manual e preparacao da experiencia pessoal

### 9.1 - Sincronizacao documental pos-commit 7bc0094

Objetivo: manter README, CHANGELOG, STATUS, ROADMAP, QA e contexto de retomada coerentes com o estado real.

### 9.2 - QA manual completo da interface

Checklist:
1. Criar usuario novo.
2. Fazer primeira aplicacao.
3. Confirmar que aparece "linha de base interna" no modo intra.
4. Confirmar que nao aparece percentil 50 enganoso na primeira aplicacao.
5. Refazer teste.
6. Confirmar comparacao intraindividual na segunda aplicacao.
7. Verificar Jung borderline como indefinido.
8. Verificar aviso de DISC derivado.
9. Verificar aviso de Spranger derivado.
10. Testar responsividade no celular.
11. Verificar relatorio textual.
12. Confirmar que a devolutiva nao parece laudo psicologico.
13. Confirmar que erros nao aparecem de forma feia para o usuario.

### 9.3 - Melhorar devolutiva textual/humana

Estrutura desejada:
1. Visao geral do perfil.
2. Tracos mais marcantes.
3. Pontos fortes provaveis.
4. Pontos de atencao.
5. Sugestoes praticas.
6. Como usar o resultado no dia a dia.
7. Limites da avaliacao.

### 9.4 - Historico visual entre aplicacoes

Evolucao natural do `NORM_MODE=intra`:
1. Lista de aplicacoes anteriores.
2. Data de cada aplicacao.
3. Comparacao entre T1, T2, T3.
4. Variacao dos fatores Big Five.
5. Aviso de que pequenas mudancas podem refletir contexto, humor, cansaco ou forma de responder.

### 9.5 - Exportacao de relatorio em PDF

Conteudo esperado:
1. Capa.
2. Data da aplicacao.
3. Aviso de nao diagnostico.
4. Big Five.
5. DISC derivado.
6. Jung exploratorio.
7. Spranger derivado.
8. Pontos fortes.
9. Pontos de atencao.
10. Historico, se houver.

### 9.6 - Validacao empirica pessoal T1/T2

Procedimento:
1. Josemar responde T1.
2. Esdra responde T1.
3. Esperar 2-4 semanas.
4. Josemar responde T2.
5. Esdra responde T2.
6. Exportar CSV.
7. Rodar analise test-retest.
8. Interpretar estabilidade com cuidado.

Isso nao torna o sistema um teste psicologico validado. E apenas uma checagem de estabilidade para uso pessoal.

### 9.7 - F9: camada de autoconhecimento com perguntas/reflexoes

Regras:
1. Perguntas abertas/reflexivas nao entram no motor de pontuacao.
2. Perguntas abertas podem alimentar apenas a devolutiva textual/reflexiva.
3. Nao misturar resposta biografica com escore psicometrico.
4. Nao transformar IA em psicologa, diagnostico ou laudo.

---

## Pendencias reais

Tecnicas:
- Chunk `charts`/Recharts > 500 kB.
- Alembic/migrations formais se o app virar produto ou se o schema evoluir muito.

Escopo/produto:
- LGPD completa fora do escopo atual; reavaliar se virar produto comercial/corporativo/RH.
- RH corporativo e dashboard de equipe fora de prioridade.

Metodologicas:
- T1/T2 pessoal ainda nao executado.
- Norma publica e exploratoria, nao populacao brasileira validada.

---

## O que nao priorizar agora

1. TIRT/F8.
2. RH corporativo.
3. Dashboard de equipe.
4. Ranking de pessoas.
5. Selecao profissional.
6. LGPD completa.
7. Produto comercial.
8. Alteracao profunda do motor psicometrico.
9. Promessa de validacao CFP/SATEPSI.
10. Laudo psicologico ou diagnostico.

Regra de ouro: nao mexer profundamente no motor agora. O foco e experiencia, QA manual, historico, relatorio e clareza documental.
