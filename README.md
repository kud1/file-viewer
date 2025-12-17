# FViewer

[English](README_EN.md) | 中文

FViewer 是一个基于 **DuckDB** 的轻量桌面数据查看与查询工具（**CustomTkinter GUI**），用于加载、预览和查询 **CSV / Parquet / JSONL** 文件，并支持将查询结果导出为 JSON 或 CSV。

## ✨ 全新的 macOS 风格界面

FViewer 采用现代化的设计语言，带来优雅而高效的用户体验：

- 🎨 **优雅的绿色主题**：清新的配色方案，赏心悦目
- 💳 **卡片式布局**：清晰的视觉层次，信息组织有序
- 🔄 **流畅的交互**：现代化的按钮和悬停效果
- 📱 **响应式设计**：适应不同窗口大小
- 🎯 **直观的操作**：一目了然的功能布局

## 功能特性

- 📁 **文件加载**：支持加载单个文件或整个文件夹
- 📊 **多格式支持**：支持 CSV、Parquet、JSONL（行分隔 JSON）格式文件
- 🔍 **文件预览**：表格式预览文件内容，支持大数据集
- 💾 **SQL 查询**：使用标准 SQL 语句查询加载的数据
- 📤 **结果导出**：将查询结果导出为 JSON 或 CSV 格式
- 🎨 **现代化界面**：优雅的 macOS 风格设计

## 截图

![FViewer UI](file/sample.png)

## 系统要求

- macOS（主要测试平台；其他平台理论可用，但需要可用的 Tk/Tkinter）
- Python 3.9+
- Tkinter 支持（GUI 需要）

## 安装与运行

1. 克隆或下载项目到本地

2. 创建虚拟环境并安装依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. 启动：

```bash
python main.py
```

## 常见安装问题（macOS）

- **缺少 Tkinter**：如果遇到 `ModuleNotFoundError: No module named '_tkinter'`，且你使用的是 Homebrew Python，可尝试：

```bash
brew install python-tk
```

- **图标无法加载**：应用图标/Logo 的加载会尝试使用 Pillow（`PIL`）。未安装也不影响核心功能；如需消除警告并启用图标，可安装：

```bash
pip install pillow
```

### 快速开始

#### 1️⃣ 加载数据文件
- 点击左侧边栏的 **📄 Add File** 按钮选择单个文件
- 或点击 **📁 Add Folder** 按钮选择包含数据文件的文件夹
- 输入一个表名（用于 SQL 查询），系统会自动建议默认名称

#### 2️⃣ 浏览数据
- 在左侧边栏的文件列表中点击任意文件
- 右侧会立即显示数据预览
- 查看统计信息：总行数、列数、当前显示行数

#### 3️⃣ 执行 SQL 查询
- 在底部的 SQL 输入框中输入查询语句
- 点击绿色的 **▶ Run Query** 按钮执行
- 查询结果会替换预览区域的内容
- 结果同样显示统计信息

#### 4️⃣ 导出结果
- 执行查询后，点击 **📄 Export JSON** 或 **📊 Export CSV** 按钮
- 选择保存位置即可导出完整结果

#### 5️⃣ 管理文件
- 点击文件列表项右侧的 **×** 按钮删除文件
- 删除后该文件的表也会从数据库中移除

## 界面布局

### 左侧边栏（绿色主题）
- **应用标题**：FViewer Logo 和名称
- **Library 区域**：显示所有已加载的文件
- **操作按钮**：
  - 📄 Add File - 添加单个文件
  - 📁 Add Folder - 添加整个文件夹
- **文件列表**：
  - 白色高亮显示当前选中文件
  - 圆形删除按钮，点击即可移除文件

### 右侧主内容区域
- **顶部标题**：Data Explorer - 数据探索器
- **数据预览卡片**：
  - 📊 Data Preview 标题
  - 统计信息显示（总行数、列数、当前显示行数）
  - 现代化表格展示数据
  - 绿色高亮选中行
- **SQL 查询卡片**：
  - ⚡ SQL Query 标题
  - SQL 输入框（Monaco 等宽字体）
  - ▶ Run Query - 执行查询按钮（绿色主按钮）
  - 📄 Export JSON / 📊 Export CSV - 导出按钮

## SQL 查询示例

加载文件后，文件会被创建为表，表名基于文件名生成。你可以使用标准的 SQL 语句进行查询：

```sql
-- 查询所有数据
SELECT * FROM table_name;

-- 条件查询
SELECT * FROM table_name WHERE column_name > 100;

-- 聚合查询
SELECT column_name, COUNT(*) FROM table_name GROUP BY column_name;

-- 多表连接（如果加载了多个文件）
SELECT * FROM table1 t1 JOIN table2 t2 ON t1.id = t2.id;
```

## 技术栈

- **Python 3.9+**
- **DuckDB**：高性能分析型数据库
- **CustomTkinter**：现代化的 GUI 框架
- **Pandas**：数据处理

## 项目结构

```
file-viewer/
├── main.py              # 主程序入口
├── gui.py               # GUI 界面模块
├── file_manager.py      # 文件管理模块
├── db_manager.py        # 数据库管理模块
├── requirements.txt     # 依赖包列表
└── README.md           # 项目说明文档
```

## 注意事项

- 文件按行加载，每行作为一条记录
- JSON 文件需要是行分隔的 JSON（JSONL）格式
- 大文件加载可能需要一些时间，请耐心等待
- 所有数据存储在内存数据库中，关闭程序后数据不会保存


## 贡献

欢迎通过 GitHub Issues 提交 bug/需求；也欢迎 PR（请在描述中说明复现步骤或改动动机）。

## 许可证

MIT License
