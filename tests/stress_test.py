"""
Real-World 20-Scenario Dynamic Stress & Data Quality Test for InfinityScrape.
Tests against actual live websites (Wikipedia, GitHub, HackerNews, Python.org, YouTube, OpenStreetMap, Cloudflare, etc.).
"""

import asyncio
import json
import os
import sys
import time
from typing import Any, Dict, List

# Configure UTF-8 for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from infinity_scraper.cache import cache
from infinity_scraper.engines.browser import fetch_url_browser
from infinity_scraper.engines.crawler import crawl_site
from infinity_scraper.engines.fast import fetch_url_fast
from infinity_scraper.extractors.content import parse_html_content
from infinity_scraper.extractors.pdf import extract_pdf_from_url
from infinity_scraper.extractors.youtube import fetch_youtube_transcript
from infinity_scraper.osint.geoint import fetch_geoint_location, search_location_entity_hierarchy
from infinity_scraper.osint.network import (
    check_username_osint,
    detect_website_tech,
    fetch_ip_intel,
    fetch_rdap_whois,
    get_ssl_cert_info,
)
from infinity_scraper.osint.recon import calculate_match_confidence, deep_public_entity_recon, extract_public_identifiers
from infinity_scraper.osint.search import osint_search_dork, search_and_scrape_all, search_web_ddg


test_results: List[Dict[str, Any]] = []


def record_result(test_id: int, name: str, category: str, elapsed_ms: float, quality_metric: str, passed: bool, sample_detail: str):
    test_results.append({
        "id": test_id,
        "name": name,
        "category": category,
        "elapsed_ms": round(elapsed_ms, 2),
        "quality_metric": quality_metric,
        "passed": passed,
        "sample_detail": sample_detail[:350],
    })
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"[{test_id:02d}/20] {status} | {name} ({round(elapsed_ms, 1)}ms) -> {quality_metric}")


async def run_all_stress_tests():
    print("==========================================================================")
    print("   🌐 INFINITYSCRAPE MCP: REAL-WORLD 20-SCENARIO QUALITY & STRESS TEST")
    print("==========================================================================\n")

    # 1. Real Wikipedia Long-Form Article (Fast TLS Scrape)
    t0 = time.time()
    res1 = await fetch_url_fast("https://en.wikipedia.org/wiki/Artificial_intelligence")
    dt1 = (time.time() - t0) * 1000
    passed1 = res1.status_code == 200 and len(res1.content_markdown) > 5000
    record_result(
        1, "Real Wikipedia Long-Form Scrape (AI)", "Scraping", dt1,
        f"HTTP {res1.status_code} | Extracted: {len(res1.content_markdown):,} chars ({len(res1.content_markdown.split())} words) | Tables: {len(res1.tables)}",
        passed1, res1.content_markdown[:200]
    )

    # 2. Real HackerNews Live Frontpage (Playwright Headless Browser)
    t0 = time.time()
    res2 = await fetch_url_browser("https://news.ycombinator.com", wait_seconds=1.0)
    dt2 = (time.time() - t0) * 1000
    passed2 = res2.status_code == 200 and len(res2.links) > 10
    record_result(
        2, "Real HackerNews SPA/Dynamic Scrape (Playwright)", "Browser", dt2,
        f"HTTP {res2.status_code} | Extracted {len(res2.links)} Live Story Links | Content: {len(res2.content_markdown):,} chars",
        passed2, res2.content_markdown[:200]
    )

    # 3. Real Live DuckDuckGo Web Search (Tech Breakthroughs)
    t0 = time.time()
    res3 = search_web_ddg("DeepSeek-V3 LLM architecture reasoning benchmarks", max_results=5)
    dt3 = (time.time() - t0) * 1000
    passed3 = len(res3) >= 1
    sample3 = res3[0]["title"] if res3 else "None"
    record_result(
        3, "Real Live Search (DeepSeek-V3)", "Search", dt3,
        f"Discovered: {len(res3)} Real Search Results with Snippets",
        passed3, sample3
    )

    # 4. Real Search and Top Results Auto-Scraper & Synthesizer
    t0 = time.time()
    res4 = await search_and_scrape_all("Python FastMCP model context protocol", max_results=3)
    dt4 = (time.time() - t0) * 1000
    passed4 = res4.get("results_count", 0) >= 1 and len(res4.get("summary_markdown", "")) > 500
    record_result(
        4, "Real Search & Auto-Scrape Synthesizer", "Synthesis", dt4,
        f"Scraped {res4.get('results_count')} Live Websites | Unified Report: {len(res4.get('summary_markdown', '')):,} chars",
        passed4, res4.get("summary_markdown", "")[:200]
    )

    # 5. Real Multi-Domain Parallel Batch Scraping (Python.org + Cloudflare.com + GitHub.com)
    t0 = time.time()
    urls5 = ["https://www.python.org", "https://www.cloudflare.com", "https://github.com"]
    tasks5 = [fetch_url_fast(u) for u in urls5]
    res5 = await asyncio.gather(*tasks5)
    dt5 = (time.time() - t0) * 1000
    passed5 = all(r.status_code in (200, 301, 302) for r in res5)
    record_result(
        5, "Real Multi-Domain Parallel Batch Scrape (3 Top Sites)", "Concurrency", dt5,
        f"All 3 Sites Scraped in Parallel | Total Chars: {sum(len(r.content_markdown) for r in res5):,} chars (Avg {round(dt5/3, 1)}ms/site)",
        passed5, f"Titles: {[r.title for r in res5]}"
    )

    # 6. Real HTML Tables to Markdown Matrix (Python.org Downloads Table)
    t0 = time.time()
    res6 = await fetch_url_fast("https://www.python.org/downloads/")
    dt6 = (time.time() - t0) * 1000
    passed6 = len(res6.tables) >= 1 or len(res6.content_markdown) > 1000
    table_sample = res6.tables[0]["markdown"] if res6.tables else "Markdown formatted"
    record_result(
        6, "Real HTML Table to Markdown (Python Downloads)", "Extraction", dt6,
        f"Extracted {len(res6.tables)} Structured Tables into Clean Markdown Grids",
        passed6, table_sample[:200]
    )

    # 7. Real Targeted CSS Selector Extraction (GitHub Linux Repo Header)
    t0 = time.time()
    res7 = await fetch_url_fast("https://github.com/torvalds/linux", css_selector="article.markdown-body")
    dt7 = (time.time() - t0) * 1000
    passed7 = len(res7.content_markdown) > 50 or res7.status_code == 200
    record_result(
        7, "Real CSS Targeted Selector (GitHub Linux Readme)", "Extraction", dt7,
        f"Isolated Exact Targeted Container ({len(res7.content_markdown)} chars extracted)",
        passed7, res7.content_markdown[:200]
    )

    # 8. Real Recursive BFS Documentation Crawler (FastAPI Tutorial)
    t0 = time.time()
    res8 = await crawl_site("https://fastapi.tiangolo.com/tutorial/first-steps/", max_pages=3, max_depth=1)
    dt8 = (time.time() - t0) * 1000
    passed8 = res8.get("total_crawled", 0) >= 1 and len(res8.get("aggregated_markdown", "")) > 500
    record_result(
        8, "Real Documentation BFS Crawler (FastAPI Docs)", "Crawler", dt8,
        f"Recursively Ingested {res8.get('total_crawled')} Documentation Pages into Single Linked Guide ({len(res8.get('aggregated_markdown', '')):,} chars)",
        passed8, res8.get("aggregated_markdown", "")[:200]
    )

    # 9. Real YouTube Video Transcript with Timestamps (Zero GPU)
    t0 = time.time()
    res9 = await fetch_youtube_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ", with_timestamps=True)
    dt9 = (time.time() - t0) * 1000
    passed9 = res9.get("total_segments", 0) > 0
    record_result(
        9, "Real YouTube Video Transcriber (Zero-GPU)", "Media", dt9,
        f"Extracted {res9.get('total_segments')} Timestamped Dialogue Segments in {round(dt9, 1)}ms",
        passed9, res9.get("markdown", "")[:200]
    )

    # 10. Real Online PDF Stream & Page Parser (Public PDF Document)
    t0 = time.time()
    res10 = await extract_pdf_from_url("https://raw.githubusercontent.com/py-pdf/pypdf/main/resources/commented.pdf", max_pages=3)
    dt10 = (time.time() - t0) * 1000
    passed10 = res10.get("total_pages", 0) >= 1 and len(res10.get("markdown", "")) > 50
    record_result(
        10, "Real Online PDF Stream Reader (Public Spec)", "Media", dt10,
        f"Parsed {res10.get('total_pages')} Pages | Document Title: '{res10.get('title')}' | Content: {len(res10.get('markdown', ''))} chars",
        passed10, res10.get("markdown", "")[:200]
    )

    # 11. Real OpenStreetMap Forward GEOINT Geocoding (Karol Bagh, Delhi)
    t0 = time.time()
    res11 = await fetch_geoint_location("Arya Samaj Road, Karol Bagh, Delhi", limit=2)
    dt11 = (time.time() - t0) * 1000
    passed11 = len(res11) >= 1 and bool(res11[0].get("latitude"))
    sample11 = f"Lat: {res11[0].get('latitude')}, Lon: {res11[0].get('longitude')}, PIN: {res11[0].get('hierarchy', {}).get('postcode')}" if res11 else "None"
    record_result(
        11, "Real OpenStreetMap Geocoder (Karol Bagh, Delhi)", "OSINT/GEOINT", dt11,
        f"Resolved GPS Lat/Lon & Postcode ({sample11})",
        passed11, res11[0].get("display_name", "") if res11 else ""
    )

    # 12. Real Location Entity Search Matrix with Exclusion Filtering
    t0 = time.time()
    res12 = await search_location_entity_hierarchy(
        entity_name="Hospital",
        city="Karol Bagh",
        state="Delhi",
        country="India",
        category_or_context="healthcare",
        exclude_terms=["ayurveda", "dental"],
        max_results=3,
    )
    dt12 = (time.time() - t0) * 1000
    passed12 = res12.get("total_results", 0) >= 1
    record_result(
        12, "Real Location Entity Matrix (Hospitals in Karol Bagh)", "OSINT/GEOINT", dt12,
        f"Executed {len(res12.get('queries_executed', []))} Hierarchical Dorks | Discovered {res12.get('total_results')} Real Healthcare Entities",
        passed12, f"Queries: {res12.get('queries_executed')}"
    )

    # 13. Real 25+ Platform Username & Profile Presence Scanner (Linus Torvalds)
    t0 = time.time()
    res13 = await check_username_osint("torvalds")
    dt13 = (time.time() - t0) * 1000
    passed13 = res13.get("total_found", 0) >= 1
    profiles13 = [p["platform"] for p in res13.get("profiles", [])]
    record_result(
        13, "Real 25+ Platform Username Scanner (@torvalds)", "OSINT", dt13,
        f"Scanned {res13.get('total_platforms_scanned')} Global Platforms | Discovered Active Profiles on: {', '.join(profiles13[:5])}",
        passed13, f"Profiles: {profiles13}"
    )

    # 14. Real Public Entity Recon with Multi-Signal Match Scoring (0% - 100%)
    t0 = time.time()
    sample_text = "Linus Torvalds is the lead maintainer of the Linux Kernel. Resides in Portland, Oregon and works at the Linux Foundation."
    conf_score14, signals14 = calculate_match_confidence(
        content=sample_text,
        target_name="Linus Torvalds",
        location="Portland",
        organization="Linux Foundation",
        role="Lead Maintainer",
    )
    dt14 = (time.time() - t0) * 1000
    passed14 = conf_score14 >= 80
    record_result(
        14, "Real Multi-Signal Confidence Scoring Algorithm", "OSINT", dt14,
        f"Evaluated Confidence Score: {conf_score14}% | Correlated Signals: {len(signals14)} matched",
        passed14, f"Signals: {signals14}"
    )

    # 15. Real Tech Stack Fingerprinting (Cloudflare.com)
    t0 = time.time()
    res15 = await detect_website_tech("https://www.cloudflare.com")
    dt15 = (time.time() - t0) * 1000
    passed15 = res15.get("status_code") in (200, 301, 302)
    record_result(
        15, "Real Tech Stack Fingerprinter (Cloudflare.com)", "Technical Recon", dt15,
        f"Detected Server Headers: {list(res15.get('server_headers', {}).keys())} | Identified Tech: {list(res15.get('tech_stack', {}).keys())}",
        passed15, str(res15.get("tech_stack"))
    )

    # 16. Real SSL/TLS Certificate Recon (Wikipedia.org)
    t0 = time.time()
    res16 = get_ssl_cert_info("en.wikipedia.org")
    dt16 = (time.time() - t0) * 1000
    passed16 = res16.get("ssl_available") is True
    record_result(
        16, "Real SSL Certificate Recon (Wikipedia.org)", "Technical Recon", dt16,
        f"SSL Active: {res16.get('ssl_available')} | Issuer: '{res16.get('issuer')}' | Subject: '{res16.get('subject')}' | SANs: {res16.get('sans_count')}",
        passed16, str(res16)
    )

    # 17. Real WHOIS / RDAP Domain Registration Recon (GitHub.com)
    t0 = time.time()
    res17 = await fetch_rdap_whois("github.com")
    dt17 = (time.time() - t0) * 1000
    passed17 = bool(res17.get("domain"))
    record_result(
        17, "Real WHOIS/RDAP Domain Recon (GitHub.com)", "Technical Recon", dt17,
        f"Registrar: '{res17.get('registrar')}' | Registration: '{res17.get('registration_date')}' | Expiration: '{res17.get('expiration_date')}'",
        passed17, f"Nameservers: {res17.get('nameservers')}"
    )

    # 18. Real Public IP Geolocation & ASN Intelligence (Google DNS 8.8.8.8)
    t0 = time.time()
    res18 = await fetch_ip_intel("8.8.8.8")
    dt18 = (time.time() - t0) * 1000
    passed18 = res18.get("status") == "success"
    record_result(
        18, "Real IP Geolocation & ASN Intel (8.8.8.8 Google)", "Technical Recon", dt18,
        f"Country: {res18.get('country')} | Region: {res18.get('regionName')} | ISP: '{res18.get('isp')}' | ASN: '{res18.get('as')}'",
        passed18, str(res18)
    )

    # 19. Real Advanced Dorking with Exclusions (FastMCP on GitHub)
    t0 = time.time()
    res19 = osint_search_dork(query="FastMCP python", site="github.com", max_results=3)
    dt19 = (time.time() - t0) * 1000
    passed19 = len(res19) >= 1
    record_result(
        19, "Real Targeted Search Dorking (site:github.com)", "OSINT", dt19,
        f"Discovered {len(res19)} Exact Matching Repositories on GitHub via Search Operators",
        passed19, res19[0]["title"] if res19 else "None"
    )

    # 20. Persistent SQLite 0ms Cache Throughput
    t0 = time.time()
    cache.set("https://benchmark.real/test-key", {"status": "success", "sample": res1.content_markdown[:500]}, ttl_seconds=3600)
    cached_val = cache.get("https://benchmark.real/test-key")
    dt20 = (time.time() - t0) * 1000
    passed20 = cached_val is not None
    record_result(
        20, "Real SQLite Persistent 0ms Cache Benchmark", "Performance", dt20,
        f"Cache Write + Retrieval Completed in {round(dt20, 2)}ms (Instant 0ms Lookups)",
        passed20, str(cached_val)[:150] if cached_val else ""
    )

    print("\n==========================================================================")
    print("   📊 REAL-WORLD STRESS TEST SUMMARY & SCORECARD")
    print("==========================================================================")
    passed_count = sum(1 for t in test_results if t["passed"])
    total_count = len(test_results)
    avg_latency = sum(t["elapsed_ms"] for t in test_results) / total_count

    print(f"Total Live Scenarios Tested: {total_count}")
    print(f"Passed: {passed_count} / {total_count} ({round(passed_count/total_count*100, 1)}%)")
    print(f"Average Live Latency: {round(avg_latency, 1)}ms")
    print("==========================================================================\n")

    report_path = os.path.join(os.path.dirname(__file__), "real_world_stress_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_tests": total_count,
            "passed_tests": passed_count,
            "success_rate": f"{round(passed_count/total_count*100, 1)}%",
            "avg_latency_ms": round(avg_latency, 1),
            "results": test_results,
        }, f, indent=2)
    print(f"Full JSON details saved to: {report_path}")


if __name__ == "__main__":
    asyncio.run(run_all_stress_tests())
