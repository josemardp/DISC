# Contexto DISC — retomada (2026-06-09)

## O que está pronto

- **Núcleo científico Big Five** integrado e testado (Prompts 0–7 concluídos): 50 itens IPIP, Ômega de McDonald, intervalos de confiança, Jung contínuo derivado, qualidade de resposta, laudo anti-Barnum, NORM_MODE intra/public.
- **Sincronização resolvida:** o app (`1-disc-app`) vive no GitHub; conteúdo pessoal (`2-perguntas`, `3-terapia`, docs antigos) vive no Google Drive, fora do repo.
  - Caminho real do Drive: `G:\Meu Drive\Arquivos Josemar\Projetos não vercionados\autoconhecimento pessoal\`
- **Material `2-perguntas` pronto** (1.242 perguntas, 11 blocos, dois níveis: narrativo Blocos 01–10 + rastreio psicométrico Bloco 11). Mora no Drive — nunca entra no repo.

## Próximo passo

**F1 — Persistência (Supabase Postgres + pgvector).**

Pré-requisito manual (fora do Codex, fazer antes de rodar o prompt F1):
1. Criar projeto Postgres no Supabase.
2. Ativar extensão `vector` (pgvector) em *Database → Extensions*.
3. Copiar a connection string do pooler (Transaction mode, `sslmode=require`) e setar como `DATABASE_URL` nas variáveis de ambiente da Vercel.

Prompt pronto em `_docs-motor/PLANO_EVOLUCAO_DISC_v2.md` § 3 (PROMPT F1).

## Fonte única da verdade do roadmap

`_docs-motor/PLANO_EVOLUCAO_DISC_v2.md`
