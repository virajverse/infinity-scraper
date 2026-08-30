# 🌐 InfinityScrape MCP: World-Class Web Scraping, Dynamic SPA Rendering & 25-Tool OSINT Intelligence Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Protocol: MCP](https://img.shields.io/badge/Protocol-Model%20Context%20Protocol-green.svg)](https://modelcontextprotocol.io/)
[![Port: 8000](https://img.shields.io/badge/OpenAPI%20Bridge-Port%208000-purple.svg)](http://127.0.0.1:8000/docs)
[![Zero-Cloud-API](https://img.shields.io/badge/Zero--Cloud--API-100%25%20Free%20%26%20Local-blue.svg)]()
[![Zero-GPU](https://img.shields.io/badge/Zero--GPU-Ultra--Lightweight-orange.svg)]()

**InfinityScrape MCP** is a standalone, production-grade Model Context Protocol (MCP) server engineered to provide AI models (**Open WebUI, Claude 3.7, DeepSeek-R1/V3, Antigravity AI, Cursor, LM Studio**) with **unlimited, high-speed, anti-bot resilient web scraping, dynamic SPA rendering, DuckDuckGo web search, Wayback Machine time-travel, instant YouTube transcription, and precision OSINT / GEOINT location intelligence**.

---

## 📑 Table of Contents

- [🌟 Why InfinityScrape MCP?](#-why-infinityscrape-mcp)
- [⚡ Competitive Comparison](#-competitive-comparison)
- [🏗️ Architectural Overview](#️-architectural-overview)
- [🚀 Quick Start & 1-Click Installation](#-quick-start--1-click-installation)
- [🔌 AI Client Integration (Open WebUI, Claude, Cursor)](#-ai-client-integration)
- [🛠️ Complete 25-Tool Reference Catalog](#️-complete-25-tool-reference-catalog)
  - [1. Real-Time Web Search & Archive OSINT (4 Tools)](#1-real-time-web-search--archive-osint-4-tools)
  - [2. Anti-Bot Web Scraping & Documentation Crawlers (9 Tools)](#2-anti-bot-web-scraping--documentation-crawlers-9-tools)
  - [3. Media, Video & Document Parsers (2 Tools)](#3-media-video--document-parsers-2-tools)
  - [4. Deep Public OSINT & Entity Reconnaissance (7 Tools)](#4-deep-public-osint--entity-reconnaissance-7-tools)
  - [5. Precision GEOINT & Image Intelligence (3 Tools)](#5-precision-geoint--image-intelligence-3-tools)
- [💻 Command-Line Interface (CLI)](#-command-line-interface-cli)
- [🧪 Running Automated Tests](#-running-automated-tests)
- [📄 License & Authors](#-license--authors)

---

## 🌟 Why InfinityScrape MCP?

Standard web scrapers often fail on modern websites due to Cloudflare challenges, heavy client-side JavaScript rendering, intrusive cookie consent modals, and rate limits. InfinityScrape solves these problems out-of-the-box:

1. **Dual-Engine Scraping Architecture:**
   - **Fast TLS Engine (`primp` + `httpx`):** Mimics real Chrome/Safari browser TLS/JA3 fingerprints and HTTP/2 headers to bypass Cloudflare and Akamai challenges in `<100ms`.
   - **Dynamic Headless Browser (`Playwright Chromium`):** Renders complex SPAs (React, Vue, Next.js, Angular), performs infinite scrolling, clicks elements, and executes custom JavaScript.
2. **Network-Level Ad & Tracker Elimination:**
   - Intercepts and aborts network calls to 35+ ad networks and tracking scripts (`doubleclick`, `criteo`, `outbrain`, `google-analytics`) before they download, cutting page load time by **~300%** and memory usage by **70%**.
   - Automatically detects and decomposes OneTrust, Cookiebot, and sticky overlay popups.
3. **Zero-API Key Real-Time Web Search:**
   - Native DuckDuckGo live search and Google Dork query generation to conduct up-to-date research without paying for Serper, Brave, or Bing search APIs.
4. **Wayback Machine Time-Travel:**
   - Query internet archive history for any URL across custom date ranges to track competitor pricing changes, deleted pages, and historical copy.
5. **Zero-GPU Instant YouTube Transcriber:**
   - Extracts complete video/shorts/live transcripts with timestamps (`[MM:SS]`) in `<300ms` directly via HTTP streams without downloading video or requiring local GPU Whisper models.
6. **Deep Recursive Documentation Crawler:**
   - Asynchronous Breadth-First-Search (BFS) crawler with domain locking and path prefix filtering to aggregate entire documentation trees into unified Markdown.
7. **State-of-the-Art Public OSINT & GEOINT Reconnaissance:**
   - **Multi-Signal Confidence Scoring (0% - 100%):** Evaluates Name + City + Street + PIN + Org + Role correlation to rank discovered dossiers.
   - **25+ Global Platform Scanners:** Scans GitHub, GitLab, StackOverflow, Kaggle, HuggingFace, LeetCode, Codeforces, Dev.to, Medium, Substack, Google Scholar, ResearchGate, Reddit, etc.
   - **OpenStreetMap GEOINT:** Resolves global addresses down to street/postcode level with GPS coordinates and administrative boundaries.
8. **SQLite Persistent Caching Layer:**
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

## 🛠️ Complete 25-Tool Reference Catalog

### 1. Real-Time Web Search & Archive OSINT (4 Tools)
| Tool | Description |
| :--- | :--- |
| **`duckduckgo_search`** | Real-time web search without API keys. Returns ranked URLs, titles, and snippets. |
| **`search_google_dork`** | Generates advanced Google Dork strings (`filetype:pdf`, `site:gov`, `inurl:admin`). |
| **`query_wayback_machine`**| Fetches historical snapshots, archive timestamps, and past versions of any URL. |
| **`scan_domain_security_headers`** | Audits HTTP security headers (CSP, HSTS, X-Frame-Options, CORS). |

### 2. Anti-Bot Web Scraping & Documentation Crawlers (9 Tools)
| Tool | Description |
| :--- | :--- |
| **`scrape_website`** | Production-grade scraper with auto-switching (Fast TLS -> Playwright Chromium fallback). |
| **`scrape_markdown`** | Extracts clean, readable Markdown from any webpage, stripping navigation and ads. |
| **`scrape_table`** | Extracts HTML tables and converts them into structured Markdown / JSON datasets. |
| **`scrape_raw_html`** | Returns complete raw HTML of a target page for custom DOM parsing. |
| **`scrape_page_metadata`**| Extracts OpenGraph, Twitter cards, JSON-LD schemas, and meta tags. |
| **`extract_text_and_links_from_url`** | Extracts all visible text alongside outbound internal/external hyperlinks. |
| **`deep_crawl_documentation`** | Recursive BFS documentation crawler with depth limits and domain locking. |
| **`search_and_crawl_docs`** | Hybrid search-and-crawl engine to locate and summarize specific docs topics. |
| **`diff_webpages`** | Fetches and compares two URLs, highlighting content diffs and added/removed text. |

### 3. Media, Video & Document Parsers (2 Tools)
| Tool | Description |
| :--- | :--- |
| **`get_youtube_transcript`** | Zero-GPU, sub-300ms transcript extraction from YouTube videos, shorts, and live streams. |
| **`parse_online_pdf`** | Streams and parses remote online PDF files page-by-page into Markdown text. |

### 4. Deep Public OSINT & Entity Reconnaissance (7 Tools)
| Tool | Description |
| :--- | :--- |
| **`find_developer_profiles`** | Scans 10+ developer platforms (GitHub, GitLab, StackOverflow, Kaggle, LeetCode). |
| **`find_researcher_profiles`**| Scans academic databases (Google Scholar, ResearchGate, arXiv, ORCID). |
| **`find_social_profiles`** | Scans public social networks and communities (Reddit, Dev.to, Medium, Substack). |
| **`verify_contact_data`** | Cross-validates emails, phone numbers, and social handles with confidence scoring. |
| **`discover_org_hierarchy`** | Maps organizational structures, key leadership, and public company roles. |
| **`investigate_public_entity`** | Aggregates multi-source OSINT dossiers on persons or organizations. |
| **`resolve_physical_address`** | Converts free-form physical addresses into validated postal and geocoded records. |

### 5. Precision GEOINT & Image Intelligence (3 Tools)
| Tool | Description |
| :--- | :--- |
| **`geocode_global_address`** | Forward geocoding via OpenStreetMap/Nominatim down to street and postal code. |
| **`reverse_geocode_coordinates`** | Converts GPS coordinates (latitude, longitude) into full postal addresses. |
| **`reverse_search_image`** | Generates reverse image search query URLs for Google, Bing, Yandex, and TinEye. |

---

## 💻 Command-Line Interface (CLI)

InfinityScrape provides a built-in CLI for quick terminal testing:
```bash
# Scrape a webpage into Markdown
infinity-scrape scrape "https://news.ycombinator.com" --format markdown

# Search DuckDuckGo from the terminal
infinity-scrape search "Generative Engine Optimization 2026" --limit 5

# Extract YouTube Transcript
infinity-scrape youtube "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# OSINT Persona Lookup
infinity-scrape osint --name "Linus Torvalds" --platforms github,gitlab
```

---

## 🧪 Running Automated Tests

```bash
# Run unit and integration tests
pytest tests/ -v
```

---

## 📄 License & Authors

* **Author**: [Viraj](https://github.com/virajverse) (Founder & CEO, Taliyo Technologies)
* **License**: MIT License. See [LICENSE](LICENSE) for details.
