"""
填空练习模块
作者：D
功能说明：英→中填空、中→英拼写、听写模式
"""
import tkinter as tk
from tkinter import ttk


class QuizInputPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        label = ttk.Label(self, text="填空练习 - 开发中", font=("微软雅黑", 16))
        label.pack(pady=50)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("测试 - 填空练习")
    root.geometry("800x600")
    page = QuizInputPage(root)
    page.pack(fill="both", expand=True)
    root.mainloop()