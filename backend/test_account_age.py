#!/usr/bin/env python3
"""
Test account age functionality
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.account_age import get_account_creation_date, format_account_age


async def test_account_age():
    """Test account age calculation"""
    print("Testing account age functionality...")

    # Test with the example ID from the original code
    test_id = 6213118742

    try:
        creation_date = await get_account_creation_date(test_id)
        if creation_date:
            print(f"User ID {test_id} creation date: {creation_date}")
            age_formatted = format_account_age(creation_date)
            print(f"Formatted age: {age_formatted}")
        else:
            print(f"Could not determine creation date for user ID {test_id}")
    except Exception as e:
        print(f"Error testing account age: {e}")

    # Test with another ID
    test_id2 = 123456789
    try:
        creation_date2 = await get_account_creation_date(test_id2)
        if creation_date2:
            print(f"User ID {test_id2} creation date: {creation_date2}")
            age_formatted2 = format_account_age(creation_date2)
            print(f"Formatted age: {age_formatted2}")
        else:
            print(f"Could not determine creation date for user ID {test_id2}")
    except Exception as e:
        print(f"Error testing account age for second ID: {e}")

    print("Test completed.")


if __name__ == "__main__":
    asyncio.run(test_account_age())
