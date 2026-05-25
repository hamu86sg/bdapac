"""
Sends PDF reports via Gmail SMTP using an app password.
"""

import os
import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def _build_message(
    sender: str,
    recipient: str,
    subject: str,
    body_text: str,
    pdf_bytes: bytes,
    pdf_filename: str,
) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg["From"]    = f"WWT APAC Monitor <{sender}>"
    msg["To"]      = recipient
    msg["Subject"] = subject

    msg.attach(MIMEText(body_text, "plain"))

    attachment = MIMEBase("application", "pdf")
    attachment.set_payload(pdf_bytes)
    encoders.encode_base64(attachment)
    attachment.add_header(
        "Content-Disposition",
        "attachment",
        filename=pdf_filename,
    )
    msg.attach(attachment)
    return msg


def send_weekly_report(pdf_bytes: bytes, run_date: datetime) -> None:
    sender       = os.environ["GMAIL_SENDER"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]
    recipient    = os.environ["RECIPIENT_EMAIL"]

    date_str     = run_date.strftime("%d %b %Y")
    subject      = f"APAC Regulatory Intelligence Memo — {date_str}"
    pdf_filename = f"APAC_Reg_Memo_{run_date.strftime('%Y%m%d')}.pdf"

    body = (
        f"Please find attached the APAC Regulatory Intelligence Memo for the week "
        f"ending {date_str}.\n\n"
        "This report covers recent, impending, and rumoured changes in laws and "
        "regulations across 13 Asia Pacific jurisdictions that may affect IT "
        "requirements for government agencies and WWT's enterprise customers.\n\n"
        "—\nWWT APAC Regulatory Monitor\n"
        "Automated report | Reply with any questions or feedback"
    )

    msg = _build_message(sender, recipient, subject, body, pdf_bytes, pdf_filename)
    _send(sender, app_password, recipient, msg)
    print(f"[INFO] Weekly report emailed to {recipient}")


def send_flash_digest(pdf_bytes: bytes, run_date: datetime, headline: str = "") -> None:
    sender       = os.environ["GMAIL_SENDER"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]
    recipient    = os.environ["RECIPIENT_EMAIL"]

    date_str     = run_date.strftime("%d %b %Y")
    subject      = f"⚡ APAC Reg Flash — {date_str}"
    if headline:
        subject += f": {headline[:60]}"
    pdf_filename = f"APAC_Reg_Flash_{run_date.strftime('%Y%m%d')}.pdf"

    body = (
        f"A significant regulatory development was detected today ({date_str}) "
        "in Asia Pacific markets.\n\n"
        "Please see the attached flash digest for details.\n\n"
        "—\nWWT APAC Regulatory Monitor"
    )

    msg = _build_message(sender, recipient, subject, body, pdf_bytes, pdf_filename)
    _send(sender, app_password, recipient, msg)
    print(f"[INFO] Flash digest emailed to {recipient}")


def _send(sender: str, app_password: str, recipient: str, msg: MIMEMultipart) -> None:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, app_password)
        smtp.sendmail(sender, [recipient], msg.as_string())
