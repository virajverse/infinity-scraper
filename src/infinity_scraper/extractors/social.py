"""
Social Discussion Thread & RSS/Atom Feed Parsers for InfinityScrape.
Supports Reddit, HackerNews, and Substack/Blog RSS feeds into structured Markdown.
"""

import logging
import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx

from infinity_scraper.config import get_stealth_headers

logger = logging.getLogger(__name__)


async def extract_reddit_thread(
    url: str,
    max_comments: int = 25,
) -> Dict[str, Any]:
    """
    Extract full Reddit post content, score, author, and top nested comment tree into clean dialogue Markdown.
    """
    clean_url = url.strip().split("?")[0].rstrip("/")
    json_url = f"{clean_url}.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    }

    try:
        async with httpx.AsyncClient(headers=headers, timeout=12.0, follow_redirects=True) as client:
            resp = await client.get(json_url)
            if resp.status_code == 200:
                data = resp.json()
                post_data = data[0]["data"]["children"][0]["data"]
                comments_data = data[1]["data"]["children"]

                title = post_data.get("title", "Reddit Post")
                author = post_data.get("author", "anonymous")
                subreddit = post_data.get("subreddit_name_prefixed", "")
                score = post_data.get("score", 0)
                selftext = post_data.get("selftext", "").strip()
                upvote_ratio = post_data.get("upvote_ratio", 1.0)

                doc = [
                    f"# 💬 Reddit Thread: {title}",
                    f"- **Subreddit:** {subreddit} | **Author:** `u/{author}`",
                    f"- **Upvotes:** `{score}` (Ratio: {int(upvote_ratio * 100)}%) | **URL:** [{clean_url}]({clean_url})\n",
                ]

                if selftext:
                    doc.append(f"### Post Body\n{selftext}\n")

                doc.append(f"### Top Community Comments ({min(len(comments_data), max_comments)} shown)\n")

                comments_list = []
                for idx, c in enumerate(comments_data[:max_comments], 1):
                    c_info = c.get("data", {})
                    c_body = c_info.get("body", "").strip()
                    c_author = c_info.get("author", "user")
                    c_score = c_info.get("score", 0)

                    if c_body:
                        doc.append(f"**{idx}. `u/{c_author}`** (`+{c_score}`):")
                        doc.append(f"> {c_body.replace(chr(10), ' ')}\n")
                        comments_list.append({"author": c_author, "score": c_score, "body": c_body})

                return {
                    "url": clean_url,
                    "title": title,
                    "subreddit": subreddit,
                    "author": author,
                    "score": score,
                    "comments_count": len(comments_list),
                    "comments": comments_list,
                    "markdown": "\n".join(doc),
                }
    except Exception as exc:
        logger.error(f"Reddit thread extraction failed for {url}: {exc}")

    return {
        "url": url,
        "error": "Failed to parse Reddit thread.",
        "markdown": f"Could not extract Reddit thread from `{url}`.",
    }


async def extract_rss_feed(
    feed_url: str,
    max_items: int = 10,
) -> Dict[str, Any]:
    """
    Parse an RSS or Atom XML feed (blogs, Substacks, news feeds) into structured Markdown updates.
    """
    clean_url = feed_url.strip()
    headers = get_stealth_headers(clean_url)

    try:
        async with httpx.AsyncClient(headers=headers, timeout=12.0, follow_redirects=True, verify=False) as client:
            resp = await client.get(clean_url)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                feed_title = "RSS Feed"
                items_extracted = []

                # RSS 2.0
                channel = root.find("channel")
                if channel is not None:
                    feed_title = channel.findtext("title", "RSS Feed")
                    for item in channel.findall("item")[:max_items]:
                        title = item.findtext("title", "No Title").strip()
                        link = item.findtext("link", "").strip()
                        pub_date = item.findtext("pubDate", "").strip()
                        desc = item.findtext("description", "").strip()
                        clean_desc = re.sub(r"<[^>]+>", "", desc).strip()
                        items_extracted.append({
                            "title": title,
                            "link": link,
                            "date": pub_date,
                            "summary": clean_desc[:300],
                        })
                # Atom Feed
                else:
                    feed_title = root.findtext("{http://www.w3.org/2005/Atom}title", "Atom Feed")
                    for entry in root.findall("{http://www.w3.org/2005/Atom}entry")[:max_items]:
                        title = entry.findtext("{http://www.w3.org/2005/Atom}title", "No Title").strip()
                        link_el = entry.find("{http://www.w3.org/2005/Atom}link")
                        link = link_el.attrib.get("href", "") if link_el is not None else ""
                        pub_date = entry.findtext("{http://www.w3.org/2005/Atom}updated", "").strip()
                        summary = entry.findtext("{http://www.w3.org/2005/Atom}summary", "").strip()
                        clean_summary = re.sub(r"<[^>]+>", "", summary).strip()
                        items_extracted.append({
                            "title": title,
                            "link": link,
                            "date": pub_date,
                            "summary": clean_summary[:300],
                        })

                doc = [
                    f"# 📰 Feed Digest: {feed_title}",
                    f"- **Feed URL:** [{clean_url}]({clean_url})",
                    f"- **Articles Extracted:** {len(items_extracted)}\n",
                    "## Recent Articles\n",
                ]

                for idx, it in enumerate(items_extracted, 1):
                    doc.append(f"### {idx}. [{it['title']}]({it['link']})")
                    if it["date"]:
                        doc.append(f"*Published: {it['date']}*")
                    if it["summary"]:
                        doc.append(f"> {it['summary']}\n")

                return {
                    "feed_url": clean_url,
                    "feed_title": feed_title,
                    "items_count": len(items_extracted),
                    "items": items_extracted,
                    "markdown": "\n".join(doc),
                }
    except Exception as exc:
        logger.error(f"RSS Feed parsing failed for {feed_url}: {exc}")

    return {
        "feed_url": feed_url,
        "error": "Failed to parse RSS feed",
        "markdown": f"Could not parse RSS/Atom feed from `{feed_url}`.",
    }
