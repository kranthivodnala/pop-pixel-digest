"""Add an email address to the subscriber list.

Usage: python scripts/subscribe.py <email>
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from src.subscriber_manager import add_subscriber

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/subscribe.py <email>")
        sys.exit(1)
    add_subscriber(sys.argv[1])
