"""
InfinityScrape FastMCP Server.
Registers and exposes all 16 web scraping, dynamic rendering, YouTube transcription, and OSINT tools.
Author: VirajVerse (https://github.com/virajverse)
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

from infinity_scraper.cache import cache
from infinity_scraper.config import DEFAULT_MAX_CHARS
from infinity_scraper.engines.browser import fetch_url_browser
from infinity_scraper.engines.crawler import crawl_site
from infinity_scraper.engines.fast import fetch_url_fast
from infinity_scraper.extractors.chunker import chunk_content_for_rag
from infinity_scraper.extractors.content import ExtractionResult
from infinity_scraper.extractors.image_exif import extract_image_exif_from_url
from infinity_scraper.extractors.pdf import extract_pdf_from_url
from infinity_scraper.extractors.social import extract_reddit_thread, extract_rss_feed
from infinity_scraper.extractors.youtube import fetch_youtube_transcript
from infinity_scraper.osint.geoint import fetch_geoint_location, search_location_entity_hierarchy
from infinity_scraper.osint.network import (
    check_username_osint,
    clean_hostname,
    detect_website_tech,
    fetch_ip_intel,
    fetch_rdap_whois,
    get_ssl_cert_info,
)
from infinity_scraper.osint.recon import deep_public_entity_recon
from infinity_scraper.osint.search import osint_search_dork, search_and_scrape_all, search_web_ddg
from infinity_scraper.osint.subdomains import audit_dns_records, enumerate_subdomains
from infinity_scraper.osint.wayback import fetch_wayback_snapshots, scrape_wayback_snapshot

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("infinity_scraper")

mcp = FastMCP(
    "InfinityScrape",
    instructions="World-Class Web Scraping, Dynamic SPA Rendering, YouTube Transcripts, and Deep OSINT/GEOINT Public Intelligence MCP Server by VirajVerse",
)


@mcp.tool()
async def scrape_url(
    url: str,
    engine: str = "auto",
    css_selector: str = "",
    max_chars: int = DEFAULT_MAX_CHARS,
    include_tables: bool = True,
    include_links: bool = False,
    include_images: bool = False,
    strip_ads: bool = True,
    use_cache: bool = True,
    force_refresh: bool = False,
    wait_seconds: float = 0.0,
) -> str:
    """
    Scrape any website and convert its content into clean, ad-free Markdown.
    """
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    cache_extra = f"{engine}:{css_selector}:{strip_ads}"
    if use_cache and not force_refresh:
        cached_result = cache.get(url, cache_extra)
        if cached_result:
            return cached_result.get("formatted_output", "")

    sel = css_selector.strip() if css_selector else None

    if "youtube.com" in url.lower() or "youtu.be" in url.lower():
        yt_res = await fetch_youtube_transcript(url=url)
        return yt_res.get("markdown", "Failed to retrieve YouTube transcript.")

    if url.lower().endswith(".pdf"):
        pdf_res = await extract_pdf_from_url(url=url)
        return pdf_res.get("markdown", "Failed to extract PDF.")

    if engine == "fast":
        res: ExtractionResult = await fetch_url_fast(url=url, css_selector=sel)
    elif engine == "browser":
        res = await fetch_url_browser(url=url, css_selector=sel, wait_seconds=wait_seconds, block_ads=strip_ads)
    else:
        res = await fetch_url_fast(url=url, css_selector=sel)
        has_thin_content = len(res.content_text.strip()) < 180 and len(res.content_markdown.strip()) < 180
        indicates_js = any(phrase in res.raw_html.lower() for phrase in [
            "enable javascript to run this app",
            "you need to enable javascript",
            "please enable javascript",
            "javascript is disabled",
            "checking your browser",
            "just a moment...",
        ])
        if (has_thin_content or indicates_js) and res.status_code in (200, 403, 503):
            logger.info(f"Auto-engine: upgrading to Playwright browser for {url}")
            res = await fetch_url_browser(url=url, css_selector=sel, wait_seconds=max(wait_seconds, 1.5), block_ads=strip_ads)

    output = res.format_output(
        include_metadata=True,
        include_links=include_links,
        include_images=include_images,
        include_tables=include_tables,
        max_chars=max_chars,
    )

    if use_cache and res.status_code == 200:
        cache.set(url, {"formatted_output": output}, extra=cache_extra, ttl_seconds=3600)

    return output


@mcp.tool()
async def search_web(
    query: str,
    max_results: int = 5,
    search_type: str = "text",
) -> str:
    """
    Perform a live web search to find relevant URLs, articles, and snippets for any topic.
    """
    results = search_web_ddg(query=query, max_results=max_results, search_type=search_type)
    if not results:
        return f"No search results found for query: '{query}'."

    parts = [f"# Search Results: {query}\n"]
    for idx, r in enumerate(results, 1):
        parts.append(f"### {idx}. [{r['title']}]({r['url']})")
        if r.get("date"):
            parts.append(f"*Date: {r['date']}*")
        if r.get("snippet"):
            parts.append(f"> {r['snippet']}\n")
    return "\n".join(parts)


@mcp.tool()
async def search_and_scrape(
    query: str,
    max_results: int = 4,
    use_browser: bool = False,
) -> str:
    """
    Autonomous research tool: searches the web and automatically scrapes the top results into a synthesized Markdown report.
    """
    data = await search_and_scrape_all(query=query, max_results=max_results, use_browser=use_browser)
    return data.get("summary_markdown", "No content retrieved.")


@mcp.tool()
async def scrape_dynamic(
    url: str,
    wait_for_selector: str = "",
    wait_seconds: float = 2.0,
    scroll_depth: int = 2,
    click_selector: str = "",
    evaluate_js: str = "",
    css_selector: str = "",
    block_ads: bool = True,
    take_screenshot: bool = False,
) -> str:
    """
    Scrape dynamic Single Page Applications (React, Vue, Next.js) with Playwright headless browser.
    """
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    res = await fetch_url_browser(
        url=url,
        wait_for_selector=wait_for_selector or None,
        wait_seconds=wait_seconds,
        scroll_depth=scroll_depth,
        click_selector=click_selector or None,
        evaluate_js=evaluate_js or None,
        css_selector=css_selector or None,
        block_ads=block_ads,
        take_screenshot=take_screenshot,
    )

    output = res.format_output(include_metadata=True, include_tables=True, include_links=True)
    if "evaluated_js_result" in res.metadata:
        output += f"\n\n### Evaluated JavaScript Output\n```json\n{json.dumps(res.metadata['evaluated_js_result'], indent=2, default=str)}\n```"
    return output


@mcp.tool()
async def extract_schema(
    url: str,
    schema: Dict[str, str],
    use_browser: bool = False,
) -> str:
    """
    Extract specific structured fields from a webpage using a key-to-CSS-selector dictionary map.
    """
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    if use_browser:
        res = await fetch_url_browser(url=url)
    else:
        res = await fetch_url_fast(url=url)

    soup = BeautifulSoup(res.raw_html, "html.parser")
    extracted_data: Dict[str, Any] = {"_url": url, "_status": res.status_code}

    # Extract any embedded JSON-LD schema on page
    json_ld_data = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            parsed = json.loads(script.string)
            if isinstance(parsed, list):
                json_ld_data.extend(parsed)
            elif isinstance(parsed, dict):
                json_ld_data.append(parsed)
        except Exception:
            pass

    for field_name, selector in schema.items():
        matches = []
        try:
            matches = soup.select(selector)
        except Exception:
            pass

        if matches:
            if len(matches) == 1:
                extracted_data[field_name] = matches[0].get_text(strip=True)
            else:
                extracted_data[field_name] = [m.get_text(strip=True) for m in matches]
        else:
            # Semantic Fallback from Meta & JSON-LD
            val = None
            f_lower = field_name.lower()
            
            # 1. Meta tag check
            meta_match = soup.find("meta", attrs={"name": f_lower}) or soup.find("meta", attrs={"property": f"og:{f_lower}"}) or soup.find("meta", attrs={"property": f_lower})
            if meta_match and meta_match.get("content"):
                val = meta_match.get("content").strip()

            # 2. JSON-LD search
            if not val and json_ld_data:
                for j in json_ld_data:
                    for k, v in j.items():
                        if k.lower() == f_lower:
                            val = v
                            break
                    if val:
                        break

            extracted_data[field_name] = val

    return json.dumps(extracted_data, indent=2, ensure_ascii=False)



@mcp.tool()
async def deep_crawl(
    start_url: str,
    max_pages: int = 5,
    max_depth: int = 2,
    same_domain_only: bool = True,
    path_prefix: str = "",
    use_browser: bool = False,
) -> str:
    """
    Recursively crawl a website or documentation tree up to max_depth and aggregate into unified documentation.
    """
    start_url = start_url.strip()
    if not start_url.startswith(("http://", "https://")):
        start_url = "https://" + start_url

    crawl_res = await crawl_site(
        start_url=start_url,
        max_pages=min(max_pages, 50),
        max_depth=min(max_depth, 5),
        same_domain_only=same_domain_only,
        path_prefix=path_prefix or None,
        use_browser=use_browser,
    )
    return crawl_res.get("aggregated_markdown", "Crawl completed with no output.")


@mcp.tool()
async def extract_structured(
    url: str,
    css_selector: str = "",
    extract_tables: bool = True,
    extract_metadata: bool = True,
    use_browser: bool = False,
) -> str:
    """
    Extract structured data (JSON-LD schema, HTML tables, metadata, and CSS-targeted nodes) as JSON.
    """
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    sel = css_selector.strip() if css_selector else None
    if use_browser:
        res = await fetch_url_browser(url=url, css_selector=sel)
    else:
        res = await fetch_url_fast(url=url, css_selector=sel)

    data = {
        "url": res.url,
        "title": res.title,
        "status_code": res.status_code,
    }
    if extract_metadata:
        data["metadata"] = res.metadata
    if extract_tables:
        data["tables"] = [tbl.get("rows") for tbl in res.tables]
    data["links_count"] = len(res.links)
    data["images_count"] = len(res.images)
    data["text_sample"] = res.content_text[:1000]

    return json.dumps(data, indent=2, ensure_ascii=False)


@mcp.tool()
async def scrape_batch(
    urls: List[str],
    use_browser: bool = False,
    concurrency: int = 4,
) -> str:
    """
    Concurrently scrape multiple URLs in parallel and return their combined Markdown.
    """
    if not urls:
        return "No URLs provided to scrape."

    semaphore = asyncio.Semaphore(concurrency)

    async def _scrape(u: str) -> str:
        u = u.strip()
        if not u.startswith(("http://", "https://")):
            u = "https://" + u
        async with semaphore:
            try:
                if use_browser:
                    r = await fetch_url_browser(url=u)
                else:
                    r = await fetch_url_fast(url=u)
                return r.format_output(include_metadata=False, max_chars=10_000)
            except Exception as e:
                return f"# Error scraping {u}\n{e}"

    tasks = [_scrape(u) for u in urls]
    results = await asyncio.gather(*tasks)
    return "\n\n---\n\n".join(results)


@mcp.tool()
async def extract_pdf(
    url: str,
    max_pages: int = 20,
) -> str:
    """
    Download and extract full text and metadata from an online PDF document.
    """
    res = await extract_pdf_from_url(url=url, max_pages=max_pages)
    return res.get("markdown", "Failed to extract PDF.")


@mcp.tool()
async def get_youtube_transcript(
    url: str,
    with_timestamps: bool = True,
) -> str:
    """
    Extract full text transcript and timestamps from any YouTube video URL in milliseconds (Zero GPU).
    """
    res = await fetch_youtube_transcript(url=url, with_timestamps=with_timestamps)
    return res.get("markdown", "Failed to retrieve transcript.")


@mcp.tool()
async def osint_deep_public_recon(
    name: str,
    location: str = "",
    street_or_locality: str = "",
    postal_code: str = "",
    organization: str = "",
    role_or_keywords: str = "",
    exclude_terms: Optional[List[str]] = None,
    must_include_terms: Optional[List[str]] = None,
    time_range: str = "",
    scrape_top_profiles: bool = True,
    max_sources_to_scrape: int = 5,
) -> str:
    """
    Ultra-Precision Public Intelligence Dossier Tool:
    Scrapes and correlates open web data across 25+ platforms with negative exclusions,
    PIN/Street drill-down, and multi-signal Confidence Scoring (0% - 100%).
    """
    data = await deep_public_entity_recon(
        name=name,
        location=location,
        street_or_locality=street_or_locality,
        postal_code=postal_code,
        organization=organization,
        role_or_keywords=role_or_keywords,
        exclude_terms=exclude_terms or None,
        must_include_terms=must_include_terms or None,
        time_range=time_range or None,
        scrape_top_profiles=scrape_top_profiles,
        max_sources_to_scrape=max_sources_to_scrape,
    )
    return data.get("dossier_markdown", "No public open data records found.")


@mcp.tool()
async def osint_geoint_lookup(
    location_query: str,
    country_code: str = "",
    limit: int = 3,
) -> str:
    """
    GEOINT Location Tool: Resolve any address, landmark, or street into a complete global administrative hierarchy.
    """
    locations = await fetch_geoint_location(location_query=location_query, country_code=country_code or None, limit=limit)
    if not locations:
        return f"No geospatial location records found for `{location_query}`."

    parts = [f"# 🌍 GEOINT Location Breakdown: {location_query}\n"]
    for idx, loc in enumerate(locations, 1):
        h = loc.get("hierarchy", {})
        parts.append(f"### Result {idx}: {loc.get('display_name')}")
        parts.append(f"- **Country:** {h.get('country')} ({h.get('country_code')})")
        parts.append(f"- **State:** {h.get('state')}")
        if h.get("state_district"):
            parts.append(f"- **District:** {h.get('state_district')}")
        parts.append(f"- **City / Town:** {h.get('city')}")
        if h.get("suburb_or_locality"):
            parts.append(f"- **Suburb / Locality:** {h.get('suburb_or_locality')}")
        if h.get("street_or_road"):
            parts.append(f"- **Street / Road:** {h.get('street_or_road')}")
        if h.get("postcode"):
            parts.append(f"- **Postal / PIN Code:** {h.get('postcode')}")
        parts.append(f"- **GPS Coordinates:** `{loc.get('latitude')}, {loc.get('longitude')}`")
        parts.append(f"- **Category / Type:** {loc.get('category')} / {loc.get('type')}\n")

    return "\n".join(parts)


@mcp.tool()
async def osint_location_entity_search(
    entity_name: str,
    country: str = "",
    state: str = "",
    city: str = "",
    postal_code: str = "",
    street_or_landmark: str = "",
    category_or_context: str = "",
    exclude_terms: Optional[List[str]] = None,
    max_results: int = 5,
) -> str:
    """
    Hierarchical Location-based OSINT Search Matrix with Negative Exclusion Filters.
    """
    data = await search_location_entity_hierarchy(
        entity_name=entity_name,
        country=country,
        state=state,
        city=city,
        postal_code=postal_code,
        street_or_landmark=street_or_landmark,
        category_or_context=category_or_context,
        exclude_terms=exclude_terms,
        max_results=max_results,
    )

    parts = [
        f"# 🎯 Location-Based OSINT Search Matrix: `{entity_name}`",
        f"**Target Entity:** {entity_name}",
        f"**Location Hierarchy Filters:** {', '.join(f'{k}={v}' for k, v in data['input_location_filter'].items() if v)}\n",
    ]

    if data.get("geoint_breakdown"):
        parts.append("## 📍 Resolved Geospatial Hierarchy (OpenStreetMap)")
        for g in data["geoint_breakdown"][:1]:
            h = g.get("hierarchy", {})
            parts.append(f"- **Matched Address:** {g.get('display_name')}")
            parts.append(f"- **PIN / Postcode:** {h.get('postcode', 'N/A')}")
            parts.append(f"- **District / Suburb:** {h.get('city_district') or h.get('suburb_or_locality', 'N/A')}")
            parts.append(f"- **GPS Lat/Lon:** `{g.get('latitude')}, {g.get('longitude')}`\n")

    parts.append(f"## 🔎 Multi-Tier Search Findings ({data.get('total_results', 0)} sources)")
    for idx, item in enumerate(data.get("results", []), 1):
        parts.append(f"### {idx}. [{item['title']}]({item['url']})")
        parts.append(f"*Triggered by Query: `{item['query_used']}`*")
        if item.get("snippet"):
            parts.append(f"> {item['snippet']}\n")

    return "\n".join(parts)


@mcp.tool()
async def osint_domain_recon(domain_or_url: str) -> str:
    """
    OSINT Tool: Gather public domain intelligence including SSL Certificate validity/issuer, DNS resolution, and WHOIS/RDAP.
    """
    domain = clean_hostname(domain_or_url)
    ssl_data = get_ssl_cert_info(domain)
    whois_data = await fetch_rdap_whois(domain)

    parts = [
        f"# OSINT Domain Recon: {domain}",
        f"## 🔒 SSL/TLS Certificate",
        f"- **SSL Valid:** {ssl_data.get('ssl_available')}",
        f"- **Subject:** {ssl_data.get('subject', 'N/A')}",
        f"- **Issuer:** {ssl_data.get('issuer', 'N/A')}",
        f"- **Valid Until:** {ssl_data.get('valid_until', 'N/A')}",
        f"- **SANs Count:** {ssl_data.get('sans_count', 0)}\n",
        f"## 📋 WHOIS & RDAP Metadata",
        f"- **Registrar:** {whois_data.get('registrar', 'N/A')}",
        f"- **Registration Date:** {whois_data.get('registration_date', 'N/A')}",
        f"- **Expiration Date:** {whois_data.get('expiration_date', 'N/A')}",
        f"- **Nameservers:** {', '.join(whois_data.get('nameservers', [])) or 'N/A'}",
    ]
    return "\n".join(parts)


@mcp.tool()
async def osint_tech_stack(url: str) -> str:
    """
    OSINT Tool: Fingerprint web technology stack, frameworks (React, Vue, Next.js, Angular, Django, etc.), CMS, CDN, and servers.
    """
    res = await detect_website_tech(url)
    parts = [f"# OSINT Tech Stack: {res.get('url', url)}\n"]

    if res.get("server_headers"):
        parts.append("### Detected Server Headers")
        for k, v in res["server_headers"].items():
            parts.append(f"- **{k}:** {v}")
        parts.append("\n")

    stack = res.get("tech_stack", {})
    if stack:
        parts.append("### Identified Technologies")
        for category, items in stack.items():
            parts.append(f"#### {category}")
            for item in items:
                parts.append(f"- {item}")
    else:
        parts.append("*No prominent standard third-party frameworks detected (custom stack or static HTML).*")

    return "\n".join(parts)


@mcp.tool()
async def osint_ip_lookup(ip_or_host: str) -> str:
    """
    OSINT Tool: Lookup public IP Geolocation, ASN, ISP, and Organization information.
    """
    data = await fetch_ip_intel(ip_or_host)
    if data.get("status") == "fail":
        return f"Could not retrieve IP intel for `{ip_or_host}`: {data.get('message', 'Lookup failed')}"

    parts = [
        f"# OSINT IP Intelligence: {data.get('query')}",
        f"- **Host / Target:** {ip_or_host}",
        f"- **Country:** {data.get('country')}",
        f"- **Region / City:** {data.get('regionName')}, {data.get('city')} (ZIP: {data.get('zip')})",
        f"- **Timezone:** {data.get('timezone')}",
        f"- **ISP:** {data.get('isp')}",
        f"- **Organization:** {data.get('org')}",
        f"- **ASN:** {data.get('as')}",
    ]
    return "\n".join(parts)


@mcp.tool()
async def osint_username_check(username: str) -> str:
    """
    OSINT Tool: Check public presence and profile existence for a handle/username across 25+ developer and creator platforms.
    """
    data = await check_username_osint(username)
    parts = [
        f"# OSINT Username Presence: `@{data['username']}`",
        f"**Platforms Scanned:** {data['total_platforms_scanned']} | **Found Profiles:** {data['total_found']}\n",
    ]
    if data.get("profiles"):
        parts.append("### Active Profiles")
        for p in data["profiles"]:
            parts.append(f"- **{p['platform']}:** [{p['profile_url']}]({p['profile_url']})")
    else:
        parts.append(f"No public profiles found for `@{data['username']}` across the standard scanned platforms.")

    return "\n".join(parts)


@mcp.tool()
async def osint_search(
    query: str,
    site: str = "",
    filetype: str = "",
    in_title: str = "",
    exclude_terms: Optional[List[str]] = None,
    time_range: str = "",
    max_results: int = 5,
) -> str:
    """
    OSINT Tool: Targeted intelligence search / dorking using advanced boolean operators (site:, filetype:pdf/xlsx/docx, intitle:, -exclude).
    """
    results = osint_search_dork(
        query=query,
        site=site or None,
        filetype=filetype or None,
        in_title=in_title or None,
        exclude_terms=exclude_terms or None,
        time_range=time_range or None,
        max_results=max_results,
    )
    if not results:
        return f"No OSINT search results found."

    parts = [f"# OSINT Dork Search Results\n"]
    for idx, r in enumerate(results, 1):
        parts.append(f"### {idx}. [{r['title']}]({r['url']})")
        if r.get("snippet"):
            parts.append(f"> {r['snippet']}\n")
    return "\n".join(parts)


@mcp.tool()
async def osint_wayback_time_machine(
    url: str,
    timestamp: str = "",
    list_snapshots: bool = False,
    limit: int = 5,
) -> str:
    """
    Wayback Machine Historical Recon Tool:
    Time-travel and retrieve archived snapshots of deleted or past webpages from the Internet Archive.
    
    Args:
        url: The webpage URL to investigate.
        timestamp: Optional 14-digit timestamp (e.g. '20210515120000'). If empty, fetches most recent.
        list_snapshots: If True, returns a list of available historical snapshot dates instead of page content.
        limit: Number of snapshot dates to return (default 5).
    """
    if list_snapshots:
        snaps = await fetch_wayback_snapshots(url, limit=limit)
        if not snaps:
            return f"No archived Wayback snapshots found for `{url}`."
        parts = [f"# 🏛️ Wayback Historical Snapshots: `{url}`\n"]
        for s in snaps:
            parts.append(f"- **{s['formatted_date']}** | Timestamp: `{s['timestamp']}` | [{s['archived_url']}]({s['archived_url']})")
        return "\n".join(parts)

    res = await scrape_wayback_snapshot(url=url, timestamp=timestamp)
    return res.get("markdown", "Failed to retrieve archived snapshot.")


@mcp.tool()
async def osint_subdomain_enumeration(
    domain: str,
    limit: int = 50,
) -> str:
    """
    Subdomain Recon Tool:
    Enumerate all public active and historical subdomains for any domain via Certificate Transparency Logs in <1 second.
    
    Args:
        domain: The root domain to scan (e.g. 'target.com' or 'github.com').
        limit: Maximum subdomains to return (default 50).
    """
    res = await enumerate_subdomains(domain=domain, limit=limit)
    return res.get("markdown", "No subdomains found.")


@mcp.tool()
async def osint_dns_audit(
    domain: str,
) -> str:
    """
    DNS & Infrastructure Audit Tool:
    Lookup IPv4, IPv6, and server infrastructure records for any domain.
    
    Args:
        domain: Domain name to audit (e.g. 'openai.com').
    """
    res = await audit_dns_records(domain=domain)
    return res.get("markdown", "DNS lookup completed.")


@mcp.tool()
async def extract_image_exif(
    image_url: str,
) -> str:
    """
    Image EXIF & Geotag Recon Tool:
    Extracts camera make/model, creation timestamp, editing software, and exact GPS coordinates (with map link) from any online image.
    
    Args:
        image_url: The direct HTTP/HTTPS URL of the image file (.jpg, .png, .tiff, .webp).
    """
    res = await extract_image_exif_from_url(image_url=image_url)
    return res.get("markdown", "Failed to extract EXIF metadata.")


@mcp.tool()
async def extract_reddit_thread_tool(
    url: str,
    max_comments: int = 25,
) -> str:
    """
    Reddit Discussion Thread Extractor:
    Extracts full Reddit post content, upvote ratio, author, and top community comments into structured dialogue Markdown.
    
    Args:
        url: Full Reddit post URL (e.g. 'https://www.reddit.com/r/programming/comments/...').
        max_comments: Number of top comments to extract (default 25).
    """
    res = await extract_reddit_thread(url=url, max_comments=max_comments)
    return res.get("markdown", "Failed to extract Reddit thread.")


@mcp.tool()
async def extract_rss_feed_tool(
    feed_url: str,
    max_items: int = 10,
) -> str:
    """
    RSS & Atom Feed Ingestion Tool:
    Extracts recent articles, publish dates, links, and summaries from any RSS or Atom feed (Substack, blogs, news).
    
    Args:
        feed_url: The RSS or Atom feed URL (e.g. 'https://openai.com/news/rss.xml' or 'https://blog.bytebytego.com/feed').
        max_items: Number of recent articles to extract (default 10).
    """
    res = await extract_rss_feed(feed_url=feed_url, max_items=max_items)
    return res.get("markdown", "Failed to extract RSS feed.")


@mcp.tool()
async def optimize_rag_chunks(
    text_or_markdown: str,
    max_chunk_chars: int = 2000,
) -> str:
    """
    Semantic RAG Chunker & Token Optimizer:
    Splits large scraped web documents into header-aware semantic chunks with token counts and section headers for LLM embeddings and context efficiency.
    
    Args:
        text_or_markdown: The large Markdown or text string to chunk.
        max_chunk_chars: Maximum characters per chunk (default 2000 ~500 tokens).
    """
    res = chunk_content_for_rag(text_or_markdown=text_or_markdown, max_chunk_chars=max_chunk_chars)
    return json.dumps(res, indent=2, ensure_ascii=False)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
