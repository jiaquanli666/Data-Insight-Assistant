"""
LangChain Tools used by the agents.
"""
import os
import uuid
from io import StringIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from langchain_core.tools import tool

from agent_project.database import get_connection
from agent_project.schema_rag import retrieve_schema_context
from agent_project.config import CHART_OUTPUT_DIR

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


@tool
def get_schema_tool(query: str) -> str:
    """搜索数据库表结构和相关查询示例。在写SQL之前必须先调用此工具来了解表名、字段名。
    参数 query: 用户的原始问题，用于检索最相关的Schema信息和查询模板。"""
    return retrieve_schema_context(query)


@tool
def execute_sql(sql: str) -> str:
    """执行SQL查询并返回结果。仅支持SELECT语句。
    参数 sql: 要执行的SELECT语句。"""
    if not sql.strip().upper().startswith("SELECT"):
        return "错误：只允许执行 SELECT 查询。"
    try:
        conn = get_connection()
        df = pd.read_sql_query(sql, conn)
        conn.close()
        if df.empty:
            return "查询结果为空。"
        return df.to_markdown(index=False, floatfmt=".2f")
    except Exception as e:
        return f"SQL执行错误: {e}"


@tool
def generate_chart(data_json: str, chart_type: str, title: str = "", x_label: str = "", y_label: str = "") -> str:
    """根据数据生成图表并保存为PNG文件。在查询Agent拿到数据后，如果需要可视化，调用此工具。
    参数 data_json: JSON字符串，格式为 {"x": [...], "y": [...]} 或 {"labels": [...], "values": [...]} 或 {"categories": [...], "series": {"系列1": [...], "系列2": [...]}}
    参数 chart_type: 图表类型，可选 bar/line/pie/scatter
    参数 title: 图表标题（可选）
    参数 x_label: X轴标签（可选）
    参数 y_label: Y轴标签（可选）
    返回值: 保存的图表文件路径"""
    import json
    data = json.loads(data_json)

    fig, ax = plt.subplots(figsize=(8, 5))

    if chart_type == "bar":
        if "categories" in data and "series" in data:
            x = data["categories"]
            width = 0.8 / len(data["series"])
            for i, (name, vals) in enumerate(data["series"].items()):
                pos = [j + i * width for j in range(len(x))]
                ax.bar(pos, vals, width, label=name)
            ax.set_xticks([j + width * (len(data["series"]) - 1) / 2 for j in range(len(x))])
            ax.set_xticklabels(x)
            ax.legend()
        else:
            ax.bar(data.get("x", data.get("labels", [])), data.get("y", data.get("values", [])))
    elif chart_type == "line":
        ax.plot(data.get("x", data.get("labels", [])), data.get("y", data.get("values", [])), marker="o")
    elif chart_type == "pie":
        ax.pie(data.get("y", data.get("values", [])), labels=data.get("x", data.get("labels", [])), autopct="%1.1f%%")
    elif chart_type == "scatter":
        ax.scatter(data.get("x", []), data.get("y", []))
    else:
        plt.close()
        return f"不支持的图表类型: {chart_type}"

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    fig.tight_layout()

    filename = f"chart_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(CHART_OUTPUT_DIR, filename)
    fig.savefig(filepath, dpi=120)
    plt.close(fig)
    return filepath


QUERY_AGENT_TOOLS = [get_schema_tool, execute_sql]
VIZ_AGENT_TOOLS = [generate_chart]
