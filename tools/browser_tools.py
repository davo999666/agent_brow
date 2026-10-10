import base64


from tools.browser_manager import get_browser_lifecycle


def take_screenshot() -> str:
    """
    Take a screenshot of the current browser page.
    """
    print("======================= take screenshot =======================")
    browser = get_browser_lifecycle()
    page = browser.get_page()

    screenshot = page.screenshot()
    image_base64 = base64.b64encode(screenshot).decode()

    return f"data:image/png;base64,{image_base64}"




