"""
Wayback Machine / Internet Archive Time-Travel and Historical Web Scraper for InfinityScrape.
Retrieves archived snapshots of deleted or historical webpages.
"""

import logging
from typing import Any, Dict, List, Optional
import httpx

from infinity_scraper.extractors.content import parse_html_content

logger = logging.getLogger(__name__)


async def fetch_wayback_snapshots(
    url: str,
    limit: int = 10,
    from_year: Optional[str] = None,
    to_year: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Query the Internet Archive CDX API for historical snapshot timestamps.
    """
    clean_url = url.strip()
    cdx_api = "http://web.archive.org/cdx/search/cdx"
    params = {
        "url": clean_url,
        "output": "json",
        "fl": "timestamp,original,mimetype,statuscode,digest",
        "filter": "statuscode:200",
        "collapse": "timestamp:8",  # 1 per day
        "limit": str(limit),
    }
    if from_year:
        params["from"] = from_year.strip()
    if to_year:
        params["to"] = to_year.strip()

    try:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            resp = await client.get(cdx_api, params=params)
            if resp.status_code == 200:
                data = resp.json()
                if len(data) > 1:
                    headers = data[0]
                    rows = data[1:]
                    snapshots = []
                    for row in rows:
                        item = dict(zip(headers, row))
                        ts = item.get("timestamp", "")
                        archived_url = f"https://web.archive.org/web/{ts}/{item.get('original')}"
                        formatted_date = f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]} {ts[8:10]}:{ts[10:12]}:{ts[12:14]}" if len(ts) >= 14 else ts
                        snapshots.append({
                            "timestamp": ts,
                            "formatted_date": formatted_date,
                            "original_url": item.get("original"),
                            "archived_url": archived_url,
                            "mimetype": item.get("mimetype"),
                            "statuscode": item.get("statuscode"),
                        })
                    return snapshots
    except Exception as exc:
        logger.error(f"Wayback CDX lookup failed for {url}: {exc}")

    return []


async def scrape_wayback_snapshot(
    url: str,
    timestamp: str = "",
) -> Dict[str, Any]:
    """
    Fetch and scrape a historical snapshot of a webpage from the Internet Archive into clean Markdown.
    """
    clean_url = url.strip()
    if not timestamp:
        snapshots = await fetch_wayback_snapshots(clean_url, limit=1)
        if not snapshots:
            return {
                "url": clean_url,
                "error": "No historical snapshots found in Internet Archive.",
                "markdown": f"No archived snapshots found for `{clean_url}`.",
            }
        timestamp = snapshots[0]["timestamp"]
        archived_url = snapshots[0]["archived_url"]
    else:
        archived_url = f"https://web.archive.org/web/{timestamp}/{clean_url}"

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            resp = await client.get(archived_url)
            if resp.status_code == 200:
                res = parse_html_content(resp.text, url=archived_url)
                formatted_date = f"{timestamp[0:4]}-{timestamp[4:6]}-{timestamp[6:8]}" if len(timestamp) >= 8 else timestamp

                doc_parts = [
                    f"# 🏛️ Historical Wayback Snapshot: {res.title or clean_url}",
                    f"- **Original Target URL:** {clean_url}",
                    f"- **Snapshot Timestamp:** `{timestamp}` ({formatted_date})",
                    f"- **Internet Archive Link:** [{archived_url}]({archived_url})\n",
                    "## Archived Page Content\n",
                    res.content_markdown,
                ]

                return {
                    "url": clean_url,
                    "timestamp": timestamp,
                    "archived_url": archived_url,
                    "title": res.title,
                    "markdown": "\n".join(doc_parts),
                }
            else:
                return {
                    "url": clean_url,
                    "error": f"Failed to fetch snapshot (HTTP {resp.status_code})",
                    "markdown": f"Failed to fetch archived snapshot from `{archived_url}` (HTTP {resp.status_code}).",
                }
    except Exception as exc:
        logger.error(f"Failed to scrape Wayback snapshot for {url}: {exc}")
        return {
            "url": clean_url,
            "error": str(exc),
            "markdown": f"Error retrieving historical snapshot: {str(exc)}",
        }
