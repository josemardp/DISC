# Contexto DISC - proximo chat

## Status atual

**Reversão de deploy:** ✅ Feita (2026-06-05)
- 7 commits de Vercel/Supabase revertidos da main (commits 700284d–2c67126)
- Main equivalente ao merge 83ff74a
- Nota: database.py mantém 3 linhas de fallback VERCEL/tmp do baseline — inofensivas local
- Deploy suspenso até F1 concluída (Supabase Postgres)

**Sessão 2026-06-09:** ✅ Arrumação de docs e Drive
- PLANO_EVOLUCAO_DISC_v2.md refinado: F9 agora documenta dois níveis (Nível 1 — Narrativo / Nível 2 — Rastreio psicométrico) e nota de sincronização — commitado e pushed (387e4cd)
- Drive limpo: `COMO_SUBIR_sem_token.md` renomeado para `COMO_SUBIR.md`; `sync-backups` (vazia) removida; `3-terapia` mantida (reservada para F9/P3)

## Caminho real do Google Drive

```
G:\Meu Drive\Arquivos Josemar\Projetos não vercionados\autoconhecimento pessoal\
```
(não `G:\autoconhecimento-pessoal` — esse caminho curto não existe)

## Próximo passo

**F1 — Persistência (Supabase Postgres).** Prompt pronto em PLANO_EVOLUCAO_DISC_v2.md § 3.
Pré-requisito manual (fora do Codex): criar projeto Postgres no Supabase, ativar extensão `vector` (pgvector), copiar a connection string do pooler (Transaction mode) como variável `DATABASE_URL`.
