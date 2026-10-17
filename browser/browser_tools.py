import base64
from datetime import datetime
from pathlib import Path


from browser.browser_manager import get_browser_lifecycle


def take_screenshot() -> str:
    """
    Take a screenshot of the current browser page.
    """
    print("======================= take screenshot =======================")
    browser = get_browser_lifecycle()
    page = browser.get_page()

    screenshot = page.screenshot()
    folder = Path("screenshots")
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"screenshot_{datetime.now():%Y%m%d_%H%M%S_%f}.png"
    (folder / filename).write_bytes(screenshot)

    image_base64 = base64.b64encode(screenshot).decode()

    return f"data:image/png;base64,{image_base64}"




