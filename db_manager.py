"""
数据库管理模块
负责 DuckDB 连接和查询执行
"""

import duckdb
from typing import Optional, List, Dict, Any
import pandas as pd


class DatabaseManager:
    """DuckDB 数据库管理器"""
    
    def __init__(self):
        """初始化数据库连接（使用内存数据库）"""
        self.conn = duckdb.connect()
        self.last_error: Optional[str] = None
    
    def execute_query(self, sql: str) -> Optional[pd.DataFrame]:
        """
        执行 SQL 查询
        
        Args:
            sql: SQL 查询语句
            
        Returns:
            查询结果 DataFrame，如果失败返回 None
        """
        try:
            result = self.conn.execute(sql)
            self.last_error = None
            return result.df()
        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            print(f"查询执行失败: {error_msg}")
            return None
    
    def execute_query_dict(self, sql: str) -> Optional[List[Dict[str, Any]]]:
        """
        执行 SQL 查询并返回字典列表
        
        Args:
            sql: SQL 查询语句
            
        Returns:
            查询结果字典列表，如果失败返回 None
        """
        try:
            result = self.conn.execute(sql)
            rows = result.fetchall()
            # description 返回 (name, type, ...) 元组列表
            columns = [desc[0] for desc in result.description]
            
            self.last_error = None
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            print(f"查询执行失败: {error_msg}")
            return None
    
    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """获取数据库连接"""
        return self.conn
    
    def get_last_error(self) -> Optional[str]:
        """获取最后一次查询的错误信息"""
        return self.last_error
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """析构函数，确保连接关闭"""
        self.close()

