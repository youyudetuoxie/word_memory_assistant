"""
程序入口
作者：田鑫（组长）
功能：初始化数据库，启动主窗口
"""

import tkinter as tk
import db_manager


def main():
    # 1. 初始化数据库（首次运行时自动建表）
    db_manager.init_db()

    # 2. 创建主窗口
    root = tk.Tk()
    root.title("单词记忆助手")
    root.geometry("1024x680")
    root.minsize(900, 600)

    # 3. 加载主界面（由 F 同学完成后取消注释下方代码）
    try:
        from mainwindow import MainWindow
        app = MainWindow(root)
        app.pack(fill="both", expand=True)
    except ImportError:
        # mainwindow.py 尚未完成时的占位界面
        import tkinter.ttk as ttk
        ttk.Label(
            root,
            text="主窗口 - 开发中\n\n数据库已初始化完成",
            font=("微软雅黑", 16),
            anchor="center"
        ).pack(expand=True)

    # 4. 居中显示窗口
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()