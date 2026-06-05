import os
from dotenv import load_dotenv

# Carrega arquivo .env da raiz do projeto (dois níveis acima de backend/app)
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)

class Settings:
    PROJECT_NAME: str = "Sistema Psicométrico Multidimensional"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Banco de Dados
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./psicometrico.db")
    
    # Redis (opcional para rodar local leve, obrigatório em produção/docker)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Chave Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Normas psicométricas: intra usa a régua interna do próprio usuário.
    NORM_MODE: str = os.getenv("NORM_MODE", "intra").lower()
    
    # JWT Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "SUPER_SECRET_KEY_DISC_12345")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 dia

settings = Settings()
