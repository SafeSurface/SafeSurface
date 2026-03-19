import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from fastapi.responses import StreamingResponse
import uuid

from app.agents.graph import build_agent_graph
from app.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# 允许前端跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_agent_graph()

class ScanRequest(BaseModel):
    query: str
    thread_id: str | None = None

@app.post("/api/v1/chat")
def chat_with_safesurface(request: ScanRequest):
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # 将标准请求转为 SSE 事件流发回前端
    def event_generator():
        inputs = {"messages": [HumanMessage(content=request.query)]}
        try:
            # 实时捕获图在游走中的每一个 Node 执行结果
            for event in graph.stream(inputs, config=config, stream_mode="updates"):
                for node_name, node_state in event.items():
                    log_msg = f"Executing sub-graph..."
                    messages = node_state.get("messages", [])
                    
                    if messages:
                        last_msg = messages[-1]
                        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                            tools = [t['name'] for t in last_msg.tool_calls]
                            log_msg = f"Invoke Tools: {tools}"
                        elif isinstance(last_msg, AIMessage):
                            # AI 生成的内容，有可能是纯决定，有可能是直接回给用户的话
                            log_msg = f"Decision made: {last_msg.content[:50]}..."
                        elif getattr(last_msg, "type", "") == "tool":
                            log_msg = f"Tool result fetched successfully."

                    # 把实时的思考步骤推给前端
                    yield_data = json.dumps({"type": "trace", "node": node_name, "content": log_msg})
                    yield f"data: {yield_data}\n\n"
            
            # 图执行结束，提取最后一条消息作为正式回复
            state = graph.get_state(config)
            final_content = "Mission sequence finished."
            if state.values.get("messages"):
                final_content = state.values["messages"][-1].content
                
            yield f"data: {json.dumps({'type': 'final', 'content': final_content, 'thread_id': thread_id})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)
