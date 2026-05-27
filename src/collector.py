"""
Fetches articles from RSS/Atom feeds and Google News RSS.

Deliberately simple: feedparser handles all URL fetching directly
(it was designed for this). A socket-level timeout prevents hanging
on slow or unresponsive sources.
"""

import hashlib
import socket
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus

import feedparser
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

from config import (
    AGGREGATOR_FEEDS,
    DAILY_LOOKBACK_HOURS,
    GOOGLE_NEWS_QUERIES,
    LOCALIZED_QUERIES,
    OFFICIAL_FEEDS,
    RELEVANCE_KEYWORDS,
    WEEKLY_LOOKBACK_DAYS,
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search?q={query}"
    "&hl={hl}&gl={gl}&ceid={ceid}"
)

SOCKET_TIMEOUT = 15    # seconds — applies to all feedparser URL fetches
MAX_ARTICLES   = 120   # cap before Groq analysis (raised to accommodate multilingual sources)


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
        try:
            summary = BeautifulSoup(summary, "lxml").get_text(separator=" ", strip=True)
        except Exception:
            pass
    return {
        "id":        _article_id(link, title),
        "title":     title,
        "url":       link,
        "summary":   summary[:1000],
        "source":    source_name,
        "published": _parse_date(entry),
    }


def _fetch_feed(url: str, source_name: str, cutoff: datetime) -> list[dict]:
    """Fetch one feed. Uses feedparser's own URL fetcher with a socket timeout."""
    old_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(SOCKET_TIMEOUT)
        feed = feedparser.parse(url, request_headers=HEADERS)
    except Exception as e:
        print(f"  [FAIL] {source_name}: {e}")
        return []
    finally:
        socket.setdefaulttimeout(old_timeout)

    if feed.bozo and not feed.entries:
        print(f"  [SKIP] {source_name}: feed error — {getattr(feed, 'bozo_exception', 'unknown')}")
        return []

    articles = []
    for entry in feed.entries:
        article = _entry_to_article(entry, source_name)
        if not _is_recent(article["published"], cutoff):
            continue
        if _quick_relevant(article["title"] + " " + article["summary"]):
            articles.append(article)

    total = len(feed.entries)
    if articles:
        print(f"  [OK] {source_name}: {total} entries → {len(articles)} relevant")
    elif total > 0:
        print(f"  [OK] {source_name}: {total} entries → 0 matched keyword filter")
    else:
        print(f"  [EMPTY] {source_name}: no entries in feed")

    return articles


def _fetch_google_news(
    query: str,
    cutoff: datetime,
    hl: str = "en",
    gl: str = "SG",
    ceid: str = "SG:en",
) -> list[dict]:
    url = GOOGLE_NEWS_RSS.format(
        query=quote_plus(query),
        hl=hl,
        gl=gl,
        ceid=ceid,
    )
    lang_tag = "" if hl == "en" else f"[{hl}] "
    return _fetch_feed(url, f"Google News: {lang_tag}{query[:55]}", cutoff)


def collect_weekly() -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=WEEKLY_LOOKBACK_DAYS)
    return _collect(cutoff)


def collect_daily() -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=DAILY_LOOKBACK_HOURS)
    return _collect(cutoff)


def _collect(cutoff: datetime) -> list[dict]:
    all_articles: list[dict] = []
    seen_ids: set[str] = set()

    print("[INFO] === Official feeds ===")
    for jurisdiction, feeds in OFFICIAL_FEEDS.items():
        for feed_def in feeds:
            articles = _fetch_feed(feed_def["url"], feed_def["name"], cutoff)
            for a in articles:
                a["jurisdiction_hint"] = jurisdiction
            all_articles.extend(articles)
            time.sleep(0.3)

    print("[INFO] === Aggregator feeds ===")
    for feed_def in AGGREGATOR_FEEDS:
        all_articles.extend(_fetch_feed(feed_def["url"], feed_def["name"], cutoff))
        time.sleep(0.3)

    print("[INFO] === Google News queries (English) ===")
    for query in GOOGLE_NEWS_QUERIES:
        all_articles.extend(_fetch_google_news(query, cutoff))
        time.sleep(0.5)

    print("[INFO] === Google News queries (local languages) ===")
    for q in LOCALIZED_QUERIES:
        all_articles.extend(_fetch_google_news(
            q["q"], cutoff,
            hl=q.get("hl", "en"),
            gl=q.get("gl", "SG"),
            ceid=q.get("ceid", "SG:en"),
        ))
        time.sleep(0.5)

    # Deduplicate
    deduped = []
    for article in all_articles:
        if article["id"] not in seen_ids:
            seen_ids.add(article["id"])
            deduped.append(article)

    print(f"\n[INFO] Total unique relevant articles collected: {len(deduped)}")

    # Sort newest-first, cap to MAX_ARTICLES
    deduped.sort(
        key=lambda a: a["published"] or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    if len(deduped) > MAX_ARTICLES:
        print(f"[INFO] Capping to {MAX_ARTICLES} most recent")
        deduped = deduped[:MAX_ARTICLES]

    return deduped
