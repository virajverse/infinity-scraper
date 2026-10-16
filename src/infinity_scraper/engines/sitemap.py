"""
High-Speed XML Sitemap & Document Graph Engine for InfinityScrape.
Supports standard sitemaps, sitemap indexes, .xml.gz gzip decompression,
and automatic robots.txt sitemap discovery.
"""

import gzip
import io
import re
import urllib.parse
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET
import httpx


def parse_sitemap_xml_data(content_bytes: bytes, max_urls: int = 500) -> Dict[str, Any]:
    """
    Parses raw XML bytes (automatically handling gzip compression and XML namespaces).
    Detects whether the document is a standard URLSet or a SitemapIndex.
    """
    # Auto-decompress if gzip magic header (\x1f\x8b)
    if content_bytes.startswith(b"\x1f\x8b"):
        try:
            content_bytes = gzip.decompress(content_bytes)
        except Exception as e:
            return {"error": f"Failed to decompress gzip sitemap: {str(e)}", "urls": [], "is_index": False}

    try:
        root = ET.fromstring(content_bytes)
    except Exception as e:
        return {"error": f"XML parse error: {str(e)}", "urls": [], "is_index": False}

    # Strip XML namespaces for uniform tag matching
    tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

    urls = []
    nested_sitemaps = []

    if tag == "sitemapindex":
        for elem in root:
            loc_node = None
            lastmod_node = None
            for child in elem:
                ctag = child.tag.split("}")[-1]
                if ctag == "loc":
                    loc_node = child.text.strip() if child.text else ""
                elif ctag == "lastmod":
                    lastmod_node = child.text.strip() if child.text else ""

            if loc_node:
                nested_sitemaps.append({
                    "sitemap_url": loc_node,
                    "lastmod": lastmod_node
                })

        return {
            "status": "success",
            "is_index": True,
            "total_nested_sitemaps": len(nested_sitemaps),
            "nested_sitemaps": nested_sitemaps[:max_urls],
            "urls": []
        }

    elif tag == "urlset":
        for elem in root:
            url_item: Dict[str, Any] = {}
            for child in elem:
                ctag = child.tag.split("}")[-1]
                if child.text:
                    url_item[ctag] = child.text.strip()

            if "loc" in url_item:
                urls.append(url_item)
                if len(urls) >= max_urls:
                    break

        return {
            "status": "success",
            "is_index": False,
            "total_urls": len(urls),
            "urls": urls
        }

    return {
        "status": "unknown_xml_structure",
        "tag": tag,
        "is_index": False,
        "urls": []
    }


async def fetch_and_parse_sitemap(sitemap_url: str, max_urls: int = 500, crawl_nested: bool = True) -> Dict[str, Any]:
    """
    Asynchronously streams and parses an online XML sitemap or sitemap index.
    If a SitemapIndex is encountered and crawl_nested is True, crawls top child sitemaps.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/xml,text/xml,application/xhtml+xml,text/html;q=0.9,*/*;q=0.8"
    }

    try:
        async with httpx.AsyncClient(timeout=25.0, follow_redirects=True, headers=headers) as client:
            resp = await client.get(sitemap_url)
            if resp.status_code != 200:
                return {
                    "status": "error",
                    "http_status": resp.status_code,
                    "error": f"HTTP {resp.status_code} while requesting sitemap",
                    "url": sitemap_url
                }

            result = parse_sitemap_xml_data(resp.content, max_urls=max_urls)
            result["url"] = sitemap_url

            # If it's a sitemap index and user wants URLs, follow first 3 child sitemaps
            if result.get("is_index") and crawl_nested and result.get("nested_sitemaps"):
                aggregated_urls = []
                for sub in result["nested_sitemaps"][:3]:
                    sub_url = sub["sitemap_url"]
                    try:
                        sub_resp = await client.get(sub_url)
                        if sub_resp.status_code == 200:
                            sub_res = parse_sitemap_xml_data(sub_resp.content, max_urls=max_urls - len(aggregated_urls))
                            for u in sub_res.get("urls", []):
                                u["parent_sitemap"] = sub_url
                                aggregated_urls.append(u)
                                if len(aggregated_urls) >= max_urls:
                                    break
                    except Exception:
                        continue
                    if len(aggregated_urls) >= max_urls:
                        break

                result["aggregated_child_urls_count"] = len(aggregated_urls)
                result["aggregated_urls"] = aggregated_urls

            return result

    except Exception as e:
        return {
            "status": "error",
            "url": sitemap_url,
            "error": f"Sitemap fetch failed: {str(e)}"
        }


async def discover_website_sitemaps(base_url: str) -> Dict[str, Any]:
    """
    Autonomously discovers all active XML sitemaps for a website by reading robots.txt
    and testing standard location heuristics (/sitemap.xml, /sitemap_index.xml, etc.).
    """
    parsed = urllib.parse.urlparse(base_url)
    root_domain = f"{parsed.scheme or 'https'}://{parsed.netloc or parsed.path}"
    discovered_sitemaps = set()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=headers) as client:
        # 1. Probe robots.txt for Sitemap: directives
        try:
            robots_url = urllib.parse.urljoin(root_domain, "/robots.txt")
            robots_resp = await client.get(robots_url)
            if robots_resp.status_code == 200:
                for line in robots_resp.text.splitlines():
                    if line.strip().lower().startswith("sitemap:"):
                        smap_candidate = line.split(":", 1)[1].strip()
                        if smap_candidate:
                            discovered_sitemaps.add(smap_candidate)
        except Exception:
            pass

        # 2. Probe common heuristic sitemap endpoints
        probes = [
            "/sitemap.xml",
            "/sitemap_index.xml",
            "/sitemap/sitemap.xml",
            "/wp-sitemap.xml",
            "/sitemap-index.xml"
        ]

        for p in probes:
            probe_url = urllib.parse.urljoin(root_domain, p)
            if probe_url in discovered_sitemaps:
                continue
            try:
                head_resp = await client.head(probe_url)
                if head_resp.status_code == 200:
                    discovered_sitemaps.add(probe_url)
            except Exception:
                pass

    return {
        "status": "success",
        "domain": root_domain,
        "total_discovered": len(discovered_sitemaps),
        "sitemaps": sorted(list(discovered_sitemaps))
    }
