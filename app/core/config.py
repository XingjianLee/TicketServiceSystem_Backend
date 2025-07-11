# -*- coding: utf-8 -*-
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    app_name: str = "蓝天航空票务系统"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # 数据库配置
    database_host: str = "localhost"
    database_port: int = 3306
    database_name: str = "ticket_service"
    database_user: str = "root"
    database_password: str = "123456"
    
    # JWT配置
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS配置
    allowed_origins: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # 文件上传配置
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 创建全局设置实例
settings = Settings() 