from typing import Literal
from langgraph.graph import END


def route_after_progress(state):
    if state.get("finished"):
        return END
    return "browser_worker"



