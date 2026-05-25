"""
Fetches articles from RSS feeds, Google News, and fallback web sources.
Returns a deduplicated list of Article dicts.
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
        "+https://github.com/wwt-apac-monitor)"
    )
}

GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search?q={query}"
    "&hl=en&gl=SG&ceid=SG:en"
)


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
        return True  # include if date unknown — better to over-collect
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    if cutoff.tzinfo is None:
        cutoff = cutoff.replace(tzinfo=timezone.utc)
    return dt >= cutoff


def _quick_relevant(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in RELEVANCE_KEYWORDS)


def _entry_to_article(entry, source_name: str) -> dict:
    title = getattr(entry, "title", "") or ""
    link  = getattr(entry, "link",  "") or ""
    summary = ""
    for field in ("summary", "description", "content"):
        raw = getattr(entry, field, None)
        if isinstance(raw, list) and raw:
            summary = raw[0].get("value", "")
            break
        if isinstance(raw, str) and raw:
            summary = raw
            break
    # strip HTML tags from summary
    if summary:
        summary = BeautifulSoup(summary, "lxml").get_text(separator=" ", strip=True)
    return {
        "id":       _article_id(link, title),
        "title":    title,
        "url":      link,
        "summary":  summary[:1000],
        "source":   source_name,
        "published": _parse_date(entry),
    }


def _fetch_feed(url: str, source_name: str, cutoff: datetime) -> list[dict]:
    try:
        feed = feedparser.parse(url, request_headers=HEADERS)
        articles = []
        for entry in feed.entries:
            article = _entry_to_article(entry, source_name)
            if not _is_recent(article["published"], cutoff):
                continue
            combined = article["title"] + " " + article["summary"]
            if _quick_relevant(combined):
                articles.append(article)
        return articles
    except Exception as e:
        print(f"[WARN] Failed to fetch {source_name} ({url}): {e}")
        return []


def _fetch_google_news(query: str, cutoff: datetime) -> list[dict]:
    url = GOOGLE_NEWS_RSS.format(query=quote_plus(query))
    source_name = f"Google News: {query[:50]}"
    return _fetch_feed(url, source_name, cutoff)


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
            time.sleep(0.3)  # polite crawl delay

    # Aggregator and analysis feeds
    for feed_def in AGGREGATOR_FEEDS:
        articles = _fetch_feed(feed_def["url"], feed_def["name"], cutoff)
        all_articles.extend(articles)
        time.sleep(0.3)

    # Google News queries
    for query in GOOGLE_NEWS_QUERIES:
        articles = _fetch_google_news(query, cutoff)
        all_articles.extend(articles)
        time.sleep(0.5)  # slightly longer to avoid rate-limiting

    # Deduplicate by article ID (based on URL or title)
    deduped = []
    for article in all_articles:
        if article["id"] not in seen_ids:
            seen_ids.add(article["id"])
            deduped.append(article)

    print(f"[INFO] Collected {len(deduped)} unique relevant articles (cutoff: {cutoff.date()})")
    return deduped
