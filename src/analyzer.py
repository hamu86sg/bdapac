"""
Two-pass Gemini analysis pipeline.

Pass 1 (Flash):  Quick relevance filter — drops noise cheaply.
Pass 2 (Flash):  Deep analysis, categorisation, and memo writing.

Uses Google Gemini via the free tier (no credit card required).
"""

import json
import os
import textwrap
from datetime import datetime

import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

FILTER_MODEL   = genai.GenerativeModel("gemini-2.0-flash")
ANALYSIS_MODEL = genai.GenerativeModel("gemini-2.0-flash")

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
      "it_categories": array from [cybersecurity, data_protection_privacy,
                        cloud_sovereignty, ai_ml_governance, telecommunications,
                        critical_infrastructure, hardware_supply_chain,
                        fintech_digital_payments, data_centre_regulation,
                        semiconductor_export_controls, digital_identity, network_equipment],
      "verticals": array from [financial_services, healthcare,
                   government_public_sector, manufacturing_industrial, telecommunications,
                   energy_utilities, data_centre_ecosystem, retail_ecommerce, education],
      "significance": one of ["HIGH", "MEDIUM", "LOW"],
      "significance_rationale": "one sentence explaining why this significance level",
      "wwt_relevance": "2-3 sentences on the specific opportunity or compliance risk for WWT accounts",
      "sources": [{"title": "source name or article headline", "url": "full URL"}]
    }

    Status definitions:
    - ENACTED: signed into law and currently in force
    - PASSED-PENDING: passed but not yet effective
    - PROPOSED: formal draft published for legislative action
    - CONSULTATION: open consultation or public comment period underway
    - RUMORED: credibly reported as planned but no formal document published yet

    Significance:
    - HIGH: broad compliance deadline within 18 months, or affects multiple major verticals,
            or involves significant hardware/software procurement implications
    - MEDIUM: affects a specific vertical or product category, timeline > 18 months or uncertain
    - LOW: informational, minor amendment, or very narrow scope

    Consolidate multiple articles about the same development into one item.
    Return ONLY the JSON array, no other text.
""").strip()

_SUMMARY_SYSTEM = textwrap.dedent("""
    You are writing the Executive Summary section of WWT's weekly APAC Regulatory
    Intelligence Memo for account managers, pre-sales engineers, and leadership.
    Write in plain, direct English. No jargon. Be specific about jurisdictions,
    timelines, and what it means for WWT's business.
""").strip()


def _gemini_json(model, prompt: str, system: str) -> str:
    full_prompt = f"{system}\n\n---\n\n{prompt}"
    response = model.generate_content(
        full_prompt,
        generation_config={"response_mime_type": "application/json"},
    )
    return response.text


# ── Pass 1: Relevance filter ──────────────────────────────────────────────────

def filter_relevant(articles: list[dict]) -> list[dict]:
    relevant = []
    for article in articles:
        text = f"Title: {article['title']}\n\nSummary: {article['summary']}"
        try:
            raw = _gemini_json(FILTER_MODEL, text, _FILTER_SYSTEM)
            result = json.loads(raw)
            if result.get("relevant"):
                article["filter_confidence"] = result.get("confidence", "medium")
                relevant.append(article)
        except Exception as e:
            print(f"[WARN] Filter failed for '{article['title'][:60]}': {e}")
            relevant.append(article)

    print(f"[INFO] Relevance filter: {len(relevant)}/{len(articles)} articles passed")
    return relevant


# ── Pass 2: Deep analysis ─────────────────────────────────────────────────────

def _format_articles(articles: list[dict]) -> str:
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
    if not articles:
        return []

    content = _format_articles(articles)
    prompt  = (
        f"Analyse the following {len(articles)} pre-filtered regulatory news articles "
        f"and return the JSON array as instructed.\n\n{content}"
    )

    try:
        raw   = _gemini_json(ANALYSIS_MODEL, prompt, _ANALYSIS_SYSTEM)
        items = json.loads(raw)
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
    high   = [i for i in items if i.get("significance") == "HIGH"]
    medium = [i for i in items if i.get("significance") == "MEDIUM"]
    low    = [i for i in items if i.get("significance") == "LOW"]

    prompt = (
        f"Week ending {run_date.strftime('%d %B %Y')}. "
        f"Total: {len(items)} items ({len(high)} HIGH, {len(medium)} MEDIUM, {len(low)} LOW).\n\n"
        f"Items:\n{json.dumps(items, indent=2, default=str)}\n\n"
        "Write a 3-5 paragraph executive summary. Open with the most urgent development. "
        "Mention specific jurisdictions, timelines, and products affected. "
        "Close with a forward-look: what to watch in the coming weeks. "
        "Flowing paragraphs only — no headers or bullet points."
    )

    try:
        response = ANALYSIS_MODEL.generate_content(f"{_SUMMARY_SYSTEM}\n\n---\n\n{prompt}")
        return response.text.strip()
    except Exception as e:
        print(f"[ERROR] Executive summary failed: {e}")
        return "Executive summary unavailable due to an error. See detailed findings below."


# ── Daily flash summary ───────────────────────────────────────────────────────

def write_flash_summary(items: list[dict], run_date: datetime) -> str:
    prompt = (
        f"Date: {run_date.strftime('%d %B %Y')}.\n\n"
        f"HIGH-significance items detected today:\n{json.dumps(items, indent=2, default=str)}\n\n"
        "Write a brief flash digest (2-3 paragraphs) for WWT account managers. "
        "Be direct about what happened, which jurisdictions are affected, the timeline, "
        "and what WWT accounts should be thinking about. "
        "Start with 'FLASH DIGEST —' and the most important headline."
    )

    try:
        response = ANALYSIS_MODEL.generate_content(f"{_SUMMARY_SYSTEM}\n\n---\n\n{prompt}")
        return response.text.strip()
    except Exception as e:
        print(f"[ERROR] Flash summary failed: {e}")
        return "Flash summary unavailable. See items below."
