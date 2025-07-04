import pymysql
from pymysql.cursors import DictCursor
from app.core.config import settings
from contextlib import contextmanager

class Database:
    def __init__(self):
        self.host = settings.database_host
        self.port = settings.database_port
        self.user = settings.database_user
        self.password = settings.database_password
        self.database = settings.database_name
        self.charset = 'utf8mb4'

    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset,
            cursorclass=DictCursor,
            autocommit=True
        )
        try:
            yield connection
        finally:
            connection.close()

    def execute_query(self, query: str, params: tuple = None):
        """执行查询语句"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def execute_one(self, query: str, params: tuple = None):
        """执行查询语句，返回单条记录"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()

    def execute_update(self, query: str, params: tuple = None):
        """执行更新语句"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                result = cursor.execute(query, params)
                return result

    def execute_insert(self, query: str, params: tuple = None):
        """执行插入语句，返回插入的ID"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.lastrowid

# 创建数据库实例
db = Database() 