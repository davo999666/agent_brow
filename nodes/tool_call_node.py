


from tools.agent_tools import browser_tools


TOOL_BY_NAME = { tool.name: tool for tool in browser_tools }


def tool_runner_node(state: dict) -> dict:
    print("======================= TOOL RUNNER =======================")

    history = state.get("history", [])

    if not history:
        print("No history found")
        return {"history": history}

    last_item = history[-1]

    action = last_item.get("action", {})

    if not action.get("tool_called"):
        print("No tool requested")
        return {"history": history}

    tool_name = action.get("tool_name")
    tool_args = action.get("tool_args", {})

    print(f"Calling tool: {tool_name}")
    print(f"Arguments: {tool_args}")

    tool = TOOL_BY_NAME.get(tool_name)

    if not tool:
        result = {
            "success": False,
            "error": f"Tool {tool_name} not found"
        }

    else:
        try:
            result = tool.invoke(tool_args)

        except Exception as e:
            result = {
                "success": False,
                "error": str(e)
            }

    print(f"Tool result: {result}")

    last_item["result"] = result

    print("======================= END TOOL RUNNER =======================\n")

    return {
        "history": history,
        "current_url": last_item.get("current_url", "")
    }