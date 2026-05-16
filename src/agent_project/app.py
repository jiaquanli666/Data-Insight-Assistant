"""
Streamlit frontend for the Data Insight Assistant.
"""
import streamlit as st

from agent_project.database import init_database
from agent_project.graph import create_graph
from agent_project.schema_rag import get_vector_store

st.set_page_config(
    page_title="数据洞察助手",
    page_icon="📊",
    layout="wide",
)

init_database()


@st.cache_resource
def load_graph():
    return create_graph()


@st.cache_resource
def init_rag():
    get_vector_store()


graph = load_graph()
init_rag()

# --- Sidebar ---
with st.sidebar:
    st.title("📊 数据洞察助手")
    st.markdown("""
    基于 **LangGraph 多 Agent 协作** 的智能数据分析系统。

    ### 三大 Agent
    - 🔍 **查询 Agent** — 自然语言转 SQL
    - 📈 **可视化 Agent** — 自动图表推荐与生成
    - 📝 **叙事 Agent** — 数据洞察写作

    ### 技术栈
    - LLM: DeepSeek-Chat
    - Embedding: DashScope
    - 框架: LangGraph + LangChain
    - 向量库: Chroma

    ### 示例数据库
    电商零售数据库，包含：
    - 5 个分类、20 个产品
    - 30 个客户、200 个订单
    """)

    st.divider()
    st.caption('试试问："哪个品类卖得最好"、"最近7天销售趋势"、"金卡 vs 普通会员消费对比"')

# --- Main ---
st.title("📊 数据洞察对话助手")
st.caption("用自然语言提问，Agent 自动查数据、画图表、写分析")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("输入你的问题，例如：上个月哪个品类销售额最高？"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            init_state = {
                "messages": [],
                "user_query": prompt,
                "is_data_question": True,
                "query_result": "",
                "chart_path": "",
                "has_chart": False,
                "narrative": "",
                "final_response": "",
            }

            try:
                result = graph.invoke(init_state)
            except Exception as e:
                result = {
                    "final_response": f"出错了: {e}",
                    "has_chart": False,
                }

        if result.get("has_chart") and result.get("chart_path"):
            st.markdown("### 📋 数据查询结果")
            st.markdown(result["query_result"])

            st.markdown("### 📈 可视化图表")
            st.image(result["chart_path"])

            st.markdown("### 📝 数据洞察")
            st.markdown(result["narrative"])
        else:
            st.markdown(result.get("final_response", "抱歉，处理过程中出现了问题。"))

        st.session_state.messages.append({
            "role": "assistant",
            "content": result.get("final_response", ""),
        })
