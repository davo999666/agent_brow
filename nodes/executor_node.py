from chains.chain import executor_chain


def executor_node(state: dict):

    history = state.get("history", [])

    response = executor_chain.invoke({ "last_history" : history[-1] })
    tool_calls = response.tool_calls

    if tool_calls:
        tool = tool_calls[0]

        action = {
            "tool_called": True,
            "tool_name": tool["name"],
            "tool_args": tool["args"],
            "reason": "",
        }
    else:
        action = {
            "tool_called": False,
            "tool_name": "",
            "tool_args": {},
            "reason": response.content,
        }
    new_history = history + [
        {
            "index": len(history),
            "current_url": state.get("current_url", ""),
            "action": action,
            "result": None,
        }
    ]




    return {
        "history": new_history,
        "finished": False,
    }