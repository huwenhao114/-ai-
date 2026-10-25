# 🎓 校园学习助手（Campus Study Assistant）

> 一个基于 LangChain + 阿里百炼的智能学习助理，能帮大学生查课程、查作业、制定学习计划、分析成绩。
>
> **选题路径**：路径 A（技术栈较完整的智能体应用）

---

## 一、项目简介

「校园学习助手」面向在校大学生，解决「课程信息分散、作业易遗忘、学习计划难坚持、成绩不会分析」的痛点。用户用自然语言提问，智能体自动调用工具完成任务，并把学习计划、成绩报告等产出物保存为 Markdown 文件。

**核心能力**：
- 🔍 **课程查询**：按名称/教师/编号搜索课程信息与教学大纲
- 📅 **作业提醒**：查询未来 N 天内即将截止的作业
- 📝 **学习计划生成**：根据课程和重点生成个性化学习计划并保存文件
- 📊 **成绩分析**：分析各科成绩，给出改进建议并生成报告

![Uploading image.png…]()

---

## 二、技术栈

| 类别 | 选型 | 说明 |
| --- | --- | --- |
| 大模型 | 阿里百炼 Qwen（qwen-plus） | 通过 OpenAI 兼容接口调用 |
| Agent 框架 | LangChain（create_tool_calling_agent） | 工具调用 + 多轮对话 |
| Web 界面 | Streamlit | 聊天界面 + 工具调用可视化 |
| 自定义工具 | 3 个 | 课程查询、作业提醒、学习计划生成、成绩分析 |
| Skill | 1 个 | `study-plan-writer`（学习计划编写规范） |
| 会话持久化 | JSON 文件 | 保存/加载多轮对话历史 |
| 产出物 | Markdown 文件 | 学习计划、成绩报告写入 output 目录 |

> 满足路径 A 最低配置 7 项中的 **7 项**（模型调用 ✓ / Agent 框架 ✓ / 3 个自定义工具 ✓ / 1 个 Skill ✓ / Streamlit 界面 ✓ / 多轮对话与会话保存 ✓ / 文件产出 ✓）。

---

## 三、环境要求

- **Python**：3.10 或以上
- **操作系统**：Windows / macOS / Linux 均可
- **网络**：能访问阿里百炼服务

---

## 四、安装与启动（Windows）

### 1. 克隆仓库

```bash
git clone <你的仓库地址>
cd MyApplication114
```

### 2. 创建虚拟环境并安装依赖

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置 API Key（使用阿里百炼）

1. 登录 [阿里百炼控制台](https://bailian.console.aliyun.com/)，创建 API Key
2. 复制 `.env.example` 为 `.env`，填入你的 Key：

```powershell
copy .env.example .env
```

编辑 `.env`：

```ini
DASHSCOPE_API_KEY=sk-你的真实Key
LLM_MODEL=qwen-plus
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

> ⚠️ `.env` 文件已被 `.gitignore` 排除，**不会提交到 GitHub**，请勿将真实 Key 写入仓库。

### 4. 启动应用

```powershell
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`。

---

## 五、使用阿里百炼的方法（详细）

### 步骤一：开通服务并获取 API Key

1. 访问 https://bailian.console.aliyun.com/ ，用阿里云账号登录
2. 左侧菜单选择「模型服务」→「API-KEY 管理」
3. 点击「创建新的 API-KEY」，复制生成的 Key（以 `sk-` 开头）

### 步骤二：开通模型

1. 在「模型广场」中找到 **通义千问**（如 qwen-plus）
2. 点击「开通服务」（部分模型有免费额度）

### 步骤三：配置到项目

将 Key 填入 `.env` 的 `DASHSCOPE_API_KEY` 即可。本项目使用阿里百炼的 **OpenAI 兼容模式**：

- Base URL：`https://dashscope.aliyuncs.com/compatible-mode/v1`
- 兼容 OpenAI SDK 的 `ChatCompletion` 接口
- 通过 LangChain 的 `ChatOpenAI` 配置 `base_url` 参数调用

### 可选：更换模型

在 `.env` 中修改 `LLM_MODEL` 即可切换：

| 模型 | 说明 |
| --- | --- |
| `qwen-turbo` | 轻量快速，适合简单任务 |
| `qwen-plus` | 均衡型，推荐默认 |
| `qwen-max` | 最强能力，适合复杂推理 |
| `qwen-long` | 长文本场景 |

---

## 六、推荐演示话术

1. **查课程**：「帮我查一下开源AI技术实践这门课的信息」
2. **查作业**：「最近有哪些作业要截止了？」
3. **做计划**：「帮我制定一个数据结构与算法的 4 周学习计划，重点复习图和排序」
4. **看成绩**：「分析一下学号 20240001 的成绩，给点学习建议」
5. **组合任务**：「我这学期操作系统学得不太好，帮我查一下这门课的信息，再制定一个 4 周的复习计划」

> 演示时可在界面展开「工具调用过程」查看 Agent 调用了哪个工具、传入了什么参数、返回了什么结果。

---

## 七、项目结构

```
MyApplication114/
├── app.py                      # Streamlit 主界面
├── agent.py                    # Agent 核心逻辑（模型 + 工具 + 多轮对话）
├── requirements.txt            # 依赖
├── .env.example                # 环境变量模板（不含真实 Key）
├── .gitignore
├── data/
│   └── courses.json            # 示例课程/成绩/作业数据
├── tools/
│   ├── __init__.py
│   ├── course_tools.py         # 课程查询 + 作业提醒工具
│   ├── study_plan_tools.py     # 学习计划生成工具
│   └── grade_tools.py          # 成绩分析工具
├── skills/
│   └── study-plan-writer/
│       └── SKILL.md            # 学习计划编写规范 Skill
├── output/                     # 生成的学习计划、成绩报告（运行时产出）
└── sessions/                   # 保存的会话历史（运行时产出）
```

---

## 八、相对课堂 demo 的增量

| 课堂 demo | 本项目增量 |
| --- | --- |
| demo_1 模型调用 + Streamlit | 扩展为多工具 Agent，不止单轮问答 |
| demo_2 OpenAI 兼容接口 + 工具调用 | 落地到阿里百炼真实服务，4 个工具协同 |
| demo_3 云端模型 + 密钥管理 | 使用 `.env` + `.gitignore` 规范管理密钥 |
| demo_5 Agent 框架 + Skills + WebUI | 新增学习计划编写 Skill、会话保存、文件产出 |

**自己新增的关键代码**：
1. `tools/study_plan_tools.py` — 学习计划生成工具，按周编排主题并写入 Markdown
2. `tools/grade_tools.py` — 成绩分析工具，自动识别薄弱课程并给出建议
3. `skills/study-plan-writer/SKILL.md` — 学习计划编写规范 Skill
4. `app.py` — Streamlit 界面中的工具调用过程可视化、会话保存/加载、产出文件下载

---

## 九、思政与合规说明

- 所有课程、成绩、作业数据均为**虚构示例**，不涉及真实学生个人信息
- 学习计划与成绩建议仅供参考，提示用户「以学校官方数据为准」
- 不代写作业、不提供考试答案、不涉及违规内容
- API Key 通过 `.env` 管理，不提交到 Git 仓库

---

## 十、常见问题

**Q：启动时报 `未配置 DASHSCOPE_API_KEY`？**
A：检查 `.env` 文件是否存在且 Key 正确，参考第五节配置。

**Q：阿里百炼如何计费？**
A：新用户有免费额度，超出后按 token 计费，详见控制台价格说明。qwen-turbo 有长期免费额度可用于测试。

**Q：能否切换到 Ollama 本地模型？**
A：可以。修改 `.env`：
```ini
OPENAI_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen2.5:7b
DASHSCOPE_API_KEY=ollama
```
需提前用 `ollama pull qwen2.5:7b` 拉取模型。

**Q：会话保存在哪里？**
A：`sessions/` 目录下，每个会话一个 JSON 文件，可在界面加载。

---

## 十一、参考来源

- LangChain 文档：https://python.langchain.com/
- 阿里百炼 OpenAI 兼容文档：https://help.aliyun.com/zh/model-studio/developer-reference/use-qwen-by-calling-api
- Streamlit 文档：https://docs.streamlit.io/
- 课堂实验 demo_1 ~ demo_5
