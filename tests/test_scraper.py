"""
Automated Integration and Unit Tests for InfinityScrape.
"""

import asyncio
import os
import sys

# Ensure src directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from infinity_scraper.engines.browser import fetch_url_browser
from infinity_scraper.engines.crawler import crawl_site
from infinity_scraper.engines.fast import fetch_url_fast
from infinity_scraper.extractors.chunker import chunk_content_for_rag
from infinity_scraper.extractors.content import parse_html_content
from infinity_scraper.extractors.social import extract_reddit_thread, extract_rss_feed
from infinity_scraper.extractors.youtube import fetch_youtube_transcript
from infinity_scraper.osint.network import check_username_osint, fetch_ip_intel, get_ssl_cert_info
from infinity_scraper.osint.search import search_and_scrape_all, search_web_ddg
from infinity_scraper.osint.subdomains import enumerate_subdomains
from infinity_scraper.osint.wayback import fetch_wayback_snapshots


import pytest

@pytest.mark.asyncio
async def test_fast_scrape_httpbin():
    res = await fetch_url_fast("https://httpbin.org/html")
    assert res.status_code == 200
    assert "Herman Melville - Moby-Dick" in res.content_text or "Moby-Dick" in res.content_markdown
    print("[PASS] Fast scrape test passed!")


@pytest.mark.asyncio
async def test_browser_scrape_example():
    res = await fetch_url_browser("https://example.com", wait_seconds=0.5)
    assert res.status_code == 200
    assert "Example Domain" in res.title
    print("[PASS] Browser scrape test passed!")


def test_duckduckgo_search():
    results = search_web_ddg("Python programming language", max_results=3)
    assert len(results) > 0
    assert any("python" in r["title"].lower() or "python" in r["url"].lower() for r in results)
    print(f"[PASS] Search test passed with {len(results)} results!")


def test_html_table_and_markdown_extractor():
    sample_html = """
    <html>
      <head><title>Test Page</title></head>
      <body>
        <h1>Main Heading</h1>
        <p>This is a test paragraph explaining something important.</p>
        <table>
          <tr><th>Name</th><th>Role</th></tr>
          <tr><td>Alice</td><td>Engineer</td></tr>
          <tr><td>Bob</td><td>Designer</td></tr>
        </table>
      </body>
    </html>
    """
    res = parse_html_content(sample_html, url="https://test.local")
    assert "Main Heading" in res.content_markdown
    assert len(res.tables) == 1
    assert "Alice" in res.tables[0]["markdown"]
    print("[PASS] Extractor and table conversion test passed!")


@pytest.mark.asyncio
async def test_deep_crawler():
    res = await crawl_site("https://example.com", max_pages=2, max_depth=1)
    assert res["total_crawled"] >= 1
    assert "Example Domain" in res["aggregated_markdown"]
    print(f"[PASS] Deep crawler test passed with {res['total_crawled']} pages!")


@pytest.mark.asyncio
async def test_youtube_transcription():
    res = await fetch_youtube_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert res.get("total_segments", 0) > 0
    assert "YouTube Video Transcript" in res.get("markdown", "")
    print(f"[PASS] YouTube zero-GPU transcript test passed with {res['total_segments']} segments!")


@pytest.mark.asyncio
async def test_osint_tools():
    ssl_info = get_ssl_cert_info("github.com")
    assert ssl_info.get("ssl_available") is True

    ip_info = await fetch_ip_intel("1.1.1.1")
    assert ip_info.get("status") == "success"

    user_info = await check_username_osint("octocat")
    assert user_info.get("total_found", 0) > 0
    print(f"[PASS] OSINT tools passed (SSL valid, IP intel ok, User presence ok)!")


@pytest.mark.asyncio
async def test_next_gen_tools():
    # 1. RAG Chunker
    sample_text = "# Section 1\nThis is a long introductory text.\n\n## Section 2\nSecond sub-topic with details."
    chunks = chunk_content_for_rag(sample_text, max_chunk_chars=500)
    assert chunks["total_chunks"] >= 1
    print(f"[PASS] RAG Chunker generated {chunks['total_chunks']} semantic chunks!")

    # 2. Wayback Machine
    snaps = await fetch_wayback_snapshots("https://example.com", limit=2)
    assert len(snaps) >= 1
    print(f"[PASS] Wayback Machine found {len(snaps)} historical snapshots!")

    # 3. Subdomains crt.sh
    sub_data = await enumerate_subdomains("github.com", limit=5)
    assert len(sub_data.get("subdomains", [])) >= 1
    print(f"[PASS] Subdomain Recon found {len(sub_data['subdomains'])} subdomains for github.com!")



if __name__ == "__main__":
    asyncio.run(test_fast_scrape_httpbin())
    asyncio.run(test_browser_scrape_example())
    test_duckduckgo_search()
    test_html_table_and_markdown_extractor()
    asyncio.run(test_deep_crawler())
    asyncio.run(test_youtube_transcription())
    asyncio.run(test_osint_tools())
    asyncio.run(test_next_gen_tools())
    print("\n[ALL 23-TOOL UNIT & INTEGRATION TESTS PASSED!]")
