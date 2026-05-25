"""
Weekly report entrypoint.
Collects the past 7 days of articles, analyses them, generates the PDF memo,
and emails it to the configured recipient.
"""

import sys
from datetime import datetime, timezone

sys.path.insert(0, "src")

from analyzer import analyse_articles, filter_relevant, write_executive_summary
from collector import collect_weekly
from emailer import send_weekly_report
from pdf_generator import generate_weekly_pdf


def main():
    run_date = datetime.now(timezone.utc)
    print(f"[START] Weekly report run — {run_date.isoformat()}")

    # 1. Collect
    raw_articles = collect_weekly()
    if not raw_articles:
        print("[WARN] No articles collected. Check source connectivity.")

    # 2. Filter
    relevant = filter_relevant(raw_articles)
    if not relevant:
        print("[WARN] No relevant articles after filtering. Report will be sparse.")

    # 3. Analyse
    items = analyse_articles(relevant)

    # 4. Executive summary
    exec_summary = write_executive_summary(items, run_date)

    # 5. Generate PDF
    pdf_bytes = generate_weekly_pdf(items, exec_summary, run_date)
    print(f"[INFO] PDF generated ({len(pdf_bytes):,} bytes)")

    # 6. Email
    send_weekly_report(pdf_bytes, run_date)
    print("[DONE] Weekly report complete.")


if __name__ == "__main__":
    main()
