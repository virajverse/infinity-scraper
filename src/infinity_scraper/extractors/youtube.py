"""
Zero-GPU YouTube Transcript Extractor for InfinityScrape.
"""

import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)


def extract_youtube_video_id(url: str) -> Optional[str]:
    url = url.strip()
    if not url:
        return None

    if re.match(r"^[a-zA-Z0-9_-]{11}$", url):
        return url

    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    if "youtube.com" in hostname:
        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/shorts/")[1].split("/")[0].split("?")[0]
        elif parsed.path.startswith("/live/"):
            return parsed.path.split("/live/")[1].split("/")[0].split("?")[0]
        elif parsed.path == "/watch":
            qs = parse_qs(parsed.query)
            if "v" in qs and qs["v"]:
                return qs["v"][0]
    elif "youtu.be" in hostname:
        return parsed.path.lstrip("/").split("?")[0]

    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    if match:
        return match.group(1)

    return None


def format_seconds_to_timestamp(seconds: float) -> str:
    total_sec = int(seconds)
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    sec = total_sec % 60
    if hours > 0:
        return f"[{hours:02d}:{minutes:02d}:{sec:02d}]"
    return f"[{minutes:02d}:{sec:02d}]"


async def fetch_youtube_transcript(
    url: str,
    languages: Optional[List[str]] = None,
    with_timestamps: bool = True,
) -> Dict[str, Any]:
    video_id = extract_youtube_video_id(url)
    if not video_id:
        return {
            "url": url,
            "error": "Invalid YouTube URL or could not extract video ID.",
            "markdown": f"**Error:** Could not extract YouTube video ID from URL: `{url}`",
        }

    lang_prefs = languages or ["en", "hi", "en-US", "en-GB", "es", "fr", "de", "ja"]
    api = YouTubeTranscriptApi()

    try:
        entries = None
        try:
            entries = api.fetch(video_id, languages=lang_prefs)
        except Exception:
            try:
                transcript_list = api.list(video_id)
                for t in transcript_list:
                    entries = t.fetch()
                    break
            except Exception:
                pass

        if not entries:
            return {
                "url": url,
                "video_id": video_id,
                "markdown": f"No transcript or closed captions available for YouTube video `{video_id}`.",
            }

        formatted_lines = []
        full_text_list = []

        for item in entries:
            text = getattr(item, "text", "") if hasattr(item, "text") else item.get("text", "")
            start = getattr(item, "start", 0.0) if hasattr(item, "start") else item.get("start", 0.0)
            text = str(text).replace("\n", " ").strip()
            timestamp = format_seconds_to_timestamp(start)

            if with_timestamps:
                formatted_lines.append(f"- **{timestamp}** {text}")
            else:
                formatted_lines.append(text)
            full_text_list.append(text)

        doc_parts = [
            f"# YouTube Video Transcript",
            f"**Video URL:** https://www.youtube.com/watch?v={video_id}",
            f"**Video ID:** `{video_id}`",
            f"**Total Segments:** {len(formatted_lines)}\n",
            "## Transcript Content\n",
            "\n".join(formatted_lines),
        ]

        return {
            "url": url,
            "video_id": video_id,
            "total_segments": len(formatted_lines),
            "full_text": " ".join(full_text_list),
            "markdown": "\n".join(doc_parts),
        }

    except Exception as exc:
        logger.error(f"YouTube transcript extraction failed for {url}: {exc}")
        return {
            "url": url,
            "video_id": video_id,
            "error": str(exc),
            "markdown": f"**Failed to retrieve YouTube transcript for `{url}`:** {str(exc)}",
        }
