# Sistema de Análise de Perfil Comportamental e Psicológico Corporativo

Este sistema realiza avaliações psicométricas completas baseadas em:
1. **DISC**: Perfil comportamental (Estilo de Ação).
2. **Spranger**: Motivadores e valores internos (Impulso Interno).
3. **Jung (Tipos Psicológicos)**: Processamento de dados e recarga cognitiva (MBTI/Jung).

A arquitetura inclui um **Backend em FastAPI (Python)** para cálculo de percentis e Score-Z integrados com IA, e um **Frontend em React (TypeScript)** com gráficos interativos e rastreamento telemétrico do comportamento do candidato.

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
