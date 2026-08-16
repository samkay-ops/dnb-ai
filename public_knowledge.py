"""
Public knowledge index for DeenBridge.

Only published content should live here.
Draft / private items must never be added.
"""

from typing import Any

# ---------------------------------------------------------------------------
# Public Knowledge Data (Published only)
# ---------------------------------------------------------------------------

PUBLIC_EVENTS = [
    {
        "id": "evt_001",
        "title": "Ramadan Community Iftar",
        "location": "Lagos, Nigeria",
        "country": "Nigeria",
        "date": "2026-03-15",
        "description": "Community iftar open to all Muslims in Lagos.",
        "published": True,
    },
    {
        "id": "evt_002",
        "title": "Seerah Conference",
        "location": "Abuagh, Nigeria",
        "country": "Nigeria",
        "date": "2026-04-10",
        "description": "A conference on the life of the Prophet ﷺ.",
        "published": True,
    },
]

PUBLIC_SCHOLARSHIPS = [
    {
        "id": "sch_001",
        "title": "Islamic Studies Scholarship 2026",
        "eligibility": "Muslim students in Nigeria",
        "deadline": "2026-05-30",
        "description": "Full scholarship for undergraduate Islamic studies.",
        "published": True,
    },
]

PUBLIC_COURSES = [
    {
        "id": "crs_001",
        "title": "Tajweed for Beginners",
        "educator": "Ustadh Ahmad",
        "description": "A structured course to learn correct Quran recitation.",
        "published": True,
    },
    {
        "id": "crs_002",
        "title": "Fiqh of Worship",
        "educator": "Sheikh Yusuf",
        "description": "Covers purification, salah, and fasting.",
        "published": True,
    },
]

PUBLIC_EDUCATORS = [
    {
        "id": "edu_001",
        "name": "Ustadh Ahmad",
        "specialty": "Tajweed & Quran",
        "published": True,
    },
    {
        "id": "edu_002",
        "name": "Sheikh Yusuf",
        "specialty": "Fiqh",
        "published": True,
    },
]


def get_all_published_items() -> list[dict[str, Any]]:
    """Return all published public knowledge items."""
    items = []
    items.extend(PUBLIC_EVENTS)
    items.extend(PUBLIC_SCHOLARSHIPS)
    items.extend(PUBLIC_COURSES)
    items.extend(PUBLIC_EDUCATORS)
    return [item for item in items if item.get("published") is True]
