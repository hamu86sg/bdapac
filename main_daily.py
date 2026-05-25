"""
Daily flash entrypoint.
Scans the past ~26 hours for HIGH-significance items.
Sends a flash digest email only if the threshold is met — otherwise silent.
"""

import sys
from datetime import datetime, timezone

sys.path.insert(0, "src")

from analyzer import analyse_articles, filter_relevant, write_flash_summary
from collector import collect_daily
from config import DAILY_FLASH_MIN_HIGH_ITEMS, DAILY_FLASH_MIN_ITEMS
from emailer import send_flash_digest
from pdf_generator import generate_flash_pdf


def main():
    run_date = datetime.now(timezone.utc)
    print(f"[START] Daily check — {run_date.isoformat()}")

    # 1. Collect last ~26h
    raw_articles = collect_daily()
    if not raw_articles:
        print("[INFO] No articles in daily window. No flash sent.")
        return

    # 2. Filter
    relevant = filter_relevant(raw_articles)
    if len(relevant) < DAILY_FLASH_MIN_ITEMS:
        print(f"[INFO] Only {len(relevant)} relevant articles — below threshold. No flash sent.")
        return

    # 3. Analyse
    items = analyse_articles(relevant)

    # 4. Check threshold
    high_items = [i for i in items if i.get("significance") == "HIGH"]

    if len(high_items) < DAILY_FLASH_MIN_HIGH_ITEMS:
        print(f"[INFO] {len(high_items)} HIGH items — below flash threshold ({DAILY_FLASH_MIN_HIGH_ITEMS}). No flash sent.")
        return

    print(f"[INFO] {len(high_items)} HIGH-significance items found — sending flash digest.")

    # 5. Flash summary
    flash_summary = write_flash_summary(high_items, run_date)

    # 6. Extract headline from first item title for email subject
    headline = high_items[0].get("title", "") if high_items else ""

    # 7. Generate PDF
    pdf_bytes = generate_flash_pdf(high_items, flash_summary, run_date)
    print(f"[INFO] Flash PDF generated ({len(pdf_bytes):,} bytes)")

    # 8. Email
    send_flash_digest(pdf_bytes, run_date, headline)
    print("[DONE] Flash digest sent.")


if __name__ == "__main__":
    main()
