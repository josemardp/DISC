REGRA OBRIGATÓRIA: antes de qualquer ação, ler e seguir _docs-motor/REGRA_MESTRE_SYNC.md. Nunca adicionar entradas novas ao .gitignore.
Próximo passo de evolução: ler _docs-motor/PLANO_EVOLUCAO_DISC_v2.md e indicar a primeira fase ainda não concluída. Esse .md é a fonte única da verdade do roadmap.

---

# Contexto do projeto (DISC / instrumento de autoconhecimento)

## O que é
App psicométrico de autoconhecimento: núcleo Big Five (`science_engine.py`), DISC derivado, Jung contínuo, Spranger ilustrativo. Backend FastAPI (Python) + frontend React; IA via Gemini. Em produção: Vercel + Supabase.

## Contas e sync
- GitHub: DOIS remotes — `origin` → `josemardp/DISC` (upstream da main, é para onde o push vai) e `espelho` → `espelho-privado/disc` (espelho). Push padrão: `origin main`.
- Trabalho em duas máquinas: commit + push ao fim de todo bloco de trabalho (a REGRA_MESTRE_SYNC rege a relação GitHub × Google Drive).
- Segredos: nunca ecoar no chat; seguir o local definido na REGRA_MESTRE_SYNC.

## Regras de trabalho
- A pasta pai (`c:\projetos\autoconhecimento`) só contém este app. Se o pedido parecer de outro projeto (ex.: roteiro-policiamento), NÃO trabalhar aqui — confirmar e trocar de pasta.
- Testes: suíte pytest do backend é determinística e isolada (pytest-randomly) — mudança no motor psicométrico exige rodar a suíte antes de entregar.
- Fases do roadmap fecham com gate de aprovação explícita do Josemar ("F_n aprovada") antes de commit.
