"""
Account age calculation utilities
"""

import datetime
import bisect
import requests
import asyncio
from typing import Optional, Dict
from functools import lru_cache

RAW_URL = "https://raw.githubusercontent.com/SantiiRepair/tdage/v1.0.4/ages.go"

# Global cache for known points
_known_points = None
_cache_lock = asyncio.Lock()

def _load_known_points() -> list:
    """
    Load known user ID to creation date mappings from GitHub
    """
    try:
        src = requests.get(RAW_URL, timeout=30)
        src.raise_for_status()
        text = src.text

        # Regex to match the Go map format: user_id: timestamp,
        import re
        pat = re.compile(r'(\d+):\s*(\d+),', re.MULTILINE)

        points = []
        for m in pat.finditer(text):
            user_id = int(m.group(1))
            # Convert milliseconds timestamp to datetime
            timestamp_ms = int(m.group(2))
            timestamp_s = timestamp_ms / 1000.0
            date = datetime.datetime.fromtimestamp(timestamp_s)
            points.append((user_id, date))

        points.sort(key=lambda x: x[0])
        return points

    except Exception as e:
        print(f"Error loading known points: {e}")
        return []

async def _get_known_points() -> list:
    """
    Get known points with caching and thread safety
    """
    global _known_points

    async with _cache_lock:
        if _known_points is None:
            # Load in a thread pool to avoid blocking
            import concurrent.futures
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                _known_points = await loop.run_in_executor(executor, _load_known_points)

    return _known_points or []

@lru_cache(maxsize=10000)
def get_creation_date(user_id: int) -> Optional[datetime.datetime]:
    """
    Get the estimated creation date for a Telegram user ID

    Args:
        user_id: Telegram user ID

    Returns:
        datetime.datetime: Estimated creation date or None if cannot determine
    """
    try:
        # This function needs to be synchronous for lru_cache
        if _known_points is None:
            # Load synchronously for first call
            _known_points_list = _load_known_points()
        else:
            _known_points_list = _known_points

        if not _known_points_list:
            return None

        ids = [p[0] for p in _known_points_list]
        pos = bisect.bisect_left(ids, user_id)

        if pos == 0:
            return _known_points_list[0][1]
        if pos >= len(_known_points_list):
            return _known_points_list[-1][1]

        id_left, date_left = _known_points_list[pos - 1]
        id_right, date_right = _known_points_list[pos]

        span = id_right - id_left
        delta_days = (date_right - date_left).days
        ratio = (user_id - id_left) / span
        est_days = int(delta_days * ratio)
        return date_left + datetime.timedelta(days=est_days)

    except Exception as e:
        print(f"Error calculating creation date for user {user_id}: {e}")
        return None

async def get_account_creation_date(user_id: int) -> Optional[datetime.datetime]:
    """
    Async wrapper for get_creation_date with proper initialization

    Args:
        user_id: Telegram user ID

    Returns:
        datetime.datetime: Estimated creation date or None if cannot determine
    """
    # Ensure known points are loaded
    await _get_known_points()

    # Use the cached synchronous function
    return get_creation_date(user_id)

def format_account_age(creation_date: datetime.datetime) -> str:
    """
    Format account age in a human-readable format

    Args:
        creation_date: Account creation date

    Returns:
        str: Formatted age string
    """
    if not creation_date:
        return "неизвестен"

    now = datetime.datetime.now()
    age = now - creation_date

    days = age.days

    if days < 1:
        return "менее 1 дня"
    elif days < 7:
        return f"{days} дн."
    elif days < 30:
        weeks = days // 7
        return f"{weeks} нед."
    elif days < 365:
        months = days // 30
        return f"{months} мес."
    else:
        years = days // 365
        months = (days % 365) // 30
        if months == 0:
            return f"{years} г."
        else:
            return f"{years} г. {months} мес."