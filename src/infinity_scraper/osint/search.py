"""
Search and Autonomous Web Discovery Engine.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

from infinity_scraper.engines.fast import fetch_url_fast
from infinity_scraper.engines.browser import fetch_url_browser
from infinity_scraper.extractors.content import ExtractionResult

logger = logging.getLogger(__name__)


def search_web_ddg(
    query: str,
    max_results: int = 5,
    region: str = "wt-wt",
    safesearch: str = "moderate",
    timelimit: Optional[str] = None,
    search_type: str = "text",
) -> List[Dict[str, Any]]:
    results = []
    if DDGS:
        try:
            with DDGS() as ddgs:
                if search_type == "news":
                    raw_results = ddgs.news(
                        query,
                        region=region,
                        safesearch=safesearch,
                        timelimit=timelimit,
                        max_results=max_results,
                    )
                else:
                    raw_results = ddgs.text(
                        query,
                        region=region,
                        safesearch=safesearch,
                        timelimit=timelimit,
                        max_results=max_results,
                    )

                for item in (raw_results or []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("href") or item.get("url", ""),
                        "snippet": item.get("body") or item.get("description", ""),
                        "date": item.get("date", ""),
                        "source": item.get("source", ""),
                    })
        except Exception as exc:
            logger.error(f"DuckDuckGo search error for '{query}': {exc}")

    return results


async def search_and_scrape_all(
    query: str,
    max_results: int = 5,
    use_browser: bool = False,
    concurrency: int = 4,
) -> Dict[str, Any]:
    search_results = search_web_ddg(query=query, max_results=max_results)

    if not search_results:
        return {
            "query": query,
            "results_count": 0,
            "summary_markdown": f"No search results found for query: '{query}'.",
            "pages": [],
        }

    semaphore = asyncio.Semaphore(concurrency)

    async def _scrape_one(item: Dict[str, Any]) -> Dict[str, Any]:
        url = item["url"]
        async with semaphore:
            if use_browser:
                res: ExtractionResult = await fetch_url_browser(url=url)
            else:
                res: ExtractionResult = await fetch_url_fast(url=url)

            return {
                "title": res.title or item.get("title", "Untitled"),
                "url": url,
                "snippet": item.get("snippet", ""),
                "markdown": res.content_markdown,
                "status_code": res.status_code,
                "metadata": res.metadata,
                "tables": res.tables,
            }

    tasks = [_scrape_one(item) for item in search_results if item.get("url")]
    scraped_pages = await asyncio.gather(*tasks, return_exceptions=False)

    doc_parts = [
        f"# Live Web Research: {query}",
        f"**Total Sources Scraped:** {len(scraped_pages)}\n",
        "## Table of Contents",
    ]

    for idx, page in enumerate(scraped_pages, 1):
        doc_parts.append(f"{idx}. [{page['title']}]({page['url']})")

    doc_parts.append("\n---\n")

    for idx, page in enumerate(scraped_pages, 1):
        doc_parts.append(f"## Source {idx}: [{page['title']}]({page['url']})")
        if page.get("snippet"):
            doc_parts.append(f"> **Search Snippet:** {page['snippet']}\n")

        content = page.get("markdown", "").strip()
        if content:
            if len(content) > 15_000:
                content = content[:15_000] + "\n\n... *(Source content truncated)*"
            doc_parts.append(content)
        else:
            doc_parts.append("*No text content could be extracted from this URL.*")

        doc_parts.append("\n---\n")

    return {
        "query": query,
        "results_count": len(scraped_pages),
        "summary_markdown": "\n".join(doc_parts),
        "pages": scraped_pages,
    }


def osint_search_dork(
    query: str,
    site: Optional[str] = None,
    filetype: Optional[str] = None,
    in_title: Optional[str] = None,
    exclude_terms: Optional[List[str]] = None,
    time_range: Optional[str] = None,
    max_results: int = 5,
) -> List[Dict[str, Any]]:
    dork_parts = []
    if site:
        dork_parts.append(f"site:{site.strip()}")
    if filetype:
        dork_parts.append(f"filetype:{filetype.strip()}")
    if in_title:
        dork_parts.append(f'intitle:"{in_title.strip()}"')
    if query:
        dork_parts.append(query.strip())
    if exclude_terms:
        for ex in exclude_terms:
            if ex.strip():
                dork_parts.append(f'-"{ex.strip()}"')

    full_query = " ".join(dork_parts)
    return search_web_ddg(query=full_query, max_results=max_results, timelimit=time_range)
