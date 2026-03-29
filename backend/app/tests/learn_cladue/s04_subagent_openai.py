"""
s04_subagent_openai.py - Subagents (PowerShell + OpenAI)

Spawn a child agent with fresh messages=[]. The child works in its own
context, sharing the filesystem, then returns only a summary to the parent.

    Parent agent                     Subagent
    +------------------+             +------------------+
    | messages=[...]   |             | messages=[]      |  <-- fresh
    |                  |  dispatch   |                  |
    | tool: task       | ----------> | while tool_use:  |
    |   prompt="..."   |             |   call tools     |
    |   description="" |             |   append results |
    |                  |  summary    |                  |
    |   result = "..." | <---------- | return last text |
    +------------------+             +------------------+

Key insight: "Process isolation gives context isolation for free."
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv
from openai import OpenAI


WORKDIR = Path.cwd().resolve()
BACKEND_ROOT = Path(__file__).resolve().parents[3]

# Load backend .env first, then process environment.
load_dotenv(BACKEND_ROOT / ".env", override=False)
load_dotenv(override=False)

# Accept both project-style and OpenAI-style variable names.
if not os.getenv("OPENAI_API_KEY") and os.getenv("LLM_API_KEY"):
    os.environ["OPENAI_API_KEY"] = os.environ["LLM_API_KEY"]
if not os.getenv("OPENAI_BASE_URL") and os.getenv("LLM_BASE_URL"):
    os.environ["OPENAI_BASE_URL"] = os.environ["LLM_BASE_URL"]
if not os.getenv("MODEL_ID") and os.getenv("LLM_MODEL"):
    os.environ["MODEL_ID"] = os.environ["LLM_MODEL"]


def normalize_base_url(base_url: str | None) -> str | None:
    if not base_url:
        return None
    url = base_url.rstrip("/")
    return url if url.endswith("/v1") else f"{url}/v1"


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=normalize_base_url(os.getenv("OPENAI_BASE_URL")),
)

MODEL = os.getenv("MODEL_ID", "gpt-4o")
SYSTEM = (
    f"You are a coding agent at {WORKDIR}. "
    "Use the task tool to delegate exploration or subtasks. "
    "This environment is Windows; prefer PowerShell commands."
)
SUBAGENT_SYSTEM = (
    f"You are a coding subagent at {WORKDIR}. "
    "Complete the given task and summarize findings concisely. "
    "This environment is Windows; prefer PowerShell commands."
)


def safe_path(p: str) -> Path:
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path


def shutil_which(name: str) -> str | None:
    for p in os.getenv("PATH", "").split(os.pathsep):
        candidate = Path(p) / (name + ".exe")
        if candidate.exists():
            return str(candidate)
    return None


def run_powershell(command: str) -> str:
    dangerous = ["Remove-Item -Recurse -Force C:\\", "shutdown", "Restart-Computer"]
    if any(d.lower() in command.lower() for d in dangerous):
        return "Error: Dangerous command blocked"

    shell = "pwsh" if shutil_which("pwsh") else "powershell"
    try:
        r = subprocess.run(
            [shell, "-NoProfile", "-Command", command],
            cwd=WORKDIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
    except Exception as e:
        return f"Error: {e}"


def run_read(path: str, limit: int | None = None) -> str:
    try:
        lines = safe_path(path).read_text(encoding="utf-8").splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more)"]
        return "\n".join(lines)[:50000]
    except Exception as e:
        return f"Error: {e}"


def run_write(path: str, content: str) -> str:
    try:
        fp = safe_path(path)
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} bytes"
    except Exception as e:
        return f"Error: {e}"


def run_edit(path: str, old_text: str, new_text: str) -> str:
    try:
        fp = safe_path(path)
        content = fp.read_text(encoding="utf-8")
        if old_text not in content:
            return f"Error: Text not found in {path}"
        fp.write_text(content.replace(old_text, new_text, 1), encoding="utf-8")
        return f"Edited {path}"
    except Exception as e:
        return f"Error: {e}"


TOOL_HANDLERS: dict[str, Callable[..., str]] = {
    "powershell": lambda **kw: run_powershell(kw["command"]),
    "read_file": lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file": lambda **kw: run_edit(kw["path"], kw["old_text"], kw["new_text"]),
}

CHILD_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "powershell",
            "description": "Run a PowerShell command in current workspace.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file contents from workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a workspace file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace exact text once in a workspace file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old_text": {"type": "string"},
                    "new_text": {"type": "string"},
                },
                "required": ["path", "old_text", "new_text"],
            },
        },
    },
]

PARENT_TOOLS = CHILD_TOOLS + [
    {
        "type": "function",
        "function": {
            "name": "task",
            "description": (
                "Spawn a subagent with fresh context. It shares filesystem "
                "but not conversation history."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "description": {
                        "type": "string",
                        "description": "Short description of the task",
                    },
                },
                "required": ["prompt"],
            },
        },
    }
]


def _assistant_message_to_dict(message: Any) -> dict[str, Any]:
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
        "tool_calls": tool_calls or None,
    }


def _last_assistant_text(messages: list[dict[str, Any]]) -> str:
    for msg in reversed(messages):
        if msg.get("role") == "assistant":
            content = msg.get("content")
            if isinstance(content, str) and content.strip():
                return content
    return ""


def run_subagent(prompt: str) -> str:
    sub_messages: list[dict[str, Any]] = [
        {"role": "system", "content": SUBAGENT_SYSTEM},
        {"role": "user", "content": prompt},
    ]

    for _ in range(30):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=sub_messages,
                tools=CHILD_TOOLS,
                tool_choice="auto",
                max_completion_tokens=8000,
            )
        except Exception as e:
            return f"Subagent error: {e}"

        if not response.choices:
            return "Subagent error: empty choices"

        message = response.choices[0].message
        sub_messages.append(_assistant_message_to_dict(message))

        if not message.tool_calls:
            text = message.content or ""
            return text.strip() or "(no summary)"

        for tc in message.tool_calls:
            name = tc.function.name
            handler = TOOL_HANDLERS.get(name)
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            try:
                output = handler(**args) if handler else f"Unknown tool: {name}"
            except Exception as e:
                output = f"Error: {e}"

            sub_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(output)[:50000],
                }
            )

    return "Subagent stopped: reached max rounds (30)"


def agent_loop(messages: list[dict[str, Any]]) -> None:
    while True:
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=PARENT_TOOLS,
                tool_choice="auto",
                max_completion_tokens=8000,
            )
        except Exception as e:
            print(f"LLM request failed: {e}")
            return

        if not response.choices:
            print("LLM request failed: empty choices")
            return

        message = response.choices[0].message
        messages.append(_assistant_message_to_dict(message))

        if not message.tool_calls:
            return

        for tc in message.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            if name == "task":
                desc = args.get("description", "subtask")
                prompt = args.get("prompt", "")
                print(f"> task ({desc}): {prompt[:80]}")
                output = run_subagent(prompt)
            else:
                handler = TOOL_HANDLERS.get(name)
                try:
                    output = handler(**args) if handler else f"Unknown tool: {name}"
                except Exception as e:
                    output = f"Error: {e}"

            print(f"  {str(output)[:200]}")
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(output),
                }
            )


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Missing OPENAI_API_KEY (or LLM_API_KEY)")
        sys.exit(1)

    history: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM}]

    while True:
        try:
            query = input("\033[36ms04 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break

        if query.strip().lower() in ("q", "exit", ""):
            break

        history.append({"role": "user", "content": query})
        agent_loop(history)

        text = _last_assistant_text(history)
        if text:
            print(text)
        print()
