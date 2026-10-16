"""
Symbiotic Orchestration Bridge: InfinityScrape <-> SpectraBrowser MCP.
Allows InfinityScrape to automatically shift blocked URLs, CAPTCHA challenges,
and login-walled pages directly to Spectra Browser's live Chrome context.
"""

import os
import sys
import logging
from typing import Any, Dict, Optional
import httpx

from infinity_scraper.extractors.content import ExtractionResult

logger = logging.getLogger(__name__)

SPECTRA_BRIDGE_URL = os.getenv("SPECTRA_BRIDGE_URL", "http://127.0.0.1:8002")


async def shift_to_spectra_browser(
    url: str,
    session_id: str = "default",
    wait_ms: int = 3000,
) -> Optional[ExtractionResult]:
    """
    Shifts an anti-bot blocked URL to Spectra Browser MCP.
    First tries local REST bridge (Port 8002), then direct Python service layer.
    """
    logger.info(f"Symbiotic Shift: Transferring anti-bot blocked URL '{url}' to Spectra Browser...")

    # Method 1: OpenAPI / REST Bridge (Port 8002)
    try:
        async with httpx.AsyncClient(timeout=35.0) as client:
            # 1. Navigate Spectra Browser to the blocked URL
            nav_resp = await client.post(
                f"{SPECTRA_BRIDGE_URL}/browser_navigate",
                json={"url": url, "session_id": session_id},
            )
            if nav_resp.status_code == 200:
                # 2. Wait for page stabilization / challenge clearance
                await client.post(
                    f"{SPECTRA_BRIDGE_URL}/browser_wait",
                    json={"ms": wait_ms, "session_id": session_id},
                )

                # 3. Inspect semantic DOM snapshot
                inspect_resp = await client.post(
                    f"{SPECTRA_BRIDGE_URL}/page_inspect",
                    json={"session_id": session_id},
                )
                if inspect_resp.status_code == 200:
                    data = inspect_resp.json()
                    title = data.get("title") or "Spectra Browser Extracted Page"
                    headings = data.get("headings", [])
                    visible_text = data.get("text_summary") or data.get("markdown") or ""

                    md_lines = [f"# {title}", f"**Source URL (Bypassed via Spectra Browser):** {url}\n"]
                    if headings:
                        md_lines.append("### Key Sections\n" + "\n".join(f"- {h}" for h in headings) + "\n")
                    if visible_text:
                        md_lines.append("### Content\n" + visible_text)

                    full_md = "\n".join(md_lines)
                    return ExtractionResult(
                        url=url,
                        title=title,
                        content_markdown=full_md,
                        content_text=visible_text,
                        status_code=200,
                        metadata={"engine": "spectra_browser_human_bridge", "bypassed_block": True},
                    )
    except Exception as rest_err:
        logger.debug(f"Spectra REST bridge connection skipped: {rest_err}")

    # Method 2: Direct In-Process Python Service Bridge
    try:
        # Dynamically discover spectra-browser-mcp src if nearby
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        spectra_src = os.path.join(parent_dir, "spectra-browser-mcp-main", "src")
        if os.path.exists(spectra_src) and spectra_src not in sys.path:
            sys.path.insert(0, spectra_src)

        from browser_qa.service import BrowserQAService
        service = BrowserQAService()
        nav_res = service.browser_navigate(url=url, session_id=session_id)
        if nav_res.get("success", False) or not nav_res.get("error"):
            import time
            time.sleep(wait_ms / 1000.0)
            inspect_res = service.page_inspect(session_id=session_id)
            title = inspect_res.get("title") or "Spectra Browser Extracted Page"
            visible_text = inspect_res.get("text_summary") or inspect_res.get("markdown") or ""

            md_lines = [f"# {title}", f"**Source URL (Bypassed via Spectra Browser):** {url}\n"]
            if visible_text:
                md_lines.append("### Content\n" + visible_text)

            return ExtractionResult(
                url=url,
                title=title,
                content_markdown="\n".join(md_lines),
                content_text=visible_text,
                status_code=200,
                metadata={"engine": "spectra_browser_direct_service", "bypassed_block": True},
            )
    except Exception as direct_err:
        logger.debug(f"Direct Spectra service execution skipped: {direct_err}")

    return None
