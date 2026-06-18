# Contexto DISC - proximo chat

> Retomada oficial pos-commits `7bc0094` (`fix(psychometrics): corrige normas e resultados derivados`), `76373d4` (`ux(copy): ajusta linguagem para app pessoal`), Sprint 10 de devolutiva pessoal e Sprint 11 de historico visual.
> Projeto atual: aplicativo pessoal de autoconhecimento. Nao e produto comercial, nao e RH em producao, nao e diagnostico, nao e laudo psicologico e nao e avaliacao psicologica profissional.

---

## Estado atual

Backend:
- `python -m pytest backend/app/ -v`: 30 testes passando.
- Warnings documentados no pytest: 0.

Frontend:
- `npm run build`: OK.
- Pendencia menor: chunk `charts`/Recharts > 500 kB, isolado no Dashboard.
- Devolutiva pessoal estruturada em resumo, tracos marcantes, pontos fortes, pontos de atencao, sugestoes praticas, uso no dia a dia e limites.
- Historico visual entre aplicacoes Big Five disponivel na tela de resultados.

Psicometria:
- Big Five/IPIP-50 e o nucleo medido diretamente.
- `NORM_MODE=intra`: primeira aplicacao cria linha de base interna; nao exibe percentil 50 enganoso.
- `NORM_MODE=public`: funcional com norma publica exploratoria `open_psychometrics_2018` em escala bruta 10-50.
- Jung e derivado exploratorio do Big Five e retorna `indefinido` quando a maioria dos eixos esta borderline.
- DISC e Spranger sao derivados heuristicos/ilustrativos do Big Five.

Escopo:
- App pessoal de autoconhecimento.
- LGPD completa fora do escopo atual; volta apenas se virar produto comercial/corporativo/RH.
- RH corporativo, ranking de pessoas e selecao profissional nao sao prioridade.

---

## O que ja foi corrigido

1. Primeira aplicacao em `NORM_MODE=intra` deixou de ser interpretada como percentil 50.
2. Baseline intraindividual passou a retornar metadados claros.
3. `NORM_MODE=public` usa `norms_ipip_neo.json` e a fonte `open_psychometrics_2018`.
4. Jung borderline majoritario retorna `indefinido`, sem tipo fechado.
5. DISC e Spranger foram rotulados como derivados/heuristicos.
6. Layout Big Five separa nome, bruto/media e barra.
7. `/questionnaire/submit` valida payload com rigor.
8. Producao exige `SECRET_KEY` segura e `ALLOWED_ORIGINS`.
9. CORS wildcard, seed demo e schema automatico ficam bloqueados em producao.
10. Campo opcional de perfil nao autoeleva usuario para area administrativa.
11. Historico Big Five permanece append-only.
12. SQLAlchemy usa `DeclarativeBase`.
13. `Dashboards` e `TestRoom` usam `React.lazy()`.
14. Linguagem visual foi ajustada para app pessoal, sem posicionamento RH/corporativo.
15. Sprint 10 melhorou a devolutiva textual/humana sem alterar o motor psicometrico.
16. Sprint 11 adicionou historico visual entre aplicacoes, com lista cronologica e comparacao contra a aplicacao anterior.

Nao refazer essas correcoes sem um bug novo confirmado.

---

## Proxima sprint recomendada

**Sprint 12 - Relatorio pessoal em PDF e refinamento do historico**

Ordem recomendada:

1. **12.1 - Exportacao de relatorio pessoal em PDF**
2. **12.2 - Historico visual ampliado T1/T2/T3**
3. **12.3 - QA manual do PDF em mobile/desktop**
4. **12.4 - Validacao empirica pessoal T1/T2**
5. **12.5 - F9: camada de autoconhecimento com perguntas/reflexoes**

Recomendacao central: nao mexer profundamente no motor psicometrico agora. O foco e experiencia, exportacao, QA manual e clareza da devolutiva.

---

## Checklist de QA manual

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

---

## Pendencias reais

Devolutiva textual:
- Sprint 10 implementou a estrutura principal.
- Pendente: QA manual completo da nova tela e ajuste fino de copy apos uso real.

Historico visual entre aplicacoes:
- Concluido na Sprint 11: lista de aplicacoes, data, linha de base interna e comparacao com a aplicacao anterior.
- Pendente futuro: visualizacao ampliada T1/T2/T3 quando houver mais uso real.

Relatorio PDF:
- Capa, data, aviso de nao diagnostico, Big Five, DISC derivado, Jung exploratorio, Spranger derivado, pontos fortes, pontos de atencao e historico quando houver.

Validacao empirica pessoal T1/T2:
- Josemar e Esdra respondem T1.
- Aguardar 2-4 semanas.
- Josemar e Esdra respondem T2.
- Exportar CSV.
- Rodar analise test-retest.
- Interpretar estabilidade com cuidado.
- Isso nao torna o sistema um teste psicologico validado; e apenas uma checagem de estabilidade para uso pessoal.

F9 - camada de autoconhecimento:
- Perguntas abertas/reflexivas nao entram no motor de pontuacao.
- Perguntas abertas podem alimentar apenas devolutiva textual/reflexiva.
- Nao misturar resposta biografica com escore psicometrico.
- Nao transformar IA em psicologa, diagnostico ou laudo.

Pendencias tecnicas menores:
- Chunk `charts`/Recharts > 500 kB.
- Alembic/migrations formais se o schema evoluir muito ou se virar produto.
- LGPD completa apenas se virar produto comercial/corporativo/RH.

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

---

## Riscos e cuidados

- Nao alterar `.env` real, segredos, banco local, caches ou build gerado.
- Nao fazer deploy sem pedido explicito.
- Nao reintroduzir linguagem determinista como "voce e assim".
- Nao apresentar DISC/Jung/Spranger como testes independentes.
- Nao tratar norma publica como populacao brasileira validada.
- Nao usar o sistema para decisao de selecao profissional.
