from typing import Literal
from langgraph.graph import END


def route_after_progress(state):
    if state.get("finished"):
        return END
    return "browser_worker"


# def route_after_tool(state):
#     history = state.get("history", [])
#     tool_name = history[-1]["action"]["tool_name"]
#     elements_len = len(history[-1].get("result", {}).get("elements", []))
#     # if tool_name == "find_and_click_element" and elements_len > 1:
#     #     return "executor"

#     return "progress_checker"
