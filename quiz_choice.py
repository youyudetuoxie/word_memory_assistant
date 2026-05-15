"""
选择题练习模块
作者：C
功能说明：4选1选择题，即时反馈，更新熟悉度
"""
import tkinter as tk
from tkinter import ttk


class QuizChoicePage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        label = ttk.Label(self, text="选择题练习 - 开发中", font=("微软雅黑", 16))
        label.pack(pady=50)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("测试 - 选择题练习")
    root.geometry("800x600")
    page = QuizChoicePage(root)
    page.pack(fill="both", expand=True)
    root.mainloop()