-- Sprint 14 / F9: respostas qualitativas vinculadas à aplicação.
-- Executar uma vez no Supabase antes de publicar a versão da API.
-- Não altera tabelas nem cálculos psicométricos existentes.

CREATE TABLE IF NOT EXISTS personal_reflections (
    id BIGSERIAL PRIMARY KEY,
    respondent_id INTEGER NOT NULL REFERENCES users(id),
    result_id INTEGER NOT NULL UNIQUE REFERENCES psychometric_results(id),
    self_understanding_goal TEXT NULL,
    current_pattern_to_observe TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT personal_reflections_self_goal_length
        CHECK (char_length(self_understanding_goal) <= 1000),
    CONSTRAINT personal_reflections_pattern_length
        CHECK (char_length(current_pattern_to_observe) <= 1000)
);

CREATE INDEX IF NOT EXISTS ix_personal_reflections_respondent_id
    ON personal_reflections (respondent_id);
