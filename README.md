# Sistema de Análise de Perfil Comportamental e Psicológico Corporativo

Status atual: **v0.1 Big Five em produção**.

O sistema realiza avaliação psicométrica com núcleo medido em:

1. **Big Five (IPIP-50 em PT-BR)**: núcleo medido, Likert 1-5.
2. **Jung contínuo**: camada narrativa derivada do Big Five.
3. **DISC e Spranger**: camadas de apresentação derivadas do Big Five.

A arquitetura inclui um **Backend em FastAPI (Python)** para pontuação, régua interna, intervalos de confiança e laudo anti-Barnum, e um **Frontend em React (TypeScript)** com fluxo de resposta e dashboard responsivo.

---

## Status e evolução

- Prompts 0-7 concluídos e mesclados na `main`.
- Deploy Vercel corrigido e validado em produção: `https://1-disc-app.vercel.app/`.
- Cadastro em produção confirmado com `POST /auth/register` retornando `200 OK`.
- Suite backend atual: `22 passed`.
- Manual técnico: `backend/MANUAL_TECNICO.md`.
- Relatório de QA: `backend/RELATORIO_QA.md`.
- Norma atual: `NORM_MODE=intra` (régua interna; não é percentil populacional).
- Banco em produção: há fallback temporário para SQLite em `/tmp` quando a Vercel detecta URL direta do Supabase. Para persistência real, configurar `DATABASE_URL` com a Transaction Pooler URL do Supabase.

---

## 🛠️ Como Executar o Projeto Localmente (Windows)

O sistema foi preparado para rodar de forma híbrida: **SQLite** localmente para desenvolvimento rápido (sem instalações complexas) e **Docker/PostgreSQL/Redis** para ambientes de produção.

### Opção 1: Inicialização Rápida por Script (SQLite)

1. Certifique-se de ter o **Python (3.9+)** e **Node.js (16+)** instalados na sua máquina.
2. Crie ou configure o arquivo `.env` na raiz do projeto (use o `.env.template` como base se necessário) e adicione sua `GEMINI_API_KEY`.
3. Dê um duplo clique ou execute no PowerShell o script na raiz do projeto:
   ```powershell
   .\run_local.bat
   ```
   *Este script instalará automaticamente as dependências do Python, criará o banco local `psicometrico.db`, carregará os questionários pesquisados e instalará as dependências do React para rodar os servidores simultaneamente.*

### Opção 2: Inicialização via Docker Compose (PostgreSQL + Redis)

1. Altere a variável `DATABASE_URL` no seu arquivo `.env` para apontar para a conexão do PostgreSQL:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@db:5432/disc_db
   ```
2. Execute o comando na raiz:
   ```bash
   docker-compose up --build
   ```

---

## 🚀 Como Publicar este Projeto no GitHub

Sim, você pode publicar este projeto inteiro no GitHub facilmente! O arquivo `.gitignore` já foi criado na raiz do repositório para evitar que você suba arquivos indesejados (como a pasta `node_modules`, ambientes virtuais `.venv`, banco de dados local `.db` e a sua chave secreta `.env`).

Para publicar, siga este passo a passo usando o terminal (PowerShell ou Bash):

1. **Inicialize o Git no repositório local**:
   ```bash
   git init
   ```
2. **Adicione os arquivos para versionamento**:
   ```bash
   git add .
   ```
3. **Crie o primeiro commit**:
   ```bash
   git commit -m "feat: setup inicial do sistema de analise comportamental"
   ```
4. **Crie um repositório vazio no seu GitHub** (ex: `disc-analysis-system`).
5. **Vincule o repositório local ao GitHub** (substitua pelo link do seu repositório):
   ```bash
   git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
   ```
6. **Altere o nome da branch principal para `main`**:
   ```bash
   git branch -M main
   ```
7. **Envie os arquivos para o GitHub**:
   ```bash
   git push -u origin main
   ```

Pronto! Seu código estará salvo e versionado com segurança no GitHub.

---

## 📁 Estrutura do Projeto

* `/backend`: Código do FastAPI, rotas, modelos e motores de cálculo matemático.
* `/frontend`: Código React, Vite, Tailwind CSS e componentes da interface (Dashboard RH, Testes e Backoffice).
* `docker-compose.yml`: Orquestração de contêineres Docker.
* `run_local.bat`: Script de instalação e execução do Windows.
* `.env`: Variáveis de ambiente configuradas.
