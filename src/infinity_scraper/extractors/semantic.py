"""
Autonomous Semantic Extraction Engine for InfinityScrape.
Provides zero-selector heuristic extraction for contacts, pricing tables, FAQs, and business entities.
"""

import re
import urllib.parse
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup


# =============================================================================
# 📞 CONTACT & LEAD INTELLIGENCE EXTRACTOR
# =============================================================================

# RFC 5322 simplified email regex with extension exclusion
EMAIL_REGEX = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
)

# Common dummy or placeholder emails to filter out
DUMMY_EMAIL_DOMAINS = {
    "example.com", "sample.com", "domain.com", "email.com",
    "test.com", "yourdomain.com", "sentry.io", "wixpress.com"
}

# Image extensions that sometimes get captured by sloppy regex
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".css", ".js")

# E.164 and international phone number pattern (8 to 15 digits)
PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}\b"
)

# Business IDs (Indian GSTIN, CIN, US EIN)
GSTIN_REGEX = re.compile(r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b")
CIN_REGEX = re.compile(r"\b[UL][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}\b")
EIN_REGEX = re.compile(r"\b[0-9]{2}-[0-9]{7}\b")

# Indian PIN code & US ZIP code patterns
PIN_CODE_REGEX = re.compile(r"\b(?:Pin\s*Code|PIN|Postal\s*Code)?[^0-9]?([1-9][0-9]{5})\b", re.IGNORECASE)
ZIP_CODE_REGEX = re.compile(r"\b\d{5}(?:-\d{4})?\b")


def extract_contact_intelligence(html_or_text: str, base_url: str = "") -> Dict[str, Any]:
    """
    Zero-selector extraction of all emails, phone numbers, WhatsApp links,
    social profiles, physical addresses, and tax/business IDs from HTML or text.
    """
    is_html = "<html" in html_or_text.lower() or "<div" in html_or_text.lower() or "<body" in html_or_text.lower()
    soup = BeautifulSoup(html_or_text, "html.parser") if is_html else None
    text_content = soup.get_text(separator=" ", strip=True) if soup else html_or_text

    emails = set()
    phones = set()
    whatsapp_numbers = set()
    social_profiles = {
        "twitter_x": set(),
        "linkedin": set(),
        "github": set(),
        "instagram": set(),
        "facebook": set(),
        "youtube": set(),
        "telegram": set(),
    }

    # 1. Extract from DOM links if HTML is available
    if soup:
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            # mailto: links
            if href.lower().startswith("mailto:"):
                clean_email = href[7:].split("?")[0].strip().lower()
                if clean_email and not any(clean_email.endswith(ext) for ext in IMAGE_EXTENSIONS):
                    emails.add(clean_email)

            # tel: links
            elif href.lower().startswith("tel:"):
                clean_tel = href[4:].split("?")[0].strip()
                if clean_tel and len(re.sub(r"\D", "", clean_tel)) >= 7:
                    phones.add(clean_tel)

            # WhatsApp links
            elif "wa.me/" in href or "api.whatsapp.com/send" in href:
                match = re.search(r"(?:phone=|wa\.me\/)(\+?\d+)", href)
                if match:
                    whatsapp_numbers.add(match.group(1))

            # Social links
            low_href = href.lower()
            if "linkedin.com/in/" in low_href or "linkedin.com/company/" in low_href:
                social_profiles["linkedin"].add(href)
            elif "twitter.com/" in low_href or "x.com/" in low_href:
                social_profiles["twitter_x"].add(href)
            elif "github.com/" in low_href and not any(x in low_href for x in ["/features", "/pricing", "/join"]):
                social_profiles["github"].add(href)
            elif "instagram.com/" in low_href:
                social_profiles["instagram"].add(href)
            elif "facebook.com/" in low_href:
                social_profiles["facebook"].add(href)
            elif "youtube.com/" in low_href or "youtu.be/" in low_href:
                social_profiles["youtube"].add(href)
            elif "t.me/" in low_href:
                social_profiles["telegram"].add(href)

    # 2. Extract from body text via Regex
    for email in EMAIL_REGEX.findall(text_content):
        low_email = email.lower()
        domain = low_email.split("@")[-1]
        if domain not in DUMMY_EMAIL_DOMAINS and not any(low_email.endswith(ext) for ext in IMAGE_EXTENSIONS):
            emails.add(low_email)

    # Phone candidates from text
    for phone_match in PHONE_REGEX.findall(text_content):
        digits_only = re.sub(r"\D", "", phone_match)
        # Filter out numbers that are too short, years (1900-2099), or clearly non-phone
        if 8 <= len(digits_only) <= 15:
            if not (len(digits_only) == 4 and digits_only.startswith(("19", "20"))):
                phones.add(phone_match.strip(" -.,()"))

    # 3. Extract Business & Tax IDs
    gstin_matches = list(set(GSTIN_REGEX.findall(text_content)))
    cin_matches = list(set(CIN_REGEX.findall(text_content)))
    ein_matches = list(set(EIN_REGEX.findall(text_content)))

    # 4. Extract Postal / PIN Codes
    pin_matches = list(set(PIN_CODE_REGEX.findall(text_content)))

    # Convert sets to sorted lists
    clean_socials = {k: sorted(list(v)) for k, v in social_profiles.items() if v}

    markdown_parts = ["### 📞 Contact & Business Intelligence"]
    if emails:
        markdown_parts.append(f"- **Emails ({len(emails)})**: {', '.join(sorted(emails))}")
    if phones:
        markdown_parts.append(f"- **Phone Numbers ({len(phones)})**: {', '.join(sorted(phones))}")
    if whatsapp_numbers:
        markdown_parts.append(f"- **WhatsApp**: {', '.join(sorted(whatsapp_numbers))}")
    if gstin_matches:
        markdown_parts.append(f"- **GSTIN (India)**: {', '.join(gstin_matches)}")
    if cin_matches:
        markdown_parts.append(f"- **CIN (India)**: {', '.join(cin_matches)}")
    if ein_matches:
        markdown_parts.append(f"- **EIN (US)**: {', '.join(ein_matches)}")
    if pin_matches:
        markdown_parts.append(f"- **PIN / Postal Codes**: {', '.join(pin_matches)}")
    if clean_socials:
        markdown_parts.append("- **Social Profiles**:")
        for net, urls in clean_socials.items():
            markdown_parts.append(f"  - *{net.capitalize()}*: {', '.join(urls)}")

    return {
        "status": "success",
        "url": base_url,
        "emails": sorted(list(emails)),
        "phones": sorted(list(phones)),
        "whatsapp": sorted(list(whatsapp_numbers)),
        "social_profiles": clean_socials,
        "business_ids": {
            "gstin": gstin_matches,
            "cin": cin_matches,
            "ein": ein_matches,
        },
        "postal_codes": pin_matches,
        "markdown_summary": "\n".join(markdown_parts)
    }


# =============================================================================
# 💳 PRICING TABLE & PLAN INTELLIGENCE EXTRACTOR
# =============================================================================

CURRENCY_SYMBOLS = ["$", "€", "£", "₹", "¥", "USD", "EUR", "GBP", "INR", "CAD", "AUD"]
BILLING_INTERVALS = ["month", "mo", "year", "yr", "annual", "quarter", "one-time", "lifetime", "user", "seat"]


def extract_pricing_intelligence(html_or_text: str, base_url: str = "") -> Dict[str, Any]:
    """
    Zero-selector extraction of SaaS/product pricing tables, plans, costs,
    feature bullets, and call-to-action buttons.
    """
    soup = BeautifulSoup(html_or_text, "html.parser")
    plans: List[Dict[str, Any]] = []

    # Potential card selectors common across modern frameworks
    card_candidates = soup.find_all(
        lambda tag: tag.name in ["div", "section", "article", "li"] and any(
            kw in " ".join(tag.get("class", [])).lower() or kw in tag.get("id", "").lower()
            for kw in ["pricing-card", "pricing-tier", "pricing-table", "price-card", "plan-card", "tier-card", "pricing__card", "package"]
        )
    )

    # Fallback: if no dedicated pricing class found, search for containers with currency symbols and headers
    if not card_candidates:
        currency_nodes = soup.find_all(string=re.compile(r"[\$€£₹]\s*\d+"))
        for cnode in currency_nodes:
            parent = cnode.find_parent(["div", "section", "article", "li"])
            if parent and parent not in card_candidates:
                # Ensure the container isn't too huge (e.g. entire body)
                if len(parent.get_text()) < 3000:
                    card_candidates.append(parent)

    seen_signatures = set()

    for card in card_candidates:
        text = card.get_text(separator="\n", strip=True)
        # Search for plan name
        name_node = card.find(["h1", "h2", "h3", "h4", "h5", "strong"])
        plan_name = name_node.get_text(strip=True) if name_node else "Standard Plan"

        # Search for price pattern (e.g. $29, $29/mo, 1,499 INR, Free, $0)
        price_match = re.search(
            r"([\$€£₹]\s*\d+(?:[.,]\d+)?|\d+(?:[.,]\d+)?\s*(?:USD|INR|EUR|GBP)|Free|\$0)",
            text,
            re.IGNORECASE
        )
        if not price_match:
            continue

        raw_price = price_match.group(1).strip()

        # Billing cycle
        billing_match = re.search(r"/(?:month|mo|year|yr|user|seat|day)", text, re.IGNORECASE)
        billing_cycle = billing_match.group(0).replace("/", "") if billing_match else "per period"

        # Unique signature to avoid duplicate nested parents
        sig = f"{plan_name}:{raw_price}"
        if sig in seen_signatures:
            continue
        seen_signatures.add(sig)

        # Feature items
        features = []
        for li in card.find_all("li"):
            feat_text = li.get_text(strip=True)
            if feat_text and len(feat_text) < 150:
                features.append(feat_text)

        # CTA Button
        cta = None
        cta_node = card.find(["a", "button"])
        if cta_node:
            cta = {
                "text": cta_node.get_text(strip=True),
                "url": urllib.parse.urljoin(base_url, cta_node.get("href", "")) if cta_node.get("href") else None
            }

        is_popular = any(
            badge in text.lower() for badge in ["popular", "recommended", "best value", "most popular", "featured"]
        )

        plans.append({
            "plan_name": plan_name,
            "price": raw_price,
            "billing_cycle": billing_cycle,
            "is_highlighted": is_popular,
            "features": features,
            "cta": cta
        })

    # Build Markdown Table
    md_lines = ["### 💳 Pricing Plans Matrix", ""]
    if plans:
        md_lines.append("| Plan | Price | Period | Popular? | Top Features |")
        md_lines.append("| :--- | :--- | :--- | :---: | :--- |")
        for p in plans:
            feats_summary = ", ".join(p["features"][:3]) if p["features"] else "N/A"
            star = "⭐ Yes" if p["is_highlighted"] else "No"
            md_lines.append(f"| **{p['plan_name']}** | `{p['price']}` | {p['billing_cycle']} | {star} | {feats_summary} |")
    else:
        md_lines.append("*No explicit pricing card structures detected on this page.*")

    return {
        "status": "success",
        "url": base_url,
        "total_plans_found": len(plans),
        "plans": plans,
        "markdown_table": "\n".join(md_lines)
    }


# =============================================================================
# ❓ FAQ & ACCORDION INTELLIGENCE EXTRACTOR
# =============================================================================

def extract_faq_intelligence(html_or_text: str, base_url: str = "") -> Dict[str, Any]:
    """
    Zero-selector extraction of FAQ sections from HTML via JSON-LD schema,
    HTML5 <details><summary>, and accordion CSS heuristics.
    """
    soup = BeautifulSoup(html_or_text, "html.parser")
    faqs: List[Dict[str, str]] = []
    seen_questions = set()

    # 1. Inspect Schema.org JSON-LD FAQPage
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            import json
            data = json.loads(script.string or "")
            if isinstance(data, dict) and data.get("@type") == "FAQPage":
                for item in data.get("mainEntity", []):
                    q = item.get("name", "").strip()
                    a = item.get("acceptedAnswer", {}).get("text", "").strip()
                    if q and q not in seen_questions:
                        seen_questions.add(q)
                        faqs.append({"question": q, "answer": a, "source": "schema_jsonld"})
        except Exception:
            pass

    # 2. Inspect HTML5 <details><summary>
    for details in soup.find_all("details"):
        summary = details.find("summary")
        if summary:
            q = summary.get_text(strip=True)
            # Remove summary to extract remaining content as answer
            summary.extract()
            a = details.get_text(separator=" ", strip=True)
            if q and len(q) > 5 and q not in seen_questions:
                seen_questions.add(q)
                faqs.append({"question": q, "answer": a, "source": "html5_details"})

    # 3. Inspect Accordion CSS / Class Heuristics
    if len(faqs) < 3:
        accordion_items = soup.find_all(
            lambda tag: any(kw in " ".join(tag.get("class", [])).lower() for kw in ["faq-item", "accordion-item", "faq-block", "qa-item"])
        )
        for item in accordion_items:
            heading = item.find(["h2", "h3", "h4", "h5", "button", "div"])
            if heading:
                q = heading.get_text(strip=True)
                # Answer is the sibling or paragraph
                answer_p = item.find(["p", "div"])
                a = answer_p.get_text(separator=" ", strip=True) if answer_p else ""
                if q.endswith("?") and q not in seen_questions:
                    seen_questions.add(q)
                    faqs.append({"question": q, "answer": a, "source": "accordion_heuristic"})

    # Build Markdown
    md_lines = ["### ❓ Frequently Asked Questions (FAQs)", ""]
    if faqs:
        for idx, f in enumerate(faqs, 1):
            md_lines.append(f"**Q{idx}: {f['question']}**")
            md_lines.append(f"{f['answer']}\n")
    else:
        md_lines.append("*No structured FAQ elements detected on this page.*")

    return {
        "status": "success",
        "url": base_url,
        "total_faqs": len(faqs),
        "faqs": faqs,
        "markdown": "\n".join(md_lines)
    }
