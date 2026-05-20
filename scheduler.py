"""
艾宾浩斯复习调度算法
作者：田鑫（组长）
功能说明：根据单词熟悉度计算下次复习日期，生成今日复习列表
"""

from datetime import date, timedelta

# 艾宾浩斯间隔天数（熟悉度 → 间隔天数）
# 参考艾宾浩斯遗忘曲线：1天、2天、4天、7天、15天
REVIEW_INTERVALS = {
    0: 0,   # 新词，当天复习
    1: 1,   # 1天后
    2: 2,   # 2天后
    3: 4,   # 4天后
    4: 7,   # 7天后
    5: 15,  # 15天后（基本掌握）
}


def calculate_next_review(familiarity: int) -> str:
    """
    根据熟悉度计算下次复习日期。

    参数:
        familiarity: 熟悉度（0-5）

    返回:
        日期字符串，格式 YYYY-MM-DD
    """
    days = REVIEW_INTERVALS.get(familiarity, 15)
    next_date = date.today() + timedelta(days=days)
    return next_date.isoformat()


def get_today_count() -> int:
    """获取今日待复习单词数量"""
    import db_manager
    words = db_manager.get_today_review_words()
    return len(words)


def get_today_list() -> list[dict]:
    """获取今日待复习单词列表"""
    import db_manager
    return db_manager.get_today_review_words()


def get_interval_description(familiarity: int) -> str:
    """
    返回熟悉度对应的间隔描述（供界面展示）。
    例如：熟悉度3 → "4天后复习"
    """
    days = REVIEW_INTERVALS.get(familiarity, 15)
    if days == 0:
        return "今天复习"
    elif days == 1:
        return "明天复习"
    else:
        return f"{days}天后复习"


# ─────────────────────────────────────────────
# 模块自测
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("艾宾浩斯复习间隔测试")
    print("=" * 40)
    for fam in range(6):
        next_date = calculate_next_review(fam)
        desc = get_interval_description(fam)
        print(f"熟悉度 {fam} → 下次复习: {next_date}  ({desc})")