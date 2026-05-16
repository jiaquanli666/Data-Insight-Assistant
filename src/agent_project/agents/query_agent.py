"""
Query Agent: Text-to-SQL agent with schema RAG.
Converts natural language questions into SQL, executes against the database,
and returns structured results.
"""
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from agent_project.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, LLM_MODEL
from agent_project.tools import QUERY_AGENT_TOOLS

QUERY_AGENT_SYSTEM_PROMPT = """你是一个数据分析助手，负责将用户的问题转换为 SQL 并查询数据库。

工作流程：
1. 首先调用 get_schema_tool 工具，传入用户的问题，获取相关的数据库表结构和查询示例
2. 根据获取到的 Schema 信息，编写正确的 SQL 语句
3. 调用 execute_sql 执行 SQL
4. 如果 SQL 执行出错，根据错误信息修正后重试
5. 查到结果后，用 markdown 表格格式原样展示数据，不要修改数字

重要规则：
- 只使用 SELECT 语句
- SQL 中的字符串使用单引号
- 涉及日期范围时使用 date() 函数，例如 date('now', '-1 month')
- 金额字段保留两位小数
- 查询默认只查状态为'已完成'的订单，除非用户明确要看其他状态
- 拿到结果后直接展示，不要编造数据"""


def create_query_agent() -> ChatOpenAI:
    llm = ChatOpenAI(
        model=LLM_MODEL,
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=0,
    )
    return create_react_agent(
        model=llm,
        tools=QUERY_AGENT_TOOLS,
        prompt=QUERY_AGENT_SYSTEM_PROMPT,
    )
