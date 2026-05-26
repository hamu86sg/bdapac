"""
PDF delivery — saves locally for GitHub Actions artifact upload.
Email via Resend is optional: only activates if RESEND_API_KEY is set.
This means the system works immediately with no external service signup.
"""

import base64
import os
from datetime import datetime


def save_weekly_report(pdf_bytes: bytes, run_date: datetime) -> str:
    """Save PDF to disk. GitHub Actions will upload it as an artifact."""
    filename = f"APAC_Reg_Memo_{run_date.strftime('%Y%m%d')}.pdf"
    with open(filename, "wb") as f:
        f.write(pdf_bytes)
    print(f"[INFO] Weekly report saved as {filename} ({len(pdf_bytes):,} bytes)")
    _try_email_weekly(pdf_bytes, run_date, filename)
    return filename


def save_flash_digest(pdf_bytes: bytes, run_date: datetime, headline: str = "") -> str:
    """Save flash PDF to disk. GitHub Actions will upload it as an artifact."""
    filename = f"APAC_Reg_Flash_{run_date.strftime('%Y%m%d')}.pdf"
    with open(filename, "wb") as f:
        f.write(pdf_bytes)
    print(f"[INFO] Flash digest saved as {filename} ({len(pdf_bytes):,} bytes)")
    _try_email_flash(pdf_bytes, run_date, filename, headline)
    return filename


# ── Optional email delivery (skipped if RESEND_API_KEY not set) ───────────────

def _try_email_weekly(pdf_bytes: bytes, run_date: datetime, filename: str) -> None:
    api_key = os.environ.get("RESEND_API_KEY", "")
    if not api_key:
        print("[INFO] RESEND_API_KEY not set — skipping email, artifact upload only")
        return
    try:
        import resend
        resend.api_key = api_key
        date_str = run_date.strftime("%d %b %Y")
        resend.Emails.send({
            "from":    "APAC Regulatory Monitor <onboarding@resend.dev>",
            "to":      [os.environ["RECIPIENT_EMAIL"]],
            "subject": f"APAC Regulatory Intelligence Memo — {date_str}",
            "text": (
                f"Please find attached the APAC Regulatory Intelligence Memo for the "
                f"week ending {date_str}.\n\n"
                "This report covers recent, impending, and rumoured regulatory changes "
                "across 13 Asia Pacific jurisdictions that may affect IT requirements "
                "for government agencies and WWT's enterprise customers.\n\n"
                "—\nWWT APAC Regulatory Monitor"
            ),
            "attachments": [{"filename": filename, "content": list(base64.b64encode(pdf_bytes))}],
        })
        print(f"[INFO] Weekly report also emailed to {os.environ['RECIPIENT_EMAIL']}")
    except Exception as e:
        print(f"[WARN] Email send failed (PDF still saved as artifact): {e}")


def _try_email_flash(pdf_bytes: bytes, run_date: datetime, filename: str, headline: str) -> None:
    api_key = os.environ.get("RESEND_API_KEY", "")
    if not api_key:
        print("[INFO] RESEND_API_KEY not set — skipping email, artifact upload only")
        return
    try:
        import resend
        resend.api_key = api_key
        date_str = run_date.strftime("%d %b %Y")
        subject  = f"⚡ APAC Reg Flash — {date_str}"
        if headline:
            subject += f": {headline[:60]}"
        resend.Emails.send({
            "from":    "APAC Regulatory Monitor <onboarding@resend.dev>",
            "to":      [os.environ["RECIPIENT_EMAIL"]],
            "subject": subject,
            "text": (
                f"A significant regulatory development was detected today ({date_str}) "
                "in Asia Pacific markets. Please see the attached flash digest.\n\n"
                "—\nWWT APAC Regulatory Monitor"
            ),
            "attachments": [{"filename": filename, "content": list(base64.b64encode(pdf_bytes))}],
        })
        print(f"[INFO] Flash digest also emailed to {os.environ['RECIPIENT_EMAIL']}")
    except Exception as e:
        print(f"[WARN] Email send failed (PDF still saved as artifact): {e}")
