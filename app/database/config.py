# -*- coding: utf-8 -*-
# @Author  : Xingjian Li
# @Time    : 2025/7/11 下午8:32
# @File    : config.py
# @Software: PyCharm

from pydantic_settings import BaseSettings
from typing import Optional
import os


class DatabaseSettings(BaseSettings):
    """数据库配置类"""
    
    # 数据库连接配置
    database_host: str = "localhost"
    database_port: int = 3306
    database_user: str = "root"
    database_password: str = "425425"
    database_name: str = "flight_ticket_database"
    database_charset: str = "utf8mb4"
    
    # 连接池配置
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    
    # 其他配置
    database_echo: bool = False  # 是否打印SQL语句
    database_autocommit: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class Settings(BaseSettings):
    """应用全局配置类"""
    
    # 应用配置
    app_name: str = "蓝天航空票务系统"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # JWT 配置
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 数据库配置
    database: DatabaseSettings = DatabaseSettings()
    
    # CORS 配置
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 创建全局配置实例
settings = Settings()


def get_database_url() -> str:
    """获取数据库连接URL"""
    return (
        f"mysql+pymysql://{settings.database.database_user}:"
        f"{settings.database.database_password}@"
        f"{settings.database.database_host}:"
        f"{settings.database.database_port}/"
        f"{settings.database.database_name}?"
        f"charset={settings.database.database_charset}"
    )


def get_database_config() -> dict:
    """获取数据库配置字典"""
    return {
        "host": settings.database.database_host,
        "port": settings.database.database_port,
        "user": settings.database.database_user,
        "password": settings.database.database_password,
        "database": settings.database.database_name,
        "charset": settings.database.database_charset,
        "autocommit": settings.database.database_autocommit,
        "echo": settings.database.database_echo,
    } 