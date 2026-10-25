"""Streamlit 交互界面：多轮对话、工具调用展示、会话保存、文件产出查看"""
import os
import json
from datetime import datetime

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from agent import get_agent_executor, serialize_messages, deserialize_messages, get_config

SESSIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.set_page_config(page_title="校园学习助手", page_icon="🎓", layout="wide")

# ---- 侧边栏 ----
with st.sidebar:
    st.markdown("## 🎓 校园学习助手")
    st.caption("基于 LangChain + 阿里百炼的智能学习助理")

    st.markdown("---")
    st.markdown("### 🛠️ 可用工具")
    st.markdown(
        "- 🔍 **课程查询**：按名称/教师/编号查课\n"
        "- 📅 **作业提醒**：近期截止作业\n"
        "- 📝 **学习计划**：生成并保存计划文件\n"
        "- 📊 **成绩分析**：生成成绩分析报告"
    )

    st.markdown("---")
    st.markdown("### ⚙️ 模型配置")

    # 读取环境变量中的默认值
    env_key, env_url, env_model = get_config()

    # API Key 输入框（优先使用界面输入，其次 .env）
    api_key = st.text_input(
        "阿里百炼 API Key",
        value=env_key or "",
        type="password",
        help="登录 https://bailian.console.aliyun.com/ 获取，也可写入 .env 文件的 DASHSCOPE_API_KEY",
        placeholder="sk-xxxxxxxxxxxxxxxx",
    )
    base_url = st.text_input("Base URL", value=env_url)
    model = st.text_input("模型名称", value=env_model)

    if api_key:
        st.success("✅ API Key 已配置")
    else:
        st.warning("⚠️ 请填入 API Key 后再对话")

    st.caption(
        "获取 Key：https://bailian.console.aliyun.com/\n"
        "推荐模型：qwen-plus（均衡）/ qwen-turbo（快速）"
    )

    # 保存到 session_state 供主区域使用
    st.session_state.api_key = api_key
    st.session_state.base_url = base_url
    st.session_state.model = model

    st.markdown("---")
    st.markdown("### 💾 会话管理")

    sessions = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".json")]
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ 新建会话", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()
    with col2:
        if st.button("💾 保存当前会话", use_container_width=True):
            if st.session_state.get("messages"):
                sid = st.session_state.get("session_id") or datetime.now().strftime("%Y%m%d_%H%M%S")
                data = {
                    "session_id": sid,
                    "messages": serialize_messages(st.session_state.messages),
                    "saved_at": datetime.now().isoformat(),
                }
                with open(os.path.join(SESSIONS_DIR, f"{sid}.json"), "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                st.session_state.session_id = sid
                st.success(f"已保存会话：{sid}")
            else:
                st.warning("暂无对话可保存")

    if sessions:
        selected = st.selectbox("加载历史会话", [""] + sorted(sessions, reverse=True))
        if selected and st.button("📂 加载此会话"):
            with open(os.path.join(SESSIONS_DIR, selected), "r", encoding="utf-8") as f:
                data = json.load(f)
            st.session_state.messages = deserialize_messages(data["messages"])
            st.session_state.session_id = data["session_id"]
            st.rerun()

# ---- 主区域 ----
st.title("🎓 校园学习助手")
st.caption("我可以帮你查课程、查作业、制定学习计划、分析成绩。试试问我吧！")

# 初始化消息
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# 显示产出文件
if st.session_state.messages:
    output_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".md") and f.startswith("latest_")]
    if output_files:
        st.markdown("---")
        st.markdown("### 📄 最新产出文件")
        for of in sorted(output_files, reverse=True):
            with open(os.path.join(OUTPUT_DIR, of), "r", encoding="utf-8") as f:
                content = f.read()
            with st.expander(f"📄 {of}", expanded=False):
                st.markdown(content)
                st.download_button(
                    label="⬇️ 下载文件",
                    data=content,
                    file_name=of,
                    mime="text/markdown",
                    key=f"dl_{of}",
                )

# 输入框
if prompt := st.chat_input("例如：帮我查一下开源AI技术实践这门课"):
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    api_key = st.session_state.get("api_key", "")
    base_url = st.session_state.get("base_url", "")
    model = st.session_state.get("model", "")

    with st.chat_message("assistant"):
        if not api_key:
            error_msg = "⚠️ 请先在左侧侧边栏填入阿里百炼 API Key 后再提问。"
            st.error(error_msg)
            st.session_state.messages.append(AIMessage(content=error_msg))
        else:
            try:
                executor = get_agent_executor(api_key=api_key, base_url=base_url, model=model)
                with st.spinner("🤖 正在思考并调用工具..."):
                    result = executor.invoke({
                        "input": prompt,
                        "chat_history": st.session_state.messages[:-1],
                    })

                response = result["output"]

                # 展示工具调用过程
                steps = result.get("intermediate_steps", [])
                if steps:
                    st.markdown("**🔧 工具调用过程：**")
                    for i, (action, observation) in enumerate(steps, 1):
                        tool_name = action.tool
                        tool_input = action.tool_input
                        with st.expander(f"工具 #{i}: `{tool_name}`", expanded=False):
                            st.markdown("**输入参数：**")
                            st.code(json.dumps(tool_input, ensure_ascii=False, indent=2), language="json")
                            st.markdown("**返回结果：**")
                            st.text(observation[:2000] + ("..." if len(observation) > 2000 else ""))

                st.markdown(response)
                st.session_state.messages.append(AIMessage(content=response))

            except Exception as e:
                err_str = str(e)
                if "401" in err_str or "api_key" in err_str.lower() or "Incorrect API key" in err_str:
                    error_msg = (
                        "❌ API Key 无效或未开通对应模型。\n\n"
                        "请检查：\n"
                        "1. Key 是否填写正确（不要有多余空格）\n"
                        "2. 是否已在百炼控制台开通该模型（qwen-plus）\n"
                        "3. 获取地址：https://bailian.console.aliyun.com/"
                    )
                elif "API Key" in err_str or "DASHSCOPE" in err_str or "未配置" in err_str:
                    error_msg = "❌ 未配置 API Key，请在左侧侧边栏填入阿里百炼 API Key。"
                else:
                    error_msg = f"❌ 出错了：{err_str}"
                st.error(error_msg)
                st.session_state.messages.append(AIMessage(content=error_msg))
