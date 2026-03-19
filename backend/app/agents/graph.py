from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

import json
from typing import Literal, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from app.models.state import SafeSurfaceState
from app.config import settings
from app.agents.tools import fetch_webpage_title
from app.agents.context_manager import ContextManager

# 动态配置适配多种兼容 OpenAI 请求格式的 API，如 DeepSeek、通义等
llm = ChatOpenAI(
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL,
    model=settings.LLM_MODEL,
    temperature=0
)

tools = [fetch_webpage_title]
llm_with_tools = llm.bind_tools(tools)

# ======= 核心增强：定义主脑的结构化思考与战术策略模型 =======
class SupervisorDecision(BaseModel):
    tactical_analysis: str = Field(description="详细分析当前战局和上下文的推理过程")
    playbook_strategy: str = Field(description="应用哪个渗透测试策略 (例如: '初始Web全表面测绘', '身份验证框爆破', 'SQL盲注探测')")
    extracted_focus: str = Field(description="当前关注的确切目标URL或IP")
    next_action: Literal["recon", "exploit", "end"] = Field(description="下发给哪个实体队伍执行")

# 让语言模型按照指定的思维结构强制输出
llm_structured_planner = llm.with_structured_output(SupervisorDecision)

def supervisor_agent(state: SafeSurfaceState) -> dict:
    print("\n" + "="*50)
    print("🧠 [Master Planner] 读取全局状态并检索战术大纲...")
    messages = state.get("messages", [])
    if not messages:
        return {"messages": []}

    # 动态注入安全状态上下文，防止 LLM 失忆，同时使用 ContextManager 处理并瘦身 Message
    context_str = ContextManager.build_global_context(state)
    optimized_messages = ContextManager.optimize_messages(messages)

    system_prompt = SystemMessage(
        content=f"""You are the Master Planner for an elite Penetration Testing AI team.
        Read the global state to understand what we've discovered so far.
        
        {context_str}
        
        RULES FOR PLAYBOOK SELECTION:
        - If the user provides a new URL/IP and no assets exist, select strategy: 'Web Attack Surface Recon' and route to 'recon'.
        - If 'recon' found forms or interesting HTTP responses, select strategy: 'Vulnerability Probing' and route to 'exploit'.
        - If we hit a wall or finished, route to 'end'.
        Always extract the latest target url to focus on.
        """
    )
    
    try:
        decision: SupervisorDecision = llm_structured_planner.invoke([system_prompt] + optimized_messages)
    except Exception as e:
        print(f"❌ LLM 结构化生成失败: {e}")
        return {"messages": [SystemMessage(content=f"Planning Error: {str(e)}")], "next_step": "end"}
        
    print(f"🧠 [战术推演]: {decision.tactical_analysis}")
    print(f"🎯 [选用策略]: {decision.playbook_strategy}")
    print(f"🔀 [路由判定] 将任务下发至 -> {decision.next_action}")
    
    # 将决策转化成易读的信息写入 message 历史，以便前端追溯
    reply_msg = AIMessage(content=f"**[Selected Playbook: {decision.playbook_strategy}]**\n{decision.tactical_analysis}")
    
    # 自动把新目标记录进攻击树 (Context Update)
    attack_tree = state.get("attack_tree", {"pending_targets": [], "exploited_targets": [], "blocked_targets": []})
    if isinstance(attack_tree, BaseModel):
        attack_tree_dict = attack_tree.model_dump()
    else:
        attack_tree_dict = attack_tree
        
    if decision.extracted_focus and decision.extracted_focus not in attack_tree_dict["pending_targets"]:
        attack_tree_dict["pending_targets"].append(decision.extracted_focus)

    return {
        "messages": [reply_msg], 
        "next_step": decision.next_action,
        "current_focus": decision.playbook_strategy, # 保存当前策略到图状态 
        "attack_tree": attack_tree_dict
    }

def recon_agent(state: SafeSurfaceState) -> dict:
    print("\n" + "-"*50)
    print("[Recon Team] 根据策略执行情报收集...")
    messages = state.get("messages", [])
    
    # 侦察兵在干活时，携带上下文和策略，并对对话 Token 瘦身
    context_str = ContextManager.build_global_context(state)
    optimized_messages = ContextManager.optimize_messages(messages)
    
    system_prompt = SystemMessage(
        content=f"""You are the Recon Team.
        Current Strategy: {state.get('current_focus')}
        Context: {context_str}
        
        Using the provided context, invoke tools to gather intelligence on the pending targets.
        Do not explain yourself, just call the relevant tools immediately."""
    )
    
    try:
        response = llm_with_tools.invoke([system_prompt] + optimized_messages)
    except Exception as e:
        print(f"❌ LLM 请求失败: {e}")
        return {"messages": [SystemMessage(content=f"Error connecting to LLM: {str(e)}")], "next_step": "end"}
        
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"🛠️ [Recon Team] 发起实网探测 -> {[t['name'] for t in response.tool_calls]}")
    else:
        print("🕵️‍♀️ [Recon Team] 无需新工具，侦察分析报告生成完毕。")
        
    return {"messages": [response]}

def should_continue_recon(state: SafeSurfaceState) -> Literal["tools", "supervisor"]:
    messages = state.get("messages", [])
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print("⚙️ [引擎] 将执行以上真实的探测工具...")
        return "tools"
    print("⚙️ [引擎] 侦察结束，将报告退回给 Master Planner...")
    return "supervisor"

def build_agent_graph():
    builder = StateGraph(SafeSurfaceState)
    tool_node = ToolNode(tools)
    
    builder.add_node("supervisor", supervisor_agent)
    builder.add_node("recon", recon_agent)
    builder.add_node("exploit", lambda s: {"messages": [SystemMessage(content="Exploit Team: Mock payload deployed. (To be implemented)")]})
    builder.add_node("tools", tool_node)
    
    builder.add_edge(START, "supervisor")
    
    builder.add_conditional_edges(
        "supervisor",
        lambda state: state.get("next_step", "end"),
        {
            "recon": "recon",
            "exploit": "exploit",
            "end": END,
            "supervisor": END
        }
    )
    
    builder.add_conditional_edges("recon", should_continue_recon)
    builder.add_edge("tools", "recon")
    builder.add_edge("exploit", "supervisor")
    
    memory = MemorySaver()
    app = builder.compile(checkpointer=memory)
    return app
