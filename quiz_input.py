"""
填空练习模块
作者：D
功能说明：英→中填空、中→英拼写、听写模式
"""

import tkinter as tk
from tkinter import ttk
import random
import difflib


# ========== 内置单词库 ==========
WORDS = [
    {"word": "abandon", "meaning": "放弃", "phonetic": "/əˈbændən/"},
    {"word": "ability", "meaning": "能力", "phonetic": "/əˈbɪləti/"},
    {"word": "absolute", "meaning": "绝对的", "phonetic": "/ˈæbsəluːt/"},
    {"word": "academic", "meaning": "学术的", "phonetic": "/ˌækəˈdemɪk/"},
    {"word": "accept", "meaning": "接受", "phonetic": "/əkˈsept/"},
    {"word": "access", "meaning": "通道;访问", "phonetic": "/ˈækses/"},
    {"word": "accident", "meaning": "事故", "phonetic": "/ˈæksɪdənt/"},
    {"word": "accompany", "meaning": "陪伴", "phonetic": "/əˈkʌmpəni/"},
    {"word": "accomplish", "meaning": "完成", "phonetic": "/əˈkʌmplɪʃ/"},
    {"word": "account", "meaning": "账户;解释", "phonetic": "/əˈkaʊnt/"},
]


# ========== TTS发音模块导入 ==========
try:
    from tts_module import speak_word
except ImportError:
    # 如果tts_module不存在，定义一个备用发音函数
    def speak_word(word):
        print(f"[模拟发音] {word}")


class QuizInputPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.current_word = None
        self.current_mode = tk.StringVar(value="英→中")
        self.question_index = 0
        self.total_questions = 10
        self.correct_count = 0
        self.total_answered = 0
        self.is_practice_started = False
        
        self._build_ui()
    
    # ---------- 构建界面 ----------
    def _build_ui(self):
        # 标题区域
        title_frame = ttk.Frame(self)
        title_frame.pack(pady=10)
        
        self.title_label = ttk.Label(
            title_frame, 
            text="填空练习", 
            font=("微软雅黑", 18, "bold")
        )
        self.title_label.pack(side="left", padx=20)
        
        self.progress_label = ttk.Label(
            title_frame, 
            text="第 0 / 10 题", 
            font=("微软雅黑", 12)
        )
        self.progress_label.pack(side="right", padx=20)
        
        # 模式选择（单选按钮）
        mode_frame = ttk.Frame(self)
        mode_frame.pack(pady=10)
        
        ttk.Label(mode_frame, text="选择模式：", font=("微软雅黑", 11)).pack(side="left")
        
        for mode in ["英→中", "中→英", "听写模式"]:
            ttk.Radiobutton(
                mode_frame,
                text=mode,
                variable=self.current_mode,
                value=mode,
                command=self._on_mode_change
            ).pack(side="left", padx=10)
        
        # 题目显示区域
        self.question_label = ttk.Label(
            self, 
            text="点击「开始练习」开始答题", 
            font=("微软雅黑", 20),
            foreground="#333"
        )
        self.question_label.pack(pady=20)
        
        # 音标显示
        self.phonetic_label = ttk.Label(
            self,
            text="",
            font=("微软雅黑", 14),
            foreground="#666"
        )
        self.phonetic_label.pack(pady=5)
        
        # 发音按钮
        self.speak_btn = ttk.Button(
            self,
            text="🔊 播放发音",
            command=self._play_word
        )
        
        # 输入区域
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=15)
        
        ttk.Label(input_frame, text="你的答案：", font=("微软雅黑", 12)).pack(side="left")
        
        self.answer_var = tk.StringVar()
        self.entry = ttk.Entry(
            input_frame,
            textvariable=self.answer_var,
            font=("微软雅黑", 14),
            width=25
        )
        self.entry.pack(side="left", padx=5)
        self.entry.bind("<Return>", lambda e: self._check_answer())
        
        self.submit_btn = ttk.Button(
            input_frame,
            text="提交",
            command=self._check_answer
        )
        self.submit_btn.pack(side="left", padx=5)
        
        # 反馈标签
        self.feedback_label = ttk.Label(
            self,
            text="",
            font=("微软雅黑", 13)
        )
        self.feedback_label.pack(pady=15)
        
        # 正确率显示
        self.score_label = ttk.Label(
            self,
            text="正确率：0%",
            font=("微软雅黑", 11),
            foreground="#666"
        )
        self.score_label.pack(pady=5)
        
        # 底部按钮
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)
        
        self.start_btn = ttk.Button(
            btn_frame,
            text="开始练习",
            command=self._start_practice
        )
        self.start_btn.pack(side="left", padx=10)
        
        self.next_btn = ttk.Button(
            btn_frame,
            text="下一题 →",
            command=self._next_question,
            state="disabled"
        )
        self.next_btn.pack(side="left", padx=10)
        
        self.return_btn = ttk.Button(
            btn_frame,
            text="返回",
            command=self._return_home
        )
        self.return_btn.pack(side="left", padx=10)
    
    # ---------- 事件处理 ----------
    def _on_mode_change(self):
        """切换模式时重置练习"""
        if self.is_practice_started:
            self._start_practice()
    
    def _start_practice(self):
        """开始练习"""
        self.is_practice_started = True
        self.question_index = 0
        self.correct_count = 0
        self.total_answered = 0
        self.start_btn.config(text="重新开始")
        self._next_question()
    
    def _next_question(self):
        """出下一题"""
        if self.question_index >= self.total_questions:
            self._show_final_result()
            return
        
        self.current_word = random.choice(WORDS)
        self.question_index += 1
        self.answer_var.set("")
        self.feedback_label.config(text="", foreground="black")
        self.entry.config(state="normal")
        self.submit_btn.config(state="normal")
        self.next_btn.config(state="disabled")
        self.entry.focus()
        
        self.progress_label.config(text=f"第 {self.question_index} / {self.total_questions} 题")
        
        mode = self.current_mode.get()
        
        if mode == "英→中":
            self.speak_btn.pack_forget()
            self.question_label.config(text=self.current_word["word"])
            self.phonetic_label.config(text=self.current_word["phonetic"])
        
        elif mode == "中→英":
            self.speak_btn.pack_forget()
            self.question_label.config(text=self.current_word["meaning"])
            self.phonetic_label.config(text="")
        
        elif mode == "听写模式":
            self.question_label.config(text="请听发音，写出你听到的单词")
            self.phonetic_label.config(text="")
            self.speak_btn.pack(pady=5)
            self._play_word()
    
    def _play_word(self):
        """播放当前单词发音"""
        if self.current_word:
            speak_word(self.current_word["word"])
    
    def _check_answer(self):
        """检查答案"""
        user_answer = self.answer_var.get().strip()
        if not user_answer:
            self.feedback_label.config(text="⚠️ 请输入答案！", foreground="orange")
            return
        
        mode = self.current_mode.get()
        self.total_answered += 1
        
        if mode == "英→中":
            correct = self._fuzzy_match(user_answer, self.current_word["meaning"])
        else:
            correct = self._fuzzy_match(user_answer, self.current_word["word"], is_english=True)
        
        if correct:
            self.correct_count += 1
            self.feedback_label.config(text="✅ 回答正确！", foreground="green")
        else:
            if mode == "英→中":
                correct_answer = self.current_word["meaning"]
            else:
                correct_answer = self.current_word["word"]
            self.feedback_label.config(
                text=f"❌ 回答错误！正确答案是：{correct_answer}",
                foreground="red"
            )
        
        self.entry.config(state="disabled")
        self.submit_btn.config(state="disabled")
        self.next_btn.config(state="normal")
        self._update_score()
        
        if self.question_index >= self.total_questions:
            self.next_btn.config(text="查看结果", command=self._show_final_result)
    
    def _fuzzy_match(self, user_answer, correct_answer, is_english=False):
        """模糊匹配，容忍小错误"""
        user = user_answer.lower().strip()
        correct = correct_answer.lower().strip()
        
        # 完全匹配
        if user == correct:
            return True
        
        # 中文模式：用分号分割多义词，匹配任一即可
        if not is_english:
            meanings = [m.strip() for m in correct.split("；")]
            for meaning in meanings:
                ratio = difflib.SequenceMatcher(None, user, meaning).ratio()
                if ratio >= 0.6:
                    return True
            return False
        
        # 英文模式：容忍少量拼写错误
        ratio = difflib.SequenceMatcher(None, user, correct).ratio()
        return ratio >= 0.8
    
    def _update_score(self):
        """更新正确率显示"""
        if self.total_answered > 0:
            rate = (self.correct_count / self.total_answered) * 100
            self.score_label.config(text=f"正确率：{rate:.1f}%")
    
    def _show_final_result(self):
        """显示最终结果"""
        if self.total_answered > 0:
            rate = (self.correct_count / self.total_answered) * 100
        else:
            rate = 0
        
        self.question_label.config(text="练习结束！")
        self.phonetic_label.config(text=f"最终正确率：{rate:.1f}%")
        self.speak_btn.pack_forget()
        self.entry.config(state="disabled")
        self.submit_btn.config(state="disabled")
        self.next_btn.config(state="disabled")
        self.feedback_label.config(
            text=f"答对 {self.correct_count} 题，共 {self.total_answered} 题",
            foreground="#333"
        )
    
    def _return_home(self):
        """返回主页（占位，实际由主窗口调用）"""
        pass


# ========== 独立测试入口 ==========
if __name__ == "__main__":
    root = tk.Tk()
    root.title("测试 - 填空练习")
    root.geometry("700x550")
    root.resizable(False, False)
    
    style = ttk.Style()
    style.theme_use("clam")
    
    page = QuizInputPage(root)
    page.pack(fill="both", expand=True)
    
    root.mainloop()