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
        # 主容器 - 现代化背景渐变效果
        main_container = ctk.CTkFrame(self.root, fg_color="#F8F9FA")
        main_container.pack(fill="both", expand=True)
        
        # 左侧：优雅的侧边栏 (参考图片风格)
        left_panel = ctk.CTkFrame(
            main_container, 
            width=280, 
            fg_color="#4CAF50",  # 优雅的绿色主题
            corner_radius=0
        )
        left_panel.pack(side="left", fill="both", padx=0, pady=0)
        left_panel.pack_propagate(False)
        
        # Logo 和标题区域
        header_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(30, 20))
        
        # 应用图标和名称
        app_title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        app_title_frame.pack(fill="x")
        
        # 加载并显示 logo 图标
        try:
            from PIL import Image
            logo_path = Path(__file__).parent / "file/logo.tiff"
            if logo_path.exists():
                logo_image = Image.open(str(logo_path))
                # 调整图片大小为 32x32
                logo_image = logo_image.resize((32, 32), Image.Resampling.LANCZOS)
                logo_ctk = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(32, 32))
                
                ctk.CTkLabel(
                    app_title_frame,
                    image=logo_ctk,
                    text=""
                ).pack(side="left", padx=(0, 10))
            else:
                # 如果 logo 不存在，使用 emoji 作为备用
                ctk.CTkLabel(
                    app_title_frame,
                    text="📊",
                    font=ctk.CTkFont(size=32),
                ).pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"无法加载 logo: {e}")
            # 使用 emoji 作为备用
            ctk.CTkLabel(
                app_title_frame,
                text="📊",
                font=ctk.CTkFont(size=32),
            ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            app_title_frame,
            text="FViewer",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        ).pack(side="left")
        
        # 文件列表标题
        file_header = ctk.CTkFrame(left_panel, fg_color="transparent")
        file_header.pack(fill="x", padx=20, pady=(20, 15))
        
        ctk.CTkLabel(
            file_header, 
            text="LIBRARY", 
            font=ctk.CTkFont(size=11, weight="bold"), 
            text_color="#E8E8E8",  # 半透明白色的实际效果
            anchor="w"
        ).pack(fill="x")
        
        # 添加文件按钮容器
        button_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # 添加文件按钮 - 现代风格
        ctk.CTkButton(
            button_frame, 
            text="📄 Add File", 
            width=120,
            height=36,
            command=self._load_file,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#66BB6B",  # 半透明白色在绿色背景上的效果
            text_color="white",
            hover_color="#80C784",  # 更亮的半透明效果
            corner_radius=8
        ).pack(side="left", padx=(0, 8), expand=True, fill="x")
        
        # 添加文件夹按钮
        ctk.CTkButton(
            button_frame, 
            text="📁 Add Folder", 
            width=120, 
            height=36,
            command=self._load_directory,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#66BB6B",  # 半透明白色在绿色背景上的效果
            text_color="white",
            hover_color="#80C784",  # 更亮的半透明效果
            corner_radius=8
        ).pack(side="left", expand=True, fill="x")
        
        # 文件列表容器
        self.file_listbox_frame = ctk.CTkScrollableFrame(
            left_panel, 
            fg_color="transparent",
            scrollbar_button_color="#80C784"  # 半透明白色在绿色背景上
        )
        self.file_listbox_frame.pack(fill="both", expand=True, padx=10, pady=0)
        
        self.file_buttons: List[Dict] = []
        
        # 右侧：主内容区域
        right_container = ctk.CTkFrame(main_container, fg_color="transparent")
        right_container.pack(side="right", fill="both", expand=True, padx=25, pady=25)
        
        # 使用 Grid 布局管理右侧区域，确保布局稳定
        right_container.grid_rowconfigure(1, weight=1)
        right_container.grid_columnconfigure(0, weight=1)
        
        # 顶部标题栏
        top_bar = ctk.CTkFrame(right_container, fg_color="transparent", height=60)
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        top_bar.pack_propagate(False)
        
        ctk.CTkLabel(
            top_bar,
            text="Data Preview",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#1F2937",
            anchor="w"
        ).pack(side="left", fill="y")
        
        # 文件预览区域 - 卡片风格
        preview_card = ctk.CTkFrame(
            right_container, 
            fg_color="white",
            corner_radius=16,
            border_width=1,
            border_color="#E5E7EB"
        )
        preview_card.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        
        # 卡片内容容器
        preview_content = ctk.CTkFrame(preview_card, fg_color="transparent")
        preview_content.pack(fill="both", expand=True, padx=25, pady=20)
        
        # 统计信息
        preview_header = ctk.CTkFrame(preview_content, fg_color="transparent")
        preview_header.pack(fill="x", pady=(0, 15))
        
        # 统计信息标签
        self.preview_stats_label = ctk.CTkLabel(
            preview_header,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="#6B7280",
            anchor="w"
        )
        self.preview_stats_label.pack(side="left", fill="x")
        
        # 表格容器 - 圆角边框
        table_container = ctk.CTkFrame(
            preview_content, 
            fg_color="#F9FAFB",
            corner_radius=12,
            border_width=1,
            border_color="#E5E7EB"
        )
        table_container.pack(fill="both", expand=True)
        
        # 表格框架
        tree_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # 滚动条 - 现代风格
        scrollbar_y = ctk.CTkScrollbar(tree_frame, orientation="vertical")
        scrollbar_y.pack(side="right", fill="y")
        
        scrollbar_x = ctk.CTkScrollbar(tree_frame, orientation="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")
        
        # Treeview表格
        self.preview_tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            show="headings"
        )
        self.preview_tree.pack(side="left", fill="both", expand=True)
        
        scrollbar_y.configure(command=self.preview_tree.yview)
        scrollbar_x.configure(command=self.preview_tree.xview)
        
        # 配置表格样式 - 优雅的现代风格
        style = ttk.Style()
        style.theme_use("clam")
        
        # 表格主体样式
        style.configure("Treeview", 
                      background="#FFFFFF",
                      foreground="#374151",
                      fieldbackground="#FFFFFF",
                      borderwidth=1,
                      relief="solid",
                      rowheight=38,
                      font=('SF Pro', 12))
        
        # 表头样式 - 更突出
        style.configure("Treeview.Heading",
                       background="#F3F4F6",
                       foreground="#1F2937",
                       borderwidth=1,
                       relief="solid",
                       font=('SF Pro', 11, 'bold'),
                       padding=10)
        
        style.map("Treeview.Heading",
                 background=[('active', '#E5E7EB')])
        
        # 选中行样式 - 优雅的蓝色
        style.map("Treeview",
                 background=[("selected", "#4CAF50")],
                 foreground=[("selected", "white")])
        
        self.preview_tree.configure(style="Treeview")
        
        # SQL 查询区域 - 卡片风格
        sql_card = ctk.CTkFrame(
            right_container, 
            fg_color="white",
            corner_radius=16,
            border_width=1,
            border_color="#E5E7EB"
        )
        sql_card.grid(row=2, column=0, sticky="ew")
        
        sql_content = ctk.CTkFrame(sql_card, fg_color="transparent")
        sql_content.pack(fill="both", padx=25, pady=20)
        
        # 查询标题
        sql_header = ctk.CTkFrame(sql_content, fg_color="transparent")
        sql_header.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(
            sql_header, 
            text="⚡ SQL Query", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1F2937"
        ).pack(side="left")
        
        # SQL 输入框 - 现代化样式
        self.sql_text = ctk.CTkTextbox(
            sql_content, 
            height=90,
            font=ctk.CTkFont(family="Monaco", size=13),
            fg_color="#F9FAFB",
            border_color="#E5E7EB",
            border_width=1,
            corner_radius=10,
            text_color="#1F2937"
        )
        self.sql_text.pack(fill="x", pady=(0, 15))
        
        # 按钮容器
        button_frame = ctk.CTkFrame(sql_content, fg_color="transparent")
        button_frame.pack(fill="x")
        
        # 运行查询按钮 - 主要动作
        ctk.CTkButton(
            button_frame, 
            text="▶ Run Query", 
            command=self._execute_query,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="#4CAF50", 
            hover_color="#45A049",
            corner_radius=10,
            text_color="white"
        ).pack(side="left", padx=(0, 12))
        
        # 导出 JSON 按钮
        ctk.CTkButton(
            button_frame, 
            text="📄 Export JSON", 
            command=lambda: self._export_result("json"),
            font=ctk.CTkFont(size=13),
            height=40,
            fg_color="#F9FAFB",
            text_color="#374151",
            hover_color="#E5E7EB",
            border_width=1,
            border_color="#D1D5DB",
            corner_radius=10
        ).pack(side="left", padx=(0, 12))
        
        # 导出 CSV 按钮
        ctk.CTkButton(
            button_frame, 
            text="📊 Export CSV", 
            command=lambda: self._export_result("csv"),
            font=ctk.CTkFont(size=13),
            height=40,
            fg_color="#F9FAFB",
            text_color="#374151",
            hover_color="#E5E7EB",
            border_width=1,
            border_color="#D1D5DB",
            corner_radius=10
        ).pack(side="left")
    
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
            # messagebox.showinfo("成功", f"文件加载成功！\n别名: {alias}\n表名: {table_name}")
            
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
                success_msg = f"文件夹加载成功！\n别名: {alias}\n表名: {table_name}"
                # self.root.after(0, lambda msg=success_msg: messagebox.showinfo("成功", msg))
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
            # 过滤掉技术性的错误信息，提供更友好的提示
            if "window" in error_str.lower() and "deleted" in error_str.lower():
                # 忽略窗口相关的错误（这些通常是 Tkinter 的内部错误，不影响功能）
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
            if path_obj.is_dir():
                original_name = path_obj.name
            else:
                original_name = path_obj.name
            
            # 显示格式：别名(文件名)，处理文件名过长
            max_name_length = 30  # 最大文件名显示长度
            if len(original_name) > max_name_length:
                display_name = original_name[:max_name_length-3] + "..."
            else:
                display_name = original_name
            display_text = f"{alias}({display_name})"
            
            # 创建列表项容器 - 现代风格
            item_frame = ctk.CTkFrame(
                self.file_listbox_frame,
                fg_color="transparent"
            )
            item_frame.pack(fill="x", pady=3, padx=5)
            
            # 删除按钮 - 圆形图标（放在最左侧）
            delete_btn = ctk.CTkButton(
                item_frame,
                text="X",
                width=24,
                height=32,
                command=lambda fp=file_path: self._delete_file(fp),
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#F44336",  # 红色
                hover_color="#C62828",  # 深红色
                text_color="white",
                corner_radius=8
            )
            delete_btn.pack(side="left", padx=(0, 5))
            
            # 文件按钮 - 优雅的侧边栏风格
            btn = ctk.CTkButton(
                item_frame,
                text=f"  📄 {display_text}",
                anchor="w",
                height=42,
                command=lambda fp=file_path: self._select_file(fp),
                font=ctk.CTkFont(size=13),
                fg_color="#73C177" if file_path == self.current_file else "transparent",
                text_color="white",
                hover_color="#5CB560",  # 悬停时的半透明效果
                corner_radius=8
            )
            btn._file_path = file_path  
            btn._full_text = f"{alias}({original_name})"
            btn.pack(side="left", fill="both", expand=True)
            
            self.file_buttons.append({'frame': item_frame, 'select_btn': btn, 'delete_btn': delete_btn})
            
            # 设置选中状态样式
            if file_path == self.current_file:
                btn.configure(fg_color="#73C177")
            else:
                btn.configure(fg_color="transparent")
    
    def _select_file(self, file_path: str):
        """选中文件并显示预览"""
        self.current_file = file_path
        
        # 更新按钮状态 - 现代风格
        for item in self.file_buttons:
            if isinstance(item, dict):
                btn = item['select_btn']
                if hasattr(btn, '_file_path') and btn._file_path == file_path:
                    btn.configure(fg_color="#73C177")  # 选中状态
                elif hasattr(btn, '_file_path'):
                    btn.configure(fg_color="transparent")
        
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
                    # 清空预览
                    for item in self.preview_tree.get_children():
                        self.preview_tree.delete(item)
                    self.preview_tree["columns"] = []
                    self.preview_stats_label.configure(text="")
                    self.current_display_data = None
                
                # 更新文件列表
                self._update_file_list()
                messagebox.showinfo("成功", "文件已删除")
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
        # 如果提供了数据，使用提供的数据；否则从文件管理器获取
        if data is None:
            preview_data = self.file_manager.get_file_preview(file_path, max_rows=max_rows)
            # 保存完整预览数据（用于导出）
            self.current_display_data = preview_data
        else:
            # 保存完整的查询结果数据（用于导出）
            self.current_display_data = data
            # 只显示前max_rows行
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
            # 设置列宽，并确保列之间有分隔
            self.preview_tree.column(header, width=150, anchor="w", stretch=False, minwidth=100)
        
        # 插入数据行，处理整型字段的显示
        for row in preview_data:
            formatted_values = []
            for h in headers:
                value = row.get(h, "")
                # 如果是浮点数且是整数（如 123.0），转换为整数显示
                if isinstance(value, float) and value.is_integer():
                    formatted_value = str(int(value))
                else:
                    formatted_value = str(value)
                formatted_values.append(formatted_value[:100])  # 限制每列显示长度
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
        stats_text = f"总行数: {total_rows} | 总列数: {total_cols} | 当前显示: {display_rows} 行"
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
            # 查询失败时清空预览内容
            self._clear_preview()
            # 获取更详细的错误信息
            error_msg = self.db_manager.get_last_error()
            if error_msg:
                messagebox.showerror("查询失败", f"SQL 查询执行失败：\n\n{error_msg}\n\n请检查 SQL 语句是否正确，或确认表名是否存在。")
            else:
                messagebox.showerror("查询失败", "SQL 查询执行失败，请检查 SQL 语句是否正确。")
            return
        
        # 查询结果直接显示在预览区域（替代文件预览）
        if self.current_file:
            # 显示查询结果，最多显示10行（但保存完整结果用于导出）
            self._show_preview(self.current_file, data=result, max_rows=10)
            
            # 更新统计信息（显示查询结果的总行数）
            total_rows = len(result)
            if result:
                total_cols = len(result[0].keys())
                display_rows = min(10, total_rows)
                stats_text = f"查询结果 - 总行数: {total_rows} | 总列数: {total_cols} | 当前显示: {display_rows} 行"
                self.preview_stats_label.configure(text=stats_text)
        else:
            messagebox.showwarning("警告", "请先加载文件")
    
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

