"""
Network, Domain, SSL, Tech Stack & Username Reconnaissance for InfinityScrape.
"""

import asyncio
import json
import logging
import re
import socket
import ssl
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx

from infinity_scraper.config import get_stealth_headers

logger = logging.getLogger(__name__)

OSINT_PLATFORMS = {
    "GitHub": "https://github.com/{username}",
    "GitLab": "https://gitlab.com/{username}",
    "StackOverflow": "https://stackoverflow.com/users/{username}",
    "HackerNews": "https://news.ycombinator.com/user?id={username}",
    "Kaggle": "https://www.kaggle.com/{username}",
    "HuggingFace": "https://huggingface.co/{username}",
    "LeetCode": "https://leetcode.com/{username}",
    "Codeforces": "https://codeforces.com/profile/{username}",
    "HackerRank": "https://www.hackerrank.com/{username}",
    "Devpost": "https://devpost.com/{username}",
    "PyPI": "https://pypi.org/user/{username}/",
    "DockerHub": "https://hub.docker.com/u/{username}",
    "NPM": "https://www.npmjs.com/~{username}",
    "SourceForge": "https://sourceforge.net/u/{username}/profile/",
    "Dev.to": "https://dev.to/{username}",
    "Medium": "https://medium.com/@{username}",
    "Substack": "https://{username}.substack.com",
    "Hashnode": "https://hashnode.com/@{username}",
    "ResearchGate": "https://www.researchgate.net/profile/{username}",
    "GoogleScholar": "https://scholar.google.com/citations?user={username}",
    "Dribbble": "https://dribbble.com/{username}",
    "Behance": "https://www.behance.net/{username}",
    "Pinterest": "https://www.pinterest.com/{username}/",
    "Reddit": "https://www.reddit.com/user/{username}",
    "Telegram": "https://t.me/{username}",
    "Keybase": "https://keybase.io/{username}",
}

TECH_SIGNATURES = {
    "Frameworks & Libraries": {
        "React": [r"react(?:\.production|\.development)?\.js", r"_next/static", r"data-reactroot", r"react-dom"],
        "Next.js": [r"_next/static", r"__NEXT_DATA__", r"next/dist"],
        "Vue.js": [r"vue(?:\.runtime|\.esm|\.min)?\.js", r"data-v-[a-f0-9]+", r"__vue__", r"nuxt"],
        "Nuxt.js": [r"_nuxt/", r"__NUXT__"],
        "Angular": [r"ng-version", r"angular(?:\.min)?\.js", r"ng-app"],
        "Svelte / SvelteKit": [r"svelte", r"__svelte"],
        "jQuery": [r"jquery(?:\.min)?\.js", r"jquery\/[0-9]"],
        "Tailwind CSS": [r"tailwind", r"cdn\.tailwindcss\.com"],
        "Bootstrap": [r"bootstrap(?:\.min)?\.(?:js|css)"],
        "Alpine.js": [r"alpine(?:\.min)?\.js", r"x-data"],
    },
    "Content Management Systems (CMS)": {
        "WordPress": [r"/wp-content/", r"/wp-includes/", r"wp-json", r"name=\"generator\" content=\"WordPress"],
        "Shopify": [r"cdn\.shopify\.com", r"Shopify\.theme", r"myshopify\.com"],
        "Webflow": [r"webflow(?:\.min)?\.js", r"data-wf-page"],
        "Ghost": [r"ghost\.org", r"name=\"generator\" content=\"Ghost"],
        "Wix": [r"wix\.com", r"_wix_"],
        "Drupal": [r"Drupal\.settings", r"name=\"generator\" content=\"Drupal"],
        "Joomla": [r"name=\"generator\" content=\"Joomla"],
    },
    "Servers, CDNs & Hosting": {
        "Cloudflare": [r"cloudflare", r"__cf_chl", r"cf-ray", r"cf-cache-status"],
        "Vercel": [r"vercel", r"x-vercel-id"],
        "Netlify": [r"netlify", r"x-nf-request-id"],
        "AWS CloudFront": [r"cloudfront\.net", r"x-amz-cf-id"],
        "Fastly": [r"fastly", r"x-fastly-request-id"],
        "Nginx": [r"nginx"],
        "Apache": [r"apache"],
    },
    "Analytics & Tracking": {
        "Google Analytics / Tag Manager": [r"googletagmanager\.com", r"google-analytics\.com", r"gtag\(", r"ga\("],
        "Meta / Facebook Pixel": [r"connect\.facebook\.net", r"fbq\("],
        "Hotjar": [r"static\.hotjar\.com", r"_hjSettings"],
        "Mixpanel": [r"cdn\.mxpnl\.com", r"mixpanel\.init"],
        "Segment": [r"cdn\.segment\.com", r"analytics\.load"],
    },
}


def clean_hostname(target: str) -> str:
    target = target.strip()
    if target.startswith(("http://", "https://")):
        return urlparse(target).netloc.split(":")[0]
    return target.split("/")[0].split(":")[0]


def get_ssl_cert_info(hostname: str, port: int = 443, timeout: float = 5.0) -> Dict[str, Any]:
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                if not cert:
                    return {"ssl_available": False, "error": "No certificate returned"}

                subject = dict(x[0] for x in cert.get("subject", ()))
                issuer = dict(x[0] for x in cert.get("issuer", ()))
                sans = [entry[1] for entry in cert.get("subjectAltName", ()) if entry[0] == "DNS"]

                return {
                    "ssl_available": True,
                    "subject": subject.get("commonName") or subject.get("organizationName", ""),
                    "issuer": issuer.get("organizationName") or issuer.get("commonName", ""),
                    "valid_from": cert.get("notBefore", ""),
                    "valid_until": cert.get("notAfter", ""),
                    "sans_count": len(sans),
                    "sample_sans": sans[:10],
                }
    except Exception as exc:
        return {"ssl_available": False, "error": str(exc)}


async def fetch_rdap_whois(domain: str) -> Dict[str, Any]:
    clean_domain = clean_hostname(domain)
    rdap_url = f"https://rdap.org/domain/{clean_domain}"
    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            resp = await client.get(rdap_url)
            if resp.status_code == 200:
                data = resp.json()
                events = {e.get("eventAction"): e.get("eventDate") for e in data.get("events", [])}
                nameservers = [ns.get("ldhName") for ns in data.get("nameservers", []) if ns.get("ldhName")]

                return {
                    "domain": data.get("ldhName", clean_domain),
                    "status": data.get("status", []),
                    "registrar": data.get("entities", [{}])[0].get("vcardArray", [None, [["fn", {}, "text", "Unknown"]]])[1][0][3] if data.get("entities") else "Unknown",
                    "registration_date": events.get("registration", "Unknown"),
                    "expiration_date": events.get("expiration", "Unknown"),
                    "last_changed": events.get("last changed", "Unknown"),
                    "nameservers": nameservers,
                }
    except Exception as exc:
        logger.debug(f"RDAP WHOIS lookup error for {domain}: {exc}")
    return {"domain": clean_domain, "info": "RDAP WHOIS record not available directly"}


async def fetch_ip_intel(ip_or_host: str) -> Dict[str, Any]:
    host = clean_hostname(ip_or_host)
    ip_addr = host
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host):
        try:
            ip_addr = socket.gethostbyname(host)
        except Exception as exc:
            return {"target": host, "error": f"DNS resolution failed: {exc}"}

    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(f"http://ip-api.com/json/{ip_addr}?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query")
            if resp.status_code == 200:
                return resp.json()
    except Exception as exc:
        logger.debug(f"IP intel error: {exc}")

    return {"query": ip_addr, "status": "fail"}


async def detect_website_tech(url: str) -> Dict[str, Any]:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    headers = get_stealth_headers(url)
    detected: Dict[str, List[str]] = {cat: [] for cat in TECH_SIGNATURES}
    server_headers: Dict[str, str] = {}

    try:
        async with httpx.AsyncClient(headers=headers, timeout=12.0, follow_redirects=True, verify=False) as client:
            resp = await client.get(url)
            html = resp.text
            resp_headers = resp.headers

            for h in ["server", "x-powered-by", "x-generator", "x-served-by", "cf-ray", "x-vercel-id"]:
                if h in resp_headers:
                    server_headers[h] = resp_headers[h]

            content_to_check = html + " " + json.dumps(dict(resp_headers))

            for category, tools in TECH_SIGNATURES.items():
                for tool_name, patterns in tools.items():
                    if any(re.search(pat, content_to_check, re.IGNORECASE) for pat in patterns):
                        detected[category].append(tool_name)

            cleaned_detected = {k: v for k, v in detected.items() if v}

            return {
                "url": url,
                "status_code": resp.status_code,
                "server_headers": server_headers,
                "tech_stack": cleaned_detected,
            }
    except Exception as exc:
        return {"url": url, "error": str(exc), "tech_stack": {}}


async def check_username_osint(username: str, concurrency: int = 8) -> Dict[str, Any]:
    username = username.strip().lstrip("@")
    if not username:
        return {"username": username, "profiles_found": []}

    semaphore = asyncio.Semaphore(concurrency)
    found_profiles = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    async def _check_platform(name: str, url_template: str):
        target_url = url_template.format(username=username)
        async with semaphore:
            try:
                async with httpx.AsyncClient(headers=headers, timeout=6.0, follow_redirects=False) as client:
                    resp = await client.get(target_url)
                    if resp.status_code in (200, 301, 302):
                        if "not found" not in resp.text.lower() and "doesn't exist" not in resp.text.lower():
                            found_profiles.append({
                                "platform": name,
                                "profile_url": target_url,
                                "status": "Found",
                            })
            except Exception:
                pass

    tasks = [_check_platform(p, u) for p, u in OSINT_PLATFORMS.items()]
    await asyncio.gather(*tasks)

    return {
        "username": username,
        "total_platforms_scanned": len(OSINT_PLATFORMS),
        "total_found": len(found_profiles),
        "profiles": found_profiles,
    }
