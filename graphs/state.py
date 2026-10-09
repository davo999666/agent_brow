from typing import Any, Dict, List, TypedDict


class Action(TypedDict, total=False):
    tool_called: bool
    tool_name: str
    tool_args: Dict[str, Any]
    reason: str


class HistoryItem(TypedDict, total=False):
    index: int
    current_url: str
    action: Action
    result: Any


class MainGraphState(TypedDict, total=False):
    goal: str
    start_url: str
    current_url: str
    history: List[HistoryItem]
    finished: bool