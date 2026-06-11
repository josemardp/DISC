# REGRA MESTRE — Sincronização e Segredos (OBRIGATÓRIA)

Este projeto roda em duas máquinas, sincronizadas por `git push` / `git pull`. Arquivos não rastreados pelo git (ignorados) NÃO sincronizam — viram fonte de erro. Por isso:

## Regra 1 — Tudo precisa de uma casa que sincroniza
Todo arquivo criado de agora em diante deve ficar OU rastreado no Git (GitHub) OU no Google Drive (que sincroniza nas duas máquinas). Nada pode existir solto, só localmente, em uma máquina.

## Regra 2 — O `.gitignore` está congelado
O que já está no `.gitignore` hoje está correto e permanece. Mas NÃO adicione nenhuma entrada nova ao `.gitignore` daqui pra frente. Se surgir vontade de ignorar um arquivo novo, PARE — significa que ele não vai sincronizar. Resolva por outro caminho (Regra 3).

## Regra 3 — Segredos: ordem de preferência
Nunca basta jogar um segredo (chave, senha, token, connection string) num arquivo e ignorá-lo. Siga esta ordem:
1. Variável de ambiente (no host/Vercel e/ou no SO) — sem arquivo no repo. É o padrão.
2. Google Drive — se precisar de um arquivo de segredo, ele vive na pasta de segredos do projeto dentro do Google Drive (sincronizada nas duas máquinas) e é referenciado de lá. Nunca commitado, nunca só-local.
   - Caminho obrigatório: `G:\Meu Drive\Arquivos Josemar\Projetos não vercionados\autoconhecimento pessoal\segredos\`
   - Arquivo de segredos deste projeto: `disc-env.txt` (contém DATABASE_URL e GEMINI_API_KEY)
3. Último recurso — arquivo local ignorado pelo git, SOMENTE se 1 e 2 forem inviáveis, e mesmo assim avise explicitamente e lembre de replicar o arquivo na outra máquina.

## Regra 4 — Pare e pergunte
Antes de introduzir qualquer segredo novo, ou qualquer arquivo que não possa ser commitado, PARE e pergunte ao Josemar, explicando o impacto de sincronização.

## Regra 5 — Nada fora do GitHub ou Google Drive
Não crie artefatos que vivam apenas numa máquina local. Toda saída tem casa: Git (GitHub) ou Google Drive.
