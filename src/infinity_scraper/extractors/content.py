"""
Content Extraction and Formatting Pipeline for InfinityScrape.
Extracts clean Markdown, structured fields, tables, metadata, and links from raw HTML.
"""

import json
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import trafilatura
from markdownify import markdownify as md

from infinity_scraper.config import AD_AND_POPUP_SELECTORS


class ExtractionResult:
    def __init__(
        self,
        url: str,
        title: str = "",
        content_markdown: str = "",
        content_text: str = "",
        raw_html: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        tables: Optional[List[Dict[str, Any]]] = None,
        links: Optional[List[Dict[str, str]]] = None,
        images: Optional[List[Dict[str, str]]] = None,
        structured_data: Optional[Dict[str, Any]] = None,
        status_code: int = 200,
        content_type: str = "text/html",
    ):
        self.url = url
        self.title = title
        self.content_markdown = content_markdown
        self.content_text = content_text
        self.raw_html = raw_html
        self.metadata = metadata or {}
        self.tables = tables or []
        self.links = links or []
        self.images = images or []
        self.structured_data = structured_data or {}
        self.status_code = status_code
        self.content_type = content_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "content_markdown": self.content_markdown,
            "metadata": self.metadata,
            "tables": self.tables,
            "links_count": len(self.links),
            "images_count": len(self.images),
            "structured_data": self.structured_data,
            "status_code": self.status_code,
        }

    def format_output(
        self,
        include_metadata: bool = True,
        include_links: bool = False,
        include_images: bool = False,
        include_tables: bool = True,
        max_chars: Optional[int] = None,
    ) -> str:
        parts = []
        if self.title:
            parts.append(f"# {self.title}\n")
        parts.append(f"**Source URL:** {self.url}\n")

        if include_metadata and self.metadata:
            meta_lines = []
            for k, v in self.metadata.items():
                if v and isinstance(v, (str, int, float)) and len(str(v)) < 300:
                    meta_lines.append(f"- **{k}:** {v}")
            if meta_lines:
                parts.append("### Metadata\n" + "\n".join(meta_lines) + "\n")

        if self.content_markdown:
            parts.append("### Content\n" + self.content_markdown.strip() + "\n")
        elif self.content_text:
            parts.append("### Text Content\n" + self.content_text.strip() + "\n")

        if include_tables and self.tables:
            parts.append("### Extracted Tables\n")
            for i, tbl in enumerate(self.tables, 1):
                if tbl.get("markdown"):
                    parts.append(f"#### Table {i}\n{tbl['markdown']}\n")

        if include_images and self.images:
            parts.append("### Images\n")
            for img in self.images[:30]:
                alt = img.get("alt", "image")
                src = img.get("src", "")
                if src:
                    parts.append(f"- ![{alt}]({src})")
            parts.append("\n")

        if include_links and self.links:
            parts.append("### Links Found\n")
            for link in self.links[:50]:
                text = link.get("text", "").strip() or "Link"
                href = link.get("href", "")
                if href:
                    parts.append(f"- [{text}]({href})")
            parts.append("\n")

        full_text = "\n".join(parts)
        if max_chars and len(full_text) > max_chars:
            full_text = full_text[:max_chars] + f"\n\n... [Content truncated at {max_chars} characters.]"
        return full_text


def extract_metadata(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    meta = {}
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        meta["title"] = title_tag.string.strip()

    for tag in soup.find_all("meta"):
        name = tag.get("name") or tag.get("property") or tag.get("itemprop")
        content = tag.get("content")
        if name and content:
            name_lower = name.lower()
            if name_lower in ["description", "og:description", "twitter:description"]:
                meta.setdefault("description", content.strip())
            elif name_lower in ["keywords", "news_keywords"]:
                meta.setdefault("keywords", content.strip())
            elif name_lower in ["author", "article:author", "og:article:author"]:
                meta.setdefault("author", content.strip())
            elif name_lower in ["og:title", "twitter:title"]:
                meta.setdefault("og_title", content.strip())
            elif name_lower in ["og:site_name"]:
                meta.setdefault("site_name", content.strip())
            elif name_lower in ["article:published_time", "og:published_time", "date"]:
                meta.setdefault("published_time", content.strip())
            elif name_lower in ["og:image", "twitter:image"]:
                meta.setdefault("image", urljoin(url, content.strip()))

    json_ld_list = []
    for script in soup.find_all("script", type="application/ld+json"):
        if script.string:
            try:
                data = json.loads(script.string.strip())
                json_ld_list.append(data)
            except Exception:
                pass
    if json_ld_list:
        meta["json_ld"] = json_ld_list

    return meta


def extract_tables(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    extracted_tables = []
    tables = soup.find_all("table")

    for tbl in tables:
        rows_data = []
        for tr in tbl.find_all("tr"):
            cells = [cell.get_text(strip=True) for cell in tr.find_all(["th", "td"])]
            if any(cells):
                rows_data.append(cells)

        if not rows_data or len(rows_data) < 2:
            continue

        header = rows_data[0]
        max_cols = max(len(r) for r in rows_data)
        padded_header = header + [""] * (max_cols - len(header))
        header_line = "| " + " | ".join(padded_header) + " |"
        separator_line = "| " + " | ".join(["---"] * max_cols) + " |"

        body_lines = []
        for r in rows_data[1:]:
            padded_row = r + [""] * (max_cols - len(r))
            body_lines.append("| " + " | ".join(padded_row) + " |")

        markdown_table = "\n".join([header_line, separator_line] + body_lines)
        extracted_tables.append({
            "rows": rows_data,
            "markdown": markdown_table,
            "num_rows": len(rows_data),
            "num_cols": max_cols,
        })

    return extracted_tables


def extract_links_and_images(soup: BeautifulSoup, base_url: str):
    links = []
    seen_hrefs = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        if href.startswith(("http://", "https://")) and href not in seen_hrefs:
            seen_hrefs.add(href)
            links.append({"text": a.get_text(strip=True), "href": href})

    images = []
    seen_srcs = set()
    for img in soup.find_all("img", src=True):
        src = urljoin(base_url, img["src"])
        if src.startswith(("http://", "https://", "data:image")) and src not in seen_srcs:
            seen_srcs.add(src)
            images.append({"alt": img.get("alt", "").strip(), "src": src})

    return links, images


def clean_html_for_markdown(soup: BeautifulSoup, strip_ads: bool = True) -> BeautifulSoup:
    soup_copy = BeautifulSoup(str(soup), "html.parser")

    for tag in soup_copy([
        "script", "style", "noscript", "iframe", "svg", "form",
        "header", "footer", "nav", "aside"
    ]):
        tag.decompose()

    if strip_ads:
        for sel in AD_AND_POPUP_SELECTORS:
            try:
                for el in soup_copy.select(sel):
                    el.decompose()
            except Exception:
                pass

        clutter_patterns = re.compile(
            r"(cookie|banner|modal|popup|advertisement|newsletter|ad-container|ad-box|disclaimer|share-buttons|sponsor|promoted|taboola|outbrain)",
            re.I,
        )
        for element in soup_copy.find_all(attrs={"class": clutter_patterns}):
            element.decompose()
        for element in soup_copy.find_all(attrs={"id": clutter_patterns}):
            element.decompose()

    for hidden in soup_copy.find_all(style=re.compile(r"display:\s*none|visibility:\s*hidden", re.I)):
        hidden.decompose()

    return soup_copy


def parse_html_content(
    html: str,
    url: str,
    css_selector: Optional[str] = None,
    xpath: Optional[str] = None,
    status_code: int = 200,
    strip_ads: bool = True,
) -> ExtractionResult:
    soup = BeautifulSoup(html, "lxml" if "lxml" in BeautifulSoup.__dict__ else "html.parser")
    meta = extract_metadata(soup, url)
    title = meta.get("title") or meta.get("og_title") or ""

    if css_selector:
        selected_elements = soup.select(css_selector)
        if selected_elements:
            combined_html = "\n".join(str(el) for el in selected_elements)
            targeted_soup = BeautifulSoup(combined_html, "html.parser")
            clean_soup = clean_html_for_markdown(targeted_soup, strip_ads=strip_ads)
            md_content = md(str(clean_soup), heading_style="ATX", strip=["img", "script"])
            text_content = clean_soup.get_text(separator="\n", strip=True)
            tables = extract_tables(targeted_soup)
            links, images = extract_links_and_images(targeted_soup, url)
            return ExtractionResult(
                url=url,
                title=title,
                content_markdown=md_content,
                content_text=text_content,
                raw_html=combined_html,
                metadata=meta,
                tables=tables,
                links=links,
                images=images,
                status_code=status_code,
            )

    trafilatura_result = trafilatura.extract(
        html,
        url=url,
        output_format="markdown",
        include_links=True,
        include_images=True,
        include_tables=True,
        include_formatting=True,
        favor_recall=True,
        no_fallback=False,
    )

    clean_soup = clean_html_for_markdown(soup, strip_ads=strip_ads)
    tables = extract_tables(soup)
    links, images = extract_links_and_images(soup, url)

    if trafilatura_result and len(trafilatura_result.strip()) > 100:
        content_markdown = trafilatura_result.strip()
    else:
        content_markdown = md(str(clean_soup), heading_style="ATX", strip=["script", "style"])

    text_content = clean_soup.get_text(separator="\n", strip=True)

    return ExtractionResult(
        url=url,
        title=title,
        content_markdown=content_markdown,
        content_text=text_content,
        raw_html=html,
        metadata=meta,
        tables=tables,
        links=links,
        images=images,
        status_code=status_code,
    )
