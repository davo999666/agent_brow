from typing import Optional
from browser.browser_lifecycle import BrowserLifecycle


_browser_lifecycle: Optional[BrowserLifecycle] = None


def set_browser_lifecycle(lifecycle: BrowserLifecycle):
    global _browser_lifecycle
    _browser_lifecycle = lifecycle


def get_browser_lifecycle() -> BrowserLifecycle:
    if _browser_lifecycle is None:
        raise RuntimeError(
            "Browser lifecycle was not initialized"
        )

    return _browser_lifecycle