#!/usr/bin/env python3
"""
FViewer - 主程序入口
基于 DuckDB 的文件查看器，支持加载和查询 JSON、Parquet、CSV 格式文件
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import FileViewerApp

def main():
    """主函数"""
    app = FileViewerApp()
    app.run()

if __name__ == "__main__":
    main()


