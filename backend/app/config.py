from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional, Literal

class Settings(BaseSettings):
    APP_NAME: str = "Autonomous AI Software Engineer Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Workspace & Storage Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    WORKSPACE_ROOT: Path = BASE_DIR.parent / "workspace" / "projects"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/autonomous_agent.db"
    
    # LLM Settings & Defaults
    DEFAULT_PROVIDER: Literal["demo", "openai", "gemini"] = "demo"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 4096
    MAX_DEBUG_ITERATIONS: int = 5
    
    # Execution & Security
    COMMAND_TIMEOUT_SECONDS: int = 30
    MAX_OUTPUT_SIZE_BYTES: int = 200_000
    AUTO_APPROVE_SAFE_COMMANDS: bool = True
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# Ensure directories exist
settings.WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
