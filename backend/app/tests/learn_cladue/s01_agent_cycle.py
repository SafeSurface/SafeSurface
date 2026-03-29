"""
s01_agent_loop.py - The Agent Loop (OpenAI version)
The core pattern:
	while model asks for tools:
		response = LLM(messages, tools)
		execute tools
		append results
"""

import json
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[3]
if str(BACKEND_ROOT) not in sys.path:
	sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(BACKEND_ROOT / ".env", override=False)
load_dotenv(override=False)

if not os.getenv("LLM_API_KEY") and os.getenv("OPENAI_API_KEY"):
	os.environ["LLM_API_KEY"] = os.environ["OPENAI_API_KEY"]
if not os.getenv("LLM_BASE_URL") and os.getenv("OPENAI_BASE_URL"):
	os.environ["LLM_BASE_URL"] = os.environ["OPENAI_BASE_URL"]
if not os.getenv("LLM_MODEL") and os.getenv("MODEL_ID"):
	os.environ["LLM_MODEL"] = os.environ["MODEL_ID"]

from app.services.llm import llm_client


SYSTEM = f"You are a coding agent at {os.getcwd()}. Use bash to solve tasks. Act, don't explain."

TOOLS = [
	{
		"type": "function",
		"function": {
			"name": "bash",
			"description": "Run a shell command.",
			"parameters": {
				"type": "object",
				"properties": {"command": {"type": "string"}},
				"required": ["command"],
			},
		},
	}
]


def run_bash(command: str) -> str:
	dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
	if any(d in command for d in dangerous):
		return "Error: Dangerous command blocked"

	try:
		r = subprocess.run(
			command,
			shell=True,
			cwd=os.getcwd(),
			capture_output=True,
			text=True,
			timeout=120,
		)
		out = (r.stdout + r.stderr).strip()
		return out[:50000] if out else "(no output)"
	except subprocess.TimeoutExpired:
		return "Error: Timeout (120s)"


def _assistant_message_to_dict(message) -> dict:
	tool_calls = []
	for tc in message.tool_calls or []:
		tool_calls.append(
			{
				"id": tc.id,
				"type": tc.type,
				"function": {
					"name": tc.function.name,
					"arguments": tc.function.arguments,
				},
			}
		)

	return {
		"role": "assistant",
		"content": message.content or "",
		"tool_calls": tool_calls if tool_calls else None,
	}


def _extract_assistant_message(completion):
	if isinstance(completion, str):
		raise RuntimeError(completion)
	if not hasattr(completion, "choices") or not completion.choices:
		raise RuntimeError(
			f"Unexpected LLM response type: {type(completion).__name__}"
		)
	return completion.choices[0].message


# -- The core pattern: call tools until the model stops asking for them --
def agent_loop(messages: list[dict]) -> None:
	while True:
		try:
			completion = llm_client.chat_with_tools(
				messages=messages,
				tools=TOOLS,
				tool_choice="auto",
				max_completion_tokens=8000,
			)
		except Exception as e:
			print(f"LLM request failed: {e}")
			return

		try:
			assistant_message = _extract_assistant_message(completion)
		except RuntimeError as e:
			print(f"LLM call failed: {e}")
			return
		messages.append(_assistant_message_to_dict(assistant_message))

		if not assistant_message.tool_calls:
			return

		for tc in assistant_message.tool_calls:
			if tc.function.name != "bash":
				output = f"Error: Unknown tool {tc.function.name}"
			else:
				try:
					args = json.loads(tc.function.arguments or "{}")
				except json.JSONDecodeError:
					args = {}
				command = args.get("command", "")
				print(f"\033[33m$ {command}\033[0m")
				output = run_bash(command)
				print(output[:200])

			messages.append(
				{
					"role": "tool",
					"tool_call_id": tc.id,
					"content": output,
				}
			)


def _last_assistant_text(messages: list[dict]) -> str:
	for m in reversed(messages):
		if m.get("role") == "assistant":
			content = m.get("content")
			if isinstance(content, str) and content.strip():
				return content
	return ""


if __name__ == "__main__":
	history: list[dict] = [{"role": "system", "content": SYSTEM}]

	while True:
		try:
			query = input("\033[36ms01 >> \033[0m")
		except (EOFError, KeyboardInterrupt):
			break

		if query.strip().lower() in ("q", "exit", ""):
			break

		history.append({"role": "user", "content": query})
		agent_loop(history)

		text = _last_assistant_text(history) # Only print the last assistant message's text content, not the tool outputs
		if text:
			print(text)
		print()


