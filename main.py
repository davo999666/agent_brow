
import threading
from queue import Queue, Empty
from urllib.parse import urlparse

from langchain_core.callbacks import BaseCallbackHandler

from graphs.main_graph import graph
from tools.browser_lifecycle import BrowserLifecycle
from tools.browser_manager import set_browser_lifecycle
from tools.desktop_panel import AgentPanel
from tools.agent_control import (
    stop_agent,
    resume_agent,
    check_agent_stop,
    AgentStopped,
)
from llm.model import stop_local_llm


class PanelStreamingHandler(BaseCallbackHandler):
    """Stream LLM tokens and tool events to Tkinter."""

    def __init__(self, panel):
        self.panel = panel

    def on_llm_new_token(self, token, **kwargs):
        if token:
            self.panel.emit("token", token)

    def on_tool_start(self, serialized, input_str, **kwargs):
        name = serialized.get("name", "Unknown tool")
        self.panel.emit("tool", f"Running: {name}")

    def on_tool_end(self, output, **kwargs):
        self.panel.emit("tool", "Tool completed")

    def on_tool_error(self, error, **kwargs):
        self.panel.emit("error", str(error))


def main():
    tasks = Queue()
    shutdown_event = threading.Event()

    # -----------------------------------
    # Desktop Panel callbacks
    # -----------------------------------

    def on_start(domain, prompt):
        domain = domain.strip()
        prompt = prompt.strip()

        if not prompt:
            return

        if domain and not domain.startswith(("http://", "https://")):
            domain = "https://" + domain

        # Cancel the current graph run.
        stop_agent()

        # Remove old queued prompts.
        while True:
            try:
                tasks.get_nowait()
                tasks.task_done()
            except Empty:
                break

        # The worker will clear cancellation only
        # when it starts this new task.
        tasks.put((domain, prompt))

        panel.emit("status", "Prompt queued")

    def on_stop():
        stop_agent()
        panel.emit("status", "Stopping...")
        print("Stop requested")

    panel = AgentPanel(
        on_start=on_start,
        on_stop=on_stop,
    )

    # -----------------------------------
    # Browser Worker
    # -----------------------------------

    def agent_worker():
        browser = BrowserLifecycle(
            url="about:blank",
            headless=False,
        )

        try:
            browser.start()
            set_browser_lifecycle(browser)

            print(
                "PLAYWRIGHT THREAD:",
                threading.get_ident()
            )

            panel.emit("status", "Browser ready")

            while not shutdown_event.is_set():
                try:
                    domain, prompt = tasks.get(timeout=0.2)

                except Empty:
                    continue

                try:
                    # Only reset cancellation when
                    # starting the next queued prompt.
                    resume_agent()

                    check_agent_stop()

                    page = browser._page

                    # Keep the current browser page when
                    # the new prompt targets the same host.
                    if domain:
                        current_host = urlparse(page.url).hostname
                        requested_host = urlparse(domain).hostname

                        if current_host != requested_host:
                            panel.emit("status", "Navigating...")

                            check_agent_stop()

                            page.goto(
                                domain,
                                wait_until="domcontentloaded",
                            )

                    check_agent_stop()

                    panel.emit("status", "Agent working...")

                    config = {
                        "configurable": {
                            "thread_id": "browser_session_1"
                        },
                        "recursion_limit": 100,
                        "callbacks": [
                            PanelStreamingHandler(panel)
                        ],
                    }

                    result = graph.invoke(
                        {
                            "goal": prompt,
                            "start_url": page.url,
                        },
                        config=config,
                    )

                    check_agent_stop()

                    final_text = (
                        result.get("final_answer")
                        or result.get("answer")
                        or result.get("reason")
                    )

                    if final_text:
                        panel.emit("result", str(final_text))
                    else:
                        panel.emit("status", "Completed")

                except AgentStopped:
                    panel.emit("status", "Stopped")
                    print("Agent stopped successfully")

                except Exception as error:
                    panel.emit("error", str(error))
                    print("Agent error:", error)

                finally:
                    tasks.task_done()

        except Exception as error:
            panel.emit(
                "error",
                f"Browser startup failed: {error}"
            )

        finally:
            try:
                browser.stop()
            finally:
                stop_local_llm()

    # -----------------------------------
    # Start Browser Worker
    # -----------------------------------

    worker = threading.Thread(
        target=agent_worker,
        daemon=False,
    )
    worker.start()

    try:
        panel.run()

    finally:
        shutdown_event.set()
        stop_agent()
        worker.join()


if __name__ == "__main__":
    main()
