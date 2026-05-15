"""
首页面板模块
作者：E
功能说明：今日待复习数量、开始复习按钮、快捷入口
"""
import tkinter as tk
from tkinter import ttk


class HomePage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        label = ttk.Label(self, text="首页 - 开发中", font=("微软雅黑", 16))
        label.pack(pady=50)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("测试 - 首页")
    root.geometry("800x600")
    page = HomePage(root)
    page.pack(fill="both", expand=True)
    root.mainloop()