"""
Dynamic Headless Browser Scraping Engine powered by Playwright with Singleton Pooling & Anti-Detection.
"""

import asyncio
import base64
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Route, Playwright

from infinity_scraper.config import (
    AD_AND_POPUP_SELECTORS,
    AD_TRACKING_DOMAINS,
    DEFAULT_TIMEOUT,
    get_random_user_agent,
    get_rotating_proxy,
)
from infinity_scraper.extractors.content import ExtractionResult, parse_html_content

logger = logging.getLogger(__name__)

STEALTH_JS = """
(() => {
    // 1. Wipe navigator.webdriver cleanly
    try {
        delete Object.getPrototypeOf(navigator).webdriver;
    } catch (e) {}
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined, configurable: true });

    // 2. Realistic Languages & Platform
    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'], configurable: true });
    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8, configurable: true });
    Object.defineProperty(navigator, 'deviceMemory', { get: () => 8, configurable: true });

    // 3. Realistic Plugins & MimeTypes
    const mockPlugins = [
        { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
        { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
        { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' }
    ];
    Object.defineProperty(navigator, 'plugins', { get: () => mockPlugins, configurable: true });

    // 4. Authentic window.chrome object
    if (!window.chrome) {
        window.chrome = {
            app: { isInstalled: false, InstallState: { DISABLED: 'DISABLED', INSTALLED: 'INSTALLED', NOT_INSTALLED: 'NOT_INSTALLED' }, RunningState: { CANNOT_RUN: 'CANNOT_RUN', READY_TO_RUN: 'READY_TO_RUN', RUNNING: 'RUNNING' } },
            runtime: { OnInstalledReason: {}, OnRestartRequiredReason: {}, PlatformArch: { X86_64: 'x86-64' }, PlatformNaclArch: {}, PlatformOs: { WIN: 'win' }, RequestUpdateCheckStatus: {} },
            loadTimes: function() {},
            csi: function() {}
        };
    }

    // 5. Spoof WebGL Vendor & Renderer (NVIDIA RTX 3080)
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) return 'Google Inc. (NVIDIA)';
        if (parameter === 37446) return 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)';
        return getParameter.apply(this, arguments);
    };
    if (typeof WebGL2RenderingContext !== 'undefined') {
        const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
        WebGL2RenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'Google Inc. (NVIDIA)';
            if (parameter === 37446) return 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)';
            return getParameter2.apply(this, arguments);
        };
    }

    // 6. Permissions API Spoofing
    if (window.navigator.permissions) {
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission, onchange: null }) :
                originalQuery(parameters)
        );
    }
})();
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

AUTO_SOLVE_TURNSTILE_JS = """
(() => {
    try {
        const iframes = Array.from(document.querySelectorAll('iframe'));
        for (const f of iframes) {
            const src = (f.getAttribute('src') || '').toLowerCase();
            const title = (f.getAttribute('title') || '').toLowerCase();
            if (src.includes('challenges.cloudflare.com') || title.includes('cloudflare') || title.includes('turnstile') || title.includes('challenge')) {
                try {
                    const rect = f.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        const evt = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window,
                            clientX: rect.left + rect.width / 2,
                            clientY: rect.top + rect.height / 2
                        });
                        f.dispatchEvent(evt);
                    }
                } catch(e) {}
            }
        }
    } catch (e) {}
})();
"""


class BrowserPool:
    """
    High-performance Singleton Browser Pool.
    Maintains a shared Chromium process while leasing ephemeral isolated contexts.
    """
    _instance: Optional["BrowserPool"] = None
    _lock = asyncio.Lock()

    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._active_contexts: int = 0

    @classmethod
    async def get_instance(cls) -> "BrowserPool":
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    async def get_browser(self, proxy: Optional[str] = None) -> Browser:
        async with self._lock:
            # If browser crashed or not started, start it
            if self._browser is None or not self._browser.is_connected():
                if self._playwright is None:
                    self._playwright = await async_playwright().start()
                
                proxy_dict = {"server": proxy} if proxy else None
                launch_args = [
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--window-size=1920,1080",
                ]

                # Priority 1: Default Playwright Chromium
                try:
                    self._browser = await self._playwright.chromium.launch(
                        headless=True,
                        args=launch_args,
                        proxy=proxy_dict,
                    )
                    return self._browser
                except Exception as e_chromium:
                    logger.info(f"Playwright Chromium binary not found or failed ({e_chromium}). Falling back to system browsers...")

                # Priority 2: System Microsoft Edge (Standard on Windows)
                try:
                    self._browser = await self._playwright.chromium.launch(
                        channel="msedge",
                        headless=True,
                        args=launch_args,
                        proxy=proxy_dict,
                    )
                    logger.info("Successfully initialized dynamic rendering using system Microsoft Edge.")
                    return self._browser
                except Exception as e_edge:
                    logger.debug(f"System Edge channel launch failed: {e_edge}")

                # Priority 3: System Google Chrome
                try:
                    self._browser = await self._playwright.chromium.launch(
                        channel="chrome",
                        headless=True,
                        args=launch_args,
                        proxy=proxy_dict,
                    )
                    logger.info("Successfully initialized dynamic rendering using system Google Chrome.")
                    return self._browser
                except Exception as e_chrome:
                    logger.debug(f"System Chrome channel launch failed: {e_chrome}")

                raise RuntimeError("No suitable browser executable found (Chromium, Edge, or Chrome). Install Playwright browser or Chrome/Edge.")
            return self._browser

    async def close_all(self):
        async with self._lock:
            if self._browser:
                try:
                    await self._browser.close()
                except Exception:
                    pass
                self._browser = None
            if self._playwright:
                try:
                    await self._playwright.stop()
                except Exception:
                    pass
                self._playwright = None


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
    cookies: Optional[List[Dict[str, Any]]] = None,
) -> ExtractionResult:
    ua = user_agent or get_random_user_agent()
    active_proxy = get_rotating_proxy(proxy)

    try:
        pool = await BrowserPool.get_instance()
        browser = await pool.get_browser(active_proxy)
    except Exception as exc:
        logger.warning(f"Browser engine unavailable for {url} ({exc}). Falling back to fast stealth HTTP engine...")
        from infinity_scraper.engines.fast import fetch_url_fast
        return await fetch_url_fast(url=url, proxy=proxy, css_selector=css_selector, timeout=timeout)

    # Ephemeral isolated context (instant ~50ms creation)
    context: BrowserContext = await browser.new_context(
        user_agent=ua,
        viewport={"width": 1920, "height": 1080},
        device_scale_factor=1,
        locale="en-US",
        timezone_id="America/New_York",
        bypass_csp=True,
        ignore_https_errors=True,
    )

    if cookies:
        try:
            await context.add_cookies(cookies)
        except Exception as e:
            logger.warning(f"Could not inject cookies: {e}")

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

        # Auto-dismiss Cookie banners
        try:
            await page.evaluate(AUTO_DISMISS_COOKIE_JS)
        except Exception:
            pass

        # Auto-detect and solve Cloudflare Turnstile iframes
        try:
            await page.evaluate(AUTO_SOLVE_TURNSTILE_JS)
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
            for _ in range(scroll_depth):
                await page.evaluate("window.scrollBy(0, window.innerHeight * 1.5)")
                await asyncio.sleep(0.5)

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
        # Context is closed cleanly in ~5ms, browser process stays warm
        try:
            await context.close()
        except Exception:
            pass

