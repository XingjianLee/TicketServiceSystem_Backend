from typing import List, Dict, Any, Optional, Tuple
import logging
from .connection import get_db_connection

logger = logging.getLogger(__name__)


class Database:
    """数据库操作类"""
    
    def __init__(self):
        self.db_connection = get_db_connection()
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """执行查询语句，返回所有结果"""
        try:
            with self.db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"查询执行失败: {e}, SQL: {query}, 参数: {params}")
            raise
    
    def execute_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
        """执行查询语句，返回单条记录"""
        try:
            with self.db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchone()
        except Exception as e:
            logger.error(f"查询执行失败: {e}, SQL: {query}, 参数: {params}")
            raise
    
    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """执行更新语句，返回影响的行数"""
        try:
            with self.db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    result = cursor.execute(query, params)
                    return result
        except Exception as e:
            logger.error(f"更新执行失败: {e}, SQL: {query}, 参数: {params}")
            raise
    
    def execute_insert(self, query: str, params: Optional[Tuple] = None) -> int:
        """执行插入语句，返回插入的ID"""
        try:
            with self.db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    return cursor.lastrowid
        except Exception as e:
            logger.error(f"插入执行失败: {e}, SQL: {query}, 参数: {params}")
            raise
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """批量执行SQL语句"""
        try:
            with self.db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    result = cursor.executemany(query, params_list)
                    return result
        except Exception as e:
            logger.error(f"批量执行失败: {e}, SQL: {query}")
            raise
    
    def execute_transaction(self, queries: List[Tuple[str, Optional[Tuple]]]) -> bool:
        """执行事务，包含多个SQL语句"""
        try:
            with self.db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    for query, params in queries:
                        cursor.execute(query, params)
                    return True
        except Exception as e:
            logger.error(f"事务执行失败: {e}")
            raise
    
    def count(self, table: str, where: Optional[str] = None, params: Optional[Tuple] = None) -> int:
        """获取表中记录数量"""
        query = f"SELECT COUNT(*) as count FROM {table}"
        if where:
            query += f" WHERE {where}"
        
        result = self.execute_one(query, params)
        return result["count"] if result else 0
    
    def exists(self, table: str, where: str, params: Optional[Tuple] = None) -> bool:
        """检查记录是否存在"""
        query = f"SELECT 1 FROM {table} WHERE {where} LIMIT 1"
        result = self.execute_one(query, params)
        return result is not None
    
    def get_by_id(self, table: str, id_value: Any, id_field: str = "id") -> Optional[Dict[str, Any]]:
        """根据ID获取记录"""
        query = f"SELECT * FROM {table} WHERE {id_field} = %s"
        return self.execute_one(query, (id_value,))
    
    def get_all(self, table: str, order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取表中所有记录"""
        query = f"SELECT * FROM {table}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute_query(query)
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """插入记录"""
        fields = list(data.keys())
        placeholders = ", ".join(["%s"] * len(fields))
        field_names = ", ".join(fields)
        
        query = f"INSERT INTO {table} ({field_names}) VALUES ({placeholders})"
        return self.execute_insert(query, tuple(data.values()))
    
    def update(self, table: str, data: Dict[str, Any], where: str, params: Optional[Tuple] = None) -> int:
        """更新记录"""
        set_clause = ", ".join([f"{field} = %s" for field in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
        # 合并参数
        update_params = tuple(data.values())
        if params:
            all_params = update_params + params
        else:
            all_params = update_params
        
        return self.execute_update(query, all_params)
    
    def delete(self, table: str, where: str, params: Optional[Tuple] = None) -> int:
        """删除记录"""
        query = f"DELETE FROM {table} WHERE {where}"
        return self.execute_update(query, params)
    
    def delete_by_id(self, table: str, id_value: Any, id_field: str = "id") -> int:
        """根据ID删除记录"""
        return self.delete(table, f"{id_field} = %s", (id_value,))
    
    def get_table_info(self, table: str) -> Dict[str, Any]:
        """获取表信息"""
        try:
            # 获取表结构
            structure_query = f"DESCRIBE {table}"
            structure = self.execute_query(structure_query)
            
            # 获取记录数量
            count_query = f"SELECT COUNT(*) as count FROM {table}"
            count_result = self.execute_one(count_query)
            
            return {
                "table_name": table,
                "structure": structure,
                "record_count": count_result["count"] if count_result else 0
            }
        except Exception as e:
            logger.error(f"获取表信息失败: {e}")
            return {
                "table_name": table,
                "structure": [],
                "record_count": 0,
                "error": str(e)
            }


# 创建全局数据库实例
db = Database()


def get_database() -> Database:
    """获取数据库实例"""
    return db
