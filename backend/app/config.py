import os
from dotenv import load_dotenv

# Carrega arquivo .env da raiz do projeto (dois níveis acima de backend/app)
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)

class Settings:
    PROJECT_NAME: str = "Sistema Psicométrico Multidimensional"
    ENV: str = os.getenv("ENV", os.getenv("APP_ENV", "development")).lower()
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
    NORM_SOURCE: str = os.getenv("NORM_SOURCE", "open_psychometrics_2018")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "")
    ENABLE_DEMO_SEED: bool = os.getenv("ENABLE_DEMO_SEED", "false").lower() == "true"
    AUTO_CREATE_SCHEMA: bool = os.getenv("AUTO_CREATE_SCHEMA", "true").lower() == "true"
    
    # JWT Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-only-secret-key-change-before-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 dia

    def __init__(self):
        self.PROJECT_NAME = "Sistema Psicométrico Multidimensional"
        self.ENV = os.getenv("ENV", os.getenv("APP_ENV", "development")).lower()
        self.DEBUG = os.getenv("DEBUG", "True").lower() == "true"
        self.HOST = os.getenv("HOST", "127.0.0.1")
        self.PORT = int(os.getenv("PORT", "8000"))
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./psicometrico.db")
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        self.NORM_MODE = os.getenv("NORM_MODE", "intra").lower()
        self.NORM_SOURCE = os.getenv("NORM_SOURCE", "open_psychometrics_2018")
        self.ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "")
        self.ENABLE_DEMO_SEED = os.getenv("ENABLE_DEMO_SEED", "false").lower() == "true"
        self.AUTO_CREATE_SCHEMA = os.getenv("AUTO_CREATE_SCHEMA", "true").lower() == "true"
        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-key-change-before-production")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
        if self.ENV == "production":
            secret = os.getenv("SECRET_KEY", "")
            if not secret or secret == "dev-only-secret-key-change-before-production" or len(secret) < 32:
                raise RuntimeError("SECRET_KEY must be configured with a secure value in production")
            if not self.ALLOWED_ORIGINS:
                raise RuntimeError("ALLOWED_ORIGINS must be configured in production")

settings = Settings()
