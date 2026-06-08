import os
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import boto3
from botocore.exceptions import ClientError


def _build_plain_text(date_str: str) -> str:
    return (
        f"POP PIXEL DIGEST — {date_str}\n"
        "Your daily entertainment roundup.\n\n"
        "Open this email in an HTML-capable client to view the full digest.\n\n"
        "---\n"
        "You're receiving this because you subscribed to Pop Pixel Digest.\n"
        "To unsubscribe, reply with subject: unsubscribe\n"
    )


def send_digest(to_email: str, html_content: str) -> bool:
    client = boto3.client("ses", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    sender = os.environ["SES_SENDER_EMAIL"]
    date_str = date.today().strftime("%B %d, %Y")
    subject = f"Pop Pixel Digest — {date_str}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Pop Pixel Digest <{sender}>"
    msg["To"] = to_email
    # List-Unsubscribe tells Gmail/Outlook this is a legitimate newsletter
    msg["List-Unsubscribe"] = f"<mailto:{sender}?subject=unsubscribe>"
    msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    msg["Precedence"] = "bulk"

    # Plain text part first — spam filters favor multipart/alternative with text fallback
    msg.attach(MIMEText(_build_plain_text(date_str), "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        client.send_raw_email(
            Source=sender,
            Destinations=[to_email],
            RawMessage={"Data": msg.as_bytes()},
        )
        print(f"[OK] Sent to {to_email}")
        return True
    except ClientError as exc:
        print(f"[ERR] Failed to send to {to_email}: {exc.response['Error']['Message']}")
        return False
