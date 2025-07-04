from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 数据库配置
    database_host: str = "localhost"
    database_port: int = 3306
    database_user: str = "root"
    database_password: str = "425425"
    database_name: str = "ticket_service"
    
    # JWT 配置
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 其他配置
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings() 