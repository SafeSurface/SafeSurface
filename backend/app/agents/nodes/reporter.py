import os
from datetime import datetime
from typing import Dict, Any
from langchain_core.messages import SystemMessage, AIMessage

from app.models.state import SafeSurfaceState
from app.utils.logger import setup_logger

logger = setup_logger("agent.reporter")

class ReporterAgent:
    """Reporting Agent responsible for compiling actions into a formal Penetration Test Report."""
    
    def __init__(self, llm_client):
        self.llm = llm_client
        # 确保 reports 目录存在，统一存放在 backend/reports 下，避免路径漂移
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.reports_dir = os.path.join(base_dir, "reports")
        os.makedirs(self.reports_dir, exist_ok=True)

    def __call__(self, state: SafeSurfaceState) -> Dict[str, Any]:
        logger.info("ReporterAgent is compiling the final penetration test report...")
        messages = state.get("messages", [])
        
        # 提取对话历史中的核心信息，过滤掉冗长的单纯工具返回（或截断）
        history_text = ""
        for msg in messages:
            if msg.type == "human":
                history_text += f"🎯 [Task/Objective]: {msg.content}\n"
            elif msg.type == "ai" and msg.content:
                history_text += f"🧠 [AI Analysis]: {msg.content}\n"
            elif msg.type == "tool":
                # 简单截断一下工具的原始返回，防止超过 Token 限制
                snippet = str(msg.content)[:300].replace('\n', ' ')
                history_text += f"✅ [Tool Execution Result Snippet]: {snippet}...\n"
                
        system_prompt = SystemMessage(
            content=(
                "You are an elite Cyber Security Reporting Secretary. "
                "Your task is to review the execution history of an autonomous penetration testing session "
                "and generate a formal, well-structured, professional MARKDOWN report. "
                "The report MUST include:\n"
                "1. **Executive Summary** (What was tested and the final outcome)\n"
                "2. **Methodology & Tactics** (What tools/methods were used, e.g., Brute Force, Web Automation)\n"
                "3. **Discoveries & Findings** (Explicitly State any successful bypasses, credentials, or vulnerabilities found)\n"
                "4. **Remediation Suggestions** (How the developers can fix the vulnerabilities)\n"
                "Do NOT output raw graphs or unrelated chat. Output ONLY the strictly formatted markdown document."
            )
        )
        
        user_prompt = AIMessage(content=f"Here is the execution log of the session:\n\n{history_text}")
        
        try:
            response = self.llm.invoke([system_prompt, user_prompt])
            report_content = response.content
            
            # 生成文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"penetration_report_{timestamp}.md"
            report_path = os.path.join(self.reports_dir, report_filename)
            
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_content)
                
            logger.info(f"✅ Formal Report successfully generated at: {report_path}")
            
            # 添加一条系统提示，告知主 Graph 路线已经结束并且生成了报告
            final_msg = AIMessage(content=f"Mission Complete. The formal penetration test report has been generated and saved to: {report_path}")
            return {"messages": [final_msg]}
            
        except Exception as e:
            logger.error(f"ReporterAgent failed to generate report: {e}")
            return {"messages": [AIMessage(content=f"Mission Complete, but report generation failed: {str(e)}")]}
