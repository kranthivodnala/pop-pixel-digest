import os
from datetime import date

import boto3
from botocore.exceptions import ClientError


def send_digest(to_email: str, html_content: str) -> bool:
    client = boto3.client("ses", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    sender = os.environ["SES_SENDER_EMAIL"]
    subject = f"Pop Pixel Digest — {date.today().strftime('%B %d, %Y')}"

    try:
        client.send_email(
            Source=sender,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {"Html": {"Data": html_content, "Charset": "UTF-8"}},
            },
        )
        print(f"[OK] Sent to {to_email}")
        return True
    except ClientError as exc:
        print(f"[ERR] Failed to send to {to_email}: {exc.response['Error']['Message']}")
        return False
