"""
主窗口框架与导航模块
作者：F
功能说明：左侧导航栏，右侧Frame切换，顶栏显示词书名和日期
"""
import tkinter as tk
from tkinter import ttk


class MainWindow(ttk.Frame):
    """主窗口"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self._build_ui()

    def _build_ui(self):
        label = ttk.Label(self, text="主窗口 - 开发中", font=("微软雅黑", 20))
        label.pack(pady=50)