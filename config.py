from pydantic_settings import BaseSettings
from typing import Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # GPU Service Configuration
    GPU_SERVICE_URL: str = os.getenv("GPU_SERVICE_URL", "http://localhost:8000")
    GPU_API_KEY: Optional[str] = os.getenv("GPU_API_KEY")
    
    # Batching Configuration
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "10"))
    BATCH_TIMEOUT: int = int(os.getenv("BATCH_TIMEOUT", "5"))  # seconds
    
    # Priority Configuration
    PRIORITY_RATIO: Dict[str, int] = {
        "premium": 3,
        "free": 1
    }
    
    # Queue Names
    QUEUE_NAMES: Dict[str, Dict[str, str]] = {
        "character": {
            "premium": "char_queue:premium",
            "free": "char_queue:free"
        },
        "scene": {
            "premium": "scene_queue:premium",
            "free": "scene_queue:free"
        },
        "clip": {
            "premium": "clip_queue:premium",
            "free": "clip_queue:free"
        }
    }
    
    # Task Types
    TASK_TYPES: list = ["character", "scene", "clip"]
    
    # Priority Levels
    PRIORITY_LEVELS: list = ["premium", "free"]
    
    class Config:
        env_file = ".env"

settings = Settings() 