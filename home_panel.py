"""
首页面板模块
作者：E
功能说明：今日待复习数量、开始复习按钮、快捷入口
"""
import tkinter as tk
from tkinter import ttk
import db_manager

class HomePage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # 卡片容器（三个数据卡片）
        self.card_container = ttk.Frame(self)
        self.card_container.pack(fill="x", padx=40, pady=40)

        # 三个卡片
        self.today_frame = self._make_card(self.card_container, "📚 今日待复习", "0")
        self.today_frame.pack(side="left", expand=True, fill="both", padx=10)

        self.streak_frame = self._make_card(self.card_container, "🔥 连续打卡", "0")
        self.streak_frame.pack(side="left", expand=True, fill="both", padx=10)

        self.wordbook_frame = self._make_card(self.card_container, "📖 词书数量", "0")
        self.wordbook_frame.pack(side="left", expand=True, fill="both", padx=10)

        # 快捷按钮区
        btn_frame = ttk.LabelFrame(self, text="快捷练习", padding=10)
        btn_frame.pack(fill="x", padx=40, pady=20)

        self.choice_btn = ttk.Button(btn_frame, text="选择题练习")
        self.choice_btn.pack(side="left", padx=20, pady=10)

        self.fill_btn = ttk.Button(btn_frame, text="填空练习")
        self.fill_btn.pack(side="left", padx=20, pady=10)

        self.dict_btn = ttk.Button(btn_frame, text="听写练习")
        self.dict_btn.pack(side="left", padx=20, pady=10)

    def _make_card(self, parent, title, value):
        """创建一个数据卡片"""
        frame = ttk.Frame(parent, relief="ridge", padding=20)
        title_label = ttk.Label(frame, text=title, font=("Arial", 12))
        title_label.pack()
        value_label = ttk.Label(frame, text=value, font=("Arial", 24, "bold"))
        value_label.pack(pady=10)
        # 保存value_label以便后面更新
        frame.value_label = value_label
        return frame

    def refresh(self):
        """刷新首页数据"""
        # 从数据库获取数据
        today_words = db_manager.get_today_review_words()
        streak = db_manager.get_streak_days()
        wordbooks = db_manager.get_all_wordbooks()

        # 更新卡片数值
        self.today_frame.value_label.config(text=str(len(today_words)))
        self.streak_frame.value_label.config(text=str(streak))
        self.wordbook_frame.value_label.config(text=str(len(wordbooks)))

    # 以下三个方法供主窗口（F同学）调用，绑定跳转功能
    def set_choice_callback(self, callback):
        self.choice_btn.config(command=callback)

    def set_fill_callback(self, callback):
        self.fill_btn.config(command=callback)

    def set_dict_callback(self, callback):
        self.dict_btn.config(command=callback)


# 单独测试用
if __name__ == "__main__":
    root = tk.Tk()
    root.title("首页测试")
    root.geometry("800x600")
    page = HomePage(root)
    page.pack(fill="both", expand=True)
    root.mainloop()