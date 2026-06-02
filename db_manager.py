"""
数据库管理模块
作者：田鑫（组长）
功能说明：SQLite数据库封装，提供所有模块调用的数据接口
数据库文件：words.db（项目根目录自动生成）

表结构：
- wordbooks：词书表
- words：单词表
- review_records：复习记录表
"""
import csv
import sqlite3
import os
from datetime import date, datetime, timedelta

# 数据库文件路径（与 main.py 同目录）
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "words.db")


# ─────────────────────────────────────────────
# 内部工具函数
# ─────────────────────────────────────────────

def _get_conn():
    """获取数据库连接，启用外键约束"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # 让查询结果支持字典方式访问
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """
    初始化数据库，创建三张表（如果不存在则创建）。
    在 main.py 启动时调用一次即可。
    """
    conn = _get_conn()
    cur = conn.cursor()

    # 词书表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wordbooks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # 单词表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            wordbook_id     INTEGER NOT NULL REFERENCES wordbooks(id) ON DELETE CASCADE,
            word            TEXT    NOT NULL,
            phonetic        TEXT    DEFAULT '',
            meaning         TEXT    NOT NULL,
            example         TEXT    DEFAULT '',
            familiarity     INTEGER NOT NULL DEFAULT 0,   -- 0~5，艾宾浩斯熟悉度
            next_review     TEXT    NOT NULL DEFAULT (date('now', 'localtime')),
            created_at      TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # 复习记录表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS review_records (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id     INTEGER NOT NULL REFERENCES words(id) ON DELETE CASCADE,
            is_correct  INTEGER NOT NULL,   -- 1=正确，0=错误
            mode        TEXT    NOT NULL,   -- 'choice' / 'input'
            reviewed_at TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    """)

    conn.commit()
    conn.close()
    print("数据库初始化完成：", DB_PATH)


# ─────────────────────────────────────────────
# 词书接口
# ─────────────────────────────────────────────

def create_wordbook(name: str) -> int:
    """
    创建词书。如果同名词书已存在，直接返回其 id。
    返回：新建（或已有）词书的 id
    """
    conn = _get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO wordbooks (name) VALUES (?)", (name,)
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        # 同名词书已存在
        row = conn.execute(
            "SELECT id FROM wordbooks WHERE name = ?", (name,)
        ).fetchone()
        return row["id"]
    finally:
        conn.close()


def get_all_wordbooks() -> list[dict]:
    """
    获取所有词书及其单词数量。
    返回：[{"id", "name", "word_count", "created_at"}, ...]
    """
    conn = _get_conn()
    rows = conn.execute("""
        SELECT w.id, w.name, w.created_at,
               COUNT(wd.id) AS word_count
        FROM wordbooks w
        LEFT JOIN words wd ON wd.wordbook_id = w.id
        GROUP BY w.id
        ORDER BY w.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_wordbook(wordbook_id: int) -> None:
    """删除词书（CASCADE 自动删除其下所有单词和复习记录）"""
    conn = _get_conn()
    conn.execute("DELETE FROM wordbooks WHERE id = ?", (wordbook_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# 单词接口
# ─────────────────────────────────────────────

def add_word(wordbook_id: int, word: str, phonetic: str,
             meaning: str, example: str = "") -> int:
    """
    向词书添加单个单词。
    返回：新单词的 id
    """
    conn = _get_conn()
    cur = conn.execute(
        """INSERT INTO words (wordbook_id, word, phonetic, meaning, example)
           VALUES (?, ?, ?, ?, ?)""",
        (wordbook_id, word.strip(), phonetic.strip(),
         meaning.strip(), example.strip())
    )
    conn.commit()
    wid = cur.lastrowid
    conn.close()
    return wid


def batch_add_words(wordbook_id: int, words: list[dict]) -> int:
    """
    批量添加单词（CSV 导入时使用）。
    words 格式：[{"word", "phonetic", "meaning", "example"}, ...]
    返回：成功插入的单词数量
    """
    conn = _get_conn()
    data = [
        (wordbook_id,
         w.get("word", "").strip(),
         w.get("phonetic", "").strip(),
         w.get("meaning", "").strip(),
         w.get("example", "").strip())
        for w in words
        if w.get("word", "").strip() and w.get("meaning", "").strip()
    ]
    conn.executemany(
        """INSERT INTO words (wordbook_id, word, phonetic, meaning, example)
           VALUES (?, ?, ?, ?, ?)""",
        data
    )
    conn.commit()
    count = len(data)
    conn.close()
    return count


def get_words_by_wordbook(wordbook_id: int) -> list[dict]:
    """
    获取词书下所有单词。
    返回：[{"id", "word", "phonetic", "meaning", "example",
             "familiarity", "next_review"}, ...]
    """
    conn = _get_conn()
    rows = conn.execute(
        """SELECT id, word, phonetic, meaning, example,
                  familiarity, next_review
           FROM words
           WHERE wordbook_id = ?
           ORDER BY word""",
        (wordbook_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_today_review_words() -> list[dict]:
    """
    获取所有词书中今日应复习的单词（next_review <= 今天）。
    返回格式同 get_words_by_wordbook。
    """
    today = date.today().isoformat()
    conn = _get_conn()
    rows = conn.execute(
        """SELECT id, word, phonetic, meaning, example,
                  familiarity, next_review
           FROM words
           WHERE next_review <= ?
           ORDER BY familiarity ASC, next_review ASC""",
        (today,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_word_familiarity(word_id: int, is_correct: bool) -> None:
    """
    根据答题结果更新单词熟悉度，并重新计算下次复习日期。
    - 答对：熟悉度 +1（上限 5）
    - 答错：熟悉度 重置为 0（需要从头复习）
    """
    # 避免循环导入，在函数内导入
    import scheduler

    conn = _get_conn()
    row = conn.execute(
        "SELECT familiarity FROM words WHERE id = ?", (word_id,)
    ).fetchone()

    if row is None:
        conn.close()
        return

    old_fam = row["familiarity"]
    if is_correct:
        new_fam = min(old_fam + 1, 5)
    else:
        new_fam = 0

    next_review = scheduler.calculate_next_review(new_fam)

    conn.execute(
        "UPDATE words SET familiarity = ?, next_review = ? WHERE id = ?",
        (new_fam, next_review, word_id)
    )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# 复习记录接口
# ─────────────────────────────────────────────

def add_review_record(word_id: int, is_correct: bool, mode: str) -> None:
    """
    写入一条复习记录。
    mode: 'choice'（选择题）或 'input'（填空/听写）
    """
    conn = _get_conn()
    conn.execute(
        """INSERT INTO review_records (word_id, is_correct, mode)
           VALUES (?, ?, ?)""",
        (word_id, 1 if is_correct else 0, mode)
    )
    conn.commit()
    conn.close()


def get_daily_stats(days: int = 30) -> list[dict]:
    """
    获取最近 N 天每日学习统计。
    返回：[{"date", "total", "correct"}, ...]，按日期升序
    """
    start_date = (date.today() - timedelta(days=days - 1)).isoformat()
    conn = _get_conn()
    rows = conn.execute(
        """SELECT date(reviewed_at) AS date,
                  COUNT(*)          AS total,
                  SUM(is_correct)   AS correct
           FROM review_records
           WHERE date(reviewed_at) >= ?
           GROUP BY date(reviewed_at)
           ORDER BY date(reviewed_at)""",
        (start_date,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_streak_days() -> int:
    """
    计算连续打卡天数：从今天往前数，连续有复习记录的天数。
    """
    conn = _get_conn()
    rows = conn.execute(
        """SELECT DISTINCT date(reviewed_at) AS d
           FROM review_records
           ORDER BY d DESC"""
    ).fetchall()
    conn.close()

    if not rows:
        return 0

    streak = 0
    check = date.today()
    for row in rows:
        d = date.fromisoformat(row["d"])
        if d == check:
            streak += 1
            check -= timedelta(days=1)
        else:
            break
    return streak


def get_wordbook_progress(wordbook_id: int) -> dict:
    """
    获取词书学习进度。
    返回：{"total", "mastered"（熟悉度>=4）, "learning", "new"}
    """
    conn = _get_conn()
    rows = conn.execute(
        "SELECT familiarity FROM words WHERE wordbook_id = ?",
        (wordbook_id,)
    ).fetchall()
    conn.close()

    total = len(rows)
    mastered = sum(1 for r in rows if r["familiarity"] >= 4)
    learning = sum(1 for r in rows if 1 <= r["familiarity"] < 4)
    new = sum(1 for r in rows if r["familiarity"] == 0)
    return {"total": total, "mastered": mastered, "learning": learning, "new": new}


# ─────────────────────────────────────────────
# 模块自测
# ─────────────────────────────────────────────

if __name__ == "__main__":
    init_db()

    # 测试：创建词书
    wb_id = create_wordbook("测试词书")
    print(f"词书 ID: {wb_id}")

    # 测试：添加单词
    add_word(wb_id, "abandon", "/əˈbændən/", "v. 放弃；抛弃", "He abandoned his plan.")
    add_word(wb_id, "achieve", "/əˈtʃiːv/", "v. 实现；完成", "She achieved her goal.")

    # 测试：批量添加
    batch_add_words(wb_id, [
        {"word": "brilliant", "phonetic": "/ˈbrɪliənt/", "meaning": "adj. 出色的；聪明的"},
        {"word": "capable",   "phonetic": "/ˈkeɪpəbl/",  "meaning": "adj. 有能力的"},
    ])

    # 测试：查询
    wbs = get_all_wordbooks()
    print("所有词书：", wbs)

    words = get_words_by_wordbook(wb_id)
    print(f"词书单词数：{len(words)}")
    for w in words:
        print(f"  {w['word']} - {w['meaning']} (熟悉度:{w['familiarity']})")

    # 测试：今日复习列表
    today_list = get_today_review_words()
    print(f"今日待复习：{len(today_list)} 个")

    # 测试：复习记录
    if words:
        update_word_familiarity(words[0]["id"], True)
        add_review_record(words[0]["id"], True, "choice")
        print(f"连续打卡天数：{get_streak_days()}")
        print("每日统计：", get_daily_stats(7))

    # 清理测试数据
    import os
    os.remove(DB_PATH)
    print("测试完成，数据库文件已清理")

# ─────────────────────────────────────────────
# 内置词书自动导入
# ─────────────────────────────────────────────

def init_builtin_wordbooks(data_folder: str = "data"):
    """
    扫描 data_folder 下的所有 .csv 文件，自动导入为词书。
    若词书表中已存在同名词书（文件名不含扩展名），则跳过。
    CSV 文件必须包含 'word' 和 'meaning' 列，可选 'phonetic'、'example' 列。
    """
    import csv
    import os

    # 获取当前文件所在目录的绝对路径，然后拼接 data_folder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, data_folder)

    if not os.path.isdir(data_path):
        print(f"内置词书目录不存在: {data_path}")
        return

    for filename in os.listdir(data_path):
        if not filename.lower().endswith(".csv"):
            continue

        # 用文件名（不含扩展名）作为词书名称
        book_name = os.path.splitext(filename)[0]

        # 检查该词书是否已存在
        conn = _get_conn()
        row = conn.execute("SELECT id FROM wordbooks WHERE name = ?", (book_name,)).fetchone()
        exists = row is not None
        conn.close()

        if exists:
            print(f"内置词书 '{book_name}' 已存在，跳过")
            continue

        # 读取 CSV 文件并导入
        file_path = os.path.join(data_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                words = []
                for row in reader:
                    word = row.get("word", "").strip()
                    meaning = row.get("meaning", "").strip()
                    if not word or not meaning:
                        continue
                    words.append({
                        "word": word,
                        "meaning": meaning,
                        "phonetic": row.get("phonetic", "").strip(),
                        "example": row.get("example", "").strip()
                    })
                if words:
                    wb_id = create_wordbook(book_name)
                    count = batch_add_words(wb_id, words)
                    print(f"内置词书 '{book_name}' 导入成功，共 {count} 个单词")
                else:
                    print(f"内置词书 '{filename}' 没有有效单词，跳过")
        except Exception as e:
            print(f"导入内置词书 '{filename}' 失败: {e}")
