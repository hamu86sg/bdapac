"""
Two-pass Claude analysis pipeline.

Pass 1 (Haiku):  Quick relevance filter — drops noise before the expensive pass.
Pass 2 (Sonnet): Deep analysis, categorization, and memo writing.

Prompt caching is applied to the long system prompts to reduce API costs.
"""

import json
import os
import textwrap
from datetime import datetime

import anthropic

from config import ANALYSIS_MODEL, FILTER_MODEL, JURISDICTIONS

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# ── System prompts ────────────────────────────────────────────────────────────

_FILTER_SYSTEM = textwrap.dedent("""
    You are a regulatory intelligence filter for World Wide Technology (WWT), a global
    IT solutions provider. Your job is to quickly assess whether a news article describes
    an actual or expected change in laws, regulations, policies, or standards that could
    affect IT requirements in Asia Pacific markets.

    IT requirements include: hardware procurement, software licensing, cloud services,
    cybersecurity controls, data protection, network equipment, AI systems, storage,
    telecommunications infrastructure, semiconductor supply chains, or data centre operations.

    Return ONLY a JSON object with this exact structure:
    {
      "relevant": true or false,
      "confidence": "high" | "medium" | "low",
      "reason": "one sentence explanation"
    }
""").strip()

_ANALYSIS_SYSTEM = textwrap.dedent("""
    You are a senior regulatory intelligence analyst for World Wide Technology (WWT),
    a leading global IT solutions provider serving government agencies and enterprises
    across Asia Pacific.

    WWT's portfolio covers: hardware (servers, networking, storage, edge), software
    (enterprise applications, security platforms), and services (managed services,
    professional services, cloud infrastructure). Key verticals: financial services,
    healthcare, government/public sector, manufacturing, telecommunications, energy,
    and the data centre ecosystem (hyperscalers, colocation providers, GPUaaS builders).

    You will be given a set of pre-filtered news articles about regulatory and legal
    developments in APAC markets. Analyse each item and return a JSON array. Each element
    must have EXACTLY these fields:

    {
      "title": "concise, descriptive title (max 80 chars)",
      "jurisdiction": one of [Australia, Japan, India, Singapore, South Korea, Hong Kong,
                              Taiwan, Malaysia, Vietnam, Thailand, Macau, New Zealand,
                              Philippines, APAC-Wide],
      "status": one of ["ENACTED", "PASSED-PENDING", "PROPOSED", "CONSULTATION", "RUMORED"],
      "status_note": "brief clarification, e.g. 'effective 1 Jan 2026' or 'comment period closes Aug 2025'",
      "summary": "3-4 sentences of plain-English explanation suitable for a non-technical executive",
      "it_categories": array of strings from [cybersecurity, data_protection_privacy,
                        cloud_sovereignty, ai_ml_governance, telecommunications,
                        critical_infrastructure, hardware_supply_chain,
                        fintech_digital_payments, data_centre_regulation,
                        semiconductor_export_controls, digital_identity, network_equipment],
      "verticals": array of strings from [financial_services, healthcare,
                   government_public_sector, manufacturing_industrial, telecommunications,
                   energy_utilities, data_centre_ecosystem, retail_ecommerce, education],
      "significance": one of ["HIGH", "MEDIUM", "LOW"],
      "significance_rationale": "one sentence explaining why this significance level",
      "wwt_relevance": "2-3 sentences explaining the specific opportunity or compliance risk
                        this creates for WWT's accounts and pipeline",
      "sources": [{"title": "source name or article headline", "url": "full URL"}]
    }

    Status definitions:
    - ENACTED: signed into law and currently in force
    - PASSED-PENDING: passed by legislature or regulator but not yet effective
    - PROPOSED: formal draft published for legislative or regulatory action
    - CONSULTATION: open consultation or public comment period underway
    - RUMORED: credibly reported as planned but no formal document yet published

    Significance definitions:
    - HIGH: broad compliance deadline within 18 months, or affects multiple major verticals,
            or involves significant hardware/software procurement implications
    - MEDIUM: affects a specific vertical or product category, timeline > 18 months or uncertain
    - LOW: informational, minor amendment, or very narrow scope

    Important: if multiple articles cover the same development, consolidate them into one item
    and include all source URLs. Return ONLY the JSON array, no other text.
""").strip()

_SUMMARY_SYSTEM = textwrap.dedent("""
    You are writing the Executive Summary section of WWT's weekly APAC Regulatory
    Intelligence Memo. Your audience is WWT account managers, pre-sales engineers,
    and leadership who are busy and need actionable intelligence quickly.

    Write in plain, direct English. No jargon. No bullet-point padding. Be specific
    about jurisdictions, timelines, and what it means for WWT's business.
""").strip()


# ── Pass 1: Relevance filter ──────────────────────────────────────────────────

def filter_relevant(articles: list[dict]) -> list[dict]:
    """Use Haiku to quickly drop articles that are not about IT regulatory changes."""
    relevant = []
    batch_size = 20

    for i in range(0, len(articles), batch_size):
        batch = articles[i : i + batch_size]
        for article in batch:
            text = f"Title: {article['title']}\n\nSummary: {article['summary']}"
            try:
                resp = client.messages.create(
                    model=FILTER_MODEL,
                    max_tokens=128,
                    system=[
                        {
                            "type": "text",
                            "text": _FILTER_SYSTEM,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    messages=[{"role": "user", "content": text}],
                )
                result = json.loads(resp.content[0].text)
                if result.get("relevant"):
                    article["filter_confidence"] = result.get("confidence", "medium")
                    relevant.append(article)
            except Exception as e:
                print(f"[WARN] Filter failed for '{article['title'][:60]}': {e}")
                relevant.append(article)  # include on error — don't silently drop

    print(f"[INFO] Relevance filter: {len(relevant)}/{len(articles)} articles passed")
    return relevant


# ── Pass 2: Deep analysis ─────────────────────────────────────────────────────

def _format_articles_for_analysis(articles: list[dict]) -> str:
    lines = []
    for i, a in enumerate(articles, 1):
        pub = a["published"].strftime("%Y-%m-%d") if a.get("published") else "unknown date"
        lines.append(
            f"[{i}] SOURCE: {a['source']} | DATE: {pub}\n"
            f"TITLE: {a['title']}\n"
            f"URL: {a['url']}\n"
            f"SUMMARY: {a['summary']}\n"
        )
    return "\n---\n".join(lines)


def analyse_articles(articles: list[dict]) -> list[dict]:
    """Run deep analysis with Sonnet. Returns structured regulatory items."""
    if not articles:
        return []

    content = _format_articles_for_analysis(articles)

    try:
        resp = client.messages.create(
            model=ANALYSIS_MODEL,
            max_tokens=8000,
            system=[
                {
                    "type": "text",
                    "text": _ANALYSIS_SYSTEM,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Analyse the following {len(articles)} pre-filtered regulatory "
                        f"news articles and return the JSON array as instructed.\n\n"
                        f"{content}"
                    ),
                }
            ],
        )
        items = json.loads(resp.content[0].text)
        print(f"[INFO] Analysis produced {len(items)} regulatory items")
        return items
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parse failed in analysis: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Analysis API call failed: {e}")
        return []


# ── Executive summary ─────────────────────────────────────────────────────────

def write_executive_summary(items: list[dict], run_date: datetime) -> str:
    """Write a 3-5 paragraph executive summary of the week's findings."""
    high   = [i for i in items if i.get("significance") == "HIGH"]
    medium = [i for i in items if i.get("significance") == "MEDIUM"]
    low    = [i for i in items if i.get("significance") == "LOW"]

    items_digest = json.dumps(items, indent=2, default=str)

    prompt = (
        f"Week ending {run_date.strftime('%d %B %Y')}.\n\n"
        f"Total regulatory items identified: {len(items)} "
        f"({len(high)} HIGH significance, {len(medium)} MEDIUM, {len(low)} LOW).\n\n"
        f"Here are all the analysed items:\n\n{items_digest}\n\n"
        "Write a 3-5 paragraph executive summary for this week's APAC Regulatory "
        "Intelligence Memo. Open with the most urgent/impactful development. "
        "Mention specific jurisdictions, timelines, and products/services affected. "
        "Close with a brief forward-look: what to watch in the coming weeks. "
        "Do not use headers or bullet points — flowing paragraphs only."
    )

    try:
        resp = client.messages.create(
            model=ANALYSIS_MODEL,
            max_tokens=1200,
            system=[
                {
                    "type": "text",
                    "text": _SUMMARY_SYSTEM,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text.strip()
    except Exception as e:
        print(f"[ERROR] Executive summary failed: {e}")
        return "Executive summary unavailable due to an error. See detailed findings below."


# ── Daily flash assessment ────────────────────────────────────────────────────

def write_flash_summary(items: list[dict], run_date: datetime) -> str:
    """Write a concise flash digest for high-significance daily findings."""
    items_digest = json.dumps(items, indent=2, default=str)

    prompt = (
        f"Date: {run_date.strftime('%d %B %Y')}.\n\n"
        f"The following HIGH-significance regulatory developments were detected today "
        f"in APAC markets:\n\n{items_digest}\n\n"
        "Write a brief flash digest (2-3 paragraphs) for WWT account managers. "
        "Be direct about what happened, which jurisdictions are affected, the timeline, "
        "and what WWT accounts should be thinking about. "
        "Start with 'FLASH DIGEST —' and the most important headline."
    )

    try:
        resp = client.messages.create(
            model=ANALYSIS_MODEL,
            max_tokens=600,
            system=[
                {
                    "type": "text",
                    "text": _SUMMARY_SYSTEM,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text.strip()
    except Exception as e:
        print(f"[ERROR] Flash summary failed: {e}")
        return "Flash summary unavailable. See items below."
