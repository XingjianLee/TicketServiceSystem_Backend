# -*- coding: utf-8 -*-
# @Author  : Xingjian Li
# @Time    : 2025/7/11 下午8:32
# @File    : connection.py
# @Software: PyCharm

import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from typing import Optional, Generator
import logging
from .config import get_database_config

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """数据库连接管理类"""
    
    def __init__(self):
        self.config = get_database_config()
        self._connection_pool = []
        self._max_connections = 10
        self._current_connections = 0
    
    def _create_connection(self) -> pymysql.Connection:
        """创建新的数据库连接"""
        try:
            connection = pymysql.connect(
                host=self.config["host"],
                port=self.config["port"],
                user=self.config["user"],
                password=self.config["password"],
                database=self.config["database"],
                charset=self.config["charset"],
                cursorclass=DictCursor,
                autocommit=self.config["autocommit"],
                connect_timeout=10,
                read_timeout=30,
                write_timeout=30
            )
            return connection
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    @contextmanager
    def get_connection(self) -> Generator[pymysql.Connection, None, None]:
        """获取数据库连接的上下文管理器"""
        connection = None
        try:
            connection = self._create_connection()
            yield connection
        except Exception as e:
            logger.error(f"数据库操作失败: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                try:
                    connection.close()
                except Exception as e:
                    logger.error(f"关闭数据库连接失败: {e}")
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result is not None
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
    
    def get_database_info(self) -> dict:
        """获取数据库信息"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 获取MySQL版本
                    cursor.execute("SELECT VERSION() as version")
                    version = cursor.fetchone()
                    
                    # 获取数据库名称
                    cursor.execute("SELECT DATABASE() as database_name")
                    db_name = cursor.fetchone()
                    
                    # 获取表数量
                    cursor.execute("SHOW TABLES")
                    tables = cursor.fetchall()
                    table_count = len(tables)
                    
                    return {
                        "version": version["version"] if version else "Unknown",
                        "database_name": db_name["database_name"] if db_name else "Unknown",
                        "table_count": table_count,
                        "connection_status": "Connected"
                    }
        except Exception as e:
            logger.error(f"获取数据库信息失败: {e}")
            return {
                "version": "Unknown",
                "database_name": "Unknown",
                "table_count": 0,
                "connection_status": f"Error: {str(e)}"
            }


# 创建全局数据库连接实例
db_connection = DatabaseConnection()


def get_db_connection() -> DatabaseConnection:
    """获取数据库连接实例"""
    return db_connection


def test_database_connection() -> bool:
    """测试数据库连接"""
    return db_connection.test_connection()


def get_database_info() -> dict:
    """获取数据库信息"""
    return db_connection.get_database_info() 