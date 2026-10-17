from chains.chain import browser_worker_chain

from browser.browser_tools import take_screenshot


def browser_worker_node(state: dict) -> dict:
    print("======================= BROWSER WORKER =======================")

    history = state.get("history", [])
    last_result = history[-1].get("result", "") if history else ""

    screenshot = take_screenshot()

    response = browser_worker_chain.invoke({
        "goal": state.get("goal", ""),
        "current_url": state.get("current_url", ""),
        "history": history[-5:],
        "last_result": last_result,
        "image_url": screenshot,
    })

    if response.tool_calls:
        tool = response.tool_calls[0]

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

    new_history = history + [{
        "index": len(history),
        "current_url": state.get("current_url", ""),
        "action": action,
        "result": None,
    }]

    print("======================= END WORKER =======================\n")

    return {
        "history": new_history,
        "finished": False,
    }