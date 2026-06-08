"""Create the DynamoDB subscribers table (run once during AWS setup).

Usage: python scripts/setup_dynamodb.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "pop-pixel-digest-subscribers")
REGION = os.environ.get("AWS_REGION", "us-east-1")


def create_table() -> None:
    dynamodb = boto3.client("dynamodb", region_name=REGION)

    try:
        dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",  # serverless — no provisioned capacity needed
        )
        print(f"Table '{TABLE_NAME}' created. Waiting for it to become active...")

        waiter = dynamodb.get_waiter("table_exists")
        waiter.wait(TableName=TABLE_NAME)
        print("Table is active and ready.")
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ResourceInUseException":
            print(f"Table '{TABLE_NAME}' already exists.")
        else:
            raise


if __name__ == "__main__":
    create_table()
