"""
Configuration, constants, headers, and anti-bot profiles for InfinityScrape.
"""

import os
import random
from typing import Dict, List, Optional, Set
from pydantic import BaseModel

DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_MAX_PAGES = 10
DEFAULT_MAX_DEPTH = 2
DEFAULT_MAX_CHARS = 100_000

USER_AGENTS = [
    # Chrome Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    # Chrome Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    # Edge Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
    # Safari Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
    # Firefox Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
]

PRIMP_IMPERSONATE_PROFILES = [
    "chrome_131",
    "chrome_130",
    "chrome_129",
    "safari_18",
    "safari_17_5",
    "edge_131",
    "firefox_133",
]

# Network-level Ad and Tracking Domains to block in Playwright
AD_TRACKING_DOMAINS: Set[str] = {
    "doubleclick.net",
    "googlesyndication.com",
    "googleadservices.com",
    "adnxs.com",
    "criteo.com",
    "outbrain.com",
    "taboola.com",
    "rubiconproject.com",
    "pubmatic.com",
    "openx.net",
    "casalemedia.com",
    "facebook.net",
    "connect.facebook.net",
    "adroll.com",
    "amazon-adsystem.com",
    "scorecardresearch.com",
    "quantserve.com",
    "hotjar.com",
    "clarity.ms",
    "segment.io",
    "ads-twitter.com",
    "analytics.tiktok.com",
    "adservice.google.com",
    "advertising.com",
    "media.net",
    "moatads.com",
    "serving-sys.com",
    "smartadserver.com",
    "teads.tv",
    "yieldmo.com",
    "bidswitch.net",
    "adsrvr.org",
    "adtechus.com",
    "adsystem.com",
    "adthrive.com",
    "mediavine.com",
}

# CSS Selectors for Ads, Cookie Banners, Paywall Modals, Newsletter Popups
AD_AND_POPUP_SELECTORS: List[str] = [
    # General Ads
    ".ad", ".ads", ".advert", ".advertisement", ".ad-container", ".ad-box", ".ad-wrapper",
    ".ad-banner", ".ad-slot", ".ad-unit", ".google-ad", ".dfp-ad", ".adsbygoogle",
    "[id^='google_ads']", "[id^='div-gpt-ad']", "[class*='sponsored']", "[class*='promoted']",
    # Cookie Banners & CMPs
    "#onetrust-banner-sdk", "#onetrust-consent-sdk", ".cookie-banner", ".cookie-consent",
    ".cookie-notice", ".cookie-popup", "#CybotCookiebotDialog", ".qc-cmp2-container",
    ".didomi-popup-container", "#truste-consent-track", "#usercentrics-root",
    # Modals, Overlays, and Newsletter Prompts
    ".modal-backdrop", ".popup-overlay", ".newsletter-popup", ".subscribe-modal",
    ".paywall-overlay", ".email-gate", ".lead-capture-modal", ".floating-banner",
    # Social Share Floating Bars & Sticky Footers
    ".social-share-fixed", ".share-bar-sticky", ".sticky-footer-ad", ".floating-footer-banner",
]


def get_random_user_agent() -> str:
    return random.choice(USER_AGENTS)

def get_random_impersonate_profile() -> str:
    return random.choice(PRIMP_IMPERSONATE_PROFILES)

def get_stealth_headers(url: Optional[str] = None, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Sec-Ch-Ua": '"Not A(Brand";v="8", "Chromium";v="133", "Google Chrome";v="133"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "Priority": "u=0, i",
    }
    if url:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        headers["Host"] = parsed.netloc

    if custom_headers:
        headers.update(custom_headers)

    return headers



def get_rotating_proxy(custom_proxy: Optional[str] = None) -> Optional[str]:

    """Returns a custom proxy if provided, or rotates through PROXY_POOL in environment."""
    if custom_proxy and custom_proxy.strip():
        return custom_proxy.strip()
    
    proxy_pool_env = os.getenv("PROXY_POOL", os.getenv("PROXIES", "")).strip()
    if proxy_pool_env:
        proxies = [p.strip() for p in proxy_pool_env.split(",") if p.strip()]
        if proxies:
            return random.choice(proxies)
            
    https_proxy = os.getenv("HTTPS_PROXY", os.getenv("HTTP_PROXY", "")).strip()
    if https_proxy:
        return https_proxy
        
    return None

