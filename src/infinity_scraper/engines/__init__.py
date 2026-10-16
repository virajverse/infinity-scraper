"""
Scraping and Crawling Engines for InfinityScrape.
"""

from infinity_scraper.engines.fast import fetch_url_fast
from infinity_scraper.engines.browser import fetch_url_browser
from infinity_scraper.engines.crawler import crawl_site
from infinity_scraper.engines.sitemap import fetch_and_parse_sitemap, discover_website_sitemaps, parse_sitemap_xml_data
from infinity_scraper.engines.diff import compute_page_diff

__all__ = [
    "fetch_url_fast",
    "fetch_url_browser",
    "crawl_site",
    "fetch_and_parse_sitemap",
    "discover_website_sitemaps",
    "parse_sitemap_xml_data",
    "compute_page_diff",
]

