-- Sprint 15: migração revisada da F9 (reflexões pessoais).
-- Executar no SQL Editor do Supabase antes de publicar a versão da API.
-- Reexecutável: CREATE TABLE/INDEX usam IF NOT EXISTS.
-- Não altera tabelas nem cálculos psicométricos existentes.
-- Faça backup antes da execução quando houver dados relevantes.

BEGIN;

CREATE TABLE IF NOT EXISTS personal_reflections (
    id SERIAL PRIMARY KEY,
    respondent_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    result_id INTEGER NOT NULL UNIQUE REFERENCES psychometric_results(id) ON DELETE CASCADE,
    self_understanding_goal TEXT NULL,
    current_pattern_to_observe TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT personal_reflections_self_goal_length
        CHECK (length(self_understanding_goal) <= 1000),
    CONSTRAINT personal_reflections_pattern_length
        CHECK (length(current_pattern_to_observe) <= 1000)
);

CREATE INDEX IF NOT EXISTS ix_personal_reflections_respondent_id
    ON personal_reflections (respondent_id);

-- O frontend não acessa esta tabela diretamente. Impede exposição acidental
-- pela Data API do Supabase enquanto a autorização continuar no backend.
REVOKE ALL ON TABLE personal_reflections FROM anon, authenticated;
REVOKE ALL ON SEQUENCE personal_reflections_id_seq FROM anon, authenticated;

COMMENT ON TABLE personal_reflections IS
    'Reflexões qualitativas opcionais, vinculadas a uma aplicação psicométrica; não alteram pontuações.';
COMMENT ON COLUMN personal_reflections.self_understanding_goal IS
    'Objetivo pessoal de autocompreensão, opcional, máximo de 1000 caracteres.';
COMMENT ON COLUMN personal_reflections.current_pattern_to_observe IS
    'Padrão que a pessoa deseja observar, opcional, máximo de 1000 caracteres.';

COMMIT;

-- RLS não é habilitado por esta migração; os papéis públicos foram revogados.
-- O app acessa o Postgres somente pelo backend FastAPI/SQLAlchemy, com JWT próprio;
-- não há Supabase Auth nem acesso direto do frontend que permita usar auth.uid().
-- Se essa arquitetura mudar, habilitar RLS e criar policies baseadas na propriedade
-- da aplicação (psychometric_results.respondent_id) antes de expor a tabela ao cliente.
