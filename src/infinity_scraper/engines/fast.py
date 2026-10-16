"""
Fast Stealth HTTP Scraping Engine using primp (TLS/JA3/HTTP2 impersonation) & httpx.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx
try:
    import primp
except ImportError:
    primp = None

from infinity_scraper.config import DEFAULT_TIMEOUT, get_stealth_headers
from infinity_scraper.extractors.content import ExtractionResult, parse_html_content

logger = logging.getLogger(__name__)


async def fetch_url_fast(
    url: str,
    proxy: Optional[str] = None,
    custom_headers: Optional[Dict[str, str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
    max_retries: int = 3,
    css_selector: Optional[str] = None,
    follow_redirects: bool = True,
) -> ExtractionResult:
    headers = get_stealth_headers(url, custom_headers)
    last_error = None

    if primp:
        for attempt in range(1, max_retries + 1):
            try:
                client = primp.AsyncClient(
                    impersonate="random",
                    proxy=proxy,
                    follow_redirects=follow_redirects,
                    timeout=timeout,
                    verify=False,
                )
                response = await client.get(url, headers=headers)
                status_code = response.status_code

                if status_code in (200, 201, 202, 203, 206):
                    html = response.text
                    return parse_html_content(
                        html=html,
                        url=url,
                        css_selector=css_selector,
                        status_code=status_code,
                    )
                elif status_code in (403, 429, 503) and attempt < max_retries:
                    await asyncio.sleep(attempt * 1.5)
                    continue
                else:
                    html = response.text
                    return parse_html_content(
                        html=html,
                        url=url,
                        css_selector=css_selector,
                        status_code=status_code,
                    )
            except Exception as exc:
                last_error = exc
                if attempt < max_retries:
                    await asyncio.sleep(attempt * 1.0)
                    continue


    try:
        async with httpx.AsyncClient(
            headers=headers,
            proxy=proxy,
            follow_redirects=follow_redirects,
            timeout=timeout,
            verify=False,
        ) as client:
            resp = await client.get(url)
            return parse_html_content(
                html=resp.text,
                url=url,
                css_selector=css_selector,
                status_code=resp.status_code,
            )
    except Exception as exc:
        logger.error(f"Fast scrape failed for {url}: {exc}")
        return ExtractionResult(
            url=url,
            title="Fetch Error",
            content_markdown=f"**Error scraping {url}:** {str(exc or last_error)}",
            content_text=f"Error: {str(exc or last_error)}",
            status_code=500,
        )
