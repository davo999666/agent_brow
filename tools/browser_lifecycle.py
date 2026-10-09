import playwright.sync_api
from playwright._impl._errors import TargetClosedError
from typing import Optional
import logging
import random

logger = logging.getLogger(__name__)


class BrowserLifecycle:
    """Manages browser lifecycle (launch, context, page, close).
    
    Responsibilities:
    - Launch browser with proper configuration
    - Create browser context with stealth settings
    - Navigate to initial URL
    - Close browser and clean up resources
    """
    def __init__(self, url: str, headless: bool = True):
        self.url = url
        self.headless = headless
        self._playwright = None
        self._browser: Optional[playwright.sync_api.Browser] = None
        self._context: Optional[playwright.sync_api.BrowserContext] = None
        self._page: Optional[playwright.sync_api.Page] = None
        self._last_url: str = ""
    
    # ------------------------------------------------------------------
    # Browser lifecycle
    # ------------------------------------------------------------------
    
    def start(self) -> None:
        """Launch browser and open the target page."""
        self._playwright = playwright.sync_api.sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            channel="chrome",
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--window-size=1920,1080",
            ]
        )
        self._context = self._browser.new_context(
            viewport={ "width": 1280, "height": 720 },
            device_scale_factor=1,
            locale="en-US",
            timezone_id="America/New_York",
        )
        self._page = self._context.new_page()
        
        
        # Human-like delay before navigation
        delay = random.uniform(1.0, 3.0)
        logger.info(f"Waiting {delay:.1f}s before navigation (human-like delay)")
        self._page.wait_for_timeout(int(delay * 1000))
        
        logger.info(f"Navigating to {self.url}")
        self._page.goto(self.url, wait_until="domcontentloaded", timeout=30000)
        self._last_url = self._page.url
    
    def stop(self) -> None:
        """Close browser and clean up resources."""
        if self._browser:
            try:
                self._browser.close()
            except Exception:  # noqa: BLE001
                pass
        if self._playwright:
            try:
                self._playwright.stop()
            except Exception:
                pass
    
    # ------------------------------------------------------------------
    # Page access
    # ------------------------------------------------------------------
    
    def get_page(self) -> Optional[playwright.sync_api.Page]:
        """Get the current page."""
        return self._page
    
    def get_last_url(self) -> str:
        """Get the last recorded URL."""
        return self._last_url
    
    def is_page_alive(self) -> bool:
        """Check if the page is still open and usable."""
        if self._page is None:
            return False
        try:
            self._page.url
            return True
        except (TargetClosedError, Exception):
            return False
    

