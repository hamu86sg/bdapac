"""
Two-pass Groq analysis pipeline.

Pass 1 (fast):  Quick relevance filter — drops noise cheaply.
Pass 2 (full):  Deep analysis, categorisation, and memo writing.

Uses Groq's free tier — no credit card required.
Model: llama-3.3-70b-versatile (very capable, free).
"""

import json
import os
import textwrap
from datetime import datetime

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

MODEL = "llama-3.3-70b-versatile"

# ── System prompts ────────────────────────────────────────────────────────────

_FILTER_SYSTEM = textwrap.dedent("""
    You are a regulatory intelligence filter for World Wide Technology (WWT), a global
    IT solutions provider. Your job is to assess whether a news article describes an ACTUAL
    REGULATORY ACTION — meaning a government, regulator, or legislature has passed, proposed,
    opened consultation on, or announced a specific law, regulation, policy, or binding standard
    that could affect IT requirements in Asia Pacific markets.

    IT requirements include: hardware procurement, software licensing, cloud services,
    cybersecurity controls, data protection, network equipment, AI systems, storage,
    telecommunications infrastructure, semiconductor supply chains, or data centre operations.

    Mark as NOT RELEVANT (relevant: false) if the article is primarily:
    - A market size report, industry forecast, or analyst market commentary
    - A cybersecurity incident count, breach statistics, or threat report with no regulatory action
    - A vendor product launch or corporate announcement
    - General opinion or commentary without a specific government/regulatory action
    - A conference report, award, or event coverage

    Mark as RELEVANT (relevant: true) only if a specific government body, regulator, or
    legislature has taken or announced a concrete regulatory action.

    Return ONLY a JSON object with this exact structure (no other text):
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

    You will be given a set of pre-filtered news articles. Your job is to identify and
    analyse items that represent ACTUAL REGULATORY DEVELOPMENTS — meaning laws, regulations,
    government policies, compliance requirements, or official standards that are enacted,
    proposed, or under consultation.

    STRICT EXCLUSION RULES — do NOT include an item if it is primarily:
    - A market research report, market size statistic, or industry forecast
    - A cybersecurity incident count, breach report, or threat statistics roundup
    - A vendor announcement, product launch, or corporate press release
    - General commentary, opinion, or analysis with no specific regulatory action
    - A conference, award, or event report
    Only include items where a government, regulator, or legislature has taken or
    announced a specific action (passed law, issued regulation, opened consultation,
    published draft, issued binding guideline, announced policy).

    For each qualifying regulatory development, return a JSON array element with EXACTLY
    these fields:

    {
      "title": "concise, descriptive title naming the specific regulation/law (max 80 chars)",
      "jurisdiction": one of [Australia, Japan, India, Singapore, South Korea, Hong Kong,
                              Taiwan, Malaysia, Vietnam, Thailand, Macau, New Zealand,
                              Philippines, APAC-Wide],
      "status": one of ["ENACTED", "PASSED-PENDING", "PROPOSED", "CONSULTATION", "RUMORED"],
      "status_note": "brief clarification, e.g. 'effective 1 Jan 2026' or 'comment period closes Aug 2025'",
      "summary": "3-4 sentences of plain-English explanation of what the regulation requires and who it affects",
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
      "wwt_relevance": "2-3 sentences on the SPECIFIC compliance requirement or procurement opportunity this creates for WWT customers — name the relevant WWT product/service category (e.g. security platforms, data centre infrastructure, network equipment) and which customer verticals are most affected",
      "sources": [{"title": "source name or article headline", "url": "full URL"}]
    }

    Status definitions:
    - ENACTED: signed into law and currently in force
    - PASSED-PENDING: passed but not yet effective (has a future effective date)
    - PROPOSED: formal draft published for legislative action
    - CONSULTATION: open consultation or public comment period underway
    - RUMORED: credibly reported as planned but no formal document published yet

    Significance:
    - HIGH: compliance deadline within 18 months, affects multiple major verticals,
            or involves significant mandatory hardware/software procurement
    - MEDIUM: affects a specific vertical or product category, timeline > 18 months or uncertain
    - LOW: informational update, minor amendment, or very narrow scope

    Consolidate multiple articles about the same regulatory development into one item.
    If no articles meet the inclusion criteria, return an empty array [].
    Return ONLY the JSON array, no other text whatsoever.
""").strip()

_SUMMARY_SYSTEM = textwrap.dedent("""
    You are writing the Executive Summary section of WWT's weekly APAC Regulatory
    Intelligence Memo for account managers, pre-sales engineers, and leadership.
    Write in plain, direct English. No jargon. Be specific about jurisdictions,
    timelines, and what it means for WWT's business.
""").strip()


def _chat(system: str, user: str, json_mode: bool = False) -> str:
    kwargs = {
        "model":    MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        "temperature": 0.2,
        "max_tokens":  8000,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


# ── Pass 1: Relevance filter ──────────────────────────────────────────────────

_BATCH_FILTER_SYSTEM = _FILTER_SYSTEM + textwrap.dedent("""

    You will receive a numbered list of articles. Return a JSON array with one object
    per article in the same order:
    [{"index": 1, "relevant": true/false, "confidence": "high/medium/low"}, ...]
""").rstrip()


def filter_relevant(articles: list[dict]) -> list[dict]:
    """Filter articles in batches of 10 — reduces API calls from N to N/10."""
    if not articles:
        return []

    relevant   = []
    batch_size = 10   # 10 articles per Groq call → 8 calls for 80 articles

    for batch_start in range(0, len(articles), batch_size):
        batch = articles[batch_start : batch_start + batch_size]

        # Format the batch as a numbered list
        lines = []
        for i, a in enumerate(batch, 1):
            lines.append(f"[{i}] TITLE: {a['title']}\nSUMMARY: {a['summary'][:300]}")
        text = "\n\n".join(lines)

        try:
            raw     = _chat(_BATCH_FILTER_SYSTEM, text, json_mode=True)
            parsed  = json.loads(raw)
            # Unwrap if Groq returned {"results": [...]} instead of bare array
            if isinstance(parsed, dict):
                parsed = next((v for v in parsed.values() if isinstance(v, list)), [])

            decisions = {item["index"]: item for item in parsed if "index" in item}
            kept, dropped = 0, 0
            for i, article in enumerate(batch, 1):
                decision = decisions.get(i, {})
                # Default to INCLUDE when uncertain — better to over-collect
                if decision.get("relevant", True):
                    article["filter_confidence"] = decision.get("confidence", "medium")
                    relevant.append(article)
                    kept += 1
                else:
                    dropped += 1
            print(f"  [FILTER] Batch {batch_start//batch_size + 1}: kept {kept}, dropped {dropped}")

        except Exception as e:
            print(f"  [WARN] Batch filter failed (including all {len(batch)}): {e}")
            relevant.extend(batch)  # include on error

    print(f"[INFO] Relevance filter: {len(relevant)}/{len(articles)} articles passed to deep analysis")
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
    """Run deep analysis. Returns a list of structured regulatory items."""
    if not articles:
        return []

    # Process in batches of 30 to stay within token limits
    all_items = []
    batch_size = 30
    for i in range(0, len(articles), batch_size):
        batch   = articles[i : i + batch_size]
        content = _format_articles(batch)
        prompt  = (
            f"Analyse the following {len(batch)} pre-filtered regulatory news articles "
            f"and return the JSON array as instructed.\n\n{content}"
        )
        try:
            raw   = _chat(_ANALYSIS_SYSTEM, prompt, json_mode=True)
            # Groq json_object mode may wrap array in a key — unwrap if needed
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                all_items.extend(parsed)
            elif isinstance(parsed, dict):
                # find the first list value
                for v in parsed.values():
                    if isinstance(v, list):
                        all_items.extend(v)
                        break
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parse failed in analysis batch {i}: {e}")
        except Exception as e:
            print(f"[ERROR] Analysis API call failed for batch {i}: {e}")

    print(f"[INFO] Analysis produced {len(all_items)} regulatory items")
    return all_items


# ── Executive summary ─────────────────────────────────────────────────────────

def write_executive_summary(items: list[dict], run_date: datetime) -> str:
    high   = [i for i in items if i.get("significance") == "HIGH"]
    medium = [i for i in items if i.get("significance") == "MEDIUM"]
    low    = [i for i in items if i.get("significance") == "LOW"]

    # Summarise items compactly to stay within token limits
    compact = [
        {k: v for k, v in item.items() if k in
         ("title","jurisdiction","status","status_note","summary","significance","wwt_relevance")}
        for item in items
    ]

    prompt = (
        f"Week ending {run_date.strftime('%d %B %Y')}. "
        f"Total: {len(items)} items ({len(high)} HIGH, {len(medium)} MEDIUM, {len(low)} LOW).\n\n"
        f"Items:\n{json.dumps(compact, indent=2, default=str)}\n\n"
        "Write a 3-5 paragraph executive summary. Open with the most urgent development. "
        "Mention specific jurisdictions, timelines, and products affected. "
        "Close with a forward-look: what to watch in the coming weeks. "
        "Flowing paragraphs only — no headers or bullet points."
    )

    try:
        return _chat(_SUMMARY_SYSTEM, prompt).strip()
    except Exception as e:
        print(f"[ERROR] Executive summary failed: {e}")
        return "Executive summary unavailable due to an error. See detailed findings below."


# ── Daily flash summary ───────────────────────────────────────────────────────

def write_flash_summary(items: list[dict], run_date: datetime) -> str:
    compact = [
        {k: v for k, v in item.items() if k in
         ("title","jurisdiction","status","status_note","summary","wwt_relevance")}
        for item in items
    ]

    prompt = (
        f"Date: {run_date.strftime('%d %B %Y')}.\n\n"
        f"HIGH-significance items detected today:\n{json.dumps(compact, indent=2, default=str)}\n\n"
        "Write a brief flash digest (2-3 paragraphs) for WWT account managers. "
        "Be direct: what happened, which jurisdictions are affected, the timeline, "
        "and what WWT accounts should be thinking about. "
        "Start with 'FLASH DIGEST —' and the most important headline."
    )

    try:
        return _chat(_SUMMARY_SYSTEM, prompt).strip()
    except Exception as e:
        print(f"[ERROR] Flash summary failed: {e}")
        return "Flash summary unavailable. See items below."
