"""学习计划生成工具：根据课程和学习重点生成个性化学习计划并保存为 Markdown 文件"""
import os
from datetime import datetime

from langchain_core.tools import tool

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


@tool
def create_study_plan(course_name: str, weeks: int = 4, focus: str = "") -> str:
    """为指定课程生成一份个性化学习计划，并保存为 Markdown 文件到 output 目录。

    Args:
        course_name: 课程名称，如「数据结构与算法」
        weeks: 计划覆盖的周数，默认 4 周
        focus: 学习重点/薄弱环节，如「图的遍历」「动态规划」等，可留空
    """
    if weeks < 1:
        weeks = 1
    if weeks > 16:
        weeks = 16

    focus_line = f"**重点突破**：{focus}" if focus else "**重点突破**：全面巩固课程核心知识点"

    lines = [
        f"# 📚 {course_name} 学习计划",
        "",
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> 计划周期：{weeks} 周",
        f"> {focus_line}",
        "",
        "---",
        "",
        "## 学习目标",
        "",
        f"在 {weeks} 周内系统掌握「{course_name}」的核心知识体系",
        f"{'，重点强化：' + focus if focus else '，查漏补缺、夯实基础'}。",
        "",
        "---",
        "",
    ]

    week_topics = _suggest_topics(course_name, weeks)
    for i in range(1, weeks + 1):
        topic = week_topics.get(i, f"第{i}周学习内容（建议结合教材对应章节）")
        lines += [
            f"## 第 {i} 周",
            "",
            f"**主题**：{topic}",
            "",
            "### 本周任务",
            "- [ ] 阅读教材对应章节（约 2 小时）",
            "- [ ] 完成课堂笔记整理（约 1 小时）",
            "- [ ] 完成课后习题 / 编程练习（约 2 小时）",
            "- [ ] 回顾本周错题与疑问（约 30 分钟）",
            "",
            "### 学习提示",
            f"- 建议每天投入 1～1.5 小时，{'聚焦薄弱环节' if focus else '保持节奏'}",
            "- 遇到问题及时记录，周末统一答疑",
            "",
        ]

    lines += [
        "---",
        "",
        "## 复习与检测",
        "",
        "- 每周末用 30 分钟做本周知识思维导图",
        "- 计划结束前完成 1 套综合练习检验学习效果",
        "- 根据检测结果调整后续学习重点",
        "",
        "---",
        "",
        "*本计划由校园学习助手智能体生成，仅供参考，请结合自身实际情况调整。*",
        "",
    ]

    content = "\n".join(lines)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_course = course_name.replace("/", "_").replace("\\", "_").replace(" ", "_")
    filename = f"study_plan_{safe_course}_{timestamp}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    # 同时保存一份最新副本，方便界面展示
    latest_path = os.path.join(OUTPUT_DIR, "latest_study_plan.md")
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(content)

    return (
        f"✅ 已为「{course_name}」生成 {weeks} 周学习计划！\n"
        f"📄 文件已保存：{filepath}\n\n"
        f"计划要点：\n"
        f"- 覆盖 {weeks} 周，每周包含阅读、笔记、练习、回顾四类任务\n"
        f"- 学习重点：{focus if focus else '全面巩固'}\n"
        f"- 可在 output 目录查看完整 Markdown 文件"
    )


def _suggest_topics(course_name: str, weeks: int) -> dict:
    """根据课程名提供每周主题建议（关键词匹配，找不到则用通用模板）"""
    cn = course_name
    presets = {
        "数据结构": ["线性表与栈队列", "串与数组", "树与二叉树", "图", "排序算法", "查找算法", "动态规划", "贪心算法"],
        "操作系统": ["操作系统概述", "进程与线程", "进程同步与死锁", "内存管理", "虚拟内存", "文件系统", "I/O系统", "设备管理"],
        "计算机网络": ["网络体系结构", "物理层", "数据链路层", "网络层IP协议", "传输层TCP/UDP", "应用层协议", "网络安全基础", "综合实验"],
        "AI": ["开源模型调用", "OpenAI兼容接口", "工具调用", "Agent框架", "Skills", "MCP", "长期记忆", "期末项目"],
        "英语": ["听说训练", "词汇积累", "阅读理解", "写作训练", "语法专项", "学术英语", "口语表达", "综合应用"],
    }
    for key, topics in presets.items():
        if key in cn:
            result = {}
            for i in range(1, weeks + 1):
                idx = min(i - 1, len(topics) - 1)
                result[i] = topics[idx]
            return result
    # 通用模板
    return {i: f"第{i}章核心知识点" for i in range(1, weeks + 1)}
