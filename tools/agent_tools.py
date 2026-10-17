from browser.browser_manager import get_browser_lifecycle
from tools.utils.element_utils import  show_click_marker
from langchain_core.tools import tool
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError



@tool
def click_at(x, y) -> dict:
    """
    Click at the specified coordinates within the 1280x720 browser viewport.
    Analyze the screenshot and select the center of the target element.

    Coordinate system:
        - Origin (0, 0) is the top-left corner.
        - X increases rightward (0–1279).
        - Y increases downward (0–719).
        - Use actual screenshot pixels, not normalized coordinates.
        - Do not repeat a failed click at the same location.

    Args:
        x: Horizontal coordinate in pixels (0–1279).
        y: Vertical coordinate in pixels (0–719).
    """

    browser = get_browser_lifecycle()
    page = browser.get_page()

    try:
        # Remove bad characters from LLM output
        if isinstance(x, str):
            x = x.replace("[", "").replace("]", "").strip()
            if "," in x:
                x = x.split(",")[0]

        if isinstance(y, str):
            y = y.replace("[", "").replace("]", "").strip()
            if "," in y:
                y = y.split(",")[0]

        x = int(float(x))
        y = int(float(y))

        show_click_marker(page, x, y, duration=4000)

        page.wait_for_timeout(500)

        page.mouse.click(x, y)

        return {
            "success": True,
            "clicked_at": {
                "x": x,
                "y": y
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@tool
def close_modal() -> dict:
    """
    Close the currently visible modal or dialog.

    Use when a popup blocks interaction with the page.
    Do not use to confirm, submit, or accept a dialog.
    """

    browser = get_browser_lifecycle()
    page = browser.get_page()

    modal_selector = (
        '[role="dialog"], '
        '[aria-modal="true"], '
        '.modal.show, '
        '[class*="modal-content"]'
    )

    modal = page.locator(modal_selector).filter(visible=True).last

    def modal_closed():
        try:
            return not modal.is_visible()
        except Exception:
            return True

    try:
        if modal.count() == 0:
            return {
                "success": False,
                "reason": "No visible modal found"
            }

        # 1. Try close buttons inside modal
        close_selectors = [
            'button[aria-label*="close" i]',
            'button[title*="close" i]',
            'button[class*="close" i]',
            '[role="button"][aria-label*="close" i]',
            'button:has(svg.lucide-x)',
            'button:has(svg[class*="close"])',
        ]

        for selector in close_selectors:
            button = modal.locator(selector).first

            if button.count() > 0 and button.is_visible():
                button.click(timeout=2000)

                if modal_closed():
                    return {
                        "success": True,
                        "method": "close_button"
                    }

        # 2. Try Escape
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)

        if modal_closed():
            return {
                "success": True,
                "method": "escape"
            }

        return {
            "success": False,
            "reason": "Could not close modal automatically"
        }

    except PlaywrightTimeoutError:
        return {
            "success": False,
            "reason": "Timed out while closing modal"
        }

@tool
def type_text(text: str, submit: bool = False) -> str:
    """
    Type text into the currently focused input or textarea.
    Optionally press Enter to submit.
    """

    browser = get_browser_lifecycle()
    page = browser.get_page()

    focused = page.evaluate("""
        () => {
            const el = document.activeElement;

            if (!el) return null;

            return {
                tag: el.tagName.toLowerCase(),
                editable: (
                    el.tagName === "INPUT" ||
                    el.tagName === "TEXTAREA" ||
                    el.isContentEditable
                )
            };
        }
    """)

    if not focused or not focused["editable"]:
        return "ERROR: No editable input is focused. Click an input field first."

    page.keyboard.insert_text(text)

    if submit:
        page.keyboard.press("Enter")

    page.wait_for_timeout(500)

    return "Typed text" + (" and submitted" if submit else "")

@tool
def scroll_page(amount: int = 500) -> str:
    """
    Scroll page vertically.
    """

    browser = get_browser_lifecycle()
    page = browser.get_page()

    page.mouse.wheel(0, amount)
    page.wait_for_timeout(500)

    return f"Scrolled {amount}px"

@tool
def go_to_url(url: str) -> str:
    """
    Navigate browser to URL.
    """

    browser = get_browser_lifecycle()
    page = browser.get_page()

    page.goto(url, wait_until="domcontentloaded", timeout=30000)

    return f"Opened {url}"

@tool
def go_back() -> str:
    """
    Navigate back to the previous page.
    """
    browser = get_browser_lifecycle()
    page = browser.get_page()

    page.go_back(wait_until="load")

    return "Navigated back to the previous page."

@tool
def click_element(element: dict) -> dict:
    """
    Smart click element.
    Finds clickable element from provided information.
    """

    browser = get_browser_lifecycle()
    page = browser.get_page()

    try:
        tag = element.get("tag", "")
        text = element.get("text", "")
        href = element.get("href", "")
        class_name = element.get("class", "")
        element_id = element.get("id", "")
        placeholder = element.get("placeholder", "")
        aria_label = element.get("ariaLabel", "")


        locators = []


        # ID
        if element_id:
            locators.append(
                page.locator(f"#{element_id}")
            )


        # aria
        if aria_label:
            locators.append(page.get_by_label(  aria_label,  exact=True ))


        # placeholder
        if placeholder:
            locators.append( page.get_by_placeholder( placeholder,  exact=True) )


        # class
        if class_name:
            css_class = ".".join( class_name.split() )
            locators.append( page.locator( f".{css_class}" ) )


        # tag + text
        if text:
            if tag:
                locators.append( page.locator( f"{tag}:has-text('{text}')" ) )

            locators.append(page.get_by_text( text, exact=True ))


        # href only if useful
        if href and href != "#":
            locators.append( page.locator(  f"[href*='{href}']" ) )


        target = None


        # Find first visible element
        for locator in locators:

            try:
                count = locator.count()

                for i in range(count):

                    item = locator.nth(i)

                    if item.is_visible():
                        target = item
                        break

                if target:
                    break

            except:
                continue



        if not target:
            return {
                "success": False,
                "error": "No clickable element found",
                "element": element
            }



        # If current element is not clickable,
        # search clickable parent
        tag_name = target.evaluate( "(e)=>e.tagName.toLowerCase()" )


        if tag_name not in [
            "a",
            "button",
            "input"
        ]:

            parent = target.locator(  "xpath=ancestor::a | ancestor::button" )


            if parent.count() > 0:
                target = parent.first



        target.scroll_into_view_if_needed( timeout=2000 )


        try:
            target.click(
                timeout=3000
            )

        except:
            target.click(
                timeout=3000,
                force=True
            )


        return {
            "success": True,
            "clicked": True,
            "tag": tag_name,
            "text": text
        }



    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

@tool
def press_key(key: str) -> dict:
    """
    Press a keyboard key on the current page.
    Example keys: Enter, Escape
    """

    browser = get_browser_lifecycle()
    page = browser.get_page()

    try:
        page.keyboard.press(key)

        return {
            "success": True,
            "action": "press_key",
            "key": key
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@tool
def find_and_click_element(search: str):
    """
    Find visible clickable elements.
    If exactly one element matches, click it automatically.
    """
    browser = get_browser_lifecycle()
    page = browser.get_page()

    try:
        elements = page.evaluate(
            """
            (search) => {
                search = (search || "").toLowerCase().trim();

                return [...document.querySelectorAll(
                    'button, a, input, textarea, select, [role="button"], [title]'
                )]
                .filter(el => {
                    const r = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);

                    const text = (
                        el.innerText ||
                        el.querySelector("span")?.innerText ||
                        el.value ||
                        el.placeholder ||
                        el.title ||
                        el.getAttribute("aria-label") ||
                        ""
                    ).trim();

                    return (
                        r.width > 0 &&
                        r.height > 0 &&
                        style.display !== "none" &&
                        style.visibility !== "hidden" &&
                        text !== "" &&
                        (
                            search === "" ||
                            text.toLowerCase().includes(search)
                        )
                    );
                })
                .map(el => {
                    const r = el.getBoundingClientRect();

                    return {
                        tag: el.tagName.toLowerCase(),
                        text: (el.innerText || el.querySelector("span")?.innerText || "").trim(),

                        center_x: Math.round(r.x + r.width / 2),
                        center_y: Math.round(r.y + r.height / 2)
                    };
                });
            }
            """,
            search,
        )


        # Auto click when only one element exists
        if len(elements) >= 1:
            element = elements[0]

            result = click_at.invoke({
                "x": element["center_x"],
                "y": element["center_y"]
            })

            return {
                "success": True,
                "action": "auto_click",
                "element": element,
                "click_result": result
            }


        return {
            "success": True,
            "action": "return_elements",
            "count": len(elements),
            "elements": elements
        }


    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

browser_tools = [
    click_at,
    close_modal,
    type_text,
    find_and_click_element,
    press_key,
    scroll_page,
    go_to_url,
    go_back,
    
]