"""
Excel data loading and processing for SchedularV3.

Enhanced from V2 with:
- Better error handling
- Support for multiple Excel formats
- Turkish character support
- Improved schedule parsing
"""
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging

from .models import Course

# Set up logging
logger = logging.getLogger(__name__)

# Default values for missing columns
DEFAULT_FACULTY = "Unknown Faculty"
DEFAULT_DEPARTMENT = "Unknown Department"
DEFAULT_CAMPUS = "Main"


def process_excel(file_path: str, sheet_name: str = 0) -> List[Course]:
    """
    Load courses from an Excel file and convert to Course objects.

    Supports additional columns: Faculty, Department, and Campus.
    If these columns are not present, default values will be used.

    Args:
        file_path: Path to the Excel file
        sheet_name: Name or index of the sheet to load (default: 0)

    Returns:
        List of Course objects

    Raises:
        ValueError: If the file cannot be processed or required columns are missing
        FileNotFoundError: If the file doesn't exist
    """
    # Check if file exists
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    try:
        # Try reading with first row as header
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Normalize column names (handle both English and Turkish)
        df = normalize_columns(df)
        
        # Validate required columns
        if "Code" not in df.columns:
            raise ValueError("Expected column 'Code' or 'Ders Kodu' not found.")
            
        logger.info(f"Successfully loaded Excel file: {file_path}")
        logger.info(f"Found {len(df)} rows")
        
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        
        # Try fallback approach with header=None
        try:
            logger.info("Trying fallback Excel reading method...")
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            
            if df.shape[1] >= 5:
                df.columns = ["Code", "Lecture Name", "Credit", "Hour", "Lecture Instructor"] + \
                             [f"Extra{i}" for i in range(df.shape[1] - 5)]
            else:
                df.columns = ["Code", "Lecture Name", "Credit", "Hour"]
            
            # Add missing Faculty, Department, Campus columns with defaults
            df = add_missing_columns(df)
            logger.info("Fallback Excel reading successful")
            
        except Exception as e2:
            logger.error(f"Fallback Excel reading failed: {e2}")
            raise ValueError(f"Could not process Excel file: {e}") from e

    # Determine teacher column name
    teacher_col = "Lecture Instructor" if "Lecture Instructor" in df.columns else None
    
    courses = []
    errors = 0

    for idx, row in df.iterrows():
        try:
            course_dict = _process_row(row, teacher_col)
            course = Course.from_dict(course_dict)
            courses.append(course)
        except Exception as e:
            errors += 1
            logger.warning(f"Error processing row {idx}: {e}")
            continue

    logger.info(f"Successfully processed {len(courses)} courses ({errors} errors)")
    return courses


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names, handling both English and Turkish names.
    Also ensures that Faculty, Department, and Campus columns are present.

    Args:
        df: DataFrame with original column names

    Returns:
        DataFrame with normalized column names
    """
    # Map Turkish column names to English
    column_mapping = {
        # Core columns
        "Ders Kodu": "Code",
        "Başlık": "Lecture Name",
        "AKTS Kredisi": "Credit",
        "Ders Saati(leri)": "Hour",
        "Ders Saati": "Hour",  # Alternative name
        
        # Instructor columns
        "Eğitmen Adı": "Instructor First Name",
        "Eğitmen Soyadı": "Instructor Last Name",
        
        # New columns with possible Turkish variants
        "Fakülte Adı": "Faculty",
        "Fakülte": "Faculty",
        "Kampüs": "Campus",
        "Bölüm": "Department",
        "Bölüm Adı": "Department",
        
        # Additional columns from the real data format
        "Yerel Kredi": "Local Credit",
        "Kalan /": "Remaining",
        "Toplam Kota": "Total Quota",
        "Live Section": "Live Section"
    }

    # Rename columns according to mapping
    df = df.rename(columns=column_mapping)

    # Handle instructor information
    if "Instructor First Name" in df.columns and "Instructor Last Name" in df.columns:
        df["Lecture Instructor"] = (
            df["Instructor First Name"].astype(str) + " " + 
            df["Instructor Last Name"].astype(str)
        )

    # Normalize the Hour column by replacing newlines and standardizing separators
    if "Hour" in df.columns:
        df["Hour"] = df["Hour"].astype(str).replace(r'\n', ', ', regex=True)
        df["Hour"] = df["Hour"].replace(r'[;/]', ', ', regex=True)

    # Add missing Faculty, Department, Campus columns with defaults
    return add_missing_columns(df)


def add_missing_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Faculty, Department, and Campus columns with defaults if they don't exist.

    Args:
        df: DataFrame to check and modify

    Returns:
        DataFrame with all required columns
    """
    # Add Faculty column if missing
    if "Faculty" not in df.columns:
        df["Faculty"] = DEFAULT_FACULTY

    # Add Department column if missing
    if "Department" not in df.columns:
        df["Department"] = DEFAULT_DEPARTMENT

    # Add Campus column if missing
    if "Campus" not in df.columns:
        df["Campus"] = DEFAULT_CAMPUS

    return df


def _process_row(row: pd.Series, teacher_col: Optional[str]) -> Dict[str, Any]:
    """
    Process a single row from the Excel dataframe.

    Args:
        row: Pandas Series representing a row from the dataframe
        teacher_col: Name of the column containing teacher information

    Returns:
        Dictionary with course information
    """
    code = str(row["Code"]).strip()
    course_name = str(row["Lecture Name"]).strip()

    # Handle credit as either integer or float
    try:
        credit = int(row["Credit"])
    except (ValueError, TypeError):
        try:
            credit = int(float(row["Credit"]))
        except (ValueError, TypeError):
            credit = 0
            logger.warning(f"Could not convert credit value '{row['Credit']}' for course {code}. Using default 0.")

    # Handle schedule parsing
    schedule_str = ""
    try:
        if "Hour" in row.index:
            hour_value = row["Hour"]

            # Check if it's a pandas Series (multiple Hour columns)
            if isinstance(hour_value, pd.Series):
                # Get first non-null value from the series
                valid_values = hour_value.dropna()
                if not valid_values.empty:
                    schedule_str = str(valid_values.iloc[0]).strip()
                else:
                    schedule_str = ""
            else:
                # Single value - check if it's not null
                if pd.notna(hour_value):
                    schedule_str = str(hour_value).strip()
                else:
                    schedule_str = ""
        else:
            schedule_str = ""

    except Exception as e:
        logger.warning(f"Error extracting schedule for course {code}: {e}")
        schedule_str = ""

    # Parse schedule
    if schedule_str and schedule_str.lower() not in ["nan", "none", ""]:
        schedule_list = parse_schedule(schedule_str)
    else:
        schedule_list = []

    # Get main code and course type
    main_code = get_main_code(code)
    course_type = get_course_type(code)
    has_lecture = True if course_type == "lecture" else False

    # Get teacher name
    teacher = "Default"
    if teacher_col and teacher_col in row.index and pd.notna(row[teacher_col]):
        teacher = str(row[teacher_col]).strip()

    # Get additional fields with defaults if missing
    try:
        faculty = str(row["Faculty"]) if "Faculty" in row.index and pd.notna(row["Faculty"]) else DEFAULT_FACULTY
        department = str(row["Department"]) if "Department" in row.index and pd.notna(row["Department"]) else DEFAULT_DEPARTMENT
        campus = str(row["Campus"]) if "Campus" in row.index and pd.notna(row["Campus"]) else DEFAULT_CAMPUS
    except Exception as e:
        logger.warning(f"Error extracting faculty/department/campus for course {code}: {e}")
        faculty = DEFAULT_FACULTY
        department = DEFAULT_DEPARTMENT
        campus = DEFAULT_CAMPUS

    # Log warning if schedule couldn't be parsed but we had a valid string
    if not schedule_list and schedule_str and schedule_str.lower() not in ["nan", "none", ""]:
        logger.warning(f"Could not parse schedule '{schedule_str}' for course {code}")

    return {
        "code": code,
        "main_code": main_code,
        "course_name": course_name,
        "credit": credit,
        "schedule": schedule_list,
        "teacher": teacher,
        "course_type": course_type,
        "has_lecture": has_lecture,
        "faculty": faculty,
        "department": department,
        "campus": campus,
    }


def get_main_code(code: str) -> str:
    """
    Extract the main course code from a full course code.

    Examples:
        "CS101-PS1" -> "CS101"
        "CS101-L2" -> "CS101"
        "CS101.1" -> "CS101"
        "CS101" -> "CS101"

    Args:
        code: Full course code

    Returns:
        Main course code
    """
    code = str(code).strip()
    
    # Check for different separators in priority order
    if "-PS" in code:
        return code.split("-PS")[0]
    elif "-L" in code:
        return code.split("-L")[0]
    elif "." in code:
        return code.split(".")[0]
    elif "-" in code:
        # Generic dash separator
        return code.split("-")[0]
    else:
        return code


def get_course_type(code: str) -> str:
    """
    Determine the course type from the course code.

    Args:
        code: Course code

    Returns:
        Course type: "ps", "lab", or "lecture"
    """
    code = str(code).upper()
    
    if "-PS" in code or "PS" in code:
        return "ps"
    elif "-L" in code or "LAB" in code:
        return "lab"
    else:
        return "lecture"


def parse_schedule(schedule_str: str) -> List[Tuple[str, int]]:
    """
    Parse a schedule string into a list of time slots.

    Supports formats like:
        "M1,W2,Th3"
        "M1, W2, Th3"
        "Monday 1, Wednesday 2"
        
    Args:
        schedule_str: String representing a schedule

    Returns:
        List of tuples (day, period)
    """
    s = str(schedule_str).strip()
    if not s or s.lower() in ["nan", "none", ""]:
        return []

    # Split by common separators
    blocks = s.replace(';', ',').replace('/', ',').split(',')
    schedule = []

    for block in blocks:
        b = block.strip()
        if not b:
            continue
            
        i = 0
        while i < len(b):
            # Try to match day abbreviation
            if b[i:i+2] == 'Th' or b[i:i+2] == 'TH':
                day = "Th"
                i += 2
            elif b[i] in ['M', 'T', 'W', 'F', 'S']:
                day = b[i]
                i += 1
            else:
                i += 1
                continue

            # Extract hour number
            hour_str = ""
            while i < len(b) and b[i].isdigit():
                hour_str += b[i]
                i += 1

            if hour_str:
                try:
                    period = int(hour_str)
                    schedule.append((day, period))
                except ValueError:
                    logger.warning(f"Could not parse period '{hour_str}' in schedule '{schedule_str}'")

    return schedule


def save_courses_to_excel(courses: List[Course], file_path: str, sheet_name: str = "Courses") -> None:
    """
    Save a list of courses to an Excel file.

    Args:
        courses: List of Course objects to save
        file_path: Path where to save the Excel file
        sheet_name: Name of the sheet (default: "Courses")
    """
    # Convert courses to dictionaries
    data = []
    for course in courses:
        course_dict = course.to_dict()
        # Convert schedule list to string for Excel
        course_dict["schedule"] = ", ".join(f"{day}{period}" for day, period in course.schedule)
        data.append(course_dict)

    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to Excel
    df.to_excel(file_path, sheet_name=sheet_name, index=False)
    logger.info(f"Saved {len(courses)} courses to {file_path}")
