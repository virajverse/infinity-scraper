"""
Dynamic Headless Browser Scraping Engine powered by Playwright.
"""

import asyncio
import base64
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Route

from infinity_scraper.config import (
    AD_AND_POPUP_SELECTORS,
    AD_TRACKING_DOMAINS,
    DEFAULT_TIMEOUT,
    get_random_user_agent,
)
from infinity_scraper.extractors.content import ExtractionResult, parse_html_content

logger = logging.getLogger(__name__)

STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
Object.defineProperty(navigator, 'plugins', {
    get: () => [{ name: 'Chrome PDF Plugin' }, { name: 'Chrome PDF Viewer' }, { name: 'Native Client' }]
});
if (!window.chrome) {
    window.chrome = { runtime: {}, loadTimes: function() {}, csi: function() {}, app: {} };
}
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
);
"""

AUTO_DISMISS_COOKIE_JS = """
(() => {
    const commonAcceptSelectors = [
        '#onetrust-accept-btn-handler',
        '.cookie-accept-all',
        'button[aria-label="Accept all"]',
        'button[aria-label="Accept All"]',
        'button:has-text("Accept All")',
        'button:has-text("Accept Cookies")',
        'button:has-text("I Agree")',
        'button:has-text("Got It")',
        'button:has-text("Allow all")',
        '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll'
    ];
    for (const sel of commonAcceptSelectors) {
        try {
            const btn = document.querySelector(sel);
            if (btn) {
                btn.click();
                break;
            }
        } catch (e) {}
    }
})();
"""


async def route_ad_blocker(route: Route):
    request = route.request
    req_url = request.url.lower()
    parsed = urlparse(req_url)
    hostname = parsed.hostname or ""

    is_ad = any(domain in hostname for domain in AD_TRACKING_DOMAINS)
    if is_ad:
        await route.abort()
        return

    if request.resource_type in ("beacon", "csp_report"):
        await route.abort()
        return

    await route.continue_()


async def fetch_url_browser(
    url: str,
    wait_for_selector: Optional[str] = None,
    wait_seconds: float = 0.0,
    scroll_depth: int = 0,
    click_selector: Optional[str] = None,
    evaluate_js: Optional[str] = None,
    take_screenshot: bool = False,
    block_ads: bool = True,
    proxy: Optional[str] = None,
    css_selector: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT,
    user_agent: Optional[str] = None,
) -> ExtractionResult:
    ua = user_agent or get_random_user_agent()
    proxy_dict = None
    if proxy:
        proxy_dict = {"server": proxy}

    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--window-size=1920,1080",
            ],
            proxy=proxy_dict,
        )

        context: BrowserContext = await browser.new_context(
            user_agent=ua,
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
            locale="en-US",
            timezone_id="America/New_York",
            bypass_csp=True,
            ignore_https_errors=True,
        )

        await context.add_init_script(STEALTH_JS)
        page: Page = await context.new_page()
        page.set_default_timeout(timeout * 1000)

        if block_ads:
            await page.route("**/*", route_ad_blocker)

        js_eval_result = None
        screenshot_base64 = None

        try:
            try:
                response = await page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
                status_code = response.status if response else 200
            except Exception:
                response = await page.goto(url, wait_until="load", timeout=timeout * 1000)
                status_code = response.status if response else 200

            try:
                await page.evaluate(AUTO_DISMISS_COOKIE_JS)
            except Exception:
                pass

            if click_selector:
                try:
                    await page.wait_for_selector(click_selector, timeout=5000)
                    await page.hover(click_selector)
                    await asyncio.sleep(0.3)
                    await page.click(click_selector)
                    await asyncio.sleep(1.0)
                except Exception as exc:
                    logger.warning(f"Could not click selector '{click_selector}': {exc}")

            if wait_for_selector:
                try:
                    await page.wait_for_selector(wait_for_selector, timeout=timeout * 1000)
                except Exception as exc:
                    logger.warning(f"Wait for selector '{wait_for_selector}' timed out: {exc}")

            if scroll_depth > 0:
                for i in range(scroll_depth):
                    await page.evaluate("window.scrollBy(0, window.innerHeight * 1.5)")
                    await asyncio.sleep(0.8)

            if wait_seconds > 0:
                await asyncio.sleep(min(wait_seconds, 30.0))

            if evaluate_js:
                try:
                    js_eval_result = await page.evaluate(evaluate_js)
                except Exception as exc:
                    js_eval_result = f"JS Evaluation Error: {exc}"

            if take_screenshot:
                screenshot_bytes = await page.screenshot(full_page=True, type="jpeg", quality=75)
                screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")

            content_html = await page.content()
            page_title = await page.title()

            result = parse_html_content(
                html=content_html,
                url=url,
                css_selector=css_selector,
                status_code=status_code,
                strip_ads=block_ads,
            )

            if not result.title and page_title:
                result.title = page_title

            if js_eval_result is not None:
                result.metadata["evaluated_js_result"] = js_eval_result

            if screenshot_base64:
                result.metadata["screenshot_jpeg_base64"] = screenshot_base64[:100] + "... (truncated in meta)"
                result.metadata["has_screenshot"] = True
                result.structured_data["screenshot_base64"] = screenshot_base64

            return result

        except Exception as exc:
            logger.error(f"Browser scrape error for {url}: {exc}")
            return ExtractionResult(
                url=url,
                title="Browser Scraping Error",
                content_markdown=f"**Error rendering {url} with browser:** {str(exc)}",
                content_text=f"Error: {str(exc)}",
                status_code=500,
            )
        finally:
            await context.close()
            await browser.close()
