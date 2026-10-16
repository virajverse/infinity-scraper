---
name: infinity-scraper
description: >-
  World-Class Autonomous AI Playbook & Cognitive Reasoning Framework for InfinityScrape MCP Suite.
  Enables any AI Agent to scrape web content with high-speed Singleton BrowserPool (~1.8s), render dynamic SPAs with Playwright,
  bypass Cloudflare Turnstile, execute 3-tier multi-engine search failovers (Anti-429), crawl documentation trees,
  transcribe YouTube videos (Zero-GPU), extract PDF text, parse Reddit discussions & RSS feeds, extract image EXIF GPS geotags,
  time-travel via Wayback Machine, enumerate subdomains, fingerprint tech stacks, and execute multi-signal OSINT & GEOINT location intelligence.
---

# ⚡ InfinityScrape MCP: Master Autonomous AI Agent Playbook (33 Tools)

This skill empowers any AI model (**Claude 3.7, GPT-4o, DeepSeek-R1/V3, Llama 3.3, Qwen, Antigravity IDE, Open WebUI**) with **god-tier data extraction, web intelligence, and multi-signal OSINT & GEOINT reconnaissance superpowers** on **Port 8000** (`http://127.0.0.1:8000/openapi.json` / `https://mcp1.taliyotechnologies.com`).

Every capability is engineered for **high performance (Singleton BrowserPool ~1.8s), 3-tier search failover resilience, zero-hallucination parameter assembly, multi-tool chaining, and dynamic self-healing**.

---

## 🧠 LLM Quick-Start & Cognitive Decision Flow

```
                     ┌───────────────────────────────────────────────┐
                     │          Research / Extraction Request        │
                     └───────────────────────┬───────────────────────┘
                                             │
      ┌──────────────────┬───────────────────┼───────────────────┬──────────────────┐
      ▼                  ▼                   ▼                   ▼                  ▼
[Single Webpage]    [Live Search]      [Media / Video]     [Company / Domain]   [Social / RSS]
      │                  │                   │                   │                  │
`scrape_url(url)`  `search_and_scrape`  `get_youtube_transcript` `osint_domain_recon` `extract_reddit_thread`
      │                  │                   │                   │                  │
(If empty SPA ➔)   (3-Tier Failover:   (Zero GPU, <300ms   `osint_tech_stack`  `extract_rss_feed`
`scrape_dynamic`   DDG + HTML + Bing)  captions)           `osint_subdomains`
```

---

## 🧭 Dynamic Intent-to-Tool Matrix (All 33 Tools)

| Intent / Trigger in User Request | Primary Tool | Parameter Strategy |
| :--- | :--- | :--- |
| **Specific Webpage / Clean Markdown** | `scrape_url` | `url`, `engine='auto'`, `strip_ads=True`, `max_chars=50000`. |
| **Live Internet Search / Anti-429** | `search_web` | `query`, `max_results=5`, `search_type='text'` (Auto 3-tier failover). |
| **Live Autonomous Web Research Report** | `search_and_scrape` | `query`, `max_results=4`, `use_browser=False`. |
| **Dynamic SPA / React / Cloudflare** | `scrape_dynamic` | `url`, `scroll_depth=2`, `wait_seconds=2.0` (Turnstile auto-bypass). |
| **Zero-Selector / Semantic Schema** | `extract_schema` | `url`, `schema={"title": "h1", "price": "price"}` (Auto JSON-LD & meta). |
| **Documentation Tree / Site Crawler** | `deep_crawl` | `start_url`, `path_prefix="/docs/"`, `max_depth=2`, `max_pages=5`. |
| **Structured Tables & JSON-LD Metadata** | `extract_structured` | `url`, `extract_tables=True`, `extract_metadata=True`. |
| **Batch Multi-URL Scraping** | `scrape_batch` | `urls=[...]`, `concurrency=4`, `use_browser=False`. |
| **Online PDF Document Parsing** | `extract_pdf` | `url`, `max_pages=20` (Streams bytes via TLS). |
| **YouTube Video / Podcast Transcription** | `get_youtube_transcript` | `url`, `with_timestamps=True` (<300ms, Zero GPU). |
| **Person / Entity Public Recon Dossier** | `osint_deep_public_recon` | `name`, `location`, `organization`, `role_or_keywords`, `exclude_terms`. |
| **Address / Landmark / Street Geocoding** | `osint_geoint_lookup` | `location_query="Karol Bagh, New Delhi"`, `limit=3`. |
| **Location Entity Hierarchy Dorking** | `osint_location_entity_search` | `entity_name`, `city`, `street_or_landmark`, `postal_code`, `exclude_terms`. |
| **Domain SSL, WHOIS & RDAP Intel** | `osint_domain_recon` | `domain_or_url="target.com"`. |
| **Website Tech Stack Fingerprinting** | `osint_tech_stack` | `url="https://target.com"`. |
| **IP Geolocation, ISP & ASN Intel** | `osint_ip_lookup` | `ip_or_host="1.1.1.1"` or `"target.com"`. |
| **Global Handle / Alias Footprint Scan** | `osint_username_check` | `username` (Scans 25+ global developer & creator platforms). |
| **Precision Dorking with Boolean Filters**| `osint_search` | `query`, `site='gov.in'`, `filetype='pdf'`, `in_title=''`, `exclude_terms`. |
| **Deleted / Historical Page Snapshot** | `osint_wayback_time_machine` | `url`, `timestamp=""`, `list_snapshots=False` (HTTPS CDX). |
| **Subdomain Enumeration (API/Staging)** | `osint_subdomain_enumeration` | `domain="target.com"`, `limit=50` (Cert Transparency crt.sh). |
| **DNS Infrastructure & Mail Server Audit**| `osint_dns_audit` | `domain="target.com"`. |
| **Image EXIF Metadata & GPS Geotags** | `extract_image_exif` | `image_url` (Camera specs, timestamp, GPS map link). |
| **Reddit Discussion Post & Comments Tree** | `extract_reddit_thread_tool` | `url`, `max_comments=25`. |
| **RSS / Atom Feed News Monitor** | `extract_rss_feed_tool` | `feed_url`, `max_items=10`. |
| **Semantic RAG Chunker & Token Optimizer** | `optimize_rag_chunks` | `text_or_markdown`, `max_chunk_chars=2000`. |
| **Zero-Selector Contact & Lead Sheet** | `extract_contacts` | `url="https://target.com"` (Auto-extracts emails, phones, WhatsApp, GSTIN/CIN). |
| **SaaS Pricing Table & Matrix Extractor**| `extract_pricing_table` | `url="https://target.com/pricing"` (Auto-detects tiers, costs, billing, CTAs). |
| **Accordion & Schema FAQs Extractor** | `extract_faqs` | `url="https://target.com/faq"` (Extracts questions & answers via JSON-LD/HTML5). |
| **High-Speed XML Sitemap Ingestion** | `crawl_sitemap` | `sitemap_url="https://target.com/sitemap.xml"`, `max_urls=200` (Gzip & Index support). |
| **Domain Sitemap Discovery Radar** | `discover_sitemaps` | `base_url="https://target.com"` (Robots.txt & endpoint probing). |
| **Word (.docx) Document Streamer** | `extract_docx_document` | `url_or_path="https://.../report.docx"` (Markdown + tables without local disk bloat). |
| **Excel (.xlsx) Spreadsheet Streamer** | `extract_xlsx_spreadsheet`| `url_or_path="https://.../data.xlsx"` (Markdown tables & structured JSON records). |
| **Temporal Page Diff & Change Radar** | `compare_page_diff` | `old_content_or_url`, `new_content_or_url` (Detects price shifts & feature deltas). |


---

## 🚀 Engine Performance & Military-Grade Anti-Bot Architecture

1. **Singleton `BrowserPool` (~1.8s SPA Renders)**:
   - Uses a persistent Playwright Chromium process with ephemeral context isolation.
   - Eliminates process cold-start latency and prevents memory leaks.
2. **Military-Grade Anti-Bot Evasions (100% Undetectable)**:
   - `navigator.webdriver`: Cleanly deleted from prototype and returns `undefined`.
   - `WebGL Vendor & Renderer`: Spoofed to authentic `Google Inc. (NVIDIA)` & `NVIDIA GeForce RTX 3080`.
   - `Hardware & Memory`: Spoofed to 8 CPU cores & 8GB device memory.
   - `Plugins & MimeTypes`: Spoofed to native Chrome PDF Viewer & NaCl plugins.
   - `TLS Handshake`: Emulates Chrome 124+ JA3/JA4 fingerprints with full HTTP/2 via `primp`.
3. **3-Tier Multi-Engine Search Failover**:
   - `DuckDuckGo API` ➡️ `DuckDuckGo HTML Lite` ➡️ `Bing HTML Fallback`.
   - Never fails on rate-limits, Captchas, or DNS anomalies.
4. **Cloudflare Turnstile & Interstitial Auto-Solver**:
   - Automatically detects challenge iframes and dispatches simulated user coordinates to bypass interstitials.
5. **Zero-Selector Semantic Schema Fallback (`extract_schema`)**:
   - `extract_schema` takes a dictionary map `{"business_name": "h2.title", "phone": "a[href^='tel:']"}`.
   - Supports directory scraping (JustDial, Indiamart, Maps) and automatically inspects `<script type="application/ld+json">` and OpenGraph meta tags when targeted CSS selectors are missing or randomized.

---

## ⚡ Multi-Tool Chaining Recipes

### 1. Autonomous Content-to-Blog Synthesis Pipeline
```
[User: "Write an in-depth article about this YouTube video / new tech release"]
   │
   ├──> Step 1: Call `get_youtube_transcript(url=...)` OR `scrape_url(url=...)`
   │    Extract key concepts, timestamps, and core technical substance.
   │
   ├──> Step 2: Call `search_and_scrape(query="[Tech] benchmarks 2026", max_results=3)`
   │    Gather industry benchmarks, competitive comparisons, and corroborating citations.
   │
   └──> Step 3: Pass synthesized 15/15 SEO content directly to `taliyo-admin-mcp`!
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
   ├──> Step 3: Call `osint_tech_stack(url="https://taliyotechnologies.com")`
   │    Identify Next.js, Supabase, Tailwind, and hosting edge nodes.
   │
   ├──> Step 4: Call `osint_deep_public_recon(name="Viraj", organization="Taliyo Technologies")`
   │    Cross-correlate GitHub, LinkedIn, patents, registries, and corporate filings.
   │
   └──> Step 5: Synthesize structured Intelligence Dossier with zero guesswork.
```

---

## 🧬 Dynamic Cognitive Reasoning & Combinatorial Pattern Engine

> **Agent Directive**: Do **NOT** restrict yourself to fixed, static recipes. The 25 tools of InfinityScrape form an orthogonal capability space. From **4 Fundamental Primitive Archetypes**, you can dynamically compose **hundreds of specialized, emergent workflow patterns** for any custom research or extraction challenge.

```
                    ┌───────────────────────────────────────────────┐
                    │    THE 4 CORE PRIMITIVE SEED ARCHETYPES       │
                    └───────────────────────┬───────────────────────┘
                                            │
         ┌──────────────────┬───────────────┴───────────────┬──────────────────┐
         ▼                  ▼                               ▼                  ▼
┌──────────────────┐ ┌───────────────────────────┐ ┌──────────────────┐ ┌────────────────────────┐
│  [Archetype A]   │ │       [Archetype B]       │ │  [Archetype C]   │ │     [Archetype D]      │
│  Wide-Spectrum   │ │     Deep Extraction &     │ │ Cross-Correlated │ │    Temporal Delta &    │
│  Recon Harvest   │ │  Multi-Format Distillation│ │   Triangulation  │ │   Semantic Synthesis   │
│                  │ │                           │ │                  │ │                        │
│ • search_web     │ │ • scrape_url              │ │ • osint_deep_... │ │ • osint_wayback_...    │
│ • search_and_... │ │ • scrape_dynamic          │ │ • osint_username │ │ • deep_crawl           │
│ • osint_search   │ │ • extract_schema          │ │ • osint_domain   │ │ • scrape_batch         │
│ • osint_subdom...│ │ • extract_pdf             │ │ • osint_geoint   │ │ • optimize_rag_chunks  │
│ • extract_rss    │ │ • get_youtube_transcript  │ │ • extract_exif   │ │                        │
│                  │ │ • extract_reddit_thread   │ │ • osint_tech_stk │ │                        │
└──────────────────┘ └───────────────────────────┘ └──────────────────┘ └────────────────────────┘
```

### 🧩 Dynamic Combinatorial Algebra: Compose Infinite Workflows
To solve any arbitrary goal, dynamically synthesize an emergent pattern by chaining 2 to 4 primitives:

$$\text{Emergent Pattern} = \text{Seed}_i \xrightarrow{\text{Data Hand-off}} \text{Seed}_j \xrightarrow{\text{Refinement}} \text{Seed}_k$$

#### 🔮 Exemplar Emergent Combinations (Generated on the Fly):

1. **Competitor Strategic Drift & Pricing Delta Engine ($D \rightarrow B \rightarrow B$)**:
   - `osint_wayback_time_machine(url, timestamp="20250101")` (Snapshot from 1 year ago)
   - `scrape_url(url)` (Current live page)
   - `extract_schema(schema={"tier": ".plan-name", "price": ".amount"})`
   - *Result*: Pinpoint exactly how much pricing increased, what features were removed, and detect silent terms-of-service shifts.

2. **Physical & Digital Business Legitimacy Audit ($A \rightarrow C \rightarrow B$)**:
   - `osint_location_entity_search(entity_name, city, street)`
   - `osint_geoint_lookup(location_query)` (Validate physical GPS existence via OpenStreetMap)
   - `osint_domain_recon` + `osint_tech_stack` (Verify digital footprint and SSL integrity)
   - `extract_structured(url, extract_tables=True)` (Extract registered office directors and corporate filings)
   - *Result*: Zero-hallucination due diligence report on vendors, agencies, or lead targets.

3. **Multi-Modal Research Paper & Video Synthesis ($B \rightarrow B \rightarrow D$)**:
   - `extract_pdf(url=arxiv_paper_url)` (Ingest dense research equations & architecture text)
   - `get_youtube_transcript(url=author_conference_talk)` (Extract high-level intuitive explanations)
   - `optimize_rag_chunks(max_chunk_chars=1500)` (Slice both into cohesive token chunks for RAG embedding)
   - *Result*: High-density executive digest combining academic rigor with spoken commentary.

4. **Real-Time Sentiment Radar & Crisis Intelligence ($A \rightarrow B \rightarrow A$)**:
   - `extract_rss_feed_tool(feed_url, max_items=15)` (Detect breaking news / security incident alert)
   - `extract_reddit_thread_tool(url=discussion_url)` (Harvest unfiltered consumer & community sentiment)
   - `osint_search(query="site:twitter.com OR site:linkedin.com incident", exclude_terms="marketing")`
   - *Result*: Real-time 360-degree PR & technical post-mortem report before official releases.

5. **Exposed Attack-Surface & Internal Infrastructure Mapping ($A \rightarrow C \rightarrow C$)**:
   - `osint_subdomain_enumeration(domain="company.com")` (Harvest staging, test, and auth subdomains)
   - `osint_dns_audit` + `osint_ip_lookup` (Map hosting IP providers, cloud egress, and SPF misconfigurations)
   - `extract_image_exif(image_url="company_team_photo.jpg")` (Extract hidden camera metadata and GPS coordinates)
   - *Result*: Comprehensive cyber reconnaissance dossier mapping internal systems without intrusive port scans.

---

## 🤝 Decoupled Agentic Symbiosis: Infinity-Scraper + Spectra-Browser MCP

> **Core Agent Directive (Zero Hardcoded Coupling):**
> InfinityScrape and SpectraBrowser are **100% decoupled, independent MCP servers**. InfinityScrape does **NOT** hardcode or execute SpectraBrowser commands under the hood.
> **The AI AGENT is the Brain & Sole Orchestrator:**
> 1. **Default High Speed:** The AI Agent initiates all research, search, sitemaps, and bulk scraping using **InfinityScrape** (<150ms per page, 33 tools).
> 2. **Signal Detection:** If InfinityScrape encounters an interactive anti-bot wall (Cloudflare Turnstile, Reddit "Prove your humanity", or 403 challenge), it does not fail silently—it returns an explicit **Anti-Bot Advisory Signal** (`requires_browser_escalation: true`).
> 3. **Agent-Driven Escalation:** The **AI Agent** reads this signal and autonomously decides to shift that single blocked target to **SpectraBrowser** (`browser_navigate(url=...)`, followed by `page_understand()` or `page_inspect()`).
> 4. **Bypass & Resume:** SpectraBrowser accesses the URL via the user's real human Chrome context. The AI Agent ingests the rendered markdown and immediately resumes high-speed bulk operations with InfinityScrape!

```
┌────────────────────────────────────────────────────────────────────────┐
│             DECOUPLED AGENTIC WATERFALL ARCHITECTURE                   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                               [AI AGENT]
                         (The Brain & Decision Maker)
                                    │
         ┌──────────────────────────┴──────────────────────────┐
         ▼                                                     ▼
┌─────────────────────────────────┐           ┌─────────────────────────────────┐
│     INFINITY SCRAPER (MCP)      │           │      SPECTRA BROWSER (MCP)      │
│ • Ultra-Fast TLS Engine (<150ms)│           │ • Live Chrome Extension / CDP   │
│ • 33 Tools: OSINT, Search, Docs │           │ • 99 Tools: DOM & Visual QA     │
│ • Fast, Lightweight (20MB RAM)  │           │ • Human Cookies & GPU Canvas    │
└────────────────┬────────────────┘           └────────────────┬────────────────┘
                 │                                             ▲
                 │ (If Anti-Bot Challenge Signal Raised)       │
                 └────────────► [AI AGENT SHIFTS] ─────────────┘
```

### 🔬 Honest Reality Check: 5 Remaining Bottlenecks (Zero Cheating)
Web scraping is an ongoing cat-and-mouse dynamic. No architecture in the world is "100% unblockable forever". Here are the true bottlenecks and how this dual suite handles them:

1. **IP / ASN Reputation Ban (Network-Level Bottleneck):**
   - *Reality*: Even with a genuine Chrome session in SpectraBrowser, if the machine's public IP address belongs to a blacklisted cloud datacenter (AWS, DigitalOcean, Hetzner) or an abused residential VPN, Cloudflare/Akamai drops connections at the TCP SYN / TLS layer.
   - *Mitigation*: Supply rotating residential or 4G/5G mobile proxies to `proxy` in InfinityScrape or launch SpectraBrowser with `--proxy-server`.

2. **Hard Interactive Visual Puzzles (Human Interaction Bottleneck):**
   - *Reality*: Cloudflare Managed Challenges pass automatically in real Chrome. However, complex 3D rotating animal puzzles, sliding jigsaws, or hCaptcha image grids cannot be solved by simple headless scripts.
   - *Mitigation*: SpectraBrowser uses `page_screenshot` for visual inspection, or triggers `session_ask_human` to allow the user to click the puzzle once in their open Chrome tab while retaining automated control.

3. **Memory & Concurrency Scaling (Resource Bottleneck):**
   - *Reality*: InfinityScrape can scrape 100 pages concurrently with 25MB RAM. SpectraBrowser runs full Chrome processes requiring 200MB–400MB RAM per tab.
   - *Rule*: Never crawl bulk sitemaps or batch scrape with SpectraBrowser. Always use InfinityScrape for volume (Tiers 1-2) and escalate ONLY challenging URLs to SpectraBrowser (Tier 3).

4. **Session Invalidation & 2FA Expiry (State Bottleneck):**
   - *Reality*: Gated platforms (LinkedIn, Twitter, banking portals) invalidate session cookies on a regular schedule or after unusual navigation velocity.
   - *Mitigation*: SpectraBrowser connects to the user's live profile (`browser_register_start`) so that whenever the user logs in once, the agent inherits all active cookies without storing raw passwords.

5. **Advanced Telemetry & Behavioral Cadence (Heuristic Bottleneck):**
   - *Reality*: Datadome and Akamai Bot Manager measure micro-jitters in mouse trajectories and keystroke interval distributions.
   - *Mitigation*: SpectraBrowser implements human-cadence physics (Bezier mouse curves, randomized typing delays, DevTools CDP synthetic events) rather than raw DOM `.click()` mutations.


