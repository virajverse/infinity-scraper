"""
Scraping and Crawling Engines for InfinityScrape.
"""

from infinity_scraper.engines.fast import fetch_url_fast
from infinity_scraper.engines.browser import fetch_url_browser
from infinity_scraper.engines.crawler import crawl_site

__all__ = ["fetch_url_fast", "fetch_url_browser", "crawl_site"]
