"""
单词记忆助手 - 程序入口
作者：全体成员
"""
import tkinter as tk
from mainwindow import MainWindow


def main():
    root = tk.Tk()
    root.title("单词记忆助手")
    root.geometry("1024x680")
    app = MainWindow(root)
    app.pack(fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    main()