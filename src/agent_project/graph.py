"""
LangGraph orchestrator: coordinates Query → Viz → Narrative agents.
"""
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from agent_project.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, LLM_MODEL
from agent_project.agents.query_agent import create_query_agent
from agent_project.agents.viz_agent import create_viz_agent
from agent_project.agents.narrative_agent import create_narrative_agent


class AgentState(TypedDict):
    messages: list
    user_query: str
    is_data_question: bool
    query_result: str
    chart_path: str
    has_chart: bool
    narrative: str
    final_response: str


COORDINATOR_PROMPT = """你是一个智能路由助手。判断用户的问题是否需要查询数据库才能回答。

需要查询数据库（返回 true）：
- 需要统计数据、排名、趋势、汇总
- 问"多少""哪个""排名""对比""趋势""占比"等涉及具体数据的问题
- 涉及销售、订单、客户、产品、库存等业务指标

不需要查询数据库（返回 false）：
- 闲聊、打招呼
- 问你的能力范围
- 纯概念解释
- 已经有足够信息可以回答的问题

只输出一个单词：true 或 false。"""


def _get_llm(temperature: float = 0):
    return ChatOpenAI(
        model=LLM_MODEL,
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=temperature,
    )


def coordinator_node(state: AgentState) -> AgentState:
    """Decide whether the user's question needs data from the database."""
    user_query = state["user_query"]

    llm = _get_llm()
    response = llm.invoke([
        SystemMessage(content=COORDINATOR_PROMPT),
        HumanMessage(content=user_query),
    ])

    is_data = "true" in response.content.lower().strip()
    state["is_data_question"] = is_data

    if not is_data:
        chat_llm = _get_llm(temperature=0.7)
        reply = chat_llm.invoke([
            SystemMessage(content="你是一个友好的数据助手，可以帮助用户分析数据。当用户问非数据问题时，友好地回答。"),
            HumanMessage(content=user_query),
        ])
        state["final_response"] = reply.content

    return state


def query_agent_node(state: AgentState) -> AgentState:
    """Run the Query Agent (Text-to-SQL with schema RAG)."""
    agent = create_query_agent()
    user_query = state["user_query"]

    result = agent.invoke({
        "messages": [
            HumanMessage(content=user_query)
        ]
    })

    # Extract the final response from the agent
    final_msg = result["messages"][-1]
    state["query_result"] = final_msg.content if hasattr(final_msg, "content") else str(final_msg)
    return state


def viz_agent_node(state: AgentState) -> AgentState:
    """Run the Visualization Agent to decide and generate charts."""
    viz_agent = create_viz_agent()
    result = viz_agent(state["user_query"], state["query_result"])

    state["has_chart"] = result["should_chart"]
    state["chart_path"] = result.get("chart_path", "")
    return state


def narrative_agent_node(state: AgentState) -> AgentState:
    """Run the Narrative Agent to write analysis."""
    narrator = create_narrative_agent()
    narrative = narrator(
        state["user_query"],
        state["query_result"],
        state["has_chart"],
    )
    state["narrative"] = narrative

    # Build final response
    parts = []
    parts.append(f"### 数据查询结果\n\n{state['query_result']}")
    if state["has_chart"]:
        parts.append(f"\n### 可视化图表\n\n![chart]({state['chart_path']})")
    parts.append(f"\n### 数据洞察\n\n{state['narrative']}")
    state["final_response"] = "\n\n".join(parts)
    return state


def route_after_coordinator(state: AgentState) -> str:
    """Route to query agent or end directly."""
    return "query_agent" if state["is_data_question"] else END


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("query_agent", query_agent_node)
    workflow.add_node("viz_agent", viz_agent_node)
    workflow.add_node("narrative_agent", narrative_agent_node)

    workflow.set_entry_point("coordinator")

    workflow.add_conditional_edges(
        "coordinator",
        route_after_coordinator,
        {"query_agent": "query_agent", END: END},
    )

    workflow.add_edge("query_agent", "viz_agent")
    workflow.add_edge("viz_agent", "narrative_agent")
    workflow.add_edge("narrative_agent", END)

    return workflow.compile()


def create_graph():
    """Create and return the compiled LangGraph application."""
    return build_graph()
