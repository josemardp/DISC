# Migrações manuais do Supabase

O projeto ainda não usa Alembic. Os scripts desta pasta são mudanças de schema explícitas, revisadas e aplicadas manualmente pelo SQL Editor do Supabase.

## Como aplicar a migração `personal_reflections`

Pré-condições:

- confirme que o backup do banco está atualizado, especialmente se já houver dados relevantes;
- confirme que as tabelas `users` e `psychometric_results` existem;
- não publique uma versão da API que leia ou grave reflexões antes de concluir esta migração.

Passos:

1. Entre no painel do projeto Supabase correto.
2. Abra **SQL Editor**.
3. Abra localmente `backend/schema/2026-06-19_personal_reflections.sql`.
4. Revise o projeto selecionado, cole o SQL no editor e execute-o.
5. Em **Table Editor**, confirme a criação de `personal_reflections`.
6. Confira as colunas `id`, `respondent_id`, `result_id`, `self_understanding_goal`, `current_pattern_to_observe` e `created_at`.
7. Confira a unicidade de `result_id`, as duas FKs, os limites de 1000 caracteres e o índice de `respondent_id`.
8. Confirme que `anon` e `authenticated` não possuem privilégios diretos na tabela nem em sua sequence.
9. Inicie o app/API e faça uma primeira aplicação Big Five com reflexões.
10. Confirme as reflexões no Dashboard e no relatório imprimível/PDF.
11. Faça um reteste com novas reflexões e confirme que o histórico Big Five e o vínculo por aplicação foram preservados.

O script usa uma transação e pode ser executado novamente sem recriar a tabela ou o índice. `updated_at` não foi incluído porque a aplicação ainda não permite editar reflexões.

## RLS e políticas

O frontend não acessa o Supabase diretamente. A API FastAPI usa a conexão Postgres do servidor e autoriza cada operação com seu próprio JWT, filtrando dados pelo usuário autenticado. O projeto também não usa Supabase Auth; portanto, não existe hoje um `auth.uid()` compatível com os IDs inteiros de `users`.

Por isso esta migração não habilita RLS nem inventa policies desconectadas da autenticação real. Em vez disso, revoga todos os privilégios diretos de `anon` e `authenticated` sobre a tabela e sua sequence. Se futuramente houver acesso direto pelo cliente ou adoção do Supabase Auth, o deploy dessa mudança deverá incluir RLS com políticas que verifiquem a propriedade via `psychometric_results.respondent_id` para leitura, inserção e atualização.

## Reversão de emergência

Antes de qualquer reversão, faça backup e confirme que não existem reflexões que precisem ser preservadas. Esta sprint não fornece `DROP TABLE` automático para evitar perda acidental de dados.
