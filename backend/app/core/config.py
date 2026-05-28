import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_BASE: str = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")

settings = Settings()