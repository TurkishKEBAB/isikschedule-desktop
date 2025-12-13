"""
ICS Calendar Export Module for SchedularV3.

This module provides functionality to export course schedules to the iCalendar
(.ics) format, allowing users to import their schedules into calendar
applications like Google Calendar, Outlook, and Apple Calendar.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from core.models import Course, Schedule

# iCalendar format constants
VCALENDAR_HEADER = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//SchedularV3//Course Schedule//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:{calendar_name}
X-WR-TIMEZONE:Europe/Istanbul
"""

VTIMEZONE_ISTANBUL = """BEGIN:VTIMEZONE
TZID:Europe/Istanbul
X-LIC-LOCATION:Europe/Istanbul
BEGIN:STANDARD
TZOFFSETFROM:+0300
TZOFFSETTO:+0300
TZNAME:TRT
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE
"""

VEVENT_TEMPLATE = """BEGIN:VEVENT
DTSTART;TZID=Europe/Istanbul:{start_dt}
DTEND;TZID=Europe/Istanbul:{end_dt}
RRULE:FREQ=WEEKLY;COUNT={weeks}
DTSTAMP:{timestamp}
UID:{uid}
SUMMARY:{summary}
DESCRIPTION:{description}
LOCATION:{location}
CATEGORIES:{category}
STATUS:CONFIRMED
TRANSP:OPAQUE
END:VEVENT
"""

VCALENDAR_FOOTER = "END:VCALENDAR\n"

# Day name to weekday number mapping (Monday=0 for Python, but we use iCalendar's MO, TU, etc.)
DAY_NAME_TO_WEEKDAY = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
    "Pazartesi": 0,
    "Salı": 1,
    "Çarşamba": 2,
    "Perşembe": 3,
    "Cuma": 4,
    "Cumartesi": 5,
    "Pazar": 6,
}

# Slot number to time mapping (assuming 1-hour slots starting at 8:30 AM)
# Slot 1 = 08:30-09:20, Slot 2 = 09:30-10:20, etc.
SLOT_START_TIMES = {
    1: (8, 30),
    2: (9, 30),
    3: (10, 30),
    4: (11, 30),
    5: (12, 30),
    6: (13, 30),
    7: (14, 30),
    8: (15, 30),
    9: (16, 30),
    10: (17, 30),
    11: (18, 30),
    12: (19, 30),
    13: (20, 30),
}

SLOT_DURATION_MINUTES = 50  # Standard class duration


def _generate_uid(course_code: str, day: str, slot: int) -> str:
    """Generate a unique identifier for a calendar event."""
    unique_string = f"{course_code}-{day}-{slot}-{uuid.uuid4().hex[:8]}"
    return f"{hashlib.md5(unique_string.encode()).hexdigest()}@schedularv3.local"


def _escape_ics_text(text: str) -> str:
    """Escape special characters for ICS format."""
    if not text:
        return ""
    # Escape backslashes first, then other special characters
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;")
    text = text.replace(",", "\\,")
    text = text.replace("\n", "\\n")
    return text


def _get_next_weekday(start_date: datetime, weekday: int) -> datetime:
    """Get the next occurrence of a specific weekday from start_date."""
    days_ahead = weekday - start_date.weekday()
    if days_ahead < 0:  # Target day already happened this week
        days_ahead += 7
    return start_date + timedelta(days=days_ahead)


def _slot_to_datetime(
    base_date: datetime, day_name: str, slot: int
) -> Tuple[datetime, datetime]:
    """
    Convert a day name and slot number to start and end datetime objects.

    Args:
        base_date: The reference date (typically semester start)
        day_name: Day of the week (e.g., "Monday", "Pazartesi")
        slot: Time slot number (1-13)

    Returns:
        Tuple of (start_datetime, end_datetime)
    """
    weekday = DAY_NAME_TO_WEEKDAY.get(day_name, 0)
    event_date = _get_next_weekday(base_date, weekday)

    start_hour, start_minute = SLOT_START_TIMES.get(slot, (8, 30))
    start_dt = event_date.replace(hour=start_hour, minute=start_minute, second=0)
    end_dt = start_dt + timedelta(minutes=SLOT_DURATION_MINUTES)

    return start_dt, end_dt


def _format_datetime(dt: datetime) -> str:
    """Format datetime for ICS (YYYYMMDDTHHMMSS)."""
    return dt.strftime("%Y%m%dT%H%M%S")


def _create_event(
    course: "Course",
    day: str,
    slot: int,
    semester_start: datetime,
    semester_weeks: int = 14,
) -> str:
    """
    Create an ICS VEVENT for a single course time slot.

    Args:
        course: Course object
        day: Day of the week
        slot: Time slot number
        semester_start: Start date of the semester
        semester_weeks: Number of weeks in the semester

    Returns:
        ICS VEVENT string
    """
    start_dt, end_dt = _slot_to_datetime(semester_start, day, slot)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")

    # Build description
    description_parts = [
        f"Course Code: {course.code}",
        f"ECTS: {course.ects}",
        f"Type: {course.course_type}",
    ]
    if course.teacher:
        description_parts.append(f"Instructor: {course.teacher}")

    description = "\\n".join(description_parts)

    # Determine location (if available)
    location = getattr(course, "room", "") or getattr(course, "location", "") or ""

    # Category based on course type
    category = course.course_type.upper() if course.course_type else "LECTURE"

    return VEVENT_TEMPLATE.format(
        start_dt=_format_datetime(start_dt),
        end_dt=_format_datetime(end_dt),
        weeks=semester_weeks,
        timestamp=timestamp,
        uid=_generate_uid(course.code, day, slot),
        summary=_escape_ics_text(f"{course.main_code} - {course.name}"),
        description=_escape_ics_text(description),
        location=_escape_ics_text(location),
        category=category,
    )


def export_schedule_to_ics(
    schedule: "Schedule",
    output_path: Path,
    calendar_name: str = "Course Schedule",
    semester_start: Optional[datetime] = None,
    semester_weeks: int = 14,
) -> Path:
    """
    Export a schedule to an ICS calendar file.

    Args:
        schedule: Schedule object containing courses
        output_path: Path where the ICS file will be saved
        calendar_name: Name for the calendar
        semester_start: Start date of the semester (defaults to next Monday)
        semester_weeks: Number of weeks in the semester

    Returns:
        Path to the created ICS file
    """
    if semester_start is None:
        # Default to next Monday
        today = datetime.now()
        semester_start = _get_next_weekday(today, 0)  # 0 = Monday

    # Build calendar content
    content_parts = [
        VCALENDAR_HEADER.format(calendar_name=_escape_ics_text(calendar_name)),
        VTIMEZONE_ISTANBUL,
    ]

    # Create events for each course and time slot
    for course in schedule.courses:
        for day, slot in course.schedule:
            event = _create_event(
                course, day, slot, semester_start, semester_weeks
            )
            content_parts.append(event)

    content_parts.append(VCALENDAR_FOOTER)

    # Write to file
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("".join(content_parts))

    return output_path


def export_schedules_to_ics(
    schedules: List["Schedule"],
    output_dir: Path,
    base_name: str = "schedule",
    semester_start: Optional[datetime] = None,
    semester_weeks: int = 14,
) -> List[Path]:
    """
    Export multiple schedules to separate ICS files.

    Args:
        schedules: List of Schedule objects
        output_dir: Directory where ICS files will be saved
        base_name: Base name for the files (will be numbered)
        semester_start: Start date of the semester
        semester_weeks: Number of weeks in the semester

    Returns:
        List of paths to created ICS files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    created_files = []
    for i, schedule in enumerate(schedules, start=1):
        file_name = f"{base_name}_{i}.ics"
        file_path = output_dir / file_name
        calendar_name = f"Schedule Option {i}"

        export_schedule_to_ics(
            schedule,
            file_path,
            calendar_name=calendar_name,
            semester_start=semester_start,
            semester_weeks=semester_weeks,
        )
        created_files.append(file_path)

    return created_files


__all__ = [
    "export_schedule_to_ics",
    "export_schedules_to_ics",
    "SLOT_START_TIMES",
    "SLOT_DURATION_MINUTES",
]
