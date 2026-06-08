import os
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Attr

TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "pop-pixel-digest-subscribers")


def _table():
    dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    return dynamodb.Table(TABLE_NAME)


def get_all_subscribers() -> list[str]:
    table = _table()
    emails = []
    scan_kwargs = {"FilterExpression": Attr("is_active").eq(True)}

    while True:
        resp = table.scan(**scan_kwargs)
        emails.extend(item["email"] for item in resp.get("Items", []))
        last_key = resp.get("LastEvaluatedKey")
        if not last_key:
            break
        scan_kwargs["ExclusiveStartKey"] = last_key

    return emails


def add_subscriber(email: str) -> None:
    _table().put_item(Item={
        "email": email,
        "subscribed_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
    })
    print(f"Subscribed: {email}")


def remove_subscriber(email: str) -> None:
    _table().update_item(
        Key={"email": email},
        UpdateExpression="SET is_active = :val",
        ExpressionAttributeValues={":val": False},
    )
    print(f"Unsubscribed: {email}")
