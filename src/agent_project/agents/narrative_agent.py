"""
Narrative Agent: turns raw query results into human-readable analysis.
Uses structured output to ensure consistent format.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from agent_project.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, LLM_MODEL

NARRATIVE_SYSTEM_PROMPT = """你是一位资深数据分析师，擅长从数据中提炼洞察并写成通俗易懂的报告。

根据用户的原始问题、SQL查询结果和图表信息，用自然语言写一段分析报告。

要求：
1. 用 2-4 段话概括核心发现
2. 引用具体数字支撑观点
3. 如果数据有趋势、排名、异常值，要指出
4. 语言简洁有力，像咨询报告的风格
5. 如果提到了图表，在叙述中注明"（见图表）"
6. 不要只是复述表格数据，要给出"so what"——数据说明了什么
"""


def create_narrative_agent():
    llm = ChatOpenAI(
        model=LLM_MODEL,
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=0.3,
    )

    def run(user_query: str, query_result: str, has_chart: bool) -> str:
        if not query_result or query_result.startswith("查询结果为空"):
            return "未能查找到相关数据，请尝试调整问题。"

        chart_note = "已生成可视化图表。" if has_chart else "未生成图表。"

        prompt = f"""用户问题：{user_query}

数据查询结果：
{query_result}

{chart_note}

请根据以上信息写一份数据洞察分析报告。"""

        response = llm.invoke([
            SystemMessage(content=NARRATIVE_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
        return response.content

    return run
