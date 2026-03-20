from typing import Literal, Dict, Any
from langchain_core.messages import SystemMessage

from app.models.state import SafeSurfaceState
from app.agents.context_manager import ContextManager
from app.utils.logger import setup_logger

logger = setup_logger("agent.recon")

class SpecialistReconAgent:
    """Specialist Agent responsible for intelligence gathering and reconnaissance."""
    
    def __init__(self, llm_client_with_tools):
        self.llm = llm_client_with_tools
        
    def __call__(self, state: SafeSurfaceState) -> Dict[str, Any]:
        logger.info("SpecialistReconAgent executing reconnaissance strategy.")
        messages = state.get("messages", [])
        
        context_str = ContextManager.build_global_context(state)
        optimized_messages = ContextManager.optimize_messages(messages)
        
        system_prompt = SystemMessage(
            content=f"""You are the Recon Team.
            Current Strategy: {state.get('current_focus')}
            Context: {context_str}
            
            Using the provided context, invoke tools to gather intelligence on the pending targets.
            Execute tool invocation without superfluous explanations."""
        )
        
        try:
            response = self.llm.invoke([system_prompt] + optimized_messages)
        except Exception as e:
            logger.error(f"SpecialistReconAgent LLM invocation failed: {e}")
            return {"messages": [SystemMessage(content=f"Execution Error: {str(e)}")], "next_step": "end"}
            
        if hasattr(response, "tool_calls") and response.tool_calls:
            logger.info(f"Executing tools: {[t['name'] for t in response.tool_calls]}")
        else:
            logger.info("Reconnaissance phase completed. Analysis generation finished.")
            
        return {"messages": [response]}


def should_continue_recon(state: SafeSurfaceState) -> Literal["tools", "supervisor"]:
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None
    
    if last_message and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        logger.info("Routing to tools execution node.")
        return "tools"
        
    logger.info("Reconnaissance ended, routing back to CoordinatorAgent.")
    return "supervisor"