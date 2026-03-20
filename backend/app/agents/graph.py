from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from app.models.state import SafeSurfaceState
from app.config import settings
from app.agents.tools import fetch_webpage_title
from app.tools.system import execute_system_command
from app.tools.network import http_request_probe
from app.tools.browser import execute_browser_automation
from app.tools.ocr import perform_image_ocr
from app.agents.nodes.coordinator import CoordinatorAgent
from app.agents.nodes.recon import SpecialistReconAgent, should_continue_recon
from app.agents.nodes.exploit import exploit_node
from app.agents.nodes.reporter import ReporterAgent

def build_agent_graph():
    base_llm = ChatOpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
    )

    # 载入原生与新增的跨平台命令行、极简发包探针等安全工具
    tools = [
        fetch_webpage_title,
        execute_system_command,
        http_request_probe,
        execute_browser_automation,
        perform_image_ocr
    ]

    llm_with_tools = base_llm.bind_tools(tools)

    # Initialize decoupled agents
    coordinator = CoordinatorAgent(base_llm)
    recon = SpecialistReconAgent(llm_with_tools)
    reporter = ReporterAgent(base_llm)

    # Graph builder logic isolated
    builder = StateGraph(SafeSurfaceState)
    tool_node = ToolNode(tools)

    builder.add_node("supervisor", coordinator)
    builder.add_node("recon", recon)
    builder.add_node("exploit", exploit_node)
    builder.add_node("tools", tool_node)
    builder.add_node("reporter", reporter)

    builder.add_edge(START, "supervisor")

    builder.add_conditional_edges(
        "supervisor",
        lambda state: state.get("next_step", "end"),
        {
            "recon": "recon",
            "exploit": "exploit",
            "end": "reporter",
            "supervisor": "reporter"
        }
    )

    builder.add_conditional_edges("recon", should_continue_recon)
    builder.add_edge("tools", "recon")
    builder.add_edge("exploit", "supervisor")
    
    # 报告生成完毕后，任务彻底落定
    builder.add_edge("reporter", END)

    memory = MemorySaver()
    app = builder.compile(checkpointer=memory)
    return app
