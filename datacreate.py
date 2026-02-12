import customtkinter as ctk
import pandas as pd
import numpy as np
from tkinter import filedialog, messagebox

# 设定外观模式与颜色主题
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class StatisticalSimulationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 窗口基础设定
        self.title("结构方程模型数据模拟器")
        self.geometry("900x850") 
        
        # 定义配色方案
        self.colors = {
            "bg": "#FFFBE6",         # 奶油白背景
            "card": "#FFFFFF",       # 纯白卡片
            "primary": "#A0C4FF",    # 淡蓝
            "secondary": "#FFB7B2",  # 淡粉
            "accent": "#B5EAD7",     # 薄荷绿
            "text": "#555555",       # 深灰字体
            "highlight": "#FFD93D"   # 高亮色
        }
        
        self.configure(fg_color=self.colors["bg"])
        
        # 数据存储容器
        self.variable_entries = [] 
        self.is_chain_mediation = None 

        # 初始化界面布局
        self._init_ui()

    def _init_ui(self):
        # 顶部标题
        self.header_label = ctk.CTkLabel(
            self, 
            text="数据模拟器 (Data Simulator) 📅", 
            font=("Microsoft YaHei UI", 24, "bold"),
            text_color=self.colors["text"]
        )
        self.header_label.pack(pady=(20, 10))

        # 1. 全局参数设置卡片
        self.settings_frame = self._create_card_frame(self)
        self.settings_frame.pack(pady=10, padx=20, fill="x")

        # 样本量输入
        self._create_input_row(self.settings_frame, "设定样本量 (N)", "entry_n", "1243")
        
        # 变量数量输入
        self.grid_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.grid_frame.pack(fill="x", padx=10, pady=10)
        
        self.entry_iv_count = self._create_compact_input(self.grid_frame, "自变量个数", "1", 0)
        self.entry_med_count = self._create_compact_input(self.grid_frame, "中介变量个数", "2", 1)
        self.entry_dv_count = self._create_compact_input(self.grid_frame, "因变量个数", "1", 2)

        # 确认配置按钮
        self.btn_confirm = ctk.CTkButton(
            self.settings_frame,
            text="生成变量配置表 ⚙️",
            command=self.generate_config_fields,
            fg_color=self.colors["primary"],
            hover_color="#8AB3EE",
            corner_radius=20,
            font=("Microsoft YaHei UI", 14, "bold")
        )
        self.btn_confirm.pack(pady=15)

        # 2. 滚动区域
        self.scroll_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent", 
            corner_radius=0
        )
        self.scroll_frame.pack(expand=True, fill="both", padx=10)

        # 3. 底部操作区
        self.action_frame = ctk.CTkFrame(self, fg_color=self.colors["bg"])
        self.action_frame.pack(fill="x", pady=20)
        
        self.btn_generate = ctk.CTkButton(
            self.action_frame,
            text="开始模拟并导出 Excel 📂",
            command=self.run_simulation,
            fg_color=self.colors["secondary"],
            hover_color="#FF9E99",
            height=50,
            width=300,
            corner_radius=25,
            font=("Microsoft YaHei UI", 16, "bold")
        )
        self.btn_generate.pack()

    def _create_card_frame(self, parent):
        return ctk.CTkFrame(
            parent, 
            fg_color=self.colors["card"], 
            corner_radius=20, 
            border_width=1, 
            border_color="#EEEEEE"
        )

    def _create_input_row(self, parent, label_text, attr_name, default_val):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)
        
        label = ctk.CTkLabel(
            frame, 
            text=f"🔍 {label_text}", 
            font=("Microsoft YaHei UI", 14),
            text_color=self.colors["text"],
            anchor="w"
        )
        label.pack(side="left", padx=10)
        
        entry = ctk.CTkEntry(
            frame, 
            width=150, 
            border_color=self.colors["primary"],
            corner_radius=10
        )
        entry.insert(0, default_val)
        entry.pack(side="right")
        setattr(self, attr_name, entry)

    def _create_compact_input(self, parent, label_text, default_val, col_idx):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col_idx, padx=10, sticky="ew")
        parent.grid_columnconfigure(col_idx, weight=1)
        
        label = ctk.CTkLabel(
            frame, 
            text=label_text, 
            font=("Microsoft YaHei UI", 12), 
            text_color=self.colors["text"]
        )
        label.pack()
        
        entry = ctk.CTkEntry(
            frame, 
            justify="center", 
            border_color=self.colors["primary"],
            corner_radius=10
        )
        entry.insert(0, default_val)
        entry.pack(fill="x", pady=5)
        return entry

    def generate_config_fields(self):
        # 清空现有控件
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.variable_entries = []
        self.is_chain_mediation = None

        try:
            n_iv = int(self.entry_iv_count.get())
            n_med = int(self.entry_med_count.get())
            n_dv = int(self.entry_dv_count.get())
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字")
            return

        def add_section(title, count, prefix, icon, color_theme):
            if count <= 0: return
            
            section_frame = self._create_card_frame(self.scroll_frame)
            section_frame.pack(pady=10, padx=10, fill="x")
            
            # --- 标题栏区域 ---
            header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=15, pady=10)

            title_label = ctk.CTkLabel(
                header_frame, 
                text=f"{icon} {title}信息", 
                font=("Microsoft YaHei UI", 15, "bold"),
                text_color=self.colors["text"],
                anchor="w"
            )
            title_label.pack(side="left")

            # --- 修正点：参数名 onvalue/offvalue (无下划线) ---
            if prefix == "M":
                self.chain_var = ctk.StringVar(value="off")
                switch = ctk.CTkSwitch(
                    header_frame, 
                    text="开启链式中介 (Chain)",
                    variable=self.chain_var, 
                    onvalue="on",   # 修正: on_value -> onvalue
                    offvalue="off", # 修正: off_value -> offvalue
                    progress_color=self.colors["highlight"],
                    font=("Microsoft YaHei UI", 12)
                )
                switch.pack(side="right")
                self.is_chain_mediation = self.chain_var
            # -----------------------------------------------
            
            for i in range(count):
                row = ctk.CTkFrame(section_frame, fg_color="transparent")
                row.pack(fill="x", padx=10, pady=5)
                
                ctk.CTkLabel(row, text=f"变量名", width=50).pack(side="left")
                name_entry = ctk.CTkEntry(row, width=120, corner_radius=10)
                name_entry.insert(0, f"{prefix}{i+1}")
                name_entry.pack(side="left", padx=5)
                
                ctk.CTkLabel(row, text="题目数", width=50).pack(side="left")
                item_entry = ctk.CTkEntry(row, width=60, corner_radius=10)
                item_entry.insert(0, "3" if prefix=="IV" else "4") 
                item_entry.pack(side="left", padx=5)
                
                scale_options = [f"{k}级量表" for k in range(1, 11)]
                scale_menu = ctk.CTkOptionMenu(
                    row, 
                    values=scale_options,
                    fg_color=color_theme,
                    button_color=color_theme,
                    text_color="#FFFFFF",
                    width=110 
                )
                scale_menu.set("5级量表")
                scale_menu.pack(side="right", padx=5)

                self.variable_entries.append({
                    "type": prefix,
                    "name": name_entry,
                    "items": item_entry,
                    "scale": scale_menu
                })

        add_section("自变量", n_iv, "IV", "🌱", self.colors["primary"])
        add_section("中介变量", n_med, "M", "🔗", self.colors["accent"])
        add_section("因变量", n_dv, "Y", "🎯", self.colors["secondary"])

    def run_simulation(self):
        try:
            N = int(self.entry_n.get())
            if not self.variable_entries:
                messagebox.showwarning("提示", "请先配置变量信息")
                return
        except ValueError:
            messagebox.showerror("错误", "样本量必须为整数")
            return

        config_list = []
        for entry in self.variable_entries:
            scale_str = entry["scale"].get()
            scale_val = int(scale_str.replace("级量表", ""))
            
            config_list.append({
                "name": entry["name"].get(),
                "n_items": int(entry["items"].get()),
                "points": scale_val,
                "type": entry["type"]
            })
        
        total_vars = len(config_list)
        
        mean = np.zeros(total_vars)
        
        use_chain = False
        if self.is_chain_mediation is not None and self.is_chain_mediation.get() == "on":
            use_chain = True

        if use_chain:
            cov_matrix = np.full((total_vars, total_vars), 0.2) 
            np.fill_diagonal(cov_matrix, 1.0)
            
            for i in range(total_vars - 1):
                cov_matrix[i, i+1] = 0.6
                cov_matrix[i+1, i] = 0.6
                
                if i + 2 < total_vars:
                     cov_matrix[i, i+2] = 0.35
                     cov_matrix[i+2, i] = 0.35
            print("Mode: 链式中介 (Chain Mediation) 已启用")
        else:
            cov_matrix = np.full((total_vars, total_vars), 0.4)
            np.fill_diagonal(cov_matrix, 1.0)
            print("Mode: 普通/平行模式 (Standard) 已启用")

        np.random.seed(2026) 
        try:
            latent_scores = np.random.multivariate_normal(mean, cov_matrix, N)
        except ValueError:
            latent_scores = np.random.multivariate_normal(mean, np.eye(total_vars), N)
            print("Warning: 矩阵非正定，回退到单位矩阵")

        final_data = {}
        
        def generate_items_logic(latent_vector, item_count, points):
            loading = 0.85
            error_std = np.sqrt(1 - loading**2)
            
            items_matrix = np.zeros((N, item_count))
            for i in range(item_count):
                raw = loading * latent_vector + error_std * np.random.normal(0, 1, N)
                
                bins = np.linspace(0, 100, points + 1)
                bins = [np.percentile(raw, b) for b in bins]
                bins[0] = -np.inf
                bins[-1] = np.inf
                
                items_matrix[:, i] = pd.cut(raw, bins=bins, labels=False) + 1
            return items_matrix

        for idx, conf in enumerate(config_list):
            var_name = conf['name']
            n_items = conf['n_items']
            scale_points = conf['points']
            
            items_data = generate_items_logic(latent_scores[:, idx], n_items, scale_points)
            
            for i in range(n_items):
                col_name = f"{var_name}{i+1}"
                final_data[col_name] = items_data[:, i]

        df = pd.DataFrame(final_data)
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="保存模拟数据"
        )
        
        if file_path:
            try:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("成功", f"数据已成功导出！\n模式：{'链式' if use_chain else '普通'}\n路径: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")

if __name__ == "__main__":
    app = StatisticalSimulationApp()
    app.mainloop()