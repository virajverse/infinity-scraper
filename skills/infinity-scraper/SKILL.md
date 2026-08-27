---
name: infinity-scraper
description: >-
  World-Class Autonomous AI Playbook & Cognitive Reasoning Framework for InfinityScrape MCP Suite.
  Enables any AI Agent to scrape web content, render dynamic SPAs, crawl documentation, transcribe
  YouTube videos, extract image EXIF GPS geotags, parse Reddit/RSS feeds, time-travel via Wayback Machine,
  enumerate subdomains, and execute multi-signal OSINT & GEOINT location intelligence.
---

# ⚡ InfinityScrape MCP: Master Autonomous AI Agent Playbook (25 Tools)

This skill empowers any AI model (**Claude 3.7, GPT-4o, DeepSeek-R1/V3, Llama 3.3, Qwen, Antigravity AI, Open WebUI**) with **god-tier data extraction, web intelligence, and multi-signal OSINT & GEOINT reconnaissance superpowers**.

Every capability is engineered for **autonomous execution, zero-hallucination parameter assembly, multi-tool chaining, and dynamic self-healing**.

---

## 🧠 The Agent's 4-Step Cognitive Loop

```
  ┌────────────────────────────────────────────────────────┐
  │ 1. SENSE: Deconstruct User Intent & Target Footprint    │
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 2. PLAN: Select Optimal Tool or Multi-Tool Recipe      │
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 3. ACT: Self-Assemble Parameters & Execute with TLS    │
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 4. ADAPT & CHAIN: Synthesize Intel / Pass to Pipeline   │
  └────────────────────────────────────────────────────────┘
```

---

## 🧭 Dynamic Intent-to-Tool Matrix (25 Tools)

| Intent / Trigger in User Request | Primary Tool | Parameter Strategy |
| :--- | :--- | :--- |
| **Specific Webpage / Clean Markdown** | `scrape_url` | `url`, `engine='auto'`, `strip_ads=True`. |
| **Dynamic SPA / Infinite Feed / React App** | `scrape_dynamic` | `url`, `scroll_depth=3`, `wait_seconds=2.0`. |
| **YouTube Video / Podcast / Shorts** | `get_youtube_transcript` | `url`, `with_timestamps=True` (<300ms, Zero GPU). |
| **Online PDF Document / Whitepaper** | `extract_pdf` | `url`, `max_pages=20` (Streams bytes via TLS). |
| **Live Internet Topic / News Research** | `search_and_scrape` | Turn question into concise query, `max_results=4`. |
| **Entire Documentation Tree Ingestion** | `deep_crawl` | `start_url`, `path_prefix="/docs/"`, `max_depth=2`. |
| **Multiple URLs Simultaneously** | `scrape_batch` | `urls=[...]`, `concurrency=4`. |
| **Specific HTML Elements / Key-Value Map** | `extract_schema` | `url`, `schema={"title": "h1", "price": ".price"}`. |
| **Structured Tables & JSON-LD Schemas** | `extract_structured` | `url`, `extract_tables=True`. |
| **Person / Developer / Company Recon Dossier** | `osint_deep_public_recon` | `name`, `location`, `organization`, `role_or_keywords`, `exclude_terms`. |
| **Address / Landmark / Street Geocoding** | `osint_geoint_lookup` | `location_query="Arya Samaj Road, Karol Bagh"`. |
| **Neighborhood / Locality Entity Dorking** | `osint_location_entity_search` | `entity_name`, `city`, `street_or_landmark`, `postal_code`. |
| **Global Handle / Alias Footprint Scanner** | `osint_username_check` | `username` (Scans 26 global developer & creator networks). |
| **Precision Dorking with Boolean Filters** | `osint_search` | `query`, `site='gov.in'`, `filetype='pdf'`, `exclude_terms`. |
| **Deleted / Historical Webpage Snapshot** | `osint_wayback_time_machine` | `url`, `timestamp=""` (Internet Archive Time-Travel). |
| **Subdomain Enumeration (API/Admin/Staging)** | `osint_subdomain_enumeration` | `domain="target.com"` (Certificate Transparency crt.sh). |
| **DNS Infrastructure & Mail Server Audit** | `osint_dns_audit` | `domain="openai.com"`. |
| **Image EXIF Metadata & GPS Geotags** | `extract_image_exif` | `image_url` (Extracts camera specs & OpenStreetMap link). |
| **Reddit Discussion Post & Comments Tree** | `extract_reddit_thread_tool` | `url`, `max_comments=25`. |
| **RSS / Atom Feed News Monitor** | `extract_rss_tool` | `feed_url` (Parses articles, timestamps, summaries). |
| **XML Sitemap Discovery & URL Discovery** | `extract_sitemap_tool` | `url` (Extracts all indexed URLs for crawling). |

---

## ⚡ God-Tier Multi-Tool Chaining Recipes

### 1. The Autonomous Content-to-Blog Synthesis Pipeline
```
[User: "Write an in-depth article about this YouTube video / new tech release"]
   │
   ├──> Step 1: Call `get_youtube_transcript(url=...)` OR `scrape_url(url=...)`
   │    Extract key concepts, timestamps, and core technical substance.
   │
   ├──> Step 2: Call `search_and_scrape(query="[Tech] benchmarks 2026", max_results=3)`
   │    Gather industry benchmarks, competitive comparisons, and corroborating citations.
   │
   └──> Step 3: Pass synthesized 15/15 SEO content directly to `taliyo-blog-engine`!
        Call `create_blog_post(...)` to publish directly to https://taliyotechnologies.com/blog.
```

### 2. The Comprehensive Target OSINT Dossier Recipe
```
[User: "Investigate company or person: Viraj / Taliyo Technologies"]
   │
   ├──> Step 1: Call `osint_subdomain_enumeration(domain="taliyotechnologies.com")`
   │    Enumerate all active staging, admin, and API infrastructure.
   │
   ├──> Step 2: Call `osint_dns_audit(domain="taliyotechnologies.com")`
   │    Map Cloudflare CDN, MX mail gateways, and SPF/DKIM records.
   │
   ├──> Step 3: Call `osint_deep_public_recon(name="Viraj", organization="Taliyo Technologies")`
   │    Cross-correlate GitHub, LinkedIn, patents, registries, and corporate filings.
   │
   └──> Step 4: Synthesize structured Intelligence Dossier with zero guesswork.
```

### 3. The Forensic Wayback Time-Machine Recipe
```
[User: "Check what changed on this website or recover a deleted page"]
   │
   ├──> Step 1: Call `osint_wayback_time_machine(url=..., timestamp="2024")`
   │    Retrieve exact snapshot from historical web archive.
   │
   ├──> Step 2: Call `scrape_url(url=...)` to get live current state.
   │
   └──> Step 3: Output side-by-side diff highlighting modified text, removed staff, or altered pricing.
```

---

## 🛡️ Autonomous Failover & Anti-Blocking Heuristics

1. **Static vs Dynamic Fallback:**
   * If `scrape_url` fails due to client-side rendering (SPA, Next.js hydration, blank body), **immediately auto-escalate** to `scrape_dynamic(url, wait_seconds=3.0)`.
2. **Rate-Limit & Block Protection:**
   * InfinityScrape uses randomized TLS client fingerprints and auto-rotating User-Agents.
   * If a site returns HTTP 403 / 429, call `osint_wayback_time_machine(url)` as an immediate fallback to read the cached public version without getting blocked!
3. **Zero Hallucination Standard:**
   * Never fabricate transcript contents or quotes. If `get_youtube_transcript` returns no captions, explain cleanly that captions are disabled for that video and offer `search_and_scrape` as an alternative.
