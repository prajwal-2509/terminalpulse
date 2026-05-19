from __future__ import annotations
import json
import asyncio
from pathlib import Path
from typing import Any

STATE_FILE = Path.home() / ".devpulse_state.json"


def read_state() -> dict:
    if not STATE_FILE.exists():
        return {"error": "No state yet. Is the daemon running?"}
    return json.loads(STATE_FILE.read_text())


def get_hottest_error() -> dict:
    state = read_state()
    hottest = state.get("hottest", [])
    error = next((e for e in hottest if e["type"] == "command_failed"), None)
    if not error:
        return {"error": "No recent errors found"}
    return {
        "cmd": error.get("cmd"),
        "exit_code": error.get("exit_code"),
        "stderr": error.get("stderr_tail", "").replace("|", "\n") if error.get("stderr_tail") else None,
        "cwd": error.get("cwd"),
        "heat": error.get("heat"),
    }


def get_active_context() -> dict:
    state = read_state()
    return {
        "active_file": state.get("active_file"),
        "active_language": state.get("active_language"),
        "project_type": state.get("project_type"),
        "git": state.get("git"),
    }


def get_history() -> list:
    state = read_state()
    return state.get("history", [])


async def handle_mcp_request(reader, writer):
    data = await reader.readline()
    try:
        request = json.loads(data)
        method = request.get("method")
        req_id = request.get("id", 1)

        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "terminalpulse",
                        "version": "0.2.0"
                    }
                }
            }

        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "get_pulse_state",
                            "description": "Get the full current coding context including hottest events, git info, and project type",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        {
                            "name": "get_hottest_error",
                            "description": "Get the most recent terminal error with full stderr output",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        {
                            "name": "get_active_context",
                            "description": "Get the active file, language, project type and git branch",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        {
                            "name": "get_history",
                            "description": "Get the last 30 minutes of coding activity as a timeline",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                    ]
                }
            }

        elif method == "tools/call":
            tool_name = request.get("params", {}).get("name")
            if tool_name == "get_pulse_state":
                result = read_state()
            elif tool_name == "get_hottest_error":
                result = get_hottest_error()
            elif tool_name == "get_active_context":
                result = get_active_context()
            elif tool_name == "get_history":
                result = get_history()
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }

        else:
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }

        writer.write((json.dumps(response) + "\n").encode())
        await writer.drain()

    except Exception as e:
        error_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32700, "message": str(e)}
        }
        writer.write((json.dumps(error_response) + "\n").encode())
        await writer.drain()
    finally:
        writer.close()


async def main():
    server = await asyncio.start_server(
        handle_mcp_request, "127.0.0.1", 7078
    )
    print("MCP server running on port 7078")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
