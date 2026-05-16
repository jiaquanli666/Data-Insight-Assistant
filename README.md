# 数据洞察对话助手 (Data Insight Assistant)

基于 **LangGraph 多 Agent 协作** 的智能数据分析系统。用户用自然语言提问，系统自动完成 SQL 查询、图表生成、数据洞察撰写三步流程。

## 架构概览

```
用户提问 → 协调 Agent（路由判断）
                ├── 闲聊 → 直接回复
                └── 数据问题 → 查询 Agent → 可视化 Agent → 叙事 Agent → 汇总输出
```

### 三个 Agent

| Agent | 职责 | 涉及技术 |
|-------|------|---------|
| **查询 Agent** | 查 Schema 知识库 → 写 SQL → 执行 → 返回结果 | ReAct Agent + Tool Calling + RAG |
| **可视化 Agent** | 判断是否需要图表 → 选择类型 → 生成 PNG | LLM 决策 + Matplotlib |
| **叙事 Agent** | 读取数据结果 → 写有洞察的分析报告 | LLM 结构化输出 |

### RAG 用途

数据库 Schema（表名、字段、关联关系）和常见查询模板通过 DashScope 做向量化存入 Chroma。查询 Agent 在写 SQL 前会先从向量库检索最相关的表结构和查询示例，拼入 Prompt，从而生成正确的 SQL。

## 技术栈

| 层 | 技术 |
|----|------|
| LLM（推理） | **DeepSeek-Chat**（通过 LangChain ChatOpenAI 接口） |
| Embedding | **DashScope** text-embedding-v2 |
| 向量库 | **Chroma** |
| Agent 框架 | **LangGraph** + **LangChain** |
| 前端 | **Streamlit** |
| 图表 | **Matplotlib** |
| 数据库 | **SQLite**（电商零售示例数据） |

## 项目结构

```
agent_project/
├── src/agent_project/
│   ├── agents/
│   │   ├── query_agent.py       # 查询 Agent（Text-to-SQL + RAG）
│   │   ├── viz_agent.py         # 可视化 Agent
│   │   └── narrative_agent.py   # 叙事 Agent
│   ├── graph.py                 # LangGraph 多 Agent 编排
│   ├── tools.py                 # 自定义 Tool（SQL 执行、图表生成）
│   ├── schema_rag.py            # Schema 向量检索模块
│   ├── database.py              # SQLite 建表 + 示例数据
│   ├── config.py                # 配置读取
│   └── app.py                   # Streamlit 前端
├── data/
│   ├── charts/                  # 生成的图表 PNG
│   ├── chroma/                  # Chroma 向量库
│   └── retail.db               # SQLite 数据库
├── pyproject.toml
└── README.md
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/你的用户名/data-insight-agent.git
cd data-insight-agent

# 安装依赖（需要 Python >= 3.12）
uv sync
```

### 2. 配置 API Key

```bash
cp .env.example .env
```

编辑 `.env`，填入你的 API Key：

```
DEEPSEEK_API_KEY=sk-your-deepseek-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DASHSCOPE_API_KEY=sk-your-dashscope-key
```

### 3. 初始化数据库

```bash
uv run python -m agent_project.database
```

### 4. 启动应用

```bash
uv run streamlit run src/agent_project/app.py
```

浏览器打开 `http://localhost:8501`。

## 示例问题

- "哪个品类销售额最高？"
- "最近 7 天的销售趋势怎么样？"
- "各城市销售额排名"
- "金卡和普通会员的客单价对比"
- "数码电子产品中哪个卖得最好？"

## 展示效果

每个数据问题会输出三段内容：

1. **数据查询结果** — SQL 查询返回的 markdown 表格
2. **可视化图表** — 自动生成的柱状图/折线图/饼图
3. **数据洞察** — Agent 撰写的分析报告，含具体数字和业务解读

## 存在的问题以及后续迭代想法

1. 目前只能画柱状图，还没有引入其他图形的画法
2. 对于数据库中还没有的数据的处理还不够完善
3. 在网页中观看麻烦，不能把所有内容全部同步显示，后续可以考虑直接生成pdf报告
