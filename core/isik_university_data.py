"""
Işık University - Sample Academic Data
Updated with real 2024-2025 Fall semester courses

Source: Official Course List (849 rows Excel file)
Courses from Computer Engineering Department
"""

from typing import List, Dict
from core.models import Course

# Sample courses from 2024-2025 Fall semester
SAMPLE_COURSES_2024_FALL: List[Dict] = [
    {
        "code": "COMP1007",
        "name": "Introduction to Computer and Software Engineering",
        "name_tr": "Bilgisayar ve Yazılım Mühendisliğine Giriş",
        "sections": [
            {
                "section": "1",
                "instructor": "Emine Ekin",
                "time_slots": ["M10"],
                "campus": "Şile",
                "ects": 1,
                "local_credit": 1
            }
        ]
    },
    {
        "code": "COMP1111",
        "name": "Fundamentals of Programming",
        "name_tr": "Programlama Temelleri",
        "sections": [
            {
                "section": "1",
                "instructor": "Tuğba Erkoç",
                "time_slots": ["T2", "T3", "T4"],
                "campus": "Şile",
                "ects": 6,
                "local_credit": 4
            }
        ]
    },
    {
        "code": "MATH1111",
        "name": "Calculus I",
        "name_tr": "Diferansiyel ve İntegral Hesap I",
        "sections": [
            {
                "section": "1",
                "instructor": "Banu Uzun",
                "time_slots": ["W1", "W2", "Th7", "Th8"],
                "campus": "Şile",
                "ects": 5,
                "local_credit": 4
            }
        ]
    },
    {
        "code": "MATH1112",
        "name": "Calculus II",
        "name_tr": "Diferansiyel ve İntegral Hesap II",
        "sections": [
            {
                "section": "1",
                "instructor": "Uğur Dursun",
                "time_slots": ["T7", "T8", "W6", "W7"],
                "campus": "Şile",
                "ects": 5,
                "local_credit": 4
            }
        ]
    },
    {
        "code": "COMP2112",
        "name": "Data Structures and Algorithms",
        "name_tr": "Veri Yapıları ve Algoritmalar",
        "sections": [
            {
                "section": "1",
                "instructor": "Berke Özenç",
                "time_slots": ["M2", "M3", "M4"],
                "campus": "Şile",
                "ects": 7,
                "local_credit": 4
            }
        ]
    },
    {
        "code": "COMP3112",
        "name": "Analysis of Algorithms",
        "name_tr": "Algoritma Analizi",
        "sections": [
            {
                "section": "1",
                "instructor": "Ahmet Feyzi Ateş",
                "time_slots": ["Th2", "Th3", "Th4"],
                "campus": "Şile",
                "ects": 5,
                "local_credit": 3
            }
        ]
    },
    {
        "code": "COMP3401",
        "name": "Computer Organization",
        "name_tr": "Bilgisayar Organizasyonu",
        "sections": [
            {
                "section": "1",
                "instructor": "Berke Özenç",
                "time_slots": ["T1", "T2", "T3"],
                "campus": "Şile",
                "ects": 5,
                "local_credit": 3
            }
        ]
    },
    {
        "code": "SOFT2101",
        "name": "Principles of Software Engineering",
        "name_tr": "Yazılım Mühendisliğinin İlkeleri",
        "sections": [
            {
                "section": "1",
                "instructor": "Ahmet Feyzi Ateş",
                "time_slots": ["M6", "M7", "M8"],
                "campus": "Şile",
                "ects": 5,
                "local_credit": 3
            }
        ]
    },
    {
        "code": "MATH2103",
        "name": "Discrete Mathematics",
        "name_tr": "Ayrık Matematik",
        "sections": [
            {
                "section": "1",
                "instructor": "Esma Diriçan Erdal",
                "time_slots": ["M1", "M2", "M3"],
                "campus": "Şile",
                "ects": 6,
                "local_credit": 4
            }
        ]
    },
    {
        "code": "MATH2201",
        "name": "Probability",
        "name_tr": "Olasılık",
        "sections": [
            {
                "section": "1",
                "instructor": "Deniz Karlı",
                "time_slots": ["T1", "T2", "T3"],
                "campus": "Şile",
                "ects": 6,
                "local_credit": 4
            }
        ]
    },
    {
        "code": "INDE2156",
        "name": "Engineering Statistics",
        "name_tr": "Mühendislik İstatistiği",
        "sections": [
            {
                "section": "1",
                "instructor": "Sonya Javadi",
                "time_slots": ["T1", "T2", "T3"],
                "campus": "Şile",
                "ects": 6,
                "local_credit": 3
            }
        ]
    }
]


def create_sample_courses() -> List[Course]:
    """
    Create Course objects from sample data.
    
    Returns:
        List of Course objects with real Işık University data
    """
    courses = []
    for course_data in SAMPLE_COURSES_2024_FALL:
        for section_data in course_data["sections"]:
            # Parse time slots to schedule format
            schedule = []
            for slot in section_data["time_slots"]:
                # Parse slot like "M10" -> ("M", 10)
                if len(slot) >= 2:
                    day = slot[:-1] if slot[:-1] in ["M", "T", "W", "Th", "F", "Sa", "Su"] else slot[0]
                    period = int(slot[len(day):])
                    schedule.append((day, period))
            
            # Create course object
            course = Course(
                code=f"{course_data['code']}.{section_data['section']}",
                main_code=course_data["code"],
                name=course_data["name"],
                ects=section_data["ects"],
                course_type="lecture",
                schedule=schedule,
                teacher=section_data["instructor"],
                faculty="Engineering and Natural Sciences",
                department="Computer Engineering",
                campus=section_data.get("campus", "Şile")
            )
            courses.append(course)
    return courses


def get_course_conflicts() -> Dict[str, List[str]]:
    """
    Get known time conflicts between sample courses.
    
    Returns:
        Dictionary mapping course codes to conflicting course codes
    """
    conflicts = {}
    
    # MATH2103 (M1,M2,M3) conflicts with COMP2112 (M2,M3,M4)
    conflicts["MATH2103"] = ["COMP2112"]
    conflicts["COMP2112"] = ["MATH2103"]
    
    # MATH2201 (T1,T2,T3) conflicts with INDE2156 (T1,T2,T3)
    conflicts["MATH2201"] = ["INDE2156", "COMP3401"]
    conflicts["INDE2156"] = ["MATH2201", "COMP3401"]
    conflicts["COMP3401"] = ["MATH2201", "INDE2156"]
    
    return conflicts


# Grade scale (Işık University official grading system)
GRADE_SCALE = {
    "AA": 4.00,  # Excellent
    "BA": 3.50,
    "BB": 3.00,
    "CB": 2.50,
    "CC": 2.00,  # Pass
    "DC": 1.50,
    "DD": 1.00,
    "F": 0.00,   # Fail
    "P": None,   # Pass (not included in GPA)
    "W": None,   # Withdraw
    "I": None,   # Incomplete
}

# GPA-based ECTS limits (Işık University regulations)
ECTS_LIMITS_BY_GPA = {
    "freshmen": 30,      # First year students cannot exceed 30 ECTS
    "low": 31,           # GPA < 2.49
    "medium": 37,        # 2.50 ≤ GPA ≤ 3.49
    "high": 43,          # GPA ≥ 3.50
    "double_major": 45,  # Double major students
}

# Campus information
CAMPUS_INFO = {
    "Şile": {
        "address": "Meşrutiyet Mahallesi, Üniversite Sokak No: 2, 34980 Şile/İstanbul",
        "area_sqm": 490000,
        "facilities": ["dormitories", "laboratories", "sports_facilities", "library", "social_facilities"],
        "departments": ["Engineering and Natural Sciences", "Art, Design and Architecture"]
    },
    "Maslak": {
        "address": "Büyükdere Caddesi, Pınar Mahallesi, No: 194-6, 34398 Maslak/İstanbul",
        "departments": ["Economics, Administrative and Social Sciences", "Vocational School"]
    }
}

# Faculty structure
FACULTIES = {
    "Engineering and Natural Sciences": {
        "departments": [
            "Computer Engineering",
            "Biomedical Engineering",
            "Electrical and Electronics Engineering",
            "Industrial Engineering",
            "Civil Engineering",
            "Mechanical Engineering",
            "Mechatronics Engineering",
            "Software Engineering"
        ],
        "campus": "Şile",
        "language": "English"
    },
    "Economics, Administrative and Social Sciences": {
        "departments": [
            "Psychology",
            "Management Information Systems",
            "Economics",
            "Business Administration",
            "International Relations",
            "International Trade and Finance"
        ],
        "campus": "Maslak",
        "language": "Turkish/English"
    },
    "Art, Design and Architecture": {
        "departments": [
            "Visual Communication Design",
            "Interior Architecture and Environmental Design",
            "Cinema and Television",
            "Industrial Design",
            "Architecture"
        ],
        "campus": "Şile",
        "language": "Turkish/English"
    }
}


if __name__ == "__main__":
    # Test sample data
    courses = create_sample_courses()
    print(f"Created {len(courses)} sample courses")
    
    for course in courses[:3]:
        print(f"\n{course.code} - {course.name}")
        print(f"  Teacher: {course.teacher}")
        print(f"  Schedule: {course.schedule}")
        print(f"  ECTS: {course.ects}")
    
    # Test conflicts
    conflicts = get_course_conflicts()
    print(f"\n\nFound {len(conflicts)} courses with conflicts")
    for code, conflicting in conflicts.items():
        print(f"  {code} conflicts with: {', '.join(conflicting)}")
