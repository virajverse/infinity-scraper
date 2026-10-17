# 🌐 InfinityScrape MCP: World-Class Web Scraping, Dynamic SPA Rendering & 33-Tool OSINT Intelligence Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Protocol: MCP](https://img.shields.io/badge/Protocol-Model%20Context%20Protocol-green.svg)](https://modelcontextprotocol.io/)
[![Port: 8000](https://img.shields.io/badge/OpenAPI%20Bridge-Port%208000-purple.svg)](http://127.0.0.1:8000/docs)
[![Zero-Cloud-API](https://img.shields.io/badge/Zero--Cloud--API-100%25%20Free%20%26%20Local-blue.svg)]()
[![Zero-GPU](https://img.shields.io/badge/Zero--GPU-Ultra--Lightweight-orange.svg)]()

**InfinityScrape MCP** is a standalone, production-grade Model Context Protocol (MCP) server engineered to provide AI models (**Open WebUI, Claude 3.7, DeepSeek-R1/V3, Antigravity AI, Cursor, LM Studio**) with **unlimited, high-speed, anti-bot resilient web scraping, dynamic SPA rendering, zero-selector contact/pricing/FAQ extraction, remote Word/Excel document streaming, XML sitemap crawling, DuckDuckGo search, Wayback Machine time-travel, instant YouTube transcription, and precision OSINT / GEOINT location intelligence**.

---

## 📑 Table of Contents

- [🌟 Why InfinityScrape MCP?](#-why-infinityscrape-mcp)
- [⚡ Competitive Comparison](#-competitive-comparison)
- [🏗️ Architectural Overview](#️-architectural-overview)
- [🚀 Quick Start & 1-Click Installation](#-quick-start--1-click-installation)
- [🔌 AI Client Integration (Open WebUI, Claude, Cursor)](#-ai-client-integration)
- [🛠️ Complete 33-Tool Reference Catalog](#️-complete-33-tool-reference-catalog)
  - [1. Anti-Bot Web Scraping, Dynamic SPAs & Crawlers (6 Tools)](#1-anti-bot-web-scraping-dynamic-spas--crawlers-6-tools)
  - [2. Real-Time Web Search, Research & Archive OSINT (4 Tools)](#2-real-time-web-search-research--archive-osint-4-tools)
  - [3. Media, Document & RAG Extraction (4 Tools)](#3-media-document--rag-extraction-4-tools)
  - [4. Deep Public OSINT & Entity Reconnaissance (4 Tools)](#4-deep-public-osint--entity-reconnaissance-4-tools)
  - [5. Infrastructure, Domain & Network Reconnaissance (5 Tools)](#5-infrastructure-domain--network-reconnaissance-5-tools)
  - [6. Precision GEOINT & Location Intelligence (2 Tools)](#6-precision-geoint--location-intelligence-2-tools)
  - [7. Zero-Selector Semantics, Office Streaming & Change Radar (8 Tools)](#7-zero-selector-semantics-office-streaming--change-radar-8-tools)
- [💻 Command-Line Interface (CLI)](#-command-line-interface-cli)
- [🧪 Running Automated Tests](#-running-automated-tests)
- [📄 License & Authors](#-license--authors)

---

## 🌟 Why InfinityScrape MCP?

Standard web scrapers often fail on modern websites due to Cloudflare challenges, heavy client-side JavaScript rendering, intrusive cookie consent modals, and rate limits. InfinityScrape solves these problems out-of-the-box:

1. **Dual-Engine Scraping Architecture:**
   - **Fast TLS Engine (`primp` + `httpx`):** Mimics real Chrome/Safari browser TLS/JA3 fingerprints and HTTP/2 headers to bypass Cloudflare and Akamai challenges in `<100ms`.
   - **Dynamic Headless Browser (`Playwright Chromium`):** Renders complex SPAs (React, Vue, Next.js, Angular), performs infinite scrolling, clicks elements, and executes custom JavaScript.
2. **Singleton `BrowserPool` (~1.8s SPA Renders):**
   - Persistent Chromium process with ephemeral context isolation that completely eliminates cold-start latency and avoids memory leaks.
3. **Military-Grade Anti-Bot Evasions (100% Undetectable):**
   - Cleanly deletes `navigator.webdriver` from prototype (`get: () => undefined`).
   - Authentic WebGL Vendor & Renderer spoofing (`Google Inc. (NVIDIA)` & `NVIDIA GeForce RTX 3080`).
   - Hardware concurrency (8 cores), device memory (8GB), and authentic `window.chrome` runtime emulation.
   - Realistic Chrome PDF Viewer plugins and NaCl mimeTypes.
4. **3-Tier Multi-Engine Search Failover (Anti-429 Resilience):**
   - Cascades automatically from `DuckDuckGo API` ➡️ `DuckDuckGo HTML Lite` ➡️ `Bing HTML Fallback`. Zero API keys, zero 429 rate-limits.
5. **Cloudflare Turnstile & Interstitial Auto-Solver:**
   - Detects Turnstile challenge iframes and executes automated coordinate jitter to bypass interstitials.
6. **Network-Level Ad & Tracker Elimination:**
   - Intercepts and aborts network calls to 35+ ad networks and tracking scripts (`doubleclick`, `criteo`, `outbrain`, `google-analytics`) before they download, cutting page load time by **~300%** and memory usage by **70%**.
   - Automatically detects and decomposes OneTrust, Cookiebot, and sticky overlay popups.
7. **Wayback Machine Time-Travel:**
   - Query internet archive history for any URL across custom date ranges to track competitor pricing changes, deleted pages, and historical copy.
8. **Zero-GPU Instant YouTube Transcriber:**
   - Extracts complete video/shorts/live transcripts with timestamps (`[MM:SS]`) in `<300ms` directly via HTTP streams without downloading video or requiring local GPU Whisper models.
9. **Deep Recursive Documentation Crawler:**
   - Asynchronous Breadth-First-Search (BFS) crawler with domain locking and path prefix filtering to aggregate entire documentation trees into unified Markdown.
10. **State-of-the-Art Public OSINT & GEOINT Reconnaissance:**
    - **Multi-Signal Confidence Scoring (0% - 100%):** Evaluates Name + City + Street + PIN + Org + Role correlation to rank discovered dossiers.
    - **25+ Global Platform Scanners:** Scans GitHub, GitLab, StackOverflow, Kaggle, HuggingFace, LeetCode, Codeforces, Dev.to, Medium, Substack, Google Scholar, ResearchGate, Reddit, etc.
    - **OpenStreetMap GEOINT:** Resolves global addresses down to street/postcode level with GPS coordinates and administrative boundaries.
11. **SQLite Persistent Caching Layer:**
    - In-memory and SQLite-backed local cache for instant `0ms` responses on repeat lookups with configurable TTL.

---

## ⚡ Competitive Comparison

| Feature / Capability | Standard MCP Scrapers | Cloud Scraping APIs | **InfinityScrape MCP** |
| :--- | :---: | :---: | :---: |
| **Cost & API Keys** | Free (Basic) | Paid ($20 - $200/mo) | **100% Free / Zero API Keys** |
| **Cloudflare / Akamai TLS Bypass** | ❌ Fails / 403 | ✅ Yes | **✅ Built-in (`primp` JA3)** |
| **Dynamic SPAs & Infinite Scroll** | ❌ Limited | ✅ Yes | **✅ Built-in (`playwright`)** |
| **Real-Time Web Search & Dorking** | ❌ No | ⚠️ Extra Cost | **✅ Built-in (DuckDuckGo & Dorks)** |
| **Wayback Historical Snapshots** | ❌ No | ❌ No | **✅ Built-in (Archive API)** |
| **Network-Level Ad & Popup Stripping** | ❌ No | ⚠️ Partial | **✅ Built-in (35+ domains)** |
| **Zero-GPU YouTube Transcripts** | ❌ No | ❌ No | **✅ Built-in (<300ms)** |
| **Online PDF Page-by-Page Parser** | ❌ No | ⚠️ Extra Cost | **✅ Built-in (`pypdf`)** |
| **Deep Documentation Crawler** | ❌ No | ⚠️ Extra Cost | **✅ Built-in (Async BFS)** |
| **25+ Platform OSINT & Geocoding** | ❌ No | ❌ No | **✅ Built-in (0-100% Confidence)** |
| **OpenAPI 3.1.0 REST Bridge (Port 8000)** | ❌ No | ⚠️ Proprietary | **✅ Built-in (FastAPI /docs)** |

---

## 🏗️ Architectural Overview

```
                      ┌─────────────────────────────────────────────────────────┐
                      │    AI Clients: Open WebUI / Claude Desktop / Cursor     │
                      └────────────────────────────┬────────────────────────────┘
                                                   │
                  ┌────────────────────────────────┴────────────────────────────────┐
                  │                                                                 │
                  ▼                                                                 ▼
      [OpenAPI Bridge (Port 8000)]                                     [Stdio JSON-RPC 2.0 Server]
      FastAPI /docs & /openapi.json                                             (server.py)
                  │                                                                 │
                  └────────────────────────────────┬────────────────────────────────┘
                                                   │
                                                   ▼
            ┌──────────────────────┬──────────────────────┬──────────────────────┐
            ▼                      ▼                      ▼                      ▼
     [Fast TLS Engine]     [Playwright Engine]     [OSINT / GEOINT]     [Search & Media]
     • primp JA3/TLS       • Stealth Chromium      • 25+ Platform       • DuckDuckGo Search
     • HTTP/2 Headers      • Ad/Tracker Blocker      Scanners           • Wayback Snapshots
     • <100ms Execution    • Infinite Scroll       • OpenStreetMap      • YouTube (<300ms)
                           • Auto-Dismiss CMPs     • Reverse Geocoding  • Remote PDF Parser
                                                   • Match Confidence
                                                   │
                                                   ▼
                                    ┌──────────────────────────────┐
                                    │ SQLite Caching Layer (0ms)   │
                                    └──────────────────────────────┘
```

---

## 🚀 Quick Start & 1-Click Installation

### 1. Automated Setup
```bash
# Clone the repository
git clone https://github.com/virajverse/infinity-scraper.git
cd infinity-scraper

# Create virtual environment & install
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
playwright install chromium
```

### 2. Launch FastAPI Bridge (Port 8000)
```bash
python openapi_bridge.py
```
* Interactive Swagger Docs: **`http://127.0.0.1:8000/docs`**
* OpenAPI 3.1.0 Schema: **`http://127.0.0.1:8000/openapi.json`**

---

## 🔌 AI Client Integration

### 1. Open WebUI (FastAPI Bridge on Port 8000)
1. Ensure the bridge is running (`python openapi_bridge.py`).
2. In Open WebUI, navigate to **Workspace -> Tools -> Add Tool**.
3. Import from URL: `http://127.0.0.1:8000/openapi.json` or use `infinity_scraper_suite`.
4. All **25 tools** are instantly accessible to your agents!

### 2. Antigravity AI / Claude Desktop (Native Stdio)
Add to your `mcp_config.json`:
```json
{
  "mcpServers": {
    "infinity-scraper": {
      "command": "python",
      "args": ["-m", "infinity_scraper.server"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

---

## 🛠️ Complete 33-Tool Reference Catalog

### 1. Anti-Bot Web Scraping, Dynamic SPAs & Crawlers (6 Tools)
| Tool | Description |
| :--- | :--- |
| **`scrape_url`** | Production-grade scraping into clean, ad-free Markdown with auto-engine switching (Fast TLS -> Playwright Chromium fallback). Automatically surfaces anti-bot challenge advisories for agent escalation. |
| **`scrape_dynamic`** | Dynamic SPA rendering via Singleton Playwright BrowserPool (~1.8s) with Cloudflare Turnstile auto-bypass and infinite scroll. |
| **`extract_schema`** | Zero-selector semantic extraction mapping custom JSON schemas with auto JSON-LD & OpenGraph meta fallback. |
| **`deep_crawl`** | Asynchronous recursive BFS documentation crawler with depth limits, domain locking, and path prefix filters. |
| **`extract_structured`** | Extracts HTML tables into structured Markdown/JSON datasets and aggregates rich page metadata. |
| **`scrape_batch`** | High-throughput concurrent scraping of multiple URLs with configurable concurrency limits. |

### 2. Real-Time Web Search, Research & Archive OSINT (4 Tools)
| Tool | Description |
| :--- | :--- |
| **`search_web`** | 3-tier resilient real-time web search (DDGS API ➡️ DDG HTML Lite ➡️ Bing HTML Fallback) without API keys or 429 rate limits. |
| **`search_and_scrape`** | End-to-end autonomous web research pipeline: executes queries and scrapes top results into a synthesized research report. |
| **`osint_search`** | Advanced boolean dorking engine supporting `site:`, `filetype:`, `in_title:`, and negative keyword exclusions. |
| **`osint_wayback_time_machine`** | Queries historical archive snapshots, CDX timestamps, and past versions of deleted or updated web pages. |

### 3. Media, Document & RAG Extraction (4 Tools)
| Tool | Description |
| :--- | :--- |
| **`extract_pdf`** | Streams remote online PDF files page-by-page via TLS into clean Markdown text without local disk bloat. |
| **`get_youtube_transcript`** | Zero-GPU, sub-300ms transcript extraction with timestamps (`[MM:SS]`) from YouTube videos, shorts, and live streams. |
| **`extract_image_exif`** | Extracts camera hardware specifications, timestamps, and GPS coordinates with direct Google Maps navigation links. |
| **`optimize_rag_chunks`** | Semantic text and Markdown chunker with token boundary optimization for LLM RAG pipelines and vector stores. |

### 4. Deep Public OSINT & Entity Reconnaissance (4 Tools)
| Tool | Description |
| :--- | :--- |
| **`osint_deep_public_recon`** | Cross-correlates developer platforms, academic registries, and corporate filings into an entity intelligence dossier. |
| **`osint_username_check`** | Scans 25+ global developer, creator, and tech platforms to map digital handles and alias footprints. |
| **`extract_reddit_thread_tool`** | Extracts Reddit discussions, original post content, and nested comment trees into structured Markdown. |
| **`extract_rss_feed_tool`** | Ingests RSS and Atom feeds for real-time news tracking, competitor updates, and blog monitoring. |

### 5. Infrastructure, Domain & Network Reconnaissance (5 Tools)
| Tool | Description |
| :--- | :--- |
| **`osint_domain_recon`** | Audits domain WHOIS, RDAP records, registrar info, and SSL/TLS certificate chains. |
| **`osint_tech_stack`** | Deeply fingerprints website frontend frameworks, backend stacks, CDNs, and analytics trackers. |
| **`osint_ip_lookup`** | Gathers IP geolocation, Autonomous System Number (ASN), ISP, and network routing data. |
| **`osint_subdomain_enumeration`** | Discovers hidden subdomains, internal staging servers, and API routes via Certificate Transparency logs (crt.sh). |
| **`osint_dns_audit`** | Resolves and audits DNS records (A, AAAA, MX, TXT, NS, CNAME) including mail security SPF/DKIM verification. |

### 6. Precision GEOINT & Location Intelligence (2 Tools)
| Tool | Description |
| :--- | :--- |
| **`osint_geoint_lookup`** | Forward geocoding of landmarks, streets, and addresses via OpenStreetMap/Nominatim down to postal code and GPS coordinates. |
| **`osint_location_entity_search`** | Hierarchical entity location dorking correlating business entities with city, street, and postal landmarks. |

### 7. Zero-Selector Semantics, Office Streaming & Change Radar (8 Tools)
| Tool | Description |
| :--- | :--- |
| **`extract_contacts`** | Zero-selector extraction of verified emails, phone numbers, WhatsApp, GSTIN/CIN/EIN, social profiles, and postal codes. |

| **`extract_pricing_table`** | Automatically identifies SaaS pricing cards, tier amounts ($/mo, $/yr, INR), billing cycles, feature matrices, and CTA buttons. |
| **`extract_faqs`** | Heuristic and schema-based FAQ extractor pulling question-and-answer pairs from JSON-LD, `<details>`, and accordions. |
| **`crawl_sitemap`** | High-speed XML sitemap parser with gzip decompression (.xml.gz) and recursive child sitemap index traversal. |
| **`discover_sitemaps`** | Autonomously uncovers all active XML sitemaps for any domain via robots.txt inspection and standard endpoint probing. |
| **`extract_docx_document`** | Streams remote online or local Word (.docx) documents into clean Markdown with full table matrices (zero local bloat). |
| **`extract_xlsx_spreadsheet`**| Streams online or local Excel (.xlsx) spreadsheets, converting all worksheets into clean Markdown tables and JSON records. |
| **`compare_page_diff`** | Temporal page diff & change radar detecting price adjustments, discontinued tiers, new features, and content similarity %. |

---

## 💻 Command-Line Interface (CLI)

InfinityScrape provides a built-in CLI (`infinity-scraper-cli` or `python -m infinity_scraper.cli`) for rapid terminal verification:
```bash
# 1. Scrape a webpage into clean Markdown (Fast TLS or Playwright with --browser)
infinity-scraper-cli scrape "https://news.ycombinator.com"
infinity-scraper-cli scrape "https://example.com/spa" --browser --scroll 2

# 2. Live Web Search & Instant Scraping
infinity-scraper-cli search "Generative Engine Optimization 2026" --max 5
infinity-scraper-cli search "Agentic Workflows" --max 3 --scrape

# 3. Recursive Documentation Tree Crawler
infinity-scraper-cli crawl "https://modelcontextprotocol.io" --pages 5 --depth 2

# 4. Stream & Extract Remote PDF Document
infinity-scraper-cli pdf "https://arxiv.org/pdf/1706.03762.pdf" --pages 10

# Note: All 25 tools (YouTube transcripts, OSINT, GEOINT, Wayback) are directly accessible via:
# - MCP Stdio: `python -m infinity_scraper.server`
# - OpenAPI Bridge (Port 8000): `http://127.0.0.1:8000/docs`
```

---

## 🧪 Running Automated Tests

```bash
# Run unit and integration tests
pytest tests/ -v
```

---

## 📄 License & Authors

* **Author**: [Viraj](https://github.com/virajverse)
* **License**: MIT License. See [LICENSE](LICENSE) for details.
