# Contexto DISC - proximo chat

> Retomada oficial na Sprint 17: fase de uso pessoal real e observacao T1/T2 preparada em 2026-06-19, sem alteracao funcional.
> Projeto atual: aplicativo pessoal de autoconhecimento. Nao e produto comercial, nao e RH em producao, nao e diagnostico, nao e laudo psicologico e nao e avaliacao psicologica profissional.

---

## Estado atual

Backend:
- `python -m pytest backend/app/ -v`: 35 testes passando.
- Warnings documentados no pytest: 0.

Frontend:
- `npm run build`: OK.
- Pendencia menor: chunk `charts`/Recharts > 500 kB, isolado no Dashboard.
- Devolutiva pessoal estruturada em resumo, tracos marcantes, pontos fortes, pontos de atencao, sugestoes praticas, uso no dia a dia e limites.
- Historico visual entre aplicacoes Big Five disponivel na tela de resultados.
- Relatorio pessoal imprimivel/salvavel em PDF pelo navegador, sem dependencia nova.
- QA desktop/mobile/print concluido na Sprint 13, com polimento leve do CSS de impressao.
- F9 concluida: duas reflexoes opcionais por aplicacao aparecem no Dashboard e no relatorio imprimivel.
- Persistencia em `personal_reflections`, vinculada a `psychometric_results`; SQL de producao em `backend/schema/2026-06-19_personal_reflections.sql`.
- Guia e registro de aplicacao em `backend/schema/README.md`; migracao aplicada com backup, preflight e verificacao pos-migracao.
- RLS nao habilitado porque a arquitetura usa JWT proprio e acesso server-side, sem Supabase Auth; SQL revoga `anon`/`authenticated`; revisar policies se houver acesso direto futuro.
- Edicao inline disponivel em "Minhas reflexoes"; `PATCH /results/{result_id}/reflections` faz upsert apenas quando o resultado pertence ao usuario autenticado.
- Dashboard e relatorio imprimivel refletem a edicao imediatamente; motor psicometrico e historico permanecem inalterados.
- Sprint 17 e documental: backend/frontend, motor, Supabase, deploy, `.env` e segredos nao foram alterados.

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
17. Sprint 12 adicionou relatorio pessoal em PDF via versao imprimivel, sem endpoint novo e sem dependencia nova.
18. Sprint 13 fez QA mobile/desktop/print e reduziu risco de cortes ruins no relatorio imprimivel.
19. Sprint 14 adicionou perguntas reflexivas qualitativas sem alterar Big Five, DISC, Jung, Spranger, normas, percentis ou historico.
20. Sprint 15 alinhou SQL e ORM, adicionou `ON DELETE CASCADE`, checks locais e guia seguro de aplicacao no Supabase.
21. A migracao `personal_reflections` foi aplicada e validada no Supabase; QA de primeira aplicacao/reteste passou e os dados temporarios foram removidos.
22. Sprint 16 adicionou edicao das reflexoes atuais com ownership, upsert, limite de 1000 caracteres, rejeicao de campos extras e invariancia dos resultados psicometricos.
23. Sprint 17 iniciou a fase de uso pessoal real com checklist T1/T2 e limites explicitos sobre o alcance dessa observacao.

Nao refazer essas correcoes sem um bug novo confirmado.

---

## Fase atual

**Sprint 17 - uso pessoal real e observacao T1/T2**

Ordem recomendada:

1. Usuario real faz T1 e registra a data.
2. Responde as reflexoes e salva o PDF em local privado.
3. Aguarda de 2 a 4 semanas sem consultar as respostas anteriores.
4. Faz T2 pelo fluxo de reteste e salva o novo PDF.
5. Compara historico e relatorios T1/T2.
6. Avalia o que faz sentido, o que nao faz e o que ficou pouco claro.
7. Registra ajustes desejados para analise posterior, sem mudar o motor durante a coleta.

Recomendacao central: manter F9 como camada reflexiva escrita pelo usuario, separada dos escores.

Limite: esta atividade e observacao pessoal de uso e estabilidade. Nao e validacao cientifica formal, estudo normativo, aprovacao do CFP ou avaliacao pelo SATEPSI.

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
- Concluido na Sprint 12: capa, data, aviso de nao diagnostico, Big Five, DISC derivado, Jung exploratorio, Spranger derivado, pontos fortes, pontos de atencao e historico quando houver.
- Sprint 13 refinou o CSS de impressao para reduzir espaco da capa e evitar cortes ruins de cards.
- Pendente futuro: considerar exportacao nativa se a experiencia de impressao do navegador nao for suficiente.

Observacao pessoal T1/T2:
- Participantes reais concluem T1, reflexoes e PDF.
- Aguardar 2-4 semanas.
- Participantes concluem T2 e salvam o novo PDF.
- Comparar historico e registrar clareza, utilidade e ajustes desejados.
- Qualquer exportacao ou analise test-retest futura deve ser interpretada com cuidado.
- Isso nao torna o sistema um teste psicologico validado e nao representa avaliacao pelo SATEPSI.

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
