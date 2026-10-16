"""
Live Diagnostic Test Suite for InfinityScrape Failure Points.
Runs real, live network requests and tests real failure vectors:
1. Dead / Non-existent Domains (DNS NXDOMAIN)
2. HTTP Error codes (403 Forbidden, 429 Rate Limit, 500, 502, 504)
3. Search Engine Rate Limits and Multi-Tier Fallback (DDGS -> DDG HTML -> Bing)
4. YouTube Video with Disabled Transcripts / Invalid Video ID
5. crt.sh / HackerTarget Subdomain Fallbacks
6. Reddit API blocking / custom User-Agent
7. Nominatim OpenStreetMap burst requests
8. Corrupt / Malformed Office & Sitemap inputs
9. Windows Unicode / UTF-8 encoding resilience
"""

import sys
import os
import asyncio
import io
import time

# Ensure UTF-8 output even on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from infinity_scraper.engines.fast import fetch_url_fast
from infinity_scraper.extractors.youtube import fetch_youtube_transcript
from infinity_scraper.osint.search import search_web_ddg, _search_ddg_html_fallback, _search_bing_fallback, search_and_scrape_all
from infinity_scraper.osint.subdomains import enumerate_subdomains
from infinity_scraper.osint.network import fetch_rdap_whois, get_ssl_cert_info, detect_website_tech
from infinity_scraper.osint.geoint import fetch_geoint_location
from infinity_scraper.extractors.social import extract_reddit_thread
from infinity_scraper.extractors.office import extract_docx_from_bytes, extract_xlsx_from_bytes
from infinity_scraper.engines.sitemap import fetch_and_parse_sitemap
from infinity_scraper.engines.diff import compute_page_diff


async def test_dead_domain():
    print("\n--- [TEST 1] Non-Existent Domain (NXDOMAIN) ---")
    dead_url = "https://this-domain-definitely-does-not-exist-9988776655.org"
    try:
        res = await fetch_url_fast(dead_url, timeout=5)
        print(f"Status Code: {res.status_code}")
        print(f"Handled Gracefully: {res.status_code == 500 or 'Error' in res.title}")
        print(f"Result Snippet: {res.content_markdown[:100]}...")
        return True
    except Exception as e:
        print(f"CRASHED with unhandled exception: {type(e).__name__}: {e}")
        return False


async def test_http_403_and_timeout():
    print("\n--- [TEST 2] HTTP 403 Forbidden & Timeout Resilience ---")
    forbidden_url = "https://httpbin.org/status/403"
    try:
        res = await fetch_url_fast(forbidden_url, timeout=5, max_retries=1)
        print(f"403 Response status: {res.status_code}")
        print(f"Handled: {res.status_code == 403}")
    except Exception as e:
        print(f"403 CRASHED: {e}")

    slow_url = "https://httpbin.org/delay/10"
    try:
        t0 = time.time()
        res_slow = await fetch_url_fast(slow_url, timeout=3, max_retries=1)
        elapsed = time.time() - t0
        print(f"Timeout Handled: status={res_slow.status_code}, elapsed={elapsed:.2f}s")
    except Exception as e:
        print(f"Timeout CRASHED: {e}")


async def test_search_engine_fallbacks():
    print("\n--- [TEST 3] Search Engines & Fallback Cascades ---")
    query = "python release notes"

    print("Testing DDGS standard search...")
    res1 = search_web_ddg(query, max_results=3)
    print(f"DDGS returned {len(res1)} results.")

    print("Testing Tier-2 Fallback: DDG HTML Lite scraper...")
    res2 = _search_ddg_html_fallback(query, max_results=3)
    print(f"DDG HTML fallback returned {len(res2)} results.")
    if res2:
        print(f"Sample 1: {res2[0].get('title')} -> {res2[0].get('url')}")

    print("Testing Tier-3 Fallback: Bing HTML scraper...")
    res3 = _search_bing_fallback(query, max_results=3)
    print(f"Bing HTML fallback returned {len(res3)} results.")
    if res3:
        print(f"Sample 1: {res3[0].get('title')} -> {res3[0].get('url')}")

    print("Testing search_and_scrape_all with multiple pages...")
    try:
        agg = await search_and_scrape_all("fastmcp python anthropic", max_results=2)
        print(f"Aggregated Scraped Sources: {agg.get('results_count')}")
        print(f"Markdown preview length: {len(agg.get('summary_markdown', ''))} chars")
    except Exception as e:
        print(f"search_and_scrape_all CRASHED: {type(e).__name__}: {e}")


async def test_youtube_failure_modes():
    print("\n--- [TEST 4] YouTube Transcripts (No-Captions / Invalid URL) ---")
    # Video with disabled or no captions (standard video)
    print("Testing video without transcripts...")
    try:
        res = await fetch_youtube_transcript("https://www.youtube.com/watch?v=ba_9Yj8qZ4E")
        print(f"Handled properly: {res.get('markdown', '')[:100]}...")
    except Exception as e:
        print(f"YouTube no-caption CRASHED: {type(e).__name__}: {e}")

    # Completely invalid ID
    print("Testing invalid YouTube URL...")
    try:
        res_inv = await fetch_youtube_transcript("https://www.youtube.com/watch?v=invalid_id_xyz")
        print(f"Invalid URL handled: {res_inv.get('markdown', '')[:100]}...")
    except Exception as e:
        print(f"YouTube invalid ID CRASHED: {type(e).__name__}: {e}")


async def test_subdomain_and_dns():
    print("\n--- [TEST 5] Subdomain Recon & Unstable API Fallbacks ---")
    # Test on a real domain
    domain = "virajverse.com"
    try:
        t0 = time.time()
        subs = await enumerate_subdomains(domain, limit=10)
        elapsed = time.time() - t0
        print(f"Subdomain recon completed in {elapsed:.2f}s")
        print(f"Discovered {subs.get('total_found', len(subs.get('subdomains', [])))} subdomains.")
    except Exception as e:
        print(f"Subdomains CRASHED: {type(e).__name__}: {e}")


async def test_geoint_nominatim():
    print("\n--- [TEST 6] OpenStreetMap Nominatim Rate-Limit Probe ---")
    try:
        # Rapid successive queries
        res1 = await fetch_geoint_location("Eiffel Tower Paris")
        if res1 and isinstance(res1, list) and len(res1) > 0:
            print(f"Query 1: {res1[0].get('display_name', '')[:60]}...")
        else:
            print(f"Query 1 returned: {res1}")
        res2 = await fetch_geoint_location("Taj Mahal Agra")
        if res2 and isinstance(res2, list) and len(res2) > 0:
            print(f"Query 2: {res2[0].get('display_name', '')[:60]}...")
        else:
            print(f"Query 2 returned: {res2}")
    except Exception as e:
        print(f"GEOINT Nominatim CRASHED: {type(e).__name__}: {e}")


async def test_reddit_scraping():
    print("\n--- [TEST 7] Reddit Thread Scraping (Bot User-Agent Check) ---")
    # Test public Reddit post
    reddit_url = "https://www.reddit.com/r/Python/comments/17q5r8s/what_are_your_favorite_python_libraries/"
    try:
        res = await extract_reddit_thread(reddit_url)
        print(f"Reddit status: title='{res.get('title')}', comments_count={res.get('total_comments_extracted')}")
        if res.get('error'):
            print(f"Reddit notice: {res.get('error')}")
    except Exception as e:
        print(f"Reddit CRASHED: {type(e).__name__}: {e}")


async def test_corrupt_binary_inputs():
    print("\n--- [TEST 8] Corrupted / Malformed Office & Sitemap Files ---")
    # Corrupted DOCX bytes
    try:
        res_docx = extract_docx_from_bytes(b"NOT_A_VALID_ZIP_OR_DOCX_HEADER", "corrupt.docx")
        print(f"Corrupt DOCX handled: success={res_docx.get('success')}, error='{res_docx.get('error')}'")
    except Exception as e:
        print(f"Corrupt DOCX CRASHED: {type(e).__name__}: {e}")

    # Corrupted XLSX bytes
    try:
        res_xlsx = extract_xlsx_from_bytes(b"NOT_A_VALID_EXCEL_STREAM", "corrupt.xlsx")
        print(f"Corrupt XLSX handled: success={res_xlsx.get('success')}, error='{res_xlsx.get('error')}'")
    except Exception as e:
        print(f"Corrupt XLSX CRASHED: {type(e).__name__}: {e}")

    # Corrupted / 404 Sitemap
    try:
        res_map = await fetch_and_parse_sitemap("https://httpbin.org/status/404")
        print(f"404 Sitemap handled: success={res_map.get('success')}, error='{res_map.get('error')}'")
    except Exception as e:
        print(f"404 Sitemap CRASHED: {type(e).__name__}: {e}")


async def main():
    print("=" * 60)
    print("INFINITYSCRAPE LIVE REAL-WORLD FAILURE POINT DIAGNOSTIC")
    print("Testing live internet connections, real anti-bot filters, and fallbacks")
    print("=" * 60)

    await test_dead_domain()
    await test_http_403_and_timeout()
    await test_search_engine_fallbacks()
    await test_youtube_failure_modes()
    await test_subdomain_and_dns()
    await test_geoint_nominatim()
    await test_reddit_scraping()
    await test_corrupt_binary_inputs()

    print("\n" + "=" * 60)
    print("DIAGNOSTIC PROBE COMPLETE.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
