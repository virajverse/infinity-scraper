"""
Deep Multi-Domain Public Entity Profiling & Multi-Signal Confidence Scoring.
"""

import asyncio
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from infinity_scraper.engines.fast import fetch_url_fast
from infinity_scraper.engines.browser import fetch_url_browser
from infinity_scraper.extractors.content import ExtractionResult
from infinity_scraper.osint.search import search_web_ddg

logger = logging.getLogger(__name__)


def extract_public_identifiers(text: str) -> Dict[str, List[str]]:
    emails = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", text)
    clean_emails = list(dict.fromkeys([
        e.lower() for e in emails 
        if not any(ign in e.lower() for ign in ["example.com", "user@domain", "sentry.io", "wixpress.com", "schema.org"])
    ]))

    social_handles = re.findall(r"(?:twitter\.com|x\.com|github\.com|linkedin\.com\/in|t\.me)\/([A-Za-z0-9_-]{2,30})", text, re.I)
    clean_handles = list(dict.fromkeys(social_handles))

    return {
        "public_emails": clean_emails[:5],
        "associated_handles": clean_handles[:8],
    }


def calculate_match_confidence(
    content: str,
    target_name: str,
    location: str = "",
    organization: str = "",
    role: str = "",
    street: str = "",
    pincode: str = "",
) -> Tuple[int, List[str]]:
    score = 0
    signals = []
    text_lower = content.lower()

    if target_name.lower() in text_lower:
        score += 35
        signals.append(f"Exact Name Match ('{target_name}')")
    else:
        name_parts = target_name.lower().split()
        if len(name_parts) > 1 and all(p in text_lower for p in name_parts):
            score += 25
            signals.append("Partial Name Match")

    if location and location.lower() in text_lower:
        score += 20
        signals.append(f"City/Region Match ('{location}')")

    if street and street.lower() in text_lower:
        score += 15
        signals.append(f"Street/Landmark Match ('{street}')")

    if pincode and pincode.strip() in text_lower:
        score += 15
        signals.append(f"PIN Code Match ('{pincode}')")

    if organization and organization.lower() in text_lower:
        score += 15
        signals.append(f"Organization Match ('{organization}')")

    if role and role.lower() in text_lower:
        score += 10
        signals.append(f"Role/Keywords Match ('{role}')")

    final_score = min(score, 100)
    return final_score, signals


async def deep_public_entity_recon(
    name: str,
    location: str = "",
    organization: str = "",
    role_or_keywords: str = "",
    street_or_locality: str = "",
    postal_code: str = "",
    exclude_terms: Optional[List[str]] = None,
    must_include_terms: Optional[List[str]] = None,
    time_range: Optional[str] = None,
    scrape_top_profiles: bool = True,
    max_sources_to_scrape: int = 5,
) -> Dict[str, Any]:
    clean_name = name.strip()
    loc = location.strip()
    org = organization.strip()
    kw = role_or_keywords.strip()
    st = street_or_locality.strip()
    pin = postal_code.strip()

    inclusion_clause = ""
    if loc:
        inclusion_clause += f' "{loc}"'
    if st:
        inclusion_clause += f' "{st}"'
    if pin:
        inclusion_clause += f' "{pin}"'
    if org:
        inclusion_clause += f' "{org}"'
    if kw:
        inclusion_clause += f' "{kw}"'

    if must_include_terms:
        for t in must_include_terms:
            if t.strip():
                inclusion_clause += f' +"{t.strip()}"'

    exclusion_clause = ""
    if exclude_terms:
        for ex in exclude_terms:
            if ex.strip():
                exclusion_clause += f' -"{ex.strip()}"'

    dork_categories = {
        "Professional & Developer Registries": [
            f'"{clean_name}"{inclusion_clause}{exclusion_clause} (site:linkedin.com/in OR site:github.com OR site:dev.to)',
        ],
        "Corporate & Director Filings": [
            f'"{clean_name}"{inclusion_clause}{exclusion_clause} ("founder" OR "director" OR "ceo" OR "partner" OR site:crunchbase.com)',
        ],
        "Public News, Media & Web Mentions": [
            f'"{clean_name}"{inclusion_clause}{exclusion_clause} ("interview" OR "announcement" OR "news")',
        ],
    }

    discovered_by_category: Dict[str, List[Dict[str, Any]]] = {}
    all_unique_urls: List[Dict[str, Any]] = []
    seen_urls = set()

    for cat_name, queries in dork_categories.items():
        discovered_by_category[cat_name] = []
        for q in queries:
            try:
                results = search_web_ddg(query=q, max_results=5, timelimit=time_range)
                for r in (results or []):
                    u = r.get("url")
                    if u and u not in seen_urls:
                        seen_urls.add(u)
                        entry = {
                            "title": r.get("title", ""),
                            "url": u,
                            "snippet": r.get("snippet", ""),
                            "category": cat_name,
                            "query": q,
                        }
                        discovered_by_category[cat_name].append(entry)
                        all_unique_urls.append(entry)
            except Exception as e:
                logger.warning(f"OSINT dork query failed for '{q}': {e}")


    scraped_profiles: List[Dict[str, Any]] = []
    if scrape_top_profiles and all_unique_urls:
        targets_to_scrape = all_unique_urls[:max_sources_to_scrape]
        semaphore = asyncio.Semaphore(3)

        async def _scrape_profile(item: Dict[str, Any]):
            u = item["url"]
            async with semaphore:
                try:
                    res: ExtractionResult = await fetch_url_fast(u)
                    if len(res.content_markdown.strip()) < 150:
                        res = await fetch_url_browser(u, wait_seconds=1.0)

                    content = res.content_markdown.strip()
                    conf_score, signals = calculate_match_confidence(
                        content=content + " " + item["snippet"],
                        target_name=clean_name,
                        location=loc,
                        organization=org,
                        role=kw,
                        street=st,
                        pincode=pin,
                    )
                    identifiers = extract_public_identifiers(content)

                    if len(content) > 8000:
                        content = content[:8000] + "\n\n... *(Scraped content truncated)*"

                    return {
                        "title": res.title or item["title"],
                        "url": u,
                        "category": item["category"],
                        "snippet": item["snippet"],
                        "confidence_score": conf_score,
                        "matched_signals": signals,
                        "public_identifiers": identifiers,
                        "extracted_markdown": content,
                        "metadata": res.metadata,
                    }
                except Exception as e:
                    return {
                        "title": item["title"],
                        "url": u,
                        "category": item["category"],
                        "confidence_score": 10,
                        "matched_signals": ["Search Index Match Only"],
                        "public_identifiers": {},
                        "error": str(e),
                    }

        tasks = [_scrape_profile(t) for t in targets_to_scrape]
        scraped_profiles = await asyncio.gather(*tasks, return_exceptions=False)
        scraped_profiles.sort(key=lambda x: x.get("confidence_score", 0), reverse=True)

    doc = [
        f"# 🌐 Ultra-Precision Public Intelligence Dossier: {clean_name}",
        f"**Search Parameters:** Location=`{loc or 'Any'}` | Street=`{st or 'Any'}` | PIN=`{pin or 'Any'}` | Org=`{org or 'Any'}` | Role=`{kw or 'Any'}`",
        f"**Exclusions:** `{', '.join(exclude_terms) if exclude_terms else 'None'}` | **Freshness:** `{time_range or 'All Time'}`",
        f"**Total Public Sources Identified:** {len(all_unique_urls)}\n",
        "## Summary of Public Discovered Footprint",
    ]

    for cat_name, items in discovered_by_category.items():
        if items:
            doc.append(f"### {cat_name} ({len(items)} found)")
            for item in items:
                doc.append(f"- [{item['title']}]({item['url']})")
                if item.get("snippet"):
                    doc.append(f"  > {item['snippet']}")
            doc.append("")

    if scraped_profiles:
        doc.append("\n---\n## 📄 Verified Scraped Profile Dossiers (Ranked by Confidence)\n")
        for idx, sp in enumerate(scraped_profiles, 1):
            score = sp.get("confidence_score", 0)
            signals_str = ", ".join(sp.get("matched_signals", []))
            doc.append(f"### Profile {idx}: [{sp['title']}]({sp['url']}) — `Confidence: {score}%`")
            doc.append(f"**Category:** {sp.get('category')} | **Signals Matched:** {signals_str}")

            ids = sp.get("public_identifiers", {})
            if ids.get("public_emails") or ids.get("associated_handles"):
                meta_bits = []
                if ids.get("public_emails"):
                    meta_bits.append(f"Emails: `{', '.join(ids['public_emails'])}`")
                if ids.get("associated_handles"):
                    meta_bits.append(f"Handles: `{', '.join(ids['associated_handles'])}`")
                doc.append(f"**Extracted Identifiers:** {' | '.join(meta_bits)}")

            if sp.get("extracted_markdown"):
                doc.append(sp["extracted_markdown"])
            doc.append("\n---\n")

    return {
        "target_name": clean_name,
        "total_sources": len(all_unique_urls),
        "categories": discovered_by_category,
        "scraped_profiles": scraped_profiles,
        "dossier_markdown": "\n".join(doc),
    }
