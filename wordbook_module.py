"""
词库管理模块
作者：B（上官可儿）
功能说明：CSV词书导入、手动添加单词、词书列表管理、查看单词、删除词书
依赖接口：
    - db_manager.create_wordbook()
    - db_manager.get_all_wordbooks()
    - db_manager.delete_wordbook()
    - db_manager.add_word()
    - db_manager.batch_add_words()
    - db_manager.get_words_by_wordbook()
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import db_manager
import db_manager
db_manager.init_db()  

class WordbookPage(ttk.Frame):
    """词库管理页面"""

    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()
        self._refresh_wordbook_list()

    # ------------------------------------------------------------------ #
    #  UI 构建
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        """构建页面 UI（顶部按钮区 + 词书表格 + 底部操作区）"""

        # ---- 顶部：标题 + 操作按钮 ----
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(
            top_frame, text="词库管理", font=("微软雅黑", 18, "bold")
        ).pack(side="left")

        ttk.Button(
            top_frame, text="导入CSV词书", command=self._import_csv
        ).pack(side="right", padx=5)
        ttk.Button(
            top_frame, text="新建词书", command=self._create_wordbook
        ).pack(side="right", padx=5)

        # ---- 中部：词书列表表格 ----
        list_frame = ttk.LabelFrame(self, text="词书列表")
        list_frame.pack(fill="both", expand=True, padx=20, pady=5)

        columns = ("id", "name", "word_count", "created_at")
        self.tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=12
        )

        self.tree.heading("id",         text="ID")
        self.tree.heading("name",       text="词书名称")
        self.tree.heading("word_count", text="单词数")
        self.tree.heading("created_at", text="创建时间")

        self.tree.column("id",         width=50,  anchor="center")
        self.tree.column("name",       width=220)
        self.tree.column("word_count", width=100, anchor="center")
        self.tree.column("created_at", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 双击查看单词
        self.tree.bind("<Double-1>", self._on_double_click)

        # ---- 底部：操作按钮 ----
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", padx=20, pady=10)

        ttk.Button(
            bottom_frame, text="查看单词", command=self._view_words
        ).pack(side="left", padx=5)
        ttk.Button(
            bottom_frame, text="删除词书", command=self._delete_wordbook
        ).pack(side="left", padx=5)
        ttk.Button(
            bottom_frame, text="手动添加单词", command=self._add_word_dialog
        ).pack(side="left", padx=5)
        ttk.Button(
            bottom_frame, text="刷新", command=self._refresh_wordbook_list
        ).pack(side="right", padx=5)

    # ------------------------------------------------------------------ #
    #  数据操作
    # ------------------------------------------------------------------ #

    def _refresh_wordbook_list(self):
        """从数据库读取词书列表并刷新表格"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        wordbooks = db_manager.get_all_wordbooks()
        for wb in wordbooks:
            self.tree.insert(
                "", "end",
                values=(
                    wb["id"],
                    wb["name"],
                    wb["word_count"],
                    wb["created_at"][:10],   # 只显示日期部分
                )
            )

    def _get_selected_wordbook(self):
        """
        获取当前选中的词书信息。
        若未选中则弹出提示，返回 None。
        返回格式：{"id": ..., "name": ...}
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个词书")
            return None
        values = self.tree.item(selected[0])["values"]
        return {"id": values[0], "name": values[1]}

    # ------------------------------------------------------------------ #
    #  功能：新建词书
    # ------------------------------------------------------------------ #

    def _create_wordbook(self):
        """弹窗让用户输入词书名称，调用 db_manager 创建"""
        dialog = tk.Toplevel(self)
        dialog.title("新建词书")
        dialog.geometry("350x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="词书名称：").pack(pady=(20, 5))
        name_entry = ttk.Entry(dialog, width=32)
        name_entry.pack(pady=5)
        name_entry.focus_set()

        def _confirm():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("提示", "词书名称不能为空", parent=dialog)
                return
            db_manager.create_wordbook(name)
            dialog.destroy()
            self._refresh_wordbook_list()
            messagebox.showinfo("成功", f"词书「{name}」创建成功！")

        # 回车也能确认
        name_entry.bind("<Return>", lambda e: _confirm())
        ttk.Button(dialog, text="确定", command=_confirm).pack(pady=10)

    # ------------------------------------------------------------------ #
    #  功能：导入 CSV 词书
    # ------------------------------------------------------------------ #

    def _import_csv(self):
        """
        让用户选择 CSV 文件，校验列名后批量写入数据库。
        CSV 必须包含 word、meaning 列，可选 phonetic、example 列。
        """
        file_path = filedialog.askopenfilename(
            title="选择 CSV 词书文件",
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")]
        )
        if not file_path:
            return

        # 读取文件
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            messagebox.showerror("错误", f"读取 CSV 失败：{e}")
            return

        # 校验必要列名
        required_cols = {"word", "meaning"}
        if not required_cols.issubset(set(df.columns)):
            messagebox.showerror(
                "格式错误",
                "CSV 文件必须包含 'word' 和 'meaning' 两列\n"
                f"当前列名：{list(df.columns)}"
            )
            return

        # 以文件名（不含扩展名）作为词书名
        import os
        book_name = os.path.splitext(os.path.basename(file_path))[0]

        # 创建词书
        wordbook_id = db_manager.create_wordbook(book_name)

        # 整理单词数据
        words = []
        for _, row in df.iterrows():
            words.append({
                "word":     str(row.get("word",     "")).strip(),
                "phonetic": str(row.get("phonetic", "")).strip(),
                "meaning":  str(row.get("meaning",  "")).strip(),
                "example":  str(row.get("example",  "")).strip(),
            })

        count = db_manager.batch_add_words(wordbook_id, words)
        self._refresh_wordbook_list()
        messagebox.showinfo(
            "导入成功",
            f"词书「{book_name}」导入成功，共 {count} 个单词"
        )

    # ------------------------------------------------------------------ #
    #  功能：删除词书
    # ------------------------------------------------------------------ #

    def _delete_wordbook(self):
        """删除选中词书及其所有单词"""
        wb = self._get_selected_wordbook()
        if wb is None:
            return

        confirm = messagebox.askyesno(
            "确认删除",
            f"确定要删除词书「{wb['name']}」及其所有单词吗？\n此操作不可撤销。"
        )
        if not confirm:
            return

        db_manager.delete_wordbook(wb["id"])
        self._refresh_wordbook_list()
        messagebox.showinfo("成功", "词书已删除")

    # ------------------------------------------------------------------ #
    #  功能：查看单词列表
    # ------------------------------------------------------------------ #

    def _view_words(self):
        """弹出新窗口，显示选中词书的全部单词"""
        wb = self._get_selected_wordbook()
        if wb is None:
            return

        words = db_manager.get_words_by_wordbook(wb["id"])

        win = tk.Toplevel(self)
        win.title(f"词书：{wb['name']}")
        win.geometry("660x420")

        cols = ("word", "phonetic", "meaning", "familiarity")
        tree = ttk.Treeview(win, columns=cols, show="headings")

        tree.heading("word",        text="单词")
        tree.heading("phonetic",    text="音标")
        tree.heading("meaning",     text="释义")
        tree.heading("familiarity", text="熟悉度")

        tree.column("word",        width=130)
        tree.column("phonetic",    width=130)
        tree.column("meaning",     width=280)
        tree.column("familiarity", width=80, anchor="center")

        sb = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        for w in words:
            tree.insert(
                "", "end",
                values=(
                    w["word"],
                    w.get("phonetic", ""),
                    w["meaning"],
                    w.get("familiarity", 0),
                )
            )

        # 状态栏：显示单词总数
        ttk.Label(
            win,
            text=f"共 {len(words)} 个单词",
            foreground="gray"
        ).pack(side="bottom", pady=5)

    # ------------------------------------------------------------------ #
    #  功能：手动添加单词
    # ------------------------------------------------------------------ #

    def _add_word_dialog(self):
        """
        弹出对话框，输入单词/音标/释义/例句，调用 db_manager.add_word() 写入。
        支持连续添加（不关窗口）。
        """
        wb = self._get_selected_wordbook()
        if wb is None:
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"手动添加单词 — {wb['name']}")
        dialog.geometry("420x300")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        fields = [
            ("单词 *",  "word"),
            ("音标",    "phonetic"),
            ("释义 *",  "meaning"),
            ("例句",    "example"),
        ]
        entries = {}

        for i, (label_text, key) in enumerate(fields):
            ttk.Label(dialog, text=label_text, width=8, anchor="e").grid(
                row=i, column=0, padx=(20, 5), pady=8, sticky="e"
            )
            entry = ttk.Entry(dialog, width=36)
            entry.grid(row=i, column=1, padx=(0, 20), pady=8)
            entries[key] = entry

        entries["word"].focus_set()

        # 状态提示
        status_label = ttk.Label(dialog, text="", foreground="green")
        status_label.grid(row=len(fields), column=0, columnspan=2, pady=5)

        def _confirm():
            word    = entries["word"].get().strip()
            meaning = entries["meaning"].get().strip()

            if not word or not meaning:
                messagebox.showwarning(
                    "提示", "单词和释义不能为空", parent=dialog
                )
                return

            db_manager.add_word(
                wb["id"],
                word,
                entries["phonetic"].get().strip(),
                meaning,
                entries["example"].get().strip(),
            )

            # 清空输入框，方便连续添加
            for entry in entries.values():
                entry.delete(0, "end")
            entries["word"].focus_set()

            status_label.config(text=f"✓ 「{word}」已添加")
            self._refresh_wordbook_list()   # 更新主列表中的单词数

        def _close():
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=len(fields) + 1, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="添加",  command=_confirm).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="关闭",  command=_close ).pack(side="left", padx=10)

        # 回车触发添加
        dialog.bind("<Return>", lambda e: _confirm())

    # ------------------------------------------------------------------ #
    #  事件：双击查看单词
    # ------------------------------------------------------------------ #

    def _on_double_click(self, event):
        """双击词书行 → 弹出单词列表"""
        self._view_words()


# ------------------------------------------------------------------ #
#  单独运行测试（不依赖主窗口）
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    # 单独运行时，用一个最简单的 db_manager 存根代替真实模块，方便测试 UI
    import types, sys

    stub = types.ModuleType("db_manager")
    _books = [
        {"id": 1, "name": "四级核心词汇", "word_count": 25,
         "created_at": "2026-05-10 10:00:00"},
        {"id": 2, "name": "高考核心词汇", "word_count": 25,
         "created_at": "2026-05-10 11:00:00"},
    ]
    _words = [
        {"id": 1, "word": "abandon",  "phonetic": "/əˈbændən/",
         "meaning": "放弃；遗弃", "familiarity": 0},
        {"id": 2, "word": "accurate", "phonetic": "/ˈækjərət/",
         "meaning": "准确的；精确的", "familiarity": 1},
    ]
    stub.get_all_wordbooks    = lambda: _books
    stub.get_words_by_wordbook= lambda wb_id: _words
    stub.create_wordbook      = lambda name: (_books.append(
        {"id": len(_books)+1, "name": name, "word_count": 0,
         "created_at": "2026-05-10 12:00:00"}), len(_books))[-1]
    stub.delete_wordbook      = lambda wb_id: None
    stub.add_word             = lambda *args, **kwargs: None
    stub.batch_add_words      = lambda wb_id, words: len(words)
    sys.modules["db_manager"] = stub

    root = tk.Tk()
    root.title("单词本 — 词库管理（测试模式）")
    root.geometry("800x600")

    page = WordbookPage(root)
    page.pack(fill="both", expand=True)

    root.mainloop()
