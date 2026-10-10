import threading

stop_event = threading.Event()


class AgentStopped(Exception):
    pass


def stop_agent():
    stop_event.set()


def resume_agent():
    stop_event.clear()


def check_agent_stop():
    if stop_event.is_set():
        raise AgentStopped("Agent stopped by user")