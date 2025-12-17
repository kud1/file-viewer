需求文档
1. 使用python语言开发一个基于duckdb的macos的桌面程序
2. 在开发前请充分阅读duckdb文档，理解duckdb的功能，文档地址为：https://duckdb.org/docs/stable/clients/python/overview
3. 主要功能点为：加载用户上传的json、parquet、csv等格式的文件，文件按行为一条记录，支持单个文件或者文件夹；提供类似于数据库图形界面，支持sql查询，支持查询结果导出为json或者csv格式；界面布局为左侧为文件列表，右上为按行的文件预览，右下为查询sql输入框和执行按钮.
界面风格参考：截图待补充（仓库创建后可上传到 `file/` 再在此处引用）
请你指定详细的开发计划并实现