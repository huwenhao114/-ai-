"""自定义工具集：课程查询、学习计划生成、成绩分析"""
from tools.course_tools import query_courses, get_upcoming_assignments
from tools.study_plan_tools import create_study_plan
from tools.grade_tools import analyze_grades

__all__ = [
    "query_courses",
    "get_upcoming_assignments",
    "create_study_plan",
    "analyze_grades",
]
