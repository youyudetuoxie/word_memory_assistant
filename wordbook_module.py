"""
词库管理模块
作者：B
功能说明：CSV词书导入、手动添加单词、词书列表管理
"""
import tkinter as tk
from tkinter import ttk


class WordbookPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        label = ttk.Label(self, text="词库管理 - 开发中", font=("微软雅黑", 16))
        label.pack(pady=50)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("测试 - 词库管理")
    root.geometry("800x600")
    page = WordbookPage(root)
    page.pack(fill="both", expand=True)
    root.mainloop()