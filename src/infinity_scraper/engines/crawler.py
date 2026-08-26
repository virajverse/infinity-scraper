"""
Asynchronous Deep BFS Web Crawler for InfinityScrape.
"""

import asyncio
from collections import deque
import logging
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urldefrag, urljoin, urlparse

from infinity_scraper.engines.fast import fetch_url_fast
from infinity_scraper.engines.browser import fetch_url_browser
from infinity_scraper.extractors.content import ExtractionResult

logger = logging.getLogger(__name__)


def normalize_url(url: str) -> str:
    defragged, _ = urldefrag(url)
    parsed = urlparse(defragged)
    path = parsed.path.rstrip("/")
    if not path:
        path = "/"
    return f"{parsed.scheme}://{parsed.netloc}{path}" + (f"?{parsed.query}" if parsed.query else "")


def is_valid_url(url: str, base_domain: str, path_prefix: Optional[str] = None, same_domain_only: bool = True) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False

    ignored_exts = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".css", ".js", ".zip", ".tar", ".gz", ".exe", ".dmg", ".mp4", ".mp3")
    if any(parsed.path.lower().endswith(ext) for ext in ignored_exts):
        return False

    if same_domain_only and parsed.netloc.lower() != base_domain.lower():
        return False

    if path_prefix and not parsed.path.startswith(path_prefix):
        return False

    return True


async def crawl_site(
    start_url: str,
    max_pages: int = 10,
    max_depth: int = 2,
    same_domain_only: bool = True,
    path_prefix: Optional[str] = None,
    use_browser: bool = False,
    concurrency: int = 3,
) -> Dict[str, Any]:
    start_url_norm = normalize_url(start_url)
    base_domain = urlparse(start_url_norm).netloc

    queue: deque = deque([(start_url_norm, 0)])
    visited: Set[str] = {start_url_norm}
    scraped_pages: List[Dict[str, Any]] = []

    semaphore = asyncio.Semaphore(concurrency)

    while queue and len(scraped_pages) < max_pages:
        batch = []
        while queue and len(batch) < concurrency and (len(scraped_pages) + len(batch)) < max_pages:
            batch.append(queue.popleft())

        if not batch:
            break

        async def _scrape_crawl_target(target_url: str, current_depth: int):
            async with semaphore:
                try:
                    if use_browser:
                        res: ExtractionResult = await fetch_url_browser(target_url)
                    else:
                        res: ExtractionResult = await fetch_url_fast(target_url)

                    page_data = {
                        "url": target_url,
                        "depth": current_depth,
                        "title": res.title or target_url,
                        "markdown": res.content_markdown,
                        "status_code": res.status_code,
                        "tables": res.tables,
                        "metadata": res.metadata,
                    }

                    discovered = []
                    if current_depth < max_depth:
                        for link_obj in res.links:
                            link_url = normalize_url(link_obj["href"])
                            if is_valid_url(link_url, base_domain, path_prefix, same_domain_only):
                                discovered.append(link_url)

                    return page_data, discovered
                except Exception as exc:
                    logger.error(f"Error crawling {target_url}: {exc}")
                    return None, []

        tasks = [_scrape_crawl_target(url, depth) for url, depth in batch]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        for page_data, discovered in results:
            if page_data:
                scraped_pages.append(page_data)

            for link_url in discovered:
                if link_url not in visited and len(visited) < (max_pages * 3):
                    visited.add(link_url)
                    curr_d = page_data["depth"] if page_data else 0
                    queue.append((link_url, curr_d + 1))

    doc_lines = [
        f"# Crawl Summary: {start_url}",
        f"- **Base Domain:** {base_domain}",
        f"- **Pages Crawled:** {len(scraped_pages)} / {max_pages} requested",
        f"- **Max Depth Reached:** {max_depth}\n",
        "## Site Hierarchy / Table of Contents\n",
    ]

    for idx, page in enumerate(scraped_pages, 1):
        indent = "  " * page.get("depth", 0)
        doc_lines.append(f"{indent}- [{page['title']}]({page['url']}) (Depth: {page.get('depth', 0)})")

    doc_lines.append("\n---\n")

    for idx, page in enumerate(scraped_pages, 1):
        doc_lines.append(f"## Page {idx}: [{page['title']}]({page['url']})")
        doc_lines.append(f"*Depth: {page.get('depth', 0)} | HTTP Status: {page.get('status_code', 200)}*\n")
        content = page.get("markdown", "").strip()
        if content:
            if len(content) > 12_000:
                content = content[:12_000] + "\n\n... *(Page content truncated for brevity)*"
            doc_lines.append(content)
        else:
            doc_lines.append("*No text content found on this page.*")
        doc_lines.append("\n---\n")

    return {
        "start_url": start_url,
        "total_crawled": len(scraped_pages),
        "pages": scraped_pages,
        "aggregated_markdown": "\n".join(doc_lines),
    }
