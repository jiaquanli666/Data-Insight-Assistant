"""
Visualization Agent: decides whether a chart would help convey the data,
chooses chart type, and generates it.
"""
import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from agent_project.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, LLM_MODEL
from agent_project.tools import generate_chart

VIZ_AGENT_SYSTEM_PROMPT = """你是一个数据可视化专家。根据用户问题和查询结果，判断是否需要生成图表。

如果需要图表，输出一个 JSON：
{
  "should_chart": true,
  "chart_type": "bar/line/pie/scatter",
  "title": "图表标题",
  "x_label": "X轴标签",
  "y_label": "Y轴标签",
  "data": { "x": [...], "y": [...] }
}

如果不需要图表（例如结果是单行数据、纯文字），输出：
{ "should_chart": false }

判断规则：
- 多行对比数据 → bar 柱状图
- 时间趋势数据 → line 折线图
- 占比分布 → pie 饼图（只有占比数据时才用）
- 散点关系 → scatter 散点图
- 单行/单值结果 → 不需要图表
"""


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM output, handling markdown code blocks."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:]) if lines[0].startswith("```") else text
        if text.endswith("```"):
            text = text[:-3]
    return json.loads(text.strip())


def create_viz_agent():
    llm = ChatOpenAI(
        model=LLM_MODEL,
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=0,
    )

    def run(user_query: str, query_result: str) -> dict:
        """Returns {"should_chart": bool, "chart_path": str|None}"""
        # If query result is empty or an error, skip chart
        if not query_result or query_result.startswith("查询结果为空") or query_result.startswith("SQL执行错误"):
            return {"should_chart": False, "chart_path": None}

        prompt = f"""用户问题：{user_query}

查询结果：
{query_result}

请根据以上信息判断是否需要生成图表。只输出JSON，不要其他内容。"""
        response = llm.invoke([
            SystemMessage(content=VIZ_AGENT_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])

        try:
            decision = _extract_json(response.content)
        except (json.JSONDecodeError, KeyError):
            return {"should_chart": False, "chart_path": None}

        if not decision.get("should_chart"):
            return {"should_chart": False, "chart_path": None}

        chart_path = generate_chart.invoke({
            "data_json": json.dumps(decision["data"]),
            "chart_type": decision["chart_type"],
            "title": decision.get("title", ""),
            "x_label": decision.get("x_label", ""),
            "y_label": decision.get("y_label", ""),
        })
        return {"should_chart": True, "chart_path": chart_path}

    return run
