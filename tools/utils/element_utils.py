

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