"""课程查询工具：根据关键词查询课程信息、查询近期作业截止日期"""
import json
import os
from datetime import datetime

from langchain_core.tools import tool

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "courses.json")


def _load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@tool
def query_courses(keyword: str) -> str:
    """根据关键词查询课程信息，支持按课程名、教师、课程ID搜索。

    Args:
        keyword: 搜索关键词，如课程名、教师姓名或课程编号（如 AI101、数据结构）
    """
    data = _load_data()
    keyword = keyword.strip().lower()
    if not keyword:
        return "请输入搜索关键词。"

    results = []
    for course in data["courses"]:
        text = f"{course['name']} {course['teacher']} {course['id']} {course['description']}".lower()
        if keyword in text:
            schedule_str = "\n".join(
                f"  - {s['day']} {s['time']} @ {s['location']}（{s['week']}）"
                for s in course["schedule"]
            )
            syllabus_str = "\n".join(f"  - {s}" for s in course["syllabus"])
            results.append(
                f"【{course['id']}】{course['name']}（{course['credits']}学分）\n"
                f"教师：{course['teacher']}\n"
                f"简介：{course['description']}\n"
                f"上课时间：\n{schedule_str}\n"
                f"教学大纲：\n{syllabus_str}"
            )

    if not results:
        return f"未找到与「{keyword}」相关的课程。可用课程：{', '.join(c['name'] for c in data['courses'])}"

    return f"共找到 {len(results)} 门课程：\n\n" + "\n\n---\n\n".join(results)


@tool
def get_upcoming_assignments(days: int = 30) -> str:
    """查询未来 N 天内即将截止的作业清单。

    Args:
        days: 查询未来多少天内的作业，默认 30 天
    """
    data = _load_data()
    course_map = {c["id"]: c["name"] for c in data["courses"]}
    today = datetime.now()
    upcoming = []

    for a in data["assignments"]:
        try:
            deadline = datetime.strptime(a["deadline"], "%Y-%m-%d")
        except ValueError:
            continue
        days_left = (deadline - today).days
        if 0 <= days_left <= days:
            course_name = course_map.get(a["course_id"], a["course_id"])
            upcoming.append(
                f"📌 [{course_name}] {a['title']}\n"
                f"   截止：{a['deadline']}（还剩 {days_left} 天）\n"
                f"   说明：{a['description']}"
            )

    if not upcoming:
        return f"未来 {days} 天内没有即将截止的作业。"

    return f"未来 {days} 天内共有 {len(upcoming)} 项作业即将截止：\n\n" + "\n\n".join(upcoming)
