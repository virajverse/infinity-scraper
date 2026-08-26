"""
Online PDF Extractor for InfinityScrape.
"""

import io
import logging
from typing import Any, Dict, List, Optional

import httpx
from pypdf import PdfReader
import primp

from infinity_scraper.config import get_stealth_headers

logger = logging.getLogger(__name__)


async def extract_pdf_from_url(
    url: str,
    max_pages: Optional[int] = None,
    timeout: int = 45,
    proxy: Optional[str] = None,
) -> Dict[str, Any]:
    headers = get_stealth_headers(url)
    pdf_bytes = None
    try:
        try:
            client = primp.AsyncClient(
                impersonate="random",
                proxy=proxy,
                follow_redirects=True,
                timeout=timeout,
                verify=False,
            )
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                pdf_bytes = resp.content
        except Exception:
            pass

        if not pdf_bytes:
            async with httpx.AsyncClient(
                headers=headers,
                proxy=proxy,
                follow_redirects=True,
                timeout=timeout,
                verify=False,
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                pdf_bytes = resp.content

        stream = io.BytesIO(pdf_bytes)
        reader = PdfReader(stream)
        num_pages = len(reader.pages)

        pages_to_read = min(num_pages, max_pages) if max_pages else num_pages
        extracted_pages: List[Dict[str, Any]] = []
        full_text_parts: List[str] = []

        for page_idx in range(pages_to_read):
            page = reader.pages[page_idx]
            page_text = page.extract_text() or ""
            extracted_pages.append({
                "page_number": page_idx + 1,
                "text": page_text.strip(),
            })
            if page_text.strip():
                full_text_parts.append(f"### Page {page_idx + 1}\n\n{page_text.strip()}")

        meta = {}
        if reader.metadata:
            for k, v in reader.metadata.items():
                if v and isinstance(v, (str, int, float)):
                    clean_k = str(k).replace("/", "")
                    meta[clean_k] = str(v)

        doc_title = meta.get("Title") or url.split("/")[-1].split("?")[0] or "PDF Document"

        markdown_output = [
            f"# {doc_title}",
            f"**Source URL:** {url}",
            f"**Total Pages:** {num_pages} (Extracted: {pages_to_read})\n",
        ]
        if meta:
            markdown_output.append("### PDF Metadata\n")
            for k, v in meta.items():
                markdown_output.append(f"- **{k}:** {v}")
            markdown_output.append("\n")

        markdown_output.append("## Content\n")
        markdown_output.extend(full_text_parts)

        return {
            "title": doc_title,
            "url": url,
            "total_pages": num_pages,
            "extracted_pages_count": pages_to_read,
            "metadata": meta,
            "markdown": "\n\n".join(markdown_output),
            "pages": extracted_pages,
        }

    except Exception as exc:
        logger.error(f"Failed to extract PDF from {url}: {exc}")
        return {
            "title": "PDF Extraction Failed",
            "url": url,
            "error": str(exc),
            "markdown": f"**Failed to extract PDF from {url}:** {str(exc)}",
            "pages": [],
        }
