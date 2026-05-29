"""
统计图表模块
作者：E
功能说明：记忆曲线图、正确率柱状图、词书进度
"""
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 修正：sans-serif 不是 sans_serif，且要用列表
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import db_manager

class StatsPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # 顶部卡片区
        self.card_frame = ttk.LabelFrame(self, text="学习概况", padding=10)
        self.card_frame.pack(fill="x", padx=20, pady=10)

        self.streak_label = ttk.Label(self.card_frame, text="连续打卡: -- 天", font=("Arial", 14))
        self.streak_label.pack(side="left", padx=20)

        self.total_label = ttk.Label(self.card_frame, text="累计学习: -- 词", font=("Arial", 14))
        self.total_label.pack(side="left", padx=20)

        self.accuracy_label = ttk.Label(self.card_frame, text="总正确率: -- %", font=("Arial", 14))
        self.accuracy_label.pack(side="left", padx=20)

        # 图表区
        self.chart_frame = ttk.Frame(self)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def refresh(self):
        # 获取数据
        stats = db_manager.get_daily_stats(30)  # 近30天
        streak = db_manager.get_streak_days()

        # 更新卡片
        self.streak_label.config(text=f"连续打卡: {streak} 天")
        total_words = sum(s["total"] for s in stats) if stats else 0
        self.total_label.config(text=f"累计学习: {total_words} 词")
        total_correct = sum(s["correct"] for s in stats) if stats else 0
        accuracy = (total_correct / total_words * 100) if total_words > 0 else 0
        self.accuracy_label.config(text=f"总正确率: {accuracy:.1f} %")

        # 清空旧图表
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if not stats:
            tip = ttk.Label(self.chart_frame, text="暂无学习数据，请先进行练习", font=("Arial", 16))
            tip.pack(pady=100)
            return

        # 准备数据
        dates = [s["date"][5:] for s in stats]  # 只显示 "月-日"
        totals = [s["total"] for s in stats]
        correct_rates = [s["correct"]/s["total"]*100 if s["total"]>0 else 0 for s in stats]

        # 折线图
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
        ax1.plot(dates, totals, marker="o", color="#3498DB", linewidth=2)
        ax1.set_title("每日学习量", fontsize=12)
        ax1.set_ylabel("单词数")
        ax1.tick_params(axis='x', rotation=45)

        # 柱状图
        colors = ["#2ECC71" if r >= 60 else "#E74C3C" for r in correct_rates]
        ax2.bar(dates, correct_rates, color=colors)
        ax2.set_title("每日正确率", fontsize=12)
        ax2.set_ylabel("正确率 (%)")
        ax2.set_ylim(0, 100)
        ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()

        # 嵌入 tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("学习统计")
    root.geometry("800x600")
    page = StatsPage(root)
    page.pack(fill="both", expand=True)
    root.mainloop()


