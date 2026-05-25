"""
Sends PDF reports via Resend (resend.com) — free tier, no SMTP setup required.
"""

import base64
import os
from datetime import datetime

import resend

resend.api_key = os.environ["RESEND_API_KEY"]

_SENDER    = "APAC Regulatory Monitor <onboarding@resend.dev>"


def _send(recipient: str, subject: str, body: str, pdf_bytes: bytes, filename: str) -> None:
    params = {
        "from":    _SENDER,
        "to":      [recipient],
        "subject": subject,
        "text":    body,
        "attachments": [
            {
                "filename": filename,
                "content":  list(base64.b64encode(pdf_bytes)),
            }
        ],
    }
    resend.Emails.send(params)


def send_weekly_report(pdf_bytes: bytes, run_date: datetime) -> None:
    recipient = os.environ["RECIPIENT_EMAIL"]
    date_str  = run_date.strftime("%d %b %Y")

    _send(
        recipient = recipient,
        subject   = f"APAC Regulatory Intelligence Memo — {date_str}",
        body      = (
            f"Please find attached the APAC Regulatory Intelligence Memo for the week "
            f"ending {date_str}.\n\n"
            "This report covers recent, impending, and rumoured changes in laws and "
            "regulations across 13 Asia Pacific jurisdictions that may affect IT "
            "requirements for government agencies and WWT's enterprise customers.\n\n"
            "—\nWWT APAC Regulatory Monitor\n"
            "Automated report | Reply with any questions or feedback"
        ),
        pdf_bytes = pdf_bytes,
        filename  = f"APAC_Reg_Memo_{run_date.strftime('%Y%m%d')}.pdf",
    )
    print(f"[INFO] Weekly report emailed to {recipient}")


def send_flash_digest(pdf_bytes: bytes, run_date: datetime, headline: str = "") -> None:
    recipient = os.environ["RECIPIENT_EMAIL"]
    date_str  = run_date.strftime("%d %b %Y")
    subject   = f"APAC Reg Flash — {date_str}"
    if headline:
        subject += f": {headline[:60]}"

    _send(
        recipient = recipient,
        subject   = subject,
        body      = (
            f"A significant regulatory development was detected today ({date_str}) "
            "in Asia Pacific markets.\n\n"
            "Please see the attached flash digest for details.\n\n"
            "—\nWWT APAC Regulatory Monitor"
        ),
        pdf_bytes = pdf_bytes,
        filename  = f"APAC_Reg_Flash_{run_date.strftime('%Y%m%d')}.pdf",
    )
    print(f"[INFO] Flash digest emailed to {recipient}")
