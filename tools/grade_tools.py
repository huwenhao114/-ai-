"""成绩分析工具：分析学生成绩，给出学习建议并保存分析报告"""
import json
import os
from datetime import datetime

from langchain_core.tools import tool

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "courses.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _score_level(score: float) -> str:
    if score >= 90:
        return "优秀"
    elif score >= 80:
        return "良好"
    elif score >= 70:
        return "中等"
    elif score >= 60:
        return "及格"
    else:
        return "需努力"


@tool
def analyze_grades(student_id: str = "20240001") -> str:
    """分析指定学号学生的本学期成绩，给出各科评价与改进建议，并保存成绩分析报告。

    Args:
        student_id: 学号，默认使用示例学号 20240001
    """
    data = _load_data()
    course_map = {c["id"]: c["name"] for c in data["courses"]}

    student_grades = [g for g in data["grades"] if g["student_id"] == student_id]
    if not student_grades:
        return f"未找到学号 {student_id} 的成绩记录。可用示例学号：20240001、20240002。"

    scores = [g["score"] for g in student_grades]
    avg = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)

    # 找出薄弱课程（低于 75 分）
    weak = [g for g in student_grades if g["score"] < 75]
    strong = [g for g in student_grades if g["score"] >= 85]

    lines = [
        f"# 📊 成绩分析报告",
        "",
        f"> 学号：{student_id}",
        f"> 学期：2026-2027 第一学期",
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
        "## 总体情况",
        "",
        f"| 指标 | 数值 |",
        f"| --- | --- |",
        f"| 已修课程数 | {len(scores)} 门 |",
        f"| 平均分 | {avg:.1f} |",
        f"| 最高分 | {max_score} |",
        f"| 最低分 | {min_score} |",
        "",
        "## 各科成绩",
        "",
        "| 课程 | 分数 | 等级 |",
        "| --- | --- | --- |",
    ]

    for g in student_grades:
        name = course_map.get(g["course_id"], g["course_id"])
        lines.append(f"| {name} | {g['score']} | {_score_level(g['score'])} |")

    lines += ["", "---", ""]

    # 学习建议
    lines += ["## 学习建议", ""]
    if weak:
        lines.append("### ⚠️ 需重点加强的课程")
        for g in weak:
            name = course_map.get(g["course_id"], g["course_id"])
            lines.append(f"- **{name}**（{g['score']}分）：建议增加练习量，优先攻克薄弱章节")
        lines.append("")
    else:
        lines.append("✅ 所有课程均达到良好水平，继续保持！")
        lines.append("")

    if strong:
        lines.append("### 🌟 优势课程")
        for g in strong:
            name = course_map.get(g["course_id"], g["course_id"])
            lines.append(f"- **{name}**（{g['score']}分）：可尝试更高难度的拓展学习")
        lines.append("")

    lines += [
        "### 💡 通用建议",
        "- 每周固定时间复习，避免考前突击",
        "- 建立错题本，定期回顾",
        "- 主动向老师和同学请教疑问",
        "- 结合学习计划工具制定针对性复习方案",
        "",
        "---",
        "",
        "*本报告由校园学习助手智能体基于示例数据生成，仅供学习参考。*",
        "",
    ]

    content = "\n".join(lines)
    filepath = os.path.join(OUTPUT_DIR, f"grade_report_{student_id}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    latest_path = os.path.join(OUTPUT_DIR, "latest_grade_report.md")
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(content)

    summary = (
        f"📊 学号 {student_id} 成绩分析完成！\n"
        f"共 {len(scores)} 门课程，平均分 {avg:.1f}（{_score_level(avg)}）\n"
        f"最高分 {max_score}，最低分 {min_score}\n"
    )
    if weak:
        weak_names = "、".join(course_map.get(g["course_id"], g["course_id"]) for g in weak)
        summary += f"⚠️ 薄弱课程：{weak_names}，建议重点复习\n"
    summary += f"📄 详细报告已保存：{filepath}"

    return summary
