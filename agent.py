"""Agent 核心逻辑：基于 LangChain + 阿里百炼 OpenAI 兼容接口 + 工具调用 + 多轮对话"""
import os
from typing import List, Dict, Optional

from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tools import query_courses, get_upcoming_assignments, create_study_plan, analyze_grades

# 优先加载项目目录下的 .env，避免 Streamlit 切换工作目录导致找不到
load_dotenv(find_dotenv(usecwd=True))

SYSTEM_PROMPT = """你是「校园学习助手」，一个帮助大学生管理学习的智能体。

你的职责：
1. 回答课程相关问题（使用 query_courses 工具查询课程信息）
2. 提醒近期作业截止日期（使用 get_upcoming_assignments 工具）
3. 为学生生成个性化学习计划（使用 create_study_plan 工具，会在 output 目录生成 Markdown 文件）
4. 分析学生成绩并给出建议（使用 analyze_grades 工具，会生成成绩分析报告）

行为准则：
- 当用户询问课程、作业、学习计划、成绩等问题时，必须调用对应的工具获取真实数据，不要凭空编造。
- 调用工具后，用中文清晰地总结结果给用户。
- 如果用户的问题不明确，主动询问需要的信息（例如课程名、周数、学号等）。
- 生成学习计划时，如果用户没指定周数，默认 4 周；如果没指定重点，询问或留空。
- 保持友好、耐心的语气，像一位贴心的学习辅导员。
- 对于成绩、制度等信息，提醒用户「以学校官方数据为准」。

你可以使用的工具：
- query_courses: 查询课程信息
- get_upcoming_assignments: 查询近期作业
- create_study_plan: 生成学习计划
- analyze_grades: 分析成绩

在回答时，如果调用了工具，请简要说明你调用了哪个工具以及结果。"""


def get_config(api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
    """获取模型配置，优先级：传入参数 > 环境变量 > 默认值"""
    final_api_key = api_key or os.getenv("DASHSCOPE_API_KEY", "")
    final_base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    final_model = model or os.getenv("LLM_MODEL", "qwen-plus")
    return final_api_key, final_base_url, final_model


def get_llm(api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None) -> ChatOpenAI:
    """获取配置好的阿里百炼大模型（OpenAI 兼容接口）"""
    final_api_key, final_base_url, final_model = get_config(api_key, base_url, model)
    if not final_api_key:
        raise ValueError(
            "未配置 API Key！请在侧边栏「模型配置」中填入阿里百炼 API Key，"
            "或在项目根目录创建 .env 文件并设置 DASHSCOPE_API_KEY。\n"
            "获取方式：https://bailian.console.aliyun.com/"
        )
    return ChatOpenAI(
        model=final_model,
        api_key=final_api_key,
        base_url=final_base_url,
        temperature=0.3,
        streaming=False,
    )


def get_agent_executor(api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None) -> AgentExecutor:
    """创建带有工具的 Agent 执行器"""
    llm = get_llm(api_key, base_url, model)
    tools = [query_courses, get_upcoming_assignments, create_study_plan, analyze_grades]

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        max_iterations=5,
    )
    return executor


def serialize_messages(messages: List[BaseMessage]) -> List[Dict[str, str]]:
    """将消息列表序列化为可保存的字典列表"""
    result = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "assistant"
        elif isinstance(msg, SystemMessage):
            role = "system"
        else:
            continue
        result.append({"role": role, "content": msg.content})
    return result


def deserialize_messages(data: List[Dict[str, str]]) -> List[BaseMessage]:
    """从字典列表反序列化为消息列表"""
    messages = []
    for item in data:
        role = item["role"]
        content = item["content"]
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        elif role == "system":
            messages.append(SystemMessage(content=content))
    return messages
