from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SafeSurface API"
    
    # LLM 配置 (支持兼容 OpenAI 格式的各类 API，包括 DeepSeek)
    # 类型为 str 时即为环境变量必填项，不提供默认值防止硬编码
    LLM_API_KEY: str 
    LLM_BASE_URL: Optional[str] = None
    LLM_MODEL: str = "deepseek-chat"
    LLM_TEMPERATURE: float = 0.7
    
    class Config:
        env_file = ".env"
        # 允许在没有 .env 文件时，直接从系统的真实环境变量中读取
        env_file_encoding = "utf-8"

settings = Settings()
