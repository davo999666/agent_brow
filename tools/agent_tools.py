from tools.browser_manager import get_browser_lifecycle
from tools.utils.element_utils import  get_locator, show_click_marker
from langchain_core.tools import tool


@tool
def click_at(x, y) -> dict:
    """
    Click at screen coordinates.
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

        show_click_marker(page, x, y, duration=3000)

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
def type_text(text: str, submit: bool = False) -> str:
    """
    Type text into the currently focused field. Optionally submit with Enter.
    """

    browser = get_browser_lifecycle()
    page = browser.get_page()

    page.keyboard.type(text)

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
            locators.append(
                page.get_by_label(
                    aria_label,
                    exact=True
                )
            )


        # placeholder
        if placeholder:
            locators.append(
                page.get_by_placeholder(
                    placeholder,
                    exact=True
                )
            )


        # class
        if class_name:
            css_class = ".".join(
                class_name.split()
            )

            locators.append(
                page.locator(
                    f".{css_class}"
                )
            )


        # tag + text
        if text:
            if tag:
                locators.append(
                    page.locator(
                        f"{tag}:has-text('{text}')"
                    )
                )

            locators.append(
                page.get_by_text(
                    text,
                    exact=True
                )
            )


        # href only if useful
        if href and href != "#":
            locators.append(
                page.locator(
                    f"[href*='{href}']"
                )
            )


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
        tag_name = target.evaluate(
            "(e)=>e.tagName.toLowerCase()"
        )


        if tag_name not in [
            "a",
            "button",
            "input"
        ]:

            parent = target.locator(
                "xpath=ancestor::a | ancestor::button"
            )


            if parent.count() > 0:
                target = parent.first



        target.scroll_into_view_if_needed(
            timeout=2000
        )


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
    # Coordinate fallback
    # click_at,
    type_text,

    find_and_click_element,

    # click_element,
    press_key,

    # Navigation
    scroll_page,
    go_to_url,
    go_back,
]