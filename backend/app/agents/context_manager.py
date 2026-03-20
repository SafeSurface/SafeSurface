import json
from typing import List
import pprint
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from pydantic import BaseModel

from app.models.state import SafeSurfaceState
from app.memory.manager import memory_manager

class ContextManager:
    """
    负责高级上下文管理，核心目标：
    1. 动态注入战地简报与 RAG 记忆。
    2. 最大限度节省 Token (截断过长的 Tool 输出、折叠古老对话)。
    """

    @staticmethod
    def build_global_context(state: SafeSurfaceState) -> str:
        """
        生成给大模型的全局状态简报，采用紧凑语法，并自动外挂 RAG
        """
        assets = state.get("assets", {})
        attack_tree = state.get("attack_tree", {})
        
        # 将原始状态字典转换为格式化的字符串
        asset_str = pprint.pformat(assets, indent=2) if assets else "None"
        
        # 处理 attack_tree 可能是 pydantic 模型的情况
        if hasattr(attack_tree, "model_dump"):
            tree_str = pprint.pformat(attack_tree.model_dump(), indent=2)
        else:
            tree_str = pprint.pformat(attack_tree, indent=2) if attack_tree else "None"

        current_focus = state.get("current_focus", "Unknown Strategy")

        # 核心：通过当前的战术意图（current_focus）去向量库中检索相关联的知识和历史
        recalled_memory = memory_manager.retrieve_context(query=current_focus, limit=2)
        episodic_mem_str = "\n".join(recalled_memory.get("episodic", [])) or "None recalled."
        long_term_mem_str = "\n".join(recalled_memory.get("long_term", [])) or "None recalled."

        return f"""
            ====== CURRENT MISSION STATE ======
            [Discovered Assets]
            {asset_str}

            [Attack Tree / Target Scope]
            {tree_str}

            [Current Operational Focus]
            {current_focus}

            ====== PAST EXP & KNOWLEDGE (RAG) ======
            [Relevant Episodic Memory (Recent findings)]
            {episodic_mem_str}

            [Long-Term Knowledge / Playbook Tactics]
            {long_term_mem_str}
            ===================================
            """
        tree = state.get("attack_tree", {"pending_targets": [], "exploited_targets": []})
        
        ctx = "<global_state>\n"
        if assets:
            # 只提取核心信息，不将整个冗余的 Pydantic 模型全盘 dump
            compact_assets = {k: {"ports": v.get("ports", []), "vulns": v.get("vulnerabilities", [])} if isinstance(v, dict) else {"ports": v.ports, "vulns": v.vulnerabilities} for k, v in assets.items()}
            ctx += f"[Assets]: {json.dumps(compact_assets, separators=(',', ':'))}\n"
        else:
            ctx += "[Assets]: None\n"
            
        if isinstance(tree, BaseModel):
            tree = tree.model_dump()
            
        ctx += f"[Pending]: {','.join(tree.get('pending_targets', []))}\n"
        ctx += f"[Exploited]: {','.join(tree.get('exploited_targets', []))}\n"
        ctx += f"[Active_Strategy]: {state.get('current_focus', 'None')}\n"
        ctx += "</global_state>"
        return ctx

    @staticmethod
    def optimize_messages(messages: List[BaseMessage], max_tokens: int = 4000) -> List[BaseMessage]:
        """
        Token 瘦身策略：
        1. 永远保留第一条 SystemMessage(如果存在) 和最新的用户的 HumanMessage。
        2. 工具返回的 ToolMessage (特别是爬虫 HTML) 容易爆炸，对超过长度的旧工具返回进行截断。
        3. 只保留最近的 N 个回合对话。
        """
        if not messages:
            return []

        optimized = []
        # 只保留最近的 8 条消息，防止无限上卷
        recent_messages = messages[-8:]
        
        for msg in recent_messages:
            if isinstance(msg, ToolMessage):
                # 渗透测试工具的输出体（如网页源码、大规模端口扫描图）非常消耗 Token
                content_str = str(msg.content)
                if len(content_str) > 800:
                    # 中间截断，保留头部和尾部
                    optimized_content = content_str[:400] + "\n...[CONTENT TRUNCATED FOR TOKEN SAVING]...\n" + content_str[-400:]
                    # 由于 Pydantic V2 控制严格，直接重新构造 ToolMessage
                    optimized.append(ToolMessage(content=optimized_content, name=msg.name, tool_call_id=msg.tool_call_id))
                    continue
            optimized.append(msg)
            
        return optimized
