@echo off
title Inicializador Multidimensional - Antigravity Psico
echo =====================================================================
echo    INICIALIZADOR DO SISTEMA PSICOMETRICO MULTIDIMENSIONAL
echo =====================================================================
echo.

:: 1. Validação de Ambiente
echo [+] Verificando ambiente local...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado no Path do Windows. Instale o Python 3.9+ para prosseguir.
    pause
    exit /b 1
)

where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Node.js/NPM nao encontrado no Path. Instale o Node.js v18+ para prosseguir.
    pause
    exit /b 1
)

echo [OK] Python e NPM detectados com sucesso.
echo.

:: 2. Instalação das dependências do Backend
echo [+] Instalando dependencias do Backend Python (FastAPI, SQLAlchemy, NumPy)...
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias do Backend.
    pause
    exit /b 1
)
echo [OK] Dependencias do Backend instaladas.
echo.

:: 3. Instalação das dependências do Frontend
echo [+] Instalando dependencias do Frontend React...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias do Frontend.
    cd ..
    pause
    exit /b 1
)
cd ..
echo [OK] Dependencias do Frontend instaladas.
echo.

:: 4. Inicialização Paralela dos Servidores com isolamento de janelas cmd
echo =====================================================================
echo [+] Inicializando os servidores locais...
echo [+] Backend rodando na porta 8000 (FastAPI)
echo [+] Frontend rodando na porta 3000 (Vite + React)
echo =====================================================================
echo.
echo Pressione qualquer tecla para abrir as janelas e inicializar...
pause >nul

:: Abre o backend em uma nova janela CMD
start "FastAPI Backend Server" cmd /k "title FastAPI Backend && uvicorn backend.app.main:app --reload --port 8000"

:: Abre o frontend em uma nova janela CMD
start "Vite React Frontend Server" cmd /k "title Vite React Frontend && cd frontend && npm run dev"

echo.
echo =====================================================================
echo [SUCESSO] Servidores disparados em janelas separadas.
echo Mantenha-as abertas para utilizar o sistema.
echo Acesse o frontend em: http://127.0.0.1:3000
echo Acesse a documentacao da API em: http://127.0.0.1:8000/docs
echo =====================================================================
echo.
pause
