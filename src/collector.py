"""
Fetches articles from RSS feeds and Google News.
Returns a deduplicated, date-sorted list of Article dicts.

Key design decisions:
- All HTTP fetches use a 10-second timeout — no hanging on slow sources.
- Total articles capped at MAX_ARTICLES (most recent first) to keep
  downstream Groq API calls within the free-tier rate limit.
"""

import hashlib
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus

import feedparser
import httpx
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

from config import (
    AGGREGATOR_FEEDS,
    DAILY_LOOKBACK_HOURS,
    GOOGLE_NEWS_QUERIES,
    OFFICIAL_FEEDS,
    RELEVANCE_KEYWORDS,
    WEEKLY_LOOKBACK_DAYS,
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; APACRegulatoryMonitor/1.0; "
        "+https://github.com/hamu86sg/bdapac)"
    )
}

GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search?q={query}"
    "&hl=en&gl=SG&ceid=SG:en"
)

FETCH_TIMEOUT   = 10     # seconds per HTTP request
MAX_ARTICLES    = 80     # cap before sending to Groq — keeps API calls manageable


def _article_id(url: str, title: str) -> str:
    key = (url or title or "").strip().lower()
    return hashlib.sha1(key.encode()).hexdigest()[:16]


def _parse_date(entry) -> datetime | None:
    for field in ("published", "updated", "created"):
        raw = getattr(entry, field, None) or entry.get(field)
        if raw:
            try:
                return dateparser.parse(raw, ignoretz=False)
            except Exception:
                pass
    return None


def _is_recent(dt: datetime | None, cutoff: datetime) -> bool:
    if dt is None:
        return True
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    if cutoff.tzinfo is None:
        cutoff = cutoff.replace(tzinfo=timezone.utc)
    return dt >= cutoff


def _quick_relevant(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in RELEVANCE_KEYWORDS)


def _entry_to_article(entry, source_name: str) -> dict:
    title   = getattr(entry, "title", "") or ""
    link    = getattr(entry, "link",  "") or ""
    summary = ""
    for field in ("summary", "description", "content"):
        raw = getattr(entry, field, None)
        if isinstance(raw, list) and raw:
            summary = raw[0].get("value", "")
            break
        if isinstance(raw, str) and raw:
            summary = raw
            break
    if summary:
        summary = BeautifulSoup(summary, "lxml").get_text(separator=" ", strip=True)
    return {
        "id":        _article_id(link, title),
        "title":     title,
        "url":       link,
        "summary":   summary[:1000],
        "source":    source_name,
        "published": _parse_date(entry),
    }


def _fetch_feed(url: str, source_name: str, cutoff: datetime) -> list[dict]:
    """Fetch one RSS/Atom feed with a hard timeout. Returns [] on any failure."""
    try:
        # Use httpx for the network call so we get a reliable timeout,
        # then hand the raw content to feedparser for parsing.
        with httpx.Client(timeout=FETCH_TIMEOUT, follow_redirects=True) as client:
            response = client.get(url, headers=HEADERS)
            response.raise_for_status()
        feed = feedparser.parse(response.text)
    except Exception as e:
        print(f"[WARN] Skipping {source_name}: {e}")
        return []

    articles = []
    for entry in feed.entries:
        article = _entry_to_article(entry, source_name)
        if not _is_recent(article["published"], cutoff):
            continue
        if _quick_relevant(article["title"] + " " + article["summary"]):
            articles.append(article)
    return articles


def _fetch_google_news(query: str, cutoff: datetime) -> list[dict]:
    url = GOOGLE_NEWS_RSS.format(query=quote_plus(query))
    return _fetch_feed(url, f"Google News: {query[:50]}", cutoff)


def collect_weekly() -> list[dict]:
    """Collect articles from the past 7 days across all sources."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=WEEKLY_LOOKBACK_DAYS)
    return _collect(cutoff)


def collect_daily() -> list[dict]:
    """Collect articles from the past ~26 hours for the daily flash check."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=DAILY_LOOKBACK_HOURS)
    return _collect(cutoff)


def _collect(cutoff: datetime) -> list[dict]:
    all_articles: list[dict] = []
    seen_ids: set[str] = set()

    # Official government/regulator feeds
    for jurisdiction, feeds in OFFICIAL_FEEDS.items():
        for feed_def in feeds:
            articles = _fetch_feed(feed_def["url"], feed_def["name"], cutoff)
            for a in articles:
                a["jurisdiction_hint"] = jurisdiction
            all_articles.extend(articles)
            time.sleep(0.2)

    # Aggregator and analysis feeds
    for feed_def in AGGREGATOR_FEEDS:
        all_articles.extend(_fetch_feed(feed_def["url"], feed_def["name"], cutoff))
        time.sleep(0.2)

    # Google News queries
    for query in GOOGLE_NEWS_QUERIES:
        all_articles.extend(_fetch_google_news(query, cutoff))
        time.sleep(0.3)

    # Deduplicate
    deduped = []
    for article in all_articles:
        if article["id"] not in seen_ids:
            seen_ids.add(article["id"])
            deduped.append(article)

    # Sort newest-first, then cap — keeps the most recent content within API limits
    deduped.sort(
        key=lambda a: a["published"] or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    if len(deduped) > MAX_ARTICLES:
        print(f"[INFO] Capping {len(deduped)} articles to {MAX_ARTICLES} most recent")
        deduped = deduped[:MAX_ARTICLES]

    print(f"[INFO] Collected {len(deduped)} articles for analysis (cutoff: {cutoff.date()})")
    return deduped
