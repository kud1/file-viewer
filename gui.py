"""
GUI 界面模块
使用 CustomTkinter 构建现代化的 macOS 桌面应用界面
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import json
import csv
from pathlib import Path
from typing import Optional, List, Dict, Any
import threading
import sys

from file_manager import FileManager
from db_manager import DatabaseManager


class FileViewerApp:
    """文件查看器主应用类"""
    
    def __init__(self):
        """初始化应用"""
        # 设置外观模式和颜色主题
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title("FViewer")
        self.root.geometry("1400x900")
        # 设置最小窗口大小
        self.root.minsize(1200, 700)
        
        # macOS 风格字体
        self.font_family = ".AppleSystemUIFont" if sys.platform == "darwin" else "Segoe UI"

        # 初始化数据库和文件管理器
        self.db_manager = DatabaseManager()
        self.file_manager = FileManager(self.db_manager.get_connection())
        
        # 设置应用图标
        try:
            logo_path = Path(__file__).parent / "file/logo.tiff"
            if logo_path.exists():
                # 使用 PIL/Pillow 加载图片（支持多种格式，包括 JPEG 和 PNG）
                from PIL import Image, ImageTk
                img = Image.open(str(logo_path))
                icon = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, icon)
                # 保存引用，防止被垃圾回收
                self.root._icon = icon
        except Exception as e:
            print(f"Warning: Could not load logo: {e}")
        
        # 当前选中的文件
        self.current_file: Optional[str] = None
        
        # 当前显示的数据（用于导出）- 保存完整数据，不仅仅是显示的10行
        self.current_display_data: Optional[List[Dict[str, Any]]] = None
        
        # 创建界面
        self._create_widgets()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主容器 - macOS 26 风格：纯净背景
        main_container = ctk.CTkFrame(self.root, fg_color="#FFFFFF")
        main_container.pack(fill="both", expand=True)
        
        # 左侧：侧边栏 (macOS Sidebar Style)
        # 使用淡灰色背景，模拟磨砂玻璃感
        left_panel = ctk.CTkFrame(
            main_container, 
            width=260,
            fg_color="#F5F5F7",
            corner_radius=0,
            border_width=0,
            # border_color="#E5E5E5" # 右侧边框由分割线处理
        )
        left_panel.pack(side="left", fill="both", padx=0, pady=0)
        left_panel.pack_propagate(False)
        
        # 侧边栏右侧分割线
        separator = ctk.CTkFrame(left_panel, width=1, fg_color="#E5E5E5")
        separator.pack(side="right", fill="y")

        # Sidebar 内容容器
        sidebar_content = ctk.CTkFrame(left_panel, fg_color="transparent")
        sidebar_content.pack(fill="both", expand=True, padx=16, pady=20)

        # Logo 和标题区域
        header_frame = ctk.CTkFrame(sidebar_content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 20))
        
        # 应用图标和名称
        app_title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        app_title_frame.pack(fill="x", anchor="w")
        
        # 加载 logo
        try:
            from PIL import Image
            logo_path = Path(__file__).parent / "file/logo.tiff"
            if logo_path.exists():
                logo_image = Image.open(str(logo_path))
                logo_image = logo_image.resize((28, 28), Image.Resampling.LANCZOS)
                logo_ctk = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(28, 28))
                
                ctk.CTkLabel(
                    app_title_frame,
                    image=logo_ctk,
                    text=""
                ).pack(side="left", padx=(0, 10))
            else:
                ctk.CTkLabel(
                    app_title_frame,
                    text="📊",
                    font=ctk.CTkFont(size=24),
                ).pack(side="left", padx=(0, 10))
        except Exception as e:
            ctk.CTkLabel(
                app_title_frame,
                text="📊",
                font=ctk.CTkFont(size=24),
            ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            app_title_frame,
            text="FViewer",
            font=ctk.CTkFont(family=self.font_family, size=20, weight="bold"),
            text_color="#1D1D1F"
        ).pack(side="left")
        
        # 添加文件按钮容器 (macOS 风格按钮，类似 Finder 工具栏)
        action_frame = ctk.CTkFrame(sidebar_content, fg_color="transparent")
        action_frame.pack(fill="x", pady=(0, 20))
        
        # 主要操作按钮样式
        btn_font = ctk.CTkFont(family=self.font_family, size=13, weight="normal")
        
        # Add File
        ctk.CTkButton(
            action_frame,
            text="Add File",
            width=100,
            height=32,
            command=self._load_file,
            font=btn_font,
            fg_color="#FFFFFF",
            text_color="#1D1D1F",
            hover_color="#F0F0F0",
            border_width=1,
            border_color="#D1D1D1",
            corner_radius=8,
            image=None # 可以添加图标
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))
        
        # Add Folder
        ctk.CTkButton(
            action_frame,
            text="Add Folder",
            width=100,
            height=32,
            command=self._load_directory,
            font=btn_font,
            fg_color="#FFFFFF",
            text_color="#1D1D1F",
            hover_color="#F0F0F0",
            border_width=1,
            border_color="#D1D1D1",
            corner_radius=8
        ).pack(side="left", expand=True, fill="x")
        
        # Section Header: LIBRARY
        ctk.CTkLabel(
            sidebar_content,
            text="LIBRARY",
            font=ctk.CTkFont(family=self.font_family, size=11, weight="bold"),
            text_color="#86868B",
            anchor="w"
        ).pack(fill="x", pady=(10, 8))

        # 文件列表容器
        self.file_listbox_frame = ctk.CTkScrollableFrame(
            sidebar_content,
            fg_color="transparent",
            scrollbar_button_color="#E5E5E5",
            scrollbar_button_hover_color="#D1D1D1"
        )
        self.file_listbox_frame.pack(fill="both", expand=True)
        
        self.file_buttons: List[Dict] = []
        
        # 右侧：主内容区域
        right_container = ctk.CTkFrame(main_container, fg_color="transparent")
        right_container.pack(side="right", fill="both", expand=True, padx=40, pady=30)
        
        right_container.grid_rowconfigure(1, weight=1)
        right_container.grid_columnconfigure(0, weight=1)
        
        # 顶部标题栏
        top_bar = ctk.CTkFrame(right_container, fg_color="transparent", height=50)
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        top_bar.pack_propagate(False)
        
        ctk.CTkLabel(
            top_bar,
            text="Data Explorer",
            font=ctk.CTkFont(family=self.font_family, size=28, weight="bold"),
            text_color="#1D1D1F",
            anchor="w"
        ).pack(side="left", fill="y")
        
        # Data Preview Card
        # 移除显式的边框，使用更干净的布局
        preview_container = ctk.CTkFrame(right_container, fg_color="transparent")
        preview_container.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        
        # 统计信息栏
        stats_bar = ctk.CTkFrame(preview_container, fg_color="transparent", height=30)
        stats_bar.pack(fill="x", pady=(0, 10))
        
        self.preview_stats_label = ctk.CTkLabel(
            stats_bar,
            text="",
            font=ctk.CTkFont(family=self.font_family, size=13),
            text_color="#86868B",
            anchor="w"
        )
        self.preview_stats_label.pack(side="left")
        
        # 表格容器
        table_border_frame = ctk.CTkFrame(
            preview_container,
            fg_color="transparent",
            border_width=1,
            border_color="#E5E5E5",
            corner_radius=12
        )
        table_border_frame.pack(fill="both", expand=True)

        # 内部 Frame 用于裁剪圆角
        table_inner_frame = ctk.CTkFrame(table_border_frame, fg_color="transparent", corner_radius=12)
        table_inner_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # 滚动条
        scrollbar_y = ctk.CTkScrollbar(table_inner_frame, orientation="vertical", button_color="#D1D1D1", button_hover_color="#A0A0A0")
        scrollbar_y.pack(side="right", fill="y")
        
        scrollbar_x = ctk.CTkScrollbar(table_inner_frame, orientation="horizontal", button_color="#D1D1D1", button_hover_color="#A0A0A0")
        scrollbar_x.pack(side="bottom", fill="x")
        
        # Treeview
        self.preview_tree = ttk.Treeview(
            table_inner_frame,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            show="headings",
            style="Modern.Treeview"
        )
        self.preview_tree.pack(side="left", fill="both", expand=True)
        
        scrollbar_y.configure(command=self.preview_tree.yview)
        scrollbar_x.configure(command=self.preview_tree.xview)
        
        # 配置 Treeview 样式
        self._setup_treeview_style()
        
        # SQL 查询区域
        sql_section = ctk.CTkFrame(
            right_container, 
            fg_color="#F5F5F7", # 浅灰色背景区别于白色主背景
            corner_radius=16
        )
        sql_section.grid(row=2, column=0, sticky="ew")
        
        sql_content = ctk.CTkFrame(sql_section, fg_color="transparent")
        sql_content.pack(fill="both", padx=24, pady=20)
        
        # SQL Header
        sql_header = ctk.CTkFrame(sql_content, fg_color="transparent")
        sql_header.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(
            sql_header, 
            text="SQL Query",
            font=ctk.CTkFont(family=self.font_family, size=16, weight="bold"),
            text_color="#1D1D1F"
        ).pack(side="left")
        
        # SQL Input
        self.sql_text = ctk.CTkTextbox(
            sql_content, 
            height=80,
            font=ctk.CTkFont(family="Menlo" if sys.platform == "darwin" else "Consolas", size=13),
            fg_color="#FFFFFF",
            border_color="#E5E5E5",
            border_width=1,
            corner_radius=10,
            text_color="#1D1D1F"
        )
        self.sql_text.pack(fill="x", pady=(0, 16))
        
        # Actions
        actions_row = ctk.CTkFrame(sql_content, fg_color="transparent")
        actions_row.pack(fill="x")
        
        # Run Button (Green Gradient Style - Simulated with solid color)
        # 使用更加鲜艳的绿色 #28C840 (macOS System Green)
        ctk.CTkButton(
            actions_row,
            text="Run Query",
            command=self._execute_query,
            font=ctk.CTkFont(family=self.font_family, size=13, weight="bold"),
            height=36,
            width=120,
            fg_color="#28C840",
            hover_color="#24B33A",
            corner_radius=18, # Pill shape
            text_color="white"
        ).pack(side="left", padx=(0, 12))
        
        # Export Buttons
        export_btn_color = "#FFFFFF"
        export_text_color = "#1D1D1F"
        export_hover_color = "#F0F0F0"

        ctk.CTkButton(
            actions_row,
            text="Export JSON",
            command=lambda: self._export_result("json"),
            font=ctk.CTkFont(family=self.font_family, size=13),
            height=36,
            fg_color=export_btn_color,
            text_color=export_text_color,
            hover_color=export_hover_color,
            border_width=1,
            border_color="#D1D1D1",
            corner_radius=18
        ).pack(side="left", padx=(0, 8))
        
        ctk.CTkButton(
            actions_row,
            text="Export CSV",
            command=lambda: self._export_result("csv"),
            font=ctk.CTkFont(family=self.font_family, size=13),
            height=36,
            fg_color=export_btn_color,
            text_color=export_text_color,
            hover_color=export_hover_color,
            border_width=1,
            border_color="#D1D1D1",
            corner_radius=18
        ).pack(side="left")

    def _setup_treeview_style(self):
        """配置 Treeview 的现代化样式"""
        style = ttk.Style()
        style.theme_use("clam")

        # 字体
        header_font = (self.font_family, 12, 'bold')
        body_font = (self.font_family, 12)

        # 颜色
        bg_color = "#FFFFFF"
        text_color = "#1D1D1F"
        header_bg = "#F5F5F7"
        header_text = "#1D1D1F"
        selected_bg = "#28C840" # macOS Green
        border_color = "#E5E5E5"

        # Treeview 主体
        style.configure("Modern.Treeview",
                      background=bg_color,
                      foreground=text_color,
                      fieldbackground=bg_color,
                      borderwidth=0,
                      rowheight=40,
                      font=body_font)

        # Treeview 表头
        style.configure("Modern.Treeview.Heading",
                       background=header_bg,
                       foreground=header_text,
                       borderwidth=1,
                       relief="flat",
                       font=header_font)

        # 表头悬停效果
        style.map("Modern.Treeview.Heading",
                 background=[('active', '#EAEAEA')])

        # 选中行样式
        style.map("Modern.Treeview",
                 background=[("selected", selected_bg)],
                 foreground=[("selected", "white")])

    def _load_file(self):
        """加载单个文件"""
        file_path = filedialog.askopenfilename(
            title="选择文件",
            filetypes=[
                ("所有支持格式", "*.csv *.parquet *.json"),
                ("CSV 文件", "*.csv"),
                ("Parquet 文件", "*.parquet"),
                ("JSON 文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            # 弹出对话框让用户输入别名
            alias = self._get_file_alias(file_path)
            if alias:
                self._process_file_load(file_path, alias)
    
    def _load_directory(self):
        """加载文件夹"""
        dir_path = filedialog.askdirectory(title="选择文件夹")
        
        if dir_path:
            # 先在主线程中获取表名，然后在后台线程中加载
            from tkinter import simpledialog
            
            default_table_name = self.file_manager.generate_table_name(Path(dir_path).name)
            
            alias = simpledialog.askstring(
                "输入表名",
                f"为文件夹 '{Path(dir_path).name}' 输入表名：\n\n"
                f"表名将用于 SQL 查询，只能包含字母、数字和下划线。\n"
                f"文件夹中的所有文件将被合并为一张表。",
                initialvalue=default_table_name
            )
            
            if alias is None:
                # 用户取消了输入
                return
            
            if not alias:
                alias = default_table_name
            else:
                # 如果用户输入了表名，需要验证并确保不冲突
                alias = self.file_manager.generate_table_name(alias)
            
            # 在新线程中加载，避免界面冻结
            threading.Thread(
                target=self._process_directory_load,
                args=(dir_path, alias),
                daemon=True
            ).start()
    
    def _get_file_alias(self, file_path: str) -> Optional[str]:
        """获取文件别名（弹出输入对话框）"""
        from tkinter import simpledialog
        
        file_name = Path(file_path).stem
        # 生成默认表名作为建议（确保不冲突）
        default_table_name = self.file_manager.generate_table_name(file_name)
        
        # 使用 simpledialog 获取用户输入（直接填入建议表名）
        alias = simpledialog.askstring(
            "输入表名",
            f"为文件 '{Path(file_path).name}' 输入表名：\n\n"
            f"表名将用于 SQL 查询，只能包含字母、数字和下划线。",
            initialvalue=default_table_name
        )
        
        # 如果用户输入了表名，需要验证并确保不冲突
        if alias:
            # 清理表名
            cleaned_alias = self.file_manager.generate_table_name(alias)
            return cleaned_alias
        
        return default_table_name
    
    def _process_file_load(self, file_path: str, alias: str):
        """处理文件加载"""
        table_name = self.file_manager.load_file(file_path, alias)
        
        if table_name:
            self._update_file_list()
            # 自动选中并预览
            self._select_file(file_path)
        else:
            messagebox.showerror("错误", f"文件加载失败：{Path(file_path).name}")
    
    def _process_directory_load(self, dir_path: str, alias: str):
        """处理文件夹加载"""
        try:
            table_name = self.file_manager.load_directory(dir_path, alias)
            
            if table_name:
                # 在主线程中更新界面
                self.root.after(0, lambda: self._update_file_list())
                # 自动选中并预览
                self.root.after(0, lambda fp=dir_path: self._select_file(fp))
            else:
                error_msg = f"无法加载文件夹 '{Path(dir_path).name}'。\n\n可能的原因：\n- 文件夹中没有支持的文件格式（CSV、Parquet、JSON）\n- 文件格式损坏或无法读取\n- 文件权限不足"
                self.root.after(0, lambda msg=error_msg: messagebox.showerror("加载失败", msg))
        except ValueError as e:
            # 格式或schema不一致的错误
            error_msg = f"文件夹格式验证失败：\n\n{str(e)}\n\n请确保：\n1. 文件夹中所有文件格式一致（都是 CSV、Parquet 或 JSON）\n2. 所有文件的内容结构（列/键）完全一致"
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("加载失败", msg))
        except Exception as e:
            # 其他错误
            error_str = str(e)
            if "window" in error_str.lower() and "deleted" in error_str.lower():
                return
            elif "permission" in error_str.lower() or "access" in error_str.lower():
                error_msg = f"无法访问文件夹 '{Path(dir_path).name}'。\n\n请检查：\n- 文件夹是否存在\n- 是否有读取权限"
            elif "not found" in error_str.lower() or "不存在" in error_str:
                error_msg = f"文件夹 '{Path(dir_path).name}' 不存在或已被删除。"
            else:
                error_msg = f"加载文件夹 '{Path(dir_path).name}' 时发生错误。\n\n错误信息：{error_str}\n\n请检查文件夹路径和文件格式是否正确。"
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("加载失败", msg))
    
    def _update_file_list(self):
        """更新文件列表显示"""
        # 清除现有按钮
        for item in self.file_buttons:
            if isinstance(item, dict):
                item['frame'].destroy()
            else:
                item.destroy()
        self.file_buttons.clear()
        
        # 添加新文件按钮
        loaded_files = self.file_manager.get_loaded_files()
        
        for file_path in loaded_files:
            alias = self.file_manager.get_file_alias(file_path)
            # 获取原文件名或文件夹名
            path_obj = Path(file_path)
            original_name = path_obj.name
            
            # 显示格式：别名
            max_name_length = 20
            if len(alias) > max_name_length:
                display_name = alias[:max_name_length-3] + "..."
            else:
                display_name = alias
            
            # 创建列表项容器
            item_frame = ctk.CTkFrame(
                self.file_listbox_frame,
                fg_color="transparent",
                height=40
            )
            item_frame.pack(fill="x", pady=2, padx=4)
            
            # 选中状态背景
            is_selected = (file_path == self.current_file)
            bg_color = "#E5E5E5" if is_selected else "transparent"
            hover_color = "#EAEAEA"

            # 整个 item_frame 模拟成一个按钮的效果比较难，这里用 Button 填充

            # 容器内部布局
            # 删除按钮 (悬停时显示会更好，但这里简化为一直显示但颜色淡)
            delete_btn = ctk.CTkButton(
                item_frame,
                text="×",
                width=24,
                height=24,
                command=lambda fp=file_path: self._delete_file(fp),
                font=ctk.CTkFont(size=16),
                fg_color="transparent",
                hover_color="#E5E5E5",
                text_color="#86868B",
                corner_radius=12
            )
            delete_btn.pack(side="right", padx=(2, 4))

            # 文件按钮
            icon = "📁" if path_obj.is_dir() else "📄"
            
            btn = ctk.CTkButton(
                item_frame,
                text=f"{icon} {display_name}",
                anchor="w",
                height=36,
                command=lambda fp=file_path: self._select_file(fp),
                font=ctk.CTkFont(family=self.font_family, size=13),
                fg_color=bg_color,
                text_color="#1D1D1F",
                hover_color=hover_color,
                corner_radius=6
            )
            btn._file_path = file_path  
            btn.pack(side="left", fill="both", expand=True)
            
            self.file_buttons.append({'frame': item_frame, 'select_btn': btn, 'delete_btn': delete_btn})
    
    def _select_file(self, file_path: str):
        """选中文件并显示预览"""
        self.current_file = file_path
        
        # 更新按钮状态
        for item in self.file_buttons:
            if isinstance(item, dict):
                btn = item['select_btn']
                if hasattr(btn, '_file_path') and btn._file_path == file_path:
                    btn.configure(fg_color="#E5E5E5")  # 选中状态 - 灰色高亮
                    btn.configure(text_color="#1D1D1F")
                elif hasattr(btn, '_file_path'):
                    btn.configure(fg_color="transparent")
                    btn.configure(text_color="#1D1D1F")
        
        # 显示预览
        self._show_preview(file_path)
    
    def _delete_file(self, file_path: str):
        """删除文件"""
        if messagebox.askyesno("确认删除", f"确定要删除文件 '{Path(file_path).name}' 吗？"):
            # 卸载文件
            if self.file_manager.unload_file(file_path):
                # 如果删除的是当前选中的文件，清除预览
                if self.current_file == file_path:
                    self.current_file = None
                    self._clear_preview()
                
                # 更新文件列表
                self._update_file_list()
                # messagebox.showinfo("成功", "文件已删除")
            else:
                messagebox.showerror("错误", "删除文件失败")
    
    def _clear_preview(self):
        """清空预览内容"""
        # 清空表格
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        self.preview_tree["columns"] = []
        # 清空统计信息
        self.preview_stats_label.configure(text="")
        # 清空当前显示数据
        self.current_display_data = None
    
    def _show_preview(self, file_path: str, data: Optional[List[Dict[str, Any]]] = None, max_rows: int = 10):
        """显示文件预览（表格样式）"""
        if data is None:
            preview_data = self.file_manager.get_file_preview(file_path, max_rows=max_rows)
            self.current_display_data = preview_data
        else:
            self.current_display_data = data
            preview_data = data[:max_rows] if data else []
        
        # 清空表格
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        self.preview_tree["columns"] = []
        
        if preview_data is None:
            self.preview_stats_label.configure(text="无法加载预览数据")
            return
        
        if not preview_data:
            self.preview_stats_label.configure(text="文件为空")
            return
        
        # 获取列名
        headers = list(preview_data[0].keys())
        
        # 配置表格列
        self.preview_tree["columns"] = headers
        for header in headers:
            self.preview_tree.heading(header, text=header)
            self.preview_tree.column(header, width=150, anchor="w", stretch=False, minwidth=100)
        
        # 插入数据行
        for row in preview_data:
            formatted_values = []
            for h in headers:
                value = row.get(h, "")
                if isinstance(value, float) and value.is_integer():
                    formatted_value = str(int(value))
                else:
                    formatted_value = str(value)
                formatted_values.append(formatted_value[:100])
            self.preview_tree.insert("", "end", values=formatted_values)
        
        # 获取表信息并显示统计
        table_name = self.file_manager.loaded_files.get(file_path)
        total_rows = 0
        total_cols = len(headers)
        display_rows = len(preview_data)
        
        if table_name:
            info = self.file_manager.get_table_info(table_name)
            if info:
                total_rows = info['row_count']
        
        # 更新统计信息标签
        stats_text = f"Total: {total_rows} rows, {total_cols} cols | Showing: {display_rows}"
        self.preview_stats_label.configure(text=stats_text)
    
    def _execute_query(self):
        """执行 SQL 查询"""
        sql = self.sql_text.get("1.0", "end-1c").strip()
        
        if not sql:
            messagebox.showwarning("警告", "请输入 SQL 查询语句")
            return
        
        # 执行查询
        result = self.db_manager.execute_query_dict(sql)
        
        if result is None:
            self._clear_preview()
            error_msg = self.db_manager.get_last_error()
            if error_msg:
                messagebox.showerror("查询失败", f"SQL 查询执行失败：\n\n{error_msg}")
            else:
                messagebox.showerror("查询失败", "SQL 查询执行失败")
            return
        
        if self.current_file:
            self._show_preview(self.current_file, data=result, max_rows=10)
            
            total_rows = len(result)
            if result:
                total_cols = len(result[0].keys())
                display_rows = min(10, total_rows)
                stats_text = f"Result: {total_rows} rows, {total_cols} cols | Showing: {display_rows}"
                self.preview_stats_label.configure(text=stats_text)
        else:
            # 如果没有选中文件，但执行了查询（比如 select 1），也应该显示
            # 这里简单处理，如果有结果就显示
            if result:
                # 临时造一个 dummy file path
                self._show_preview("query_result", data=result, max_rows=10)
                total_rows = len(result)
                total_cols = len(result[0].keys())
                display_rows = min(10, total_rows)
                stats_text = f"Result: {total_rows} rows, {total_cols} cols | Showing: {display_rows}"
                self.preview_stats_label.configure(text=stats_text)

    def _export_result(self, format_type: str):
        """导出当前显示的数据（预览或查询结果）"""
        if self.current_display_data is None or not self.current_display_data:
            messagebox.showwarning("警告", "没有可导出的数据")
            return
        
        # 选择保存路径
        if format_type == "json":
            file_path = filedialog.asksaveasfilename(
                title="保存为 JSON",
                defaultextension=".json",
                filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
            )
            if file_path:
                self._export_to_json(file_path)
        elif format_type == "csv":
            file_path = filedialog.asksaveasfilename(
                title="保存为 CSV",
                defaultextension=".csv",
                filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")]
            )
            if file_path:
                self._export_to_csv(file_path)
    
    def _export_to_json(self, file_path: str):
        """导出为 JSONL 格式（每行一条记录）"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for record in self.current_display_data:
                    # 每行写入一个JSON对象
                    json.dump(record, f, ensure_ascii=False)
                    f.write('\n')
            messagebox.showinfo("成功", f"结果已导出到：{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{e}")
    
    def _export_to_csv(self, file_path: str):
        """导出为 CSV 格式"""
        try:
            if not self.current_display_data:
                return
            
            headers = list(self.current_display_data[0].keys())
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(self.current_display_data)
            
            messagebox.showinfo("成功", f"结果已导出到：{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{e}")
    
    def _on_closing(self):
        """窗口关闭事件处理"""
        self.db_manager.close()
        self.root.destroy()
    
    def run(self):
        """运行应用"""
        self.root.mainloop()
