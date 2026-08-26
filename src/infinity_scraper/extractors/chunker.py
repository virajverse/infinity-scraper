"""
Semantic RAG Chunker & Token Optimizer for InfinityScrape.
Splits massive scraped pages into header-aware semantic chunks with index pointers for LLM embeddings and context efficiency.
"""

import re
from typing import Any, Dict, List, Optional


def chunk_content_for_rag(
    text_or_markdown: str,
    max_chunk_chars: int = 2000,
    overlap_chars: int = 200,
) -> Dict[str, Any]:
    """
    Split markdown into semantic chunks based on ATX headers (#, ##, ###) and paragraph breaks.
    """
    raw = text_or_markdown.strip()
    if not raw:
        return {"total_chunks": 0, "chunks": [], "markdown_preview": "Empty content."}

    # Split by headers while keeping headers
    sections = re.split(r"(?=(?:\n|^)#{1,4}\s+)", raw)
    chunks: List[Dict[str, Any]] = []

    current_chunk = ""
    current_header = "Introduction"

    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue

        # Check if section starts with header
        header_match = re.match(r"^#{1,4}\s+(.+)", sec)
        if header_match:
            current_header = header_match.group(1).split("\n")[0].strip()

        if len(current_chunk) + len(sec) < max_chunk_chars:
            current_chunk += ("\n\n" if current_chunk else "") + sec
        else:
            if current_chunk:
                chunks.append({
                    "chunk_id": len(chunks) + 1,
                    "section_header": current_header,
                    "character_count": len(current_chunk),
                    "estimated_tokens": int(len(current_chunk) / 4),
                    "text": current_chunk.strip(),
                })
            # Handle oversized individual section
            if len(sec) > max_chunk_chars:
                # Sub-chunk by paragraphs
                paragraphs = sec.split("\n\n")
                sub_chunk = ""
                for p in paragraphs:
                    if len(sub_chunk) + len(p) < max_chunk_chars:
                        sub_chunk += ("\n\n" if sub_chunk else "") + p
                    else:
                        if sub_chunk:
                            chunks.append({
                                "chunk_id": len(chunks) + 1,
                                "section_header": current_header,
                                "character_count": len(sub_chunk),
                                "estimated_tokens": int(len(sub_chunk) / 4),
                                "text": sub_chunk.strip(),
                            })
                        sub_chunk = p
                current_chunk = sub_chunk
            else:
                current_chunk = sec

    if current_chunk:
        chunks.append({
            "chunk_id": len(chunks) + 1,
            "section_header": current_header,
            "character_count": len(current_chunk),
            "estimated_tokens": int(len(current_chunk) / 4),
            "text": current_chunk.strip(),
        })

    doc = [
        f"# 🧩 Semantic RAG Chunker Summary",
        f"- **Original Length:** {len(raw):,} characters (~{int(len(raw)/4):,} tokens)",
        f"- **Total Semantic Chunks Generated:** {len(chunks)}",
        f"- **Max Chunk Size:** {max_chunk_chars} chars\n",
        "## Chunk Index Matrix\n",
    ]

    for c in chunks:
        doc.append(f"### Chunk #{c['chunk_id']} (`{c['section_header']}`) — ~{c['estimated_tokens']} Tokens")
        doc.append(f"> {c['text'][:150]}...\n")

    return {
        "total_chunks": len(chunks),
        "total_original_chars": len(raw),
        "estimated_total_tokens": int(len(raw) / 4),
        "chunks": chunks,
        "markdown": "\n".join(doc),
    }
