# 🌐 InfinityScrape MCP: World-Class Web Scraping & Deep OSINT Intelligence Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Protocol: MCP](https://img.shields.io/badge/Protocol-Model%20Context%20Protocol-green.svg)](https://modelcontextprotocol.io/)
[![Zero-Cloud-API](https://img.shields.io/badge/Zero--Cloud--API-100%25%20Free%20%26%20Local-purple.svg)]()
[![Zero-GPU](https://img.shields.io/badge/Zero--GPU-Ultra--Lightweight-orange.svg)]()

**InfinityScrape MCP** is a standalone, production-grade Model Context Protocol (MCP) server engineered to provide AI models (**LM Studio, Claude Desktop, Cursor, Open WebUI, Antigravity AI**) with **unlimited, high-speed, anti-bot resilient web scraping, dynamic SPA rendering, instant YouTube transcription, and precision OSINT / GEOINT location intelligence**.

---

## 📑 Table of Contents

- [🌟 Why InfinityScrape MCP?](#-why-infinityscrape-mcp)
- [⚡ Competitive Comparison](#-competitive-comparison)
- [🏗️ Architectural Overview](#️-architectural-overview)
- [🚀 Quick Start & 1-Click Installation](#-quick-start--1-click-installation)
- [🔌 AI Client Integration (LM Studio, Claude, Cursor)](#-ai-client-integration)
- [🛠️ Complete 16-Tool Reference Guide](#️-complete-16-tool-reference-guide)
  - [1. Web Scraping & Content Crawling](#1-web-scraping--content-crawling)
  - [2. Media, Video & Document Parsers](#2-media-video--document-parsers)
  - [3. Deep Public OSINT & Entity Reconnaissance](#3-deep-public-osint--entity-reconnaissance)
  - [4. Technical, Domain & Network Intelligence](#4-technical-domain--network-intelligence)
- [🧠 Autonomous AI Agent Playbook (`SKILL.md`)](#-autonomous-ai-agent-playbook)
- [💻 Command-Line Interface (CLI)](#-command-line-interface-cli)
- [🧪 Running Automated Tests](#-running-automated-tests)
- [📄 License & Authors](#-license--authors)

---

## 🌟 Why InfinityScrape MCP?

Standard web scrapers often fail on modern websites due to Cloudflare challenges, heavy client-side JavaScript rendering, intrusive cookie consent modals, and rate limits. InfinityScrape solves these problems out-of-the-box:

1. **Dual-Engine Architecture:**
   - **Fast TLS Engine (`primp` + `httpx`):** Mimics real Chrome/Safari browser TLS/JA3 fingerprints and HTTP/2 headers to bypass Cloudflare and Akamai challenges in `<100ms`.
   - **Dynamic Headless Browser (`Playwright Chromium`):** Renders complex SPAs (React, Vue, Next.js, Angular), performs infinite scrolling, clicks elements, and executes custom JavaScript.
2. **Network-Level Ad & Tracker Elimination:**
   - Intercepts and aborts network calls to 35+ ad networks and tracking scripts (`doubleclick`, `criteo`, `outbrain`, `google-analytics`) before they download, cutting page load time by **~300%** and memory usage by **70%**.
   - Automatically detects and decomposes OneTrust, Cookiebot, and sticky overlay popups.
3. **Zero-GPU Instant YouTube Transcriber:**
   - Extracts complete video/shorts/live transcripts with timestamps (`[MM:SS]`) in `<300ms` directly via HTTP streams without downloading video or requiring local GPU Whisper models.
4. **Deep Recursive Documentation Crawler:**
   - Asynchronous Breadth-First-Search (BFS) crawler with domain locking and path prefix filtering to aggregate entire documentation trees into unified Markdown.
5. **State-of-the-Art Public OSINT & GEOINT Reconnaissance:**
   - **Multi-Signal Confidence Scoring (0% - 100%):** Evaluates Name + City + Street + PIN + Org + Role correlation to rank discovered dossiers.
   - **25+ Global Platform Scanners:** Scans GitHub, GitLab, StackOverflow, Kaggle, HuggingFace, LeetCode, Codeforces, Dev.to, Medium, Substack, Google Scholar, ResearchGate, Reddit, etc.
   - **OpenStreetMap GEOINT:** Resolves global addresses down to street/postcode level with GPS coordinates and administrative boundaries.
6. **SQLite Persistent Caching Layer:**
   - In-memory and SQLite-backed local cache for instant `0ms` responses on repeat lookups with configurable TTL.

---

## ⚡ Competitive Comparison

| Feature / Capability | Standard MCP Scrapers | Cloud Scraping APIs | **InfinityScrape MCP** |
| :--- | :---: | :---: | :---: |
| **Cost & API Keys** | Free (Basic) | Paid ($20 - $200/mo) | **100% Free / Zero API Keys** |
| **Cloudflare / Akamai TLS Bypass** | ❌ Fails / 403 | ✅ Yes | **✅ Built-in (`primp` JA3)** |
| **Dynamic SPAs & Infinite Scroll** | ❌ Limited | ✅ Yes | **✅ Built-in (`playwright`)** |
| **Network-Level Ad & Popup Stripping** | ❌ No | ⚠️ Partial | **✅ Built-in (35+ domains)** |
| **Zero-GPU YouTube Transcripts** | ❌ No | ❌ No | **✅ Built-in (<300ms)** |
| **Online PDF Page-by-Page Parser** | ❌ No | ⚠️ Extra Cost | **✅ Built-in (`pypdf`)** |
| **Deep Documentation Crawler** | ❌ No | ⚠️ Extra Cost | **✅ Built-in (Async BFS)** |
| **25+ Platform OSINT & Geocoding** | ❌ No | ❌ No | **✅ Built-in (0-100% Confidence)** |
| **Local SQLite 0ms Caching** | ❌ No | ❌ No | **✅ Built-in (Auto TTL)** |

---

## 🏗️ Architectural Overview

```
                      ┌────────────────────────────────────────────────┐
                      │    AI Client (LM Studio / Claude / Cursor)     │
                      └───────────────────────┬────────────────────────┘
                                              │ JSON-RPC 2.0 (Stdio)
                                              ▼
                      ┌────────────────────────────────────────────────┐
                      │          InfinityScrape MCP Server             │
                      │                  (server.py)                   │
                      └───────┬────────────────┬───────────────┬───────┘
                              │                │               │
            ┌─────────────────┴─┐     ┌────────┴────────┐    ┌─┴────────────────┐
            ▼                   ▼     ▼                 ▼    ▼                  ▼
     [Fast TLS Engine]     [Playwright Engine]   [OSINT / GEOINT]   [Media & PDF Engines]
     • primp JA3/TLS       • Stealth Chromium    • 25+ Platform     • YouTube (<300ms)
     • HTTP/2 Stealth      • Network Ad Blocker    Scanners         • Remote PDF Stream
     • <100ms Execution    • Infinite Scroll     • OpenStreetMap    • Table Markdownify
                           • Auto-Dismiss CMPs   • Match Confidence
                                    │
                                    ▼
                      ┌────────────────────────────────┐
                      │ SQLite Caching Layer (0ms TTL) │
                      └────────────────────────────────┘
```

---

## 🚀 Quick Start & 1-Click Installation

### Prerequisites
- Python 3.10, 3.11, or 3.12+ installed.
- Windows, macOS, or Linux.

### 1-Click Setup:

#### On Windows:
Double-click [`install.bat`](install.bat) or run in PowerShell:
```powershell
.\install.bat
```

#### On Linux / macOS:
```bash
chmod +x install.sh
./install.sh
```

#### Manual Setup (Any Platform):
```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
# Windows: .venv\Scripts\activate | Linux/Mac: source .venv/bin/activate

# 3. Install requirements & Playwright browser
pip install -r requirements.txt
playwright install chromium
```

---

## 🔌 AI Client Integration

### 1. LM Studio (v0.3+)
Go to **Settings ➔ Developer ➔ MCP Servers ➔ Edit Config** and add:
```json
{
  "mcpServers": {
    "infinity-scraper": {
      "command": "C:/path/to/infinity-scraper/.venv/Scripts/python.exe",
      "args": [
        "-m",
        "infinity_scraper.server"
      ],
      "cwd": "C:/path/to/infinity-scraper",
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### 2. Claude Desktop
Edit `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):
```json
{
  "mcpServers": {
    "infinity-scraper": {
      "command": "C:/path/to/infinity-scraper/.venv/Scripts/python.exe",
      "args": [
        "-m",
        "infinity_scraper.server"
      ]
    }
  }
}
```

### 3. Cursor IDE
In Cursor Settings ➔ **Features ➔ MCP Servers ➔ Add New MCP Server**:
- **Name:** `infinity-scraper`
- **Type:** `command`
- **Command:** `C:/path/to/infinity-scraper/.venv/Scripts/python.exe -m infinity_scraper.server`

---

## 🛠️ Complete 23-Tool Reference Guide

### 1. Web Scraping & Content Crawling

| Tool | Purpose | Key Parameters |
| :--- | :--- | :--- |
| `scrape_url` | Universal scraping with auto-upgrading TLS-to-Browser engine. | `url`, `engine='auto'`, `strip_ads=True`, `use_cache=True` |
| `scrape_dynamic` | Headless browser for SPAs, infinite scrolls, and click actions. | `url`, `scroll_depth=3`, `click_selector`, `wait_seconds` |
| `search_web` | Real-time internet search via DuckDuckGo. | `query`, `max_results=5`, `search_type='text'` |
| `search_and_scrape` | Searches web and automatically scrapes top results into a cited report. | `query`, `max_results=4` |
| `deep_crawl` | Recursive async BFS site crawler for full documentation trees. | `start_url`, `max_pages=10`, `max_depth=2`, `path_prefix` |
| `scrape_batch` | Concurrently scrape multiple URLs in parallel. | `urls` (list), `concurrency=4` |
| `extract_schema` | Extract targeted fields using a CSS selector map to JSON. | `url`, `schema={"title": "h1", "price": ".price"}` |
| `extract_structured` | Extract JSON-LD, OpenGraph metadata, and HTML tables. | `url`, `extract_tables=True` |
| `optimize_rag_chunks`| Semantic RAG chunker & token optimizer for massive pages. | `text_or_markdown`, `max_chunk_chars=2000` |

---

### 2. Media, Social, Video & Document Parsers

| Tool | Purpose | Key Parameters |
| :--- | :--- | :--- |
| `get_youtube_transcript` | Zero-GPU YouTube video transcript extraction with timestamps. | `url`, `with_timestamps=True`, `languages` |
| `extract_pdf` | Streams and extracts remote online PDF documents page-by-page. | `url`, `max_pages=20` |
| `extract_image_exif` | Extracts camera specs, timestamps, and GPS geotags from photos. | `image_url` |
| `extract_reddit_thread_tool` | Ingests Reddit posts, scores, and nested comment dialogues. | `url`, `max_comments=25` |
| `extract_rss_feed_tool` | Real-time RSS/Atom feed parser for blogs, Substack, and news. | `feed_url`, `max_items=10` |

---

### 3. Deep Public OSINT & Entity Reconnaissance

| Tool | Purpose | Key Parameters |
| :--- | :--- | :--- |
| `osint_deep_public_recon` | Multi-domain open web profile scraper & confidence-ranked dossier builder. | `name`, `location`, `street_or_locality`, `postal_code`, `organization`, `role_or_keywords`, `exclude_terms`, `time_range` |
| `osint_geoint_lookup` | Global OpenStreetMap forward geocoding & administrative breakdown. | `location_query`, `country_code` |
| `osint_location_entity_search`| Hierarchical location drill-down search matrix with negative filters. | `entity_name`, `country`, `city`, `street_or_landmark`, `postal_code` |
| `osint_username_check` | Scans username presence across 26 coding, academic, and creative networks. | `username` |
| `osint_search` | Precision search dorking (`site:`, `filetype:pdf`, `intitle:`, `-exclude`). | `query`, `site`, `filetype`, `exclude_terms` |

---

### 4. Technical, Domain & Network Intelligence

| Tool | Purpose | Key Parameters |
| :--- | :--- | :--- |
| `osint_domain_recon` | Inspects domain SSL/TLS certificate validity, DNS, and RDAP/WHOIS. | `domain_or_url` |
| `osint_tech_stack` | Detects frontend frameworks (React, Next.js, Vue), CMS, CDN, and servers. | `url` |
| `osint_ip_lookup` | Public IP Geolocation, ASN, ISP, and Organization intel. | `ip_or_host` |
| `osint_wayback_time_machine`| Historical time-travel & deleted webpage snapshot scraper. | `url`, `timestamp`, `list_snapshots` |
| `osint_subdomain_enumeration`| Certificate Transparency subdomains discovery in <1 sec. | `domain`, `limit=50` |
| `osint_dns_audit` | Deep DNS records (IPv4, IPv6, MX) infrastructure audit. | `domain` |

---

## 🧠 Autonomous AI Agent Playbook

InfinityScrape includes an advanced **Cognitive Reasoning Framework (`skills/infinity-scraper/SKILL.md`)** that teaches autonomous AI agents how to:
- Dynamically deconstruct user prompts into search and location clues.
- Multi-tool chain across tools (e.g. `Search ➔ Filter ➔ Batch Scrape` or `Geocode ➔ Locality Dork ➔ Profile Extraction`).
- Auto-escalate from fast TLS to Playwright headless browser when encountering dynamic React single-page apps.

👉 Read the full agent playbook: [`skills/infinity-scraper/SKILL.md`](skills/infinity-scraper/SKILL.md)

---

## 💻 Command-Line Interface (CLI)

You can also use InfinityScrape directly from your terminal:

```powershell
# Scrape a URL to Markdown
python -m infinity_scraper.cli scrape "https://example.com"

# Scrape dynamic SPA with infinite scroll
python -m infinity_scraper.cli scrape "https://news.ycombinator.com" --browser --scroll 3

# Live search and auto-scrape top results
python -m infinity_scraper.cli search "Quantum computing breakthroughs" --scrape --max 4

# Crawl documentation tree
python -m infinity_scraper.cli crawl "https://docs.python.org/3/library/asyncio.html" --pages 5 --depth 2

# Extract remote PDF
python -m infinity_scraper.cli pdf "https://example.com/report.pdf" --pages 10
```

---

## 🧪 Running Automated Tests

Run the comprehensive unit and integration test suite:

```powershell
python -m tests.test_scraper
```

**Test Coverage:**
- ✅ Fast TLS Impersonator
- ✅ Playwright Dynamic Browser
- ✅ DuckDuckGo Live Search
- ✅ HTML Table to Markdown Converter
- ✅ Recursive BFS Documentation Crawler
- ✅ Zero-GPU YouTube Transcript Extraction
- ✅ OSINT SSL, IP Intel & 25+ Platform Presence Check

---

## 📄 License & Copyright Protection

This project is licensed under the **MIT License (with Mandatory Attribution & DMCA Enforcement)**.

> [!IMPORTANT]
> **Mandatory Attribution Notice:**
> - You are free to use, modify, and integrate this project for commercial or personal use.
> - **However, the original Author Attribution and Copyright notice MUST be preserved in all copies, forks, or derivative distributions.**
> - **Removing the author's name/credits and re-uploading/pushing to GitHub as your own work is strictly prohibited and constitutes copyright infringement.** Any infringing repository is subject to immediate **GitHub DMCA Takedown & Repository Deletion** and legal enforcement.

- **Author / Creator:** **[VirajVerse](https://github.com/virajverse)**
- **Repository:** [https://github.com/virajverse/infinity-scraper-mcp](https://github.com/virajverse/infinity-scraper-mcp)
- See [`LICENSE`](LICENSE) for complete legal terms.
