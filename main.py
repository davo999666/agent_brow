from graphs.main_graph import graph
from tools.browser_lifecycle import BrowserLifecycle
from tools.browser_manager import set_browser_lifecycle


def main():
    goal = "Find an apartment for sale with a budget of $50,000."
    start_url = "https://www.list.am"

    browser_lifecycle = BrowserLifecycle(url=start_url, headless=False)

    try:
        browser_lifecycle.start()

        set_browser_lifecycle(browser_lifecycle)

        result = graph.invoke({"goal": goal, "start_url": start_url})

        print(result)

    finally:
        browser_lifecycle.stop()


if __name__ == "__main__":
    main()
