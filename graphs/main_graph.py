from langgraph.graph import StateGraph
from graphs.state import MainGraphState
from graphs.routers import route_after_progress
from nodes.browser_worker_node import browser_worker_node
from nodes.progress_checker_node import progress_checker_node
from nodes.tool_call_node import tool_runner_node
from langgraph.checkpoint.memory import InMemorySaver

from tools.agent_control import check_agent_stop

def cancellable(node):
    def wrapper(state):
        check_agent_stop()

        result = node(state)

        check_agent_stop()

        return result

    return wrapper


builder = StateGraph(MainGraphState)

# Add nodes
builder.add_node( "browser_worker", cancellable(browser_worker_node))
builder.add_node("tool_call", tool_runner_node)
builder.add_node("progress_checker", progress_checker_node)

# Set entry point
builder.set_entry_point("browser_worker")

# Add edges
builder.add_edge("browser_worker", "tool_call")
builder.add_edge("tool_call", "progress_checker")

# Add conditional edges for routing
builder.add_conditional_edges( "progress_checker", route_after_progress)

checkpointer = InMemorySaver()

graph = builder.compile(checkpointer=checkpointer)
