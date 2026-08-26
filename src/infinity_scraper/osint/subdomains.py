"""
Subdomain Enumeration & DNS Security Audit for InfinityScrape.
Uses Certificate Transparency (crt.sh) logs, HackerTarget, and Async DNS Probing without API keys.
"""

import asyncio
import logging
import re
import socket
from typing import Any, Dict, List, Set
from urllib.parse import urlparse
import httpx

from infinity_scraper.osint.network import clean_hostname

logger = logging.getLogger(__name__)

COMMON_SUBDOMAINS = [
    "www", "api", "app", "dev", "staging", "docs", "admin", "mail",
    "portal", "auth", "login", "cdn", "status", "blog", "test",
    "git", "internal", "secure", "cloud", "dashboard", "hub"
]


async def probe_dns_subdomain(subdomain: str) -> bool:
    try:
        loop = asyncio.get_running_loop()
        await loop.getaddrinfo(subdomain, None, socket.AF_INET)
        return True
    except Exception:
        return False


async def enumerate_subdomains(
    domain: str,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Enumerate all public active and historical subdomains for a domain using multiple zero-API fallback engines.
    """
    clean_domain = clean_hostname(domain)
    discovered_subdomains: Set[str] = set()

    # Source 1: HackerTarget API (Fast & reliable)
    try:
        ht_url = f"https://api.hackertarget.com/hostsearch/?q={clean_domain}"
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            resp = await client.get(ht_url)
            if resp.status_code == 200 and "error" not in resp.text.lower():
                for line in resp.text.splitlines():
                    if "," in line:
                        host = line.split(",")[0].strip().lower()
                        if host.endswith(clean_domain):
                            discovered_subdomains.add(host)
    except Exception:
        pass

    # Source 2: crt.sh (Certificate Transparency)
    if len(discovered_subdomains) < 5:
        try:
            crt_url = f"https://crt.sh/?q=%.{clean_domain}&output=json"
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(crt_url)
                if resp.status_code == 200:
                    entries = resp.json()
                    for entry in entries:
                        name_value = entry.get("name_value", "")
                        for sub in name_value.split("\n"):
                            sub_clean = sub.strip().lower()
                            if sub_clean.endswith(clean_domain) and "*" not in sub_clean:
                                discovered_subdomains.add(sub_clean)
        except Exception:
            pass

    # Source 3: Common Prefix DNS Probe fallback
    if len(discovered_subdomains) < 3:
        probe_tasks = []
        for prefix in COMMON_SUBDOMAINS:
            candidate = f"{prefix}.{clean_domain}"
            probe_tasks.append((candidate, probe_dns_subdomain(candidate)))

        for cand, task in probe_tasks:
            try:
                if await task:
                    discovered_subdomains.add(cand)
            except Exception:
                pass

    sorted_subs = sorted(list(discovered_subdomains))[:limit]

    doc = [
        f"# 📡 Subdomain Reconnaissance: `{clean_domain}`",
        f"- **Base Domain:** {clean_domain}",
        f"- **Total Discovered Subdomains:** {len(discovered_subdomains)} (Showing top {len(sorted_subs)})\n",
        "### Discovered Subdomains\n",
    ]

    for s in sorted_subs:
        doc.append(f"- `https://{s}`")

    return {
        "domain": clean_domain,
        "total_discovered": len(discovered_subdomains),
        "subdomains": sorted_subs,
        "markdown": "\n".join(doc),
    }


async def audit_dns_records(
    domain: str,
) -> Dict[str, Any]:
    """
    Audit DNS records including IPv4, IPv6, and server infrastructure.
    """
    clean_domain = clean_hostname(domain)
    records: Dict[str, Any] = {
        "domain": clean_domain,
        "ipv4_addresses": [],
        "ipv6_addresses": [],
    }

    try:
        ip_info = socket.getaddrinfo(clean_domain, None, socket.AF_INET)
        records["ipv4_addresses"] = list(dict.fromkeys([item[4][0] for item in ip_info]))
    except Exception:
        pass

    try:
        ip6_info = socket.getaddrinfo(clean_domain, None, socket.AF_INET6)
        records["ipv6_addresses"] = list(dict.fromkeys([item[4][0] for item in ip6_info]))
    except Exception:
        pass

    doc = [
        f"# 🛡️ DNS & Infrastructure Audit: `{clean_domain}`",
        f"- **IPv4 Addresses:** {', '.join(records['ipv4_addresses']) or 'None'}",
        f"- **IPv6 Addresses:** {', '.join(records['ipv6_addresses']) or 'None'}",
    ]

    return {
        "domain": clean_domain,
        "dns_records": records,
        "markdown": "\n".join(doc),
    }
