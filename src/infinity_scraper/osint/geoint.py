"""
GEOINT & Hierarchical Location Intelligence for InfinityScrape.
"""

import logging
from typing import Any, Dict, List, Optional
import httpx

from infinity_scraper.osint.search import search_web_ddg

logger = logging.getLogger(__name__)


async def fetch_geoint_location(
    location_query: str,
    country_code: Optional[str] = None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location_query.strip(),
        "format": "json",
        "addressdetails": "1",
        "limit": str(limit),
    }
    if country_code:
        params["countrycodes"] = country_code.lower().strip()

    headers = {
        "User-Agent": "InfinityScrape-OSINT-GEOINT/1.0 (https://github.com/virajverse/infinity-scraper-mcp)",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        async with httpx.AsyncClient(headers=headers, timeout=12.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                raw_data = resp.json()
                results = []
                for item in raw_data:
                    addr = item.get("address", {})
                    results.append({
                        "display_name": item.get("display_name", ""),
                        "type": item.get("type", ""),
                        "category": item.get("class", ""),
                        "latitude": item.get("lat"),
                        "longitude": item.get("lon"),
                        "bounding_box": item.get("boundingbox", []),
                        "hierarchy": {
                            "country": addr.get("country", ""),
                            "country_code": addr.get("country_code", "").upper(),
                            "state": addr.get("state", ""),
                            "state_district": addr.get("state_district", ""),
                            "county": addr.get("county", ""),
                            "city": addr.get("city") or addr.get("town") or addr.get("village", ""),
                            "city_district": addr.get("city_district", ""),
                            "suburb_or_locality": addr.get("suburb") or addr.get("neighbourhood", ""),
                            "street_or_road": addr.get("road", ""),
                            "postcode": addr.get("postcode", ""),
                        },
                    })
                return results
    except Exception as exc:
        logger.error(f"GEOINT location lookup failed for '{location_query}': {exc}")

    return []


async def search_location_entity_hierarchy(
    entity_name: str,
    country: str = "",
    state: str = "",
    city: str = "",
    postal_code: str = "",
    street_or_landmark: str = "",
    category_or_context: str = "",
    exclude_terms: Optional[List[str]] = None,
    max_results: int = 5,
) -> Dict[str, Any]:
    loc_components = [c.strip() for c in [street_or_landmark, city, state, postal_code, country] if c.strip()]
    location_query = ", ".join(loc_components) if loc_components else city or country or "Global"

    geo_data = []
    if location_query != "Global":
        geo_data = await fetch_geoint_location(location_query, limit=3)

    exclusion = ""
    if exclude_terms:
        for ex in exclude_terms:
            if ex.strip():
                exclusion += f' -"{ex.strip()}"'

    search_queries = []
    if street_or_landmark:
        t1 = f'"{entity_name}" "{street_or_landmark}"'
        if city:
            t1 += f' "{city}"'
        search_queries.append(t1 + exclusion)

    if postal_code or city:
        t2_parts = [f'"{entity_name}"']
        if city:
            t2_parts.append(f'"{city}"')
        if postal_code:
            t2_parts.append(f'"{postal_code}"')
        if state:
            t2_parts.append(f'"{state}"')
        search_queries.append(" ".join(t2_parts) + exclusion)

    t3 = f'"{entity_name}"'
    if city or state or country:
        t3 += f' "{city or state or country}"'
    if category_or_context:
        t3 += f' "{category_or_context}"'
    search_queries.append(t3 + exclusion)

    unique_queries = list(dict.fromkeys(search_queries))
    gathered_findings = []
    seen_urls = set()

    for q in unique_queries:
        res = search_web_ddg(query=q, max_results=max_results)
        for r in res:
            u = r.get("url")
            if u and u not in seen_urls:
                seen_urls.add(u)
                gathered_findings.append({
                    "query_used": q,
                    "title": r.get("title", ""),
                    "url": u,
                    "snippet": r.get("snippet", ""),
                })

    return {
        "target_entity": entity_name,
        "input_location_filter": {
            "country": country,
            "state": state,
            "city": city,
            "postal_code": postal_code,
            "street_or_landmark": street_or_landmark,
            "category": category_or_context,
            "exclusions": exclude_terms or [],
        },
        "geoint_breakdown": geo_data,
        "queries_executed": unique_queries,
        "total_results": len(gathered_findings),
        "results": gathered_findings,
    }
