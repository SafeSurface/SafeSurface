import os
from openai import OpenAI
from typing import List, Dict, Any, Optional
from app.config import settings


def _normalize_base_url(base_url: Optional[str]) -> Optional[str]:
    if not base_url:
        return base_url
    url = base_url.rstrip("/")
    if url.endswith("/v1"):
        return url
    return f"{url}/v1"

class LLMClient:
    """
    统一的大模型调用工具类，基于 OpenAI SDK 封装，兼容 DeepSeek 及其他模型。
    自动读取 app.config 中的环境变量 (API Key, Base URL, Model 等)。
    """
    
    def __init__(self):
        # 初始化 OpenAI 客户端，自动使用统一配置
        self.client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=_normalize_base_url(settings.LLM_BASE_URL)
        )
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE

    def chat(self, prompt: str, system_prompt: str = "You are a helpful assistant") -> str:
        """
        进行简单的单轮对话
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error connecting to LLM: {str(e)}"

    def chat_history(self, messages: List[Dict[str, str]]) -> str:
        """
        支持多轮历史对话的调用
        :param messages: 类似 [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=messages,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error connecting to LLM: {str(e)}"

    def chat_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        tool_choice: str = "auto",
        max_completion_tokens: int = 8000,
    ) -> Any:
        """
        支持工具调用的对话，返回 OpenAI 原始响应对象。
        """
        return self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            max_completion_tokens=max_completion_tokens,
            stream=False,
        )

# 提供一个全局单例实例供其他模块直接引入使用
llm_client = LLMClient()
