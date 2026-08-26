"""
Command-line interface (CLI) for InfinityScrape.
"""

import argparse
import asyncio
import sys

from infinity_scraper.engines.browser import fetch_url_browser
from infinity_scraper.engines.crawler import crawl_site
from infinity_scraper.engines.fast import fetch_url_fast
from infinity_scraper.extractors.pdf import extract_pdf_from_url
from infinity_scraper.osint.search import search_and_scrape_all, search_web_ddg


def main():
    parser = argparse.ArgumentParser(description="InfinityScrape: World-Class Web Scraping CLI by VirajVerse")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scrape_parser = subparsers.add_parser("scrape", help="Scrape a single URL")
    scrape_parser.add_argument("url", help="URL to scrape")
    scrape_parser.add_argument("--browser", action="store_true", help="Use Playwright headless browser")
    scrape_parser.add_argument("--selector", default=None, help="CSS selector to extract")
    scrape_parser.add_argument("--scroll", type=int, default=0, help="Scroll depth for infinite scroll")

    search_parser = subparsers.add_parser("search", help="Search the web")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--max", type=int, default=5, help="Max results")
    search_parser.add_argument("--scrape", action="store_true", help="Scrape top results")

    crawl_parser = subparsers.add_parser("crawl", help="Recursively crawl a site")
    crawl_parser.add_argument("url", help="Start URL")
    crawl_parser.add_argument("--pages", type=int, default=5, help="Max pages")
    crawl_parser.add_argument("--depth", type=int, default=2, help="Max depth")

    pdf_parser = subparsers.add_parser("pdf", help="Extract online PDF")
    pdf_parser.add_argument("url", help="PDF URL")
    pdf_parser.add_argument("--pages", type=int, default=20, help="Max pages")

    args = parser.parse_args()

    async def _run():
        if args.command == "scrape":
            if args.browser or args.scroll > 0:
                res = await fetch_url_browser(url=args.url, css_selector=args.selector, scroll_depth=args.scroll)
            else:
                res = await fetch_url_fast(url=args.url, css_selector=args.selector)
            print(res.format_output())

        elif args.command == "search":
            if args.scrape:
                res = await search_and_scrape_all(query=args.query, max_results=args.max)
                print(res["summary_markdown"])
            else:
                results = search_web_ddg(query=args.query, max_results=args.max)
                for r in results:
                    print(f"[{r['title']}]({r['url']})\n{r['snippet']}\n")

        elif args.command == "crawl":
            res = await crawl_site(start_url=args.url, max_pages=args.pages, max_depth=args.depth)
            print(res["aggregated_markdown"])

        elif args.command == "pdf":
            res = await extract_pdf_from_url(url=args.url, max_pages=args.pages)
            print(res["markdown"])

    asyncio.run(_run())


if __name__ == "__main__":
    main()
