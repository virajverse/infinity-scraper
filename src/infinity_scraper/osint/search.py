"""
Search and Autonomous Web Discovery Engine.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

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

import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, unquote

def _search_ddg_html_fallback(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Fallback search using DuckDuckGo HTML Lite when API rate-limits."""
    results = []
    try:
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        with httpx.Client(timeout=8.0, follow_redirects=True) as client:
            resp = client.post(url, data={"q": query}, headers=headers)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for item in soup.select(".result"):
                    title_elem = item.select_one(".result__title a")
                    snippet_elem = item.select_one(".result__snippet")
                    if title_elem and title_elem.get("href"):
                        raw_href = title_elem.get("href")
                        # Extract real URL from /l/?uddg=...
                        real_url = raw_href
                        if "uddg=" in raw_href:
                            try:
                                real_url = unquote(raw_href.split("uddg=")[1].split("&")[0])
                            except Exception:
                                real_url = raw_href
                        results.append({
                            "title": title_elem.get_text(strip=True),
                            "url": real_url,
                            "snippet": snippet_elem.get_text(strip=True) if snippet_elem else "",
                            "source": "DuckDuckGo HTML",
                        })
                        if len(results) >= max_results:
                            break
    except Exception as e:
        logger.warning(f"DDG HTML fallback error: {e}")
    return results


def _search_bing_fallback(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Fallback search using Bing HTML scraper."""
    results = []
    try:
        url = f"https://www.bing.com/search?q={quote_plus(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
        }
        with httpx.Client(timeout=8.0, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for li in soup.select("li.b_algo"):
                    title_elem = li.select_one("h2 a")
                    snippet_elem = li.select_one(".b_caption p, .b_snippet")
                    if title_elem and title_elem.get("href"):
                        results.append({
                            "title": title_elem.get_text(strip=True),
                            "url": title_elem.get("href"),
                            "snippet": snippet_elem.get_text(strip=True) if snippet_elem else "",
                            "source": "Bing",
                        })
                        if len(results) >= max_results:
                            break
    except Exception as e:
        logger.warning(f"Bing search fallback error: {e}")
    return results


def search_web_ddg(
    query: str,
    max_results: int = 5,
    region: str = "us-en",
    safesearch: str = "moderate",
    timelimit: Optional[str] = None,
    search_type: str = "text",
) -> List[Dict[str, Any]]:

    results = []
    # Tier 1: DDGS API
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
            logger.warning(f"DuckDuckGo API search rate-limited / error for '{query}': {exc}. Switching to fallback engines...")

    # Tier 2: DuckDuckGo HTML Lite Fallback
    if not results:
        results = _search_ddg_html_fallback(query=query, max_results=max_results)

    # Tier 3: Bing HTML Fallback
    if not results:
        results = _search_bing_fallback(query=query, max_results=max_results)

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
    results_raw = await asyncio.gather(*tasks, return_exceptions=True)
    scraped_pages = [p for p in results_raw if isinstance(p, dict) and p.get("url")]

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
