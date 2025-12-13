"""
Excel import/export for SchedularV3.

Real Işık University Excel format support with proper time slot parsing.
Handles formats like: "M1, M2, T3" -> [("Monday", 1), ("Monday", 2), ("Tuesday", 3)]
"""
import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Literal, Union

# TimeSlot is a tuple of (day_name: str, period: int)
TimeSlot = Tuple[str, int]

# CourseType literal type
CourseType = Literal["lecture", "lab", "ps"]

from .models import Course

# Set up logging
logger = logging.getLogger(__name__)

# Day name mappings (abbreviated to full name)
DAY_MAP = {
    "M": "Monday",
    "T": "Tuesday",
    "W": "Wednesday",
    "Th": "Thursday",
    "F": "Friday",
    "S": "Saturday",
    "Su": "Sunday"
}

# Turkish to English column mappings
COLUMN_MAP = {
    "Ders Kodu": "code",
    "Course Code": "code",
    "Kod": "code",

    "Başlık": "name",
    "Course Name": "name",
    "Ders Adı": "name",
    "Ders İsmi": "name",
    "Title": "name",

    "AKTS Kredisi": "ects",
    "AKTS": "ects",
    "ECTS": "ects",
    "Kredi": "ects",
    "Credit": "ects",
    "Yerel Kredi": "local_credit",

    "Kampüs": "campus",
    "Campus": "campus",

    "Eğitmen Adı": "teacher_first",
    "Teacher First Name": "teacher_first",
    "Instructor First": "teacher_first",

    "Eğitmen Soyadı": "teacher_last",
    "Teacher Last Name": "teacher_last",
    "Instructor Last": "teacher_last",

    "Fakülte Adı": "faculty",
    "Faculty": "faculty",
    "Fakülte": "faculty",

    "Ders Saati": "schedule",  # Correct: Contains "M1, T2" format
    # NOTE: "Ders Saati(leri)" is NOT included - it contains hour count (numeric), not time slots!
    "Schedule": "schedule",
    "Time Slots": "schedule",
    "Zaman": "schedule"
}


def parse_time_slot(slot_str: str) -> Optional[TimeSlot]:
    """
    Parse a single time slot string like "M1", "Th5", "T10" into (day, period).

    Args:
        slot_str: Time slot string (e.g., "M1", "Th5")

    Returns:
        Tuple of (day_name, period_number) or None if invalid

    Examples:
        "M1" -> ("Monday", 1)
        "Th5" -> ("Thursday", 5)
        "F10" -> ("Friday", 10)
    """
    slot_str = slot_str.strip()

    if not slot_str:
        return None

    # Try two-character day codes first (Th, Su)
    for abbr, full_name in [("Th", "Thursday"), ("Su", "Sunday")]:
        if slot_str.startswith(abbr):
            try:
                period_str = slot_str[len(abbr):].strip()
                if period_str:
                    period = int(period_str)
                    if period > 0:
                        return (full_name, period)
                    else:
                        logger.warning(f"Invalid period number (must be > 0) in slot: {slot_str}")
                        return None
            except ValueError:
                logger.warning(f"Invalid period number in slot: {slot_str}")
                return None

    # Try single-character day codes
    if len(slot_str) >= 2:
        day_abbr = slot_str[0]
        if day_abbr in DAY_MAP:
            try:
                period_str = slot_str[1:].strip()
                if period_str:
                    period = int(period_str)
                    if period > 0:
                        return (DAY_MAP[day_abbr], period)
                    else:
                        logger.warning(f"Invalid period number (must be > 0) in slot: {slot_str}")
                        return None
            except ValueError:
                logger.warning(f"Invalid period number in slot: {slot_str}")
                return None

    logger.warning(f"Could not parse time slot: {slot_str}")
    return None


def parse_schedule(schedule_str: str) -> List[TimeSlot]:
    """
    Parse schedule string into list of TimeSlot tuples.

    Args:
        schedule_str: Schedule string like "M1, M2, T3" or "Th5, Th6, F7"

    Returns:
        List of (day, period) tuples

    Examples:
        "M1, M2, T3" -> [("Monday", 1), ("Monday", 2), ("Tuesday", 3)]
        "Th5, F10" -> [("Thursday", 5), ("Friday", 10)]
    """
    if not schedule_str or pd.isna(schedule_str):
        return []

    schedule_str = str(schedule_str).strip()
    if not schedule_str:
        return []

    # If it's just a number (like "3"), it's not a valid schedule - skip it
    try:
        float(schedule_str)  # Will succeed if it's a pure number
        # It's a number, not a schedule string - return empty
        return []
    except ValueError:
        pass  # Good, it's not a pure number

    slots = []
    # Split by comma and process each slot
    for slot in schedule_str.split(","):
        parsed = parse_time_slot(slot)
        if parsed:
            slots.append(parsed)

    return slots


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names from Turkish/English to standard internal names.

    Args:
        df: DataFrame with original column names

    Returns:
        DataFrame with normalized column names
    """
    # Create a mapping of current columns to normalized names
    column_mapping = {}
    for col in df.columns:
        if col in COLUMN_MAP:
            column_mapping[col] = COLUMN_MAP[col]

    # Rename columns
    df = df.rename(columns=column_mapping)

    return df


def determine_course_type(code: str) -> CourseType:
    """
    Determine course type from course code.

    Args:
        code: Course code (e.g., "COMP1111.1", "COMP1111-L.1", "COMP2112-PS.1")

    Returns:
        Course type: "lecture", "lab", or "ps"
    """
    if not code:
        return "lecture"

    code_upper = code.upper()

    if "-L." in code_upper or "-LAB." in code_upper or code_upper.endswith("-L"):
        return "lab"
    elif "-PS." in code_upper or code_upper.endswith("-PS"):
        return "ps"
    else:
        return "lecture"


def extract_main_code(code: str) -> str:
    """
    Extract main course code without section info.

    Args:
        code: Full course code (e.g., "COMP1111.1", "COMP1111-L.1")

    Returns:
        Main course code (e.g., "COMP1111")
    """
    if not code:
        return ""

    # Remove section info after . or -
    for sep in ["-", "."]:
        if sep in code:
            return code.split(sep)[0].strip()
    return code.strip()


def process_excel(
    file_path: Union[str, Path],
    sheet_name: Union[str, int] = 0
) -> List[Course]:
    """
    Load courses from an Excel file in Işık University format.

    Expected columns:
        - Ders Kodu / Course Code
        - Başlık / Course Name
        - AKTS Kredisi / ECTS
        - Kampüs / Campus
        - Eğitmen Adı / Teacher First Name
        - Eğitmen Soyadı / Teacher Last Name
        - Fakülte Adı / Faculty
        - Ders Saati(leri) / Schedule

    Args:
        file_path: Path to Excel file
        sheet_name: Sheet name or index (default: 0 for first sheet)

    Returns:
        List of Course objects

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If required columns are missing
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    try:
        # Read Excel file
        df = pd.read_excel(str(file_path), sheet_name=sheet_name)
        logger.info(f"Loaded Excel file with {len(df)} rows")

        # Normalize column names
        df = normalize_columns(df)

        # Check for required columns
        required = ["code", "name", "ects", "schedule"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}. Available columns: {list(df.columns)}")

        courses = []

        for idx, row in df.iterrows():
            try:
                # Parse basic info
                code = str(row["code"]).strip() if pd.notna(row["code"]) else ""
                if not code or code == "nan":
                    logger.warning(f"Row {idx}: Missing or invalid course code, skipping")
                    continue

                name = str(row["name"]).strip() if pd.notna(row["name"]) else ""
                if not name or name == "nan":
                    logger.warning(f"Row {idx}: Missing course name for {code}, skipping")
                    continue

                # Parse ECTS with better error handling
                ects = 0
                if pd.notna(row["ects"]):
                    try:
                        ects = int(float(row["ects"]))
                    except (ValueError, TypeError):
                        logger.warning(f"Row {idx}: Invalid ECTS value '{row['ects']}' for {code}, using 0")
                        ects = 0

                # Parse schedule
                schedule_str = ""
                if "schedule" in df.columns and pd.notna(row["schedule"]):
                    # Handle potential Series objects (when multiple columns map to same name)
                    sched_value = row["schedule"]
                    if isinstance(sched_value, pd.Series):
                        # Take the first non-empty value from the Series
                        for val in sched_value:
                            if pd.notna(val) and str(val).strip() and str(val).strip() != "nan":
                                # Check if it looks like a time slot (contains letters)
                                val_str = str(val).strip()
                                if any(c.isalpha() for c in val_str):
                                    schedule_str = val_str
                                    break
                    else:
                        schedule_str = str(sched_value).strip()

                schedule = parse_schedule(schedule_str)

                # Determine course type from code
                course_type: CourseType = determine_course_type(code)

                # Extract main code
                main_code = extract_main_code(code)

                # Build teacher name
                teacher = None
                if "teacher_first" in df.columns and "teacher_last" in df.columns:
                    first = str(row["teacher_first"]).strip() if pd.notna(row["teacher_first"]) else ""
                    last = str(row["teacher_last"]).strip() if pd.notna(row["teacher_last"]) else ""

                    # Remove 'nan' strings
                    if first == "nan":
                        first = ""
                    if last == "nan":
                        last = ""

                    if first and last:
                        teacher = f"{first} {last}"
                    elif first:
                        teacher = first
                    elif last:
                        teacher = last

                # Get optional fields with better validation
                faculty = "Unknown Faculty"
                if "faculty" in df.columns and pd.notna(row.get("faculty")):
                    fac_str = str(row["faculty"]).strip()
                    if fac_str and fac_str != "nan":
                        faculty = fac_str

                campus = "Main"
                if "campus" in df.columns and pd.notna(row.get("campus")):
                    camp_str = str(row["campus"]).strip()
                    if camp_str and camp_str != "nan":
                        campus = camp_str

                # Determine if it has lecture
                has_lecture = course_type == "lecture"

                # Create Course object
                course = Course(
                    code=code,
                    main_code=main_code,
                    name=name,
                    ects=ects,
                    course_type=course_type,
                    schedule=schedule,
                    teacher=teacher,
                    has_lecture=has_lecture,
                    faculty=faculty,
                    campus=campus
                )

                courses.append(course)

            except Exception as e:
                logger.warning(f"Error processing row {idx}: {e}")
                continue

        logger.info(f"Successfully loaded {len(courses)} courses")
        return courses

    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        raise


def format_schedule_for_excel(schedule: List[TimeSlot]) -> str:
    """
    Format schedule list back to Excel string format.

    Args:
        schedule: List of (day, period) tuples

    Returns:
        Formatted string like "M1, M2, T3"
    """
    if not schedule:
        return ""

    # Handle dictionary format (Course.schedule)
    if isinstance(schedule, dict):
        flat_schedule = []
        for day, slots in schedule.items():
            for slot in slots:
                flat_schedule.append((day, slot))
        schedule = flat_schedule

    # Reverse day mapping (include special cases)
    day_to_abbr = {
        "Monday": "M",
        "Tuesday": "T",
        "Wednesday": "W",
        "Thursday": "Th",
        "Friday": "F",
        "Saturday": "S",
        "Sunday": "Su"
    }

    slot_strings = []
    for day, period in schedule:
        abbr = day_to_abbr.get(day, day[:2] if len(day) >= 2 else day[0])
        slot_strings.append(f"{abbr}{period}")

    return ", ".join(slot_strings)


def save_courses_to_excel(
    courses: List[Course],
    file_path: Union[str, Path],
    sheet_name: str = "Courses"
) -> None:
    """
    Save courses to an Excel file in Işık University format.

    Args:
        courses: List of Course objects to save
        file_path: Output Excel file path
        sheet_name: Sheet name (default: "Courses")
    """
    if not courses:
        # Create empty DataFrame with correct columns
        df = pd.DataFrame(columns=[
            "Ders Kodu", "Başlık", "Yerel Kredi", "AKTS Kredisi",
            "Kampüs", "Eğitmen Adı", "Eğitmen Soyadı", "Fakülte Adı", "Ders Saati(leri)"
        ])
    else:
        data = []
        for course in courses:
            # Split teacher name
            teacher_first = ""
            teacher_last = ""
            if course.teacher:
                parts = course.teacher.split()
                if len(parts) >= 2:
                    teacher_first = " ".join(parts[:-1])
                    teacher_last = parts[-1]
                else:
                    teacher_first = course.teacher

            data.append({
                "Ders Kodu": course.code,
                "Başlık": course.name,
                "Yerel Kredi": course.ects,  # Can be adjusted
                "AKTS Kredisi": course.ects,
                "Kampüs": course.campus,
                "Eğitmen Adı": teacher_first,
                "Eğitmen Soyadı": teacher_last,
                "Fakülte Adı": course.faculty,
                "Ders Saati(leri)": format_schedule_for_excel(course.schedule)
            })

        df = pd.DataFrame(data)

    # Save to Excel
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_excel(str(file_path), sheet_name=sheet_name, index=False)
    logger.info(f"Saved {len(courses)} courses to {file_path}")
