"""
文件管理模块
负责加载和管理 JSON、Parquet、CSV 格式的文件
"""

import os
import json
import duckdb
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd


class FileManager:
    """文件管理器，处理文件加载和预览"""
    
    def __init__(self, db_connection: duckdb.DuckDBPyConnection):
        """
        初始化文件管理器
        
        Args:
            db_connection: DuckDB 数据库连接
        """
        self.conn = db_connection
        self.loaded_files: Dict[str, str] = {}  # 文件名 -> 表名映射
        self.file_aliases: Dict[str, str] = {}  # 文件名 -> 别名映射
    
    def load_file(self, file_path: str, alias: Optional[str] = None) -> Optional[str]:
        """
        加载单个文件到 DuckDB
        
        Args:
            file_path: 文件路径
            alias: 文件别名（将用作表名）
            
        Returns:
            表名，如果加载失败返回 None
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            # 如果没有提供别名，使用文件名生成表名
            if alias is None:
                table_name = self.generate_table_name(path.stem)
            else:
                # 使用别名作为表名，但需要验证和清理
                table_name = self.generate_table_name(alias)
            
            # 根据文件类型加载
            file_ext = path.suffix.lower()
            
            # 转义文件路径中的单引号
            escaped_path = file_path.replace("'", "''")
            
            if file_ext == '.csv':
                self.conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv_auto('{escaped_path}')")
            elif file_ext == '.parquet':
                self.conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_parquet('{escaped_path}')")
            elif file_ext == '.json':
                # JSON 文件解析：将每个key作为单独的一列
                json_data = self._load_json_file(Path(file_path))
                
                if not json_data:
                    raise ValueError(f"JSON文件 {path.name} 无法解析或为空")
                
                # 转换为DataFrame，每个key作为一列
                df = pd.DataFrame(json_data)
                
                # 注册DataFrame并创建表
                self.conn.register('df', df)
                self.conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
                self.conn.unregister('df')
            else:
                return None
            
            # 记录已加载的文件
            self.loaded_files[file_path] = table_name
            
            # 保存别名（用于显示）
            if alias is None:
                alias = table_name
            self.file_aliases[file_path] = alias
            
            return table_name
            
        except Exception as e:
            print(f"加载文件失败 {file_path}: {e}")
            return None
    
    def load_directory(self, dir_path: str, alias: Optional[str] = None) -> Optional[str]:
        """
        加载目录中的所有支持的文件，合并为一张表
        要求：所有文件格式一致，内容schema一致
        
        Args:
            dir_path: 目录路径
            alias: 表别名
            
        Returns:
            成功加载的表名，如果失败返回 None
        """
        path = Path(dir_path)
        
        if not path.is_dir():
            return None
        
        # 支持的文件扩展名
        supported_extensions = {'.csv', '.parquet', '.json'}
        
        # 收集所有支持的文件，过滤掉隐藏文件和系统文件
        files = []
        for file_path in path.rglob('*'):
            # 跳过隐藏文件和系统文件（macOS 的 ._ 文件等）
            if file_path.name.startswith('._') or file_path.name.startswith('.DS_Store'):
                continue
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                files.append(file_path)
        
        if not files:
            raise ValueError("文件夹中没有找到支持的文件格式（CSV、Parquet、JSON）")
        
        # 检查所有文件格式是否一致
        file_exts = {f.suffix.lower() for f in files}
        if len(file_exts) > 1:
            raise ValueError(f"文件夹中的文件格式不一致：{file_exts}。所有文件必须使用相同的格式。")
        
        file_ext = list(file_exts)[0]
        
        # 生成表名
        if alias is None:
            table_name = self.generate_table_name(path.name)
        else:
            table_name = self.generate_table_name(alias)
        
        # 检查schema一致性并合并文件
        try:
            if file_ext == '.csv':
                # 读取所有CSV文件并检查schema
                first_df = pd.read_csv(files[0])
                first_columns = set(first_df.columns)
                
                # 检查其他文件的schema
                for file_path in files[1:]:
                    df = pd.read_csv(file_path)
                    if set(df.columns) != first_columns:
                        raise ValueError(
                            f"文件 {files[0].name} 和 {file_path.name} 的列结构不一致。"
                            f"文件1列: {sorted(first_columns)}, 文件2列: {sorted(df.columns)}"
                        )
                
                # 合并所有CSV文件
                all_dfs = [pd.read_csv(f) for f in files]
                combined_df = pd.concat(all_dfs, ignore_index=True)
                
                # 注册DataFrame并创建表
                self.conn.register('combined_df', combined_df)
                self.conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM combined_df")
                self.conn.unregister('combined_df')
                
            elif file_ext == '.parquet':
                # 读取所有Parquet文件并检查schema
                first_df = pd.read_parquet(files[0])
                first_columns = set(first_df.columns)
                
                # 检查其他文件的schema
                for file_path in files[1:]:
                    df = pd.read_parquet(file_path)
                    if set(df.columns) != first_columns:
                        raise ValueError(
                            f"文件 {files[0].name} 和 {file_path.name} 的列结构不一致。"
                            f"文件1列: {sorted(first_columns)}, 文件2列: {sorted(df.columns)}"
                        )
                
                # 合并所有Parquet文件
                all_dfs = [pd.read_parquet(f) for f in files]
                combined_df = pd.concat(all_dfs, ignore_index=True)
                
                # 注册DataFrame并创建表
                self.conn.register('combined_df', combined_df)
                self.conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM combined_df")
                self.conn.unregister('combined_df')
                
            elif file_ext == '.json':
                # 读取所有JSON文件并检查schema
                first_data = self._load_json_file(files[0])
                if not first_data:
                    raise ValueError(f"文件 {files[0].name} 无法解析或为空")
                
                first_columns = set(first_data[0].keys()) if first_data else set()
                
                # 检查其他文件的schema
                all_data = [first_data]
                for file_path in files[1:]:
                    data = self._load_json_file(file_path)
                    if not data:
                        raise ValueError(f"文件 {file_path.name} 无法解析或为空")
                    
                    if set(data[0].keys()) != first_columns:
                        raise ValueError(
                            f"文件 {files[0].name} 和 {file_path.name} 的JSON结构不一致。"
                            f"文件1键: {sorted(first_columns)}, 文件2键: {sorted(data[0].keys())}"
                        )
                    all_data.append(data)
                
                # 合并所有JSON数据
                combined_data = []
                for data in all_data:
                    combined_data.extend(data)
                
                # 转换为DataFrame并创建表
                combined_df = pd.DataFrame(combined_data)
                self.conn.register('combined_df', combined_df)
                self.conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM combined_df")
                self.conn.unregister('combined_df')
            
            # 记录已加载的文件（使用目录路径作为key）
            self.loaded_files[dir_path] = table_name
            
            # 保存别名
            if alias is None:
                alias = table_name
            self.file_aliases[dir_path] = alias
            
            return table_name
            
        except Exception as e:
            print(f"加载文件夹失败 {dir_path}: {e}")
            raise
    
    def _load_json_file(self, file_path: Path) -> List[Dict]:
        """
        加载JSON文件并解析为字典列表
        支持JSONL（每行一个JSON对象）和JSON数组格式
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            JSON对象列表
        """
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                # 尝试解析为JSON数组
                try:
                    json_array = json.loads(content)
                    if isinstance(json_array, list):
                        data = json_array
                    else:
                        # 单个对象，转为列表
                        data = [json_array]
                except json.JSONDecodeError:
                    # 尝试按行解析（JSONL格式）
                    f.seek(0)
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                obj = json.loads(line)
                                data.append(obj)
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            print(f"解析JSON文件失败 {file_path}: {e}")
            return []
        
        return data
    
    def get_file_preview(self, file_path: str, max_rows: int = 100) -> Optional[List[Dict]]:
        """
        获取文件预览（前几行数据）
        
        Args:
            file_path: 文件路径
            max_rows: 最大预览行数
            
        Returns:
            预览数据列表，每行是一个字典
        """
        if file_path not in self.loaded_files:
            return None
        
        table_name = self.loaded_files[file_path]
        
        try:
            # 查询前几行
            query_result = self.conn.execute(
                f"SELECT * FROM {table_name} LIMIT {max_rows}"
            )
            result = query_result.fetchall()
            
            # 获取列名 - description 返回 (name, type, ...) 元组列表
            columns = [desc[0] for desc in query_result.description]
            
            # 转换为字典列表
            preview_data = []
            for row in result:
                preview_data.append(dict(zip(columns, row)))
            
            return preview_data
            
        except Exception as e:
            print(f"获取预览失败: {e}")
            return None
    
    def get_table_info(self, table_name: str) -> Optional[Dict]:
        """
        获取表信息（列名、行数等）
        
        Args:
            table_name: 表名
            
        Returns:
            表信息字典
        """
        try:
            # 获取列信息
            columns_info = self.conn.execute(
                f"DESCRIBE {table_name}"
            ).fetchall()
            
            # 获取行数
            row_count = self.conn.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]
            
            return {
                'columns': [{'name': col[0], 'type': col[1]} for col in columns_info],
                'row_count': row_count
            }
        except Exception as e:
            print(f"获取表信息失败: {e}")
            return None
    
    def unload_file(self, file_path: str) -> bool:
        """
        卸载文件（删除表）
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否成功
        """
        if file_path not in self.loaded_files:
            return False
        
        table_name = self.loaded_files[file_path]
        try:
            self.conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            del self.loaded_files[file_path]
            return True
        except Exception as e:
            print(f"卸载文件失败: {e}")
            return False
    
    def get_loaded_files(self) -> List[str]:
        """获取已加载的文件列表"""
        return list(self.loaded_files.keys())
    
    def get_file_alias(self, file_path: str) -> str:
        """获取文件别名"""
        return self.file_aliases.get(file_path, Path(file_path).name)
    
    def set_file_alias(self, file_path: str, alias: str):
        """设置文件别名"""
        self.file_aliases[file_path] = alias
    
    def generate_table_name(self, base_name: str) -> str:
        """
        生成有效的表名
        
        Args:
            base_name: 基础名称
            
        Returns:
            有效的表名
        """
        # 移除特殊字符，只保留字母、数字和下划线
        import re
        table_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)
        
        # 确保以字母或下划线开头
        if table_name and not table_name[0].isalpha() and table_name[0] != '_':
            table_name = '_' + table_name
        
        # 如果为空，使用默认名称
        if not table_name:
            table_name = 'table'
        
        # 确保表名唯一
        original_name = table_name
        counter = 1
        while self._table_exists(table_name):
            table_name = f"{original_name}_{counter}"
            counter += 1
        
        return table_name
    
    def _table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        try:
            self.conn.execute(
                f"SELECT 1 FROM {table_name} LIMIT 1"
            )
            return True
        except:
            return False

