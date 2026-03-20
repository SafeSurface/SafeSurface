from typing import Literal, Dict, Any
from langchain_core.messages import SystemMessage, AIMessage
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

from app.models.state import SafeSurfaceState
from app.agents.context_manager import ContextManager
from app.utils.logger import setup_logger

logger = setup_logger("agent.coordinator")

class SupervisorDecision(BaseModel):
    tactical_analysis: str = Field(description="Detailed tactical analysis and reasoning for the current operation.")
    playbook_strategy: str = Field(description="The selected penetration testing playbook or strategy (e.g., 'Initial Web Surface Recon', 'Blind SQLi Probe').")
    extracted_focus: str = Field(description="The definitive target URL or IP extracted for focus.")
    next_action: Literal["recon", "exploit", "end"] = Field(description="The specific team or next action to route the execution to.")

class CoordinatorAgent:
    """Coordinator Agent responsible for strategic planning and routing."""

    def __init__(self, llm_client):
        self.llm = llm_client
        self.parser = PydanticOutputParser(pydantic_object=SupervisorDecision)

    def __call__(self, state: SafeSurfaceState) -> Dict[str, Any]:
        logger.info("CoordinatorAgent initialized reading global state and fetching playbook.")
        messages = state.get("messages", [])
        if not messages:
            return {"messages": []}

        context_str = ContextManager.build_global_context(state)
        optimized_messages = ContextManager.optimize_messages(messages)

        system_prompt = SystemMessage(
            content=f"""You are the Master Planner for an elite Penetration Testing AI team.
            Read the global state to understand what we've discovered so far.

            {context_str}

            RULES FOR PLAYBOOK SELECTION:
            - If the user provides a new URL/IP and no assets exist, select strategy: 'Web Attack Surface Recon' and route to 'recon'.
            - If 'recon' found forms or interesting HTTP responses, select strategy: 'Vulnerability Probing' and route to 'exploit'.
            - If progress stalls or the objective is complete, route to 'end'.
            Always accurately extract the latest target to focus on.

            {self.parser.get_format_instructions()}
            """
        )

        try:
            raw_response = self.llm.invoke([system_prompt] + optimized_messages)
            decision: SupervisorDecision = self.parser.parse(raw_response.content)
        except Exception as e:
            logger.error(f"CoordinatorAgent structured generation failed: {e}") 
            return {"messages": [SystemMessage(content=f"Planning Error: {str(e)}")], "next_step": "end"}
        
        logger.info(f"Tactical Analysis: {decision.tactical_analysis}")
        logger.info(f"Selected Strategy: {decision.playbook_strategy}")
        logger.info(f"Routing task to: {decision.next_action}")
        
        reply_msg = AIMessage(content=f"**[Selected Playbook: {decision.playbook_strategy}]**\n{decision.tactical_analysis}")
        
        attack_tree = state.get("attack_tree", {"pending_targets": [], "exploited_targets": [], "blocked_targets": []})
        attack_tree_dict = attack_tree.model_dump() if isinstance(attack_tree, BaseModel) else attack_tree
            
        if decision.extracted_focus and decision.extracted_focus not in attack_tree_dict["pending_targets"]:
            attack_tree_dict["pending_targets"].append(decision.extracted_focus)

        return {
            "messages": [reply_msg], 
            "next_step": decision.next_action,
            "current_focus": decision.playbook_strategy,
            "attack_tree": attack_tree_dict
        }