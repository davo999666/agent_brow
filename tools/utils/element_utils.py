from tools.browser_manager import get_browser_lifecycle


def get_locator(page, element):

    tag = element.get("tag")
    text = element.get("text")
    placeholder = element.get("placeholder")
    aria = element.get("ariaLabel")
    element_id = element.get("id")
    href = element.get("href")

    # strongest selector
    if element_id:
        return page.locator(f"#{element_id}")


    # exact href
    if href:
        return page.locator(
            f'{tag}[href="{href}"]'
            if tag
            else f'[href="{href}"]'
        )


    # input placeholder
    if placeholder:
        return page.get_by_placeholder(
            placeholder,
            exact=True
        )


    # aria label
    if aria:
        return page.get_by_label(
            aria,
            exact=True
        )


    # tag + text
    if tag and text:
        return page.locator(
            f"{tag}:has-text('{text}')"
        )


    # only text
    if text:
        return page.get_by_text(
            text,
            exact=True
        )


    return None





def show_click_marker(page, x, y, duration=2000):
    """
    Show a red click marker on the page and remove it after duration.
    """

    page.evaluate(
        """
        ([x, y, duration]) => {

            const old = document.getElementById(
                "agent-click-marker"
            );

            if (old) {
                old.remove();
            }


            const marker = document.createElement("div");

            marker.id = "agent-click-marker";

            marker.style.position = "fixed";
            marker.style.left = (x - 10) + "px";
            marker.style.top = (y - 10) + "px";
            marker.style.width = "20px";
            marker.style.height = "20px";
            marker.style.background = "red";
            marker.style.border = "3px solid white";
            marker.style.borderRadius = "50%";
            marker.style.zIndex = "999999";
            marker.style.pointerEvents = "none";


            document.body.appendChild(marker);


            setTimeout(() => {

                const element = document.getElementById(
                    "agent-click-marker"
                );

                if (element) {
                    element.remove();
                }

            }, duration);
        }
        """,
        [x, y, duration]
    )