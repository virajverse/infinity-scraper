"""
Temporal Page Diff & Change Radar Engine for InfinityScrape.
Compares historical vs live webpages, detecting pricing changes, removed features,
and new additions with semantic heuristic categorization.
"""

import difflib
import re
from typing import Any, Dict, List


def compute_page_diff(
    old_content: str,
    new_content: str,
    label_old: str = "Historical",
    label_new: str = "Live"
) -> Dict[str, Any]:
    """
    Computes a precise line-by-line and semantic difference between two versions of text/markdown.
    Detects pricing movements, new/removed headings, and content similarity percentage.
    """
    old_lines = [line.strip() for line in old_content.splitlines() if line.strip()]
    new_lines = [line.strip() for line in new_content.splitlines() if line.strip()]

    # Sequence Matcher for Overall Similarity Ratio
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
    similarity_ratio = round(matcher.ratio() * 100, 2)

    # Line-by-line Unified Diff
    diff_generator = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=label_old,
        tofile=label_new,
        lineterm=""
    )

    diff_lines = list(diff_generator)
    added_lines = [l[1:].strip() for l in diff_lines if l.startswith("+") and not l.startswith("+++")]
    removed_lines = [l[1:].strip() for l in diff_lines if l.startswith("-") and not l.startswith("---")]

    # Semantic Heuristic: Pricing Changes
    price_pattern = re.compile(r"[\$€£₹]\s*\d+(?:[.,]\d+)?|\b\d+(?:[.,]\d+)?\s*(?:USD|INR|EUR|GBP)\b")
    old_prices = set(price_pattern.findall(old_content))
    new_prices = set(price_pattern.findall(new_content))

    added_prices = list(new_prices - old_prices)
    dropped_prices = list(old_prices - new_prices)

    # Semantic Heuristic: Heading Changes (# Heading)
    heading_pattern = re.compile(r"^\s*#{1,4}\s+(.+)$", re.MULTILINE)
    old_headings = set(h.strip() for h in heading_pattern.findall(old_content))
    new_headings = set(h.strip() for h in heading_pattern.findall(new_content))


    added_headings = list(new_headings - old_headings)
    removed_headings = list(old_headings - new_headings)

    # Markdown Summary
    md_lines = [
        f"### ⏱️ Temporal Page Diff & Change Radar",
        f"- **Similarity**: `{similarity_ratio}%` identical",
        f"- **Lines Added**: `{len(added_lines)}` | **Lines Removed**: `{len(removed_lines)}`",
        ""
    ]

    if added_prices or dropped_prices:
        md_lines.append("#### 💳 Pricing Movements Detected:")
        if added_prices:
            md_lines.append(f"- **New Price Points**: {', '.join(added_prices)}")
        if dropped_prices:
            md_lines.append(f"- **Discontinued / Shifted Prices**: {', '.join(dropped_prices)}")
        md_lines.append("")

    if added_headings or removed_headings:
        md_lines.append("#### 📑 Structural / Feature Headings:")
        if added_headings:
            md_lines.append(f"- **New Features/Sections**: {', '.join(added_headings)}")
        if removed_headings:
            md_lines.append(f"- **Removed Sections**: {', '.join(removed_headings)}")
        md_lines.append("")

    if added_lines or removed_lines:
        md_lines.append("#### 📝 Top Diff Snippets:")
        md_lines.append("```diff")
        for line in diff_lines[:30]:  # Limit to top 30 diff lines
            md_lines.append(line)
        if len(diff_lines) > 30:
            md_lines.append(f"... ({len(diff_lines) - 30} more lines in full diff)")
        md_lines.append("```")
    else:
        md_lines.append("*Both pages are 100% identical. Zero content drift detected.*")

    return {
        "status": "success",
        "similarity_percentage": similarity_ratio,
        "total_added_lines": len(added_lines),
        "total_removed_lines": len(removed_lines),
        "pricing_drift": {
            "new_prices": added_prices,
            "discontinued_prices": dropped_prices
        },
        "heading_drift": {
            "new_headings": added_headings,
            "removed_headings": removed_headings
        },
        "added_lines": added_lines[:50],
        "removed_lines": removed_lines[:50],
        "markdown_diff": "\n".join(md_lines)
    }
