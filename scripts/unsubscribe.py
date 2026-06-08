"""Remove an email address from the subscriber list.

Usage: python scripts/unsubscribe.py <email>
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from src.subscriber_manager import remove_subscriber

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/unsubscribe.py <email>")
        sys.exit(1)
    remove_subscriber(sys.argv[1])
