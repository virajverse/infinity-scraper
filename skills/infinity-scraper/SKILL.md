---
name: infinity-scraper
description: >-
  World-Class Autonomous AI Playbook & Cognitive Reasoning Framework for InfinityScrape MCP Suite.
  Enables any AI Agent to scrape web content, render dynamic SPAs, crawl documentation, transcribe
  YouTube videos, extract image EXIF GPS geotags, parse Reddit/RSS feeds, time-travel via Wayback Machine,
  enumerate subdomains, and execute multi-signal OSINT & GEOINT location intelligence.
---

# InfinityScrape MCP: Master Autonomous AI Agent Playbook (23 Tools)

This skill empowers any AI model (**Claude 3.7, GPT-4o, Llama 3.3, DeepSeek-R1/V3, Qwen, Antigravity AI, Open WebUI, LM Studio, Cursor**) to **dynamically reason, self-assemble parameters, multi-tool chain, and autonomously adapt** to any scraping or intelligence challenge on the internet.

---

## 🧠 The Agent's 4-Step Cognitive Loop

```
  ┌──────────────────────────────────────────────┐
  │ 1. SENSE: Deconstruct Intent & Extract Clues │
  └──────────────────────┬───────────────────────┘
                         ▼
  ┌──────────────────────────────────────────────┐
  │ 2. PLAN: Select Optimal Tool or Tool-Chain   │
  └──────────────────────┬───────────────────────┘
                         ▼
  ┌──────────────────────────────────────────────┐
  │ 3. ACT: Self-Assemble Parameters Dynamically │
  └──────────────────────┬───────────────────────┘
                         ▼
  ┌──────────────────────────────────────────────┐
  │ 4. ADAPT: Evaluate Result & Escalate/Pivot   │
  └──────────────────────────────────────────────┘
```

---

## 🧭 Dynamic Intent-to-Tool Mapping (23 Tools)

| Intent / Trigger in User Request | Primary Tool to Invoke | Parameter Strategy |
| :--- | :--- | :--- |
| **Specific Webpage / Article URL** | `scrape_url` | `url`, `engine='auto'`, `strip_ads=True`. |
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
| **RSS / Substack / Blog Feed Monitor** | `extract_rss_feed_tool` | `feed_url`, `max_items=10`. |
| **Website Tech Stack (React/Vue/CMS/CDN)** | `osint_tech_stack` | `url="https://site.com"`. |
| **SSL/TLS Certificate Validity & SANs** | `osint_domain_recon` | `domain_or_url`. |
| **Public IP Geolocation & ASN Lookup** | `osint_ip_lookup` | `ip_or_host`. |
| **Large Scraped Document Token Optimization** | `optimize_rag_chunks` | `text_or_markdown`, `max_chunk_chars=2000`. |

---

## 🔄 Advanced Multi-Tool Chaining Patterns

### Pattern A: "Competitor Infrastructure & Security Audit"
1. `osint_subdomain_enumeration(domain="company.com")` ➔ Discovers `api.company.com`, `app.company.com`.
2. `osint_tech_stack(url="https://app.company.com")` ➔ Identifies Next.js, Cloudflare, React.
3. `osint_domain_recon(domain_or_url="company.com")` ➔ Audits SSL certificate expiry and RDAP registrar.

### Pattern B: "Investigative Historical Time-Travel"
1. User gives a broken/deleted link.
2. `osint_wayback_time_machine(url="https://site.com/deleted-article", list_snapshots=True)` ➔ Finds active dates.
3. `osint_wayback_time_machine(url="https://site.com/deleted-article", timestamp="20220101")` ➔ Recovers original Markdown text.

### Pattern C: "Social Intelligence & Sentiment Extraction"
1. `search_web(query="DeepSeek-V3 review site:reddit.com")` ➔ Finds top Reddit discussion link.
2. `extract_reddit_thread_tool(url="https://reddit.com/r/...")` ➔ Ingests structured dialogue and top comments.

### Pattern D: "Image Geolocation & EXIF Verification"
1. `extract_image_exif(image_url="https://target.com/photo.jpg")` ➔ Extracts GPS Lat/Lon.
2. If GPS found: `osint_geoint_lookup(location_query="<lat>, <lon>")` ➔ Resolves exact street name, suburb, and PIN code!

---

## 🛡️ Best Practices & Execution Guardrails

1. **Context Window Efficiency:** Always prefer clean Markdown over raw HTML. Use `optimize_rag_chunks` when dealing with massive >100K token documents.
2. **Attribution & Citations:** Always link source URLs as `[Title](URL)` in your final responses.
3. **Negative Dorking:** In OSINT recon, always specify `exclude_terms` for common names to avoid celebrity or spam pollution.
