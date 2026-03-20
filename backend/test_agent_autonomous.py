import os
# Force clear the powershell cached empty variables before anything else
if os.environ.get("LLM_API_KEY") == "":
    os.environ.pop("LLM_API_KEY", None)

import logging
from app.agents.graph import build_agent_graph
from langchain_core.messages import HumanMessage

# 为了防止控制台太乱，我们暂时关掉 httpx 的底层日志
logging.getLogger("httpx").setLevel(logging.WARNING)

def run_autonomous_agent():
    app = build_agent_graph()
    
    # 模拟用户在前端输入了一段渗透需求
    user_prompt = """
    Mission: Please conduct a dictionary brute force attack on the Web authentication interface.
    Target: http://localhost:8887/login.php
    Constraint: 
    1. We suspect the username is 'admin'.
    2. Try the following passwords: '123456', 'admin', 'password'.
    3. Use your browser automation tool to fill in the form and click the submit button. You can extract HTML to check if the word "Welcome" appears or if the URL changes, which indicates a successful bypass.
    4. Provide the correct credentials once you succeed.
    """
    
    inputs = {"messages": [HumanMessage(content=user_prompt)]}
    config = {"configurable": {"thread_id": "dvwa-autonomous-test"}}
    
    print("==================================================")
    print("🚀 [Agent System Started] Deploying Autonomous Mission...")
    print("==================================================\n")

    # 驱动 LangGraph 状态机流转
    for event in app.stream(inputs, config=config, stream_mode="updates"):
        for node_name, node_state in event.items():
            print(f"\n📍 [Current Node]: {node_name.upper()}")
            messages = node_state.get("messages", [])
            
            if messages:
                last_msg = messages[-1]
                
                # 如果这个节点输出的是工具调用请求（大模型决定使用工具了）
                if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    print(f"🧠 [Agent Decision]: AI decided to engage tools:")
                    for t in last_msg.tool_calls:
                        print(f"   🔧 Tool Name: {t['name']}")
                        print(f"   ⚙️ Arguments: {t['args']}")
                        
                # 如果是最终生成的文本总结
                elif last_msg.type == "ai":
                    print(f"🗣️ [Agent Speech]:\n{last_msg.content}")
                    
                # 真实的工具执行完毕的返回结果
                elif last_msg.type == "tool":
                    print(f"✅ [Tool Result Snippet]: {str(last_msg.content)[:200]}... (truncated)")

    # 在流转结束后，把所有的重要 AI 回复提取出来形成一份 Markdown 报告
    print("\n==================================================")
    print("📝 [Report Generation] Compiling Penetration Test Report...")
    
    # 提取完整状态
    final_state = app.get_state(config)
    messages = final_state.values.get("messages", [])
    
    report_content = "# SafeSurface AI Penetration Test Report\n\n"
    report_content += "## 🎯 Mission Objective\n" + user_prompt.strip() + "\n\n"
    report_content += "## 🧠 Agent Execution Log\n\n"
    
    for msg in messages:
        if msg.type == "ai" and msg.content:
            report_content += f"### Assistant Analysis:\n{msg.content}\n\n"
            
    # 写入文件 (测试环境的临时简化报告)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    report_filename = os.path.join(base_dir, "reports", "test_report_summary.md")
    os.makedirs(os.path.dirname(report_filename), exist_ok=True)
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"✅ Report successfully saved to: {os.path.abspath(report_filename)}")
    print("==================================================")

if __name__ == "__main__":
    run_autonomous_agent()
