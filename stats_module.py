"""
统计图表模块
作者：E
功能说明：记忆曲线图、正确率柱状图、词书进度
"""
import tkinter as tk
from tkinter import ttk


class StatsPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        label = ttk.Label(self, text="学习统计 - 开发中", font=("微软雅黑", 16))
        label.pack(pady=50)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("测试 - 学习统计")
    root.geometry("800x600")
    page = StatsPage(root)
    page.pack(fill="both", expand=True)
    root.mainloop()