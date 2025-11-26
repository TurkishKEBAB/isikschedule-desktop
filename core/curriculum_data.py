"""
Işık University - Computer Engineering Curriculum Database

Source: Official Computer Engineering Program Page (REAL DATA from student transcript)
Year: 2021 and later entry students
Total ECTS Requirement: 240 ECTS (8 semesters)
Total Local Credits: 149
URL: isikun.edu.tr

This module contains the ACTUAL curriculum for Computer Engineering
as provided by Işık University official records.
"""

from typing import Dict, List, TypedDict


class CourseInfo(TypedDict):
    """Course information structure."""
    code: str
    name_en: str
    name_tr: str
    ects: int
    local_credit: int
    course_type: str  # "mandatory", "area_elective", "general_elective"
    category: str  # "core", "engineering", "math", "physics", "general"


# ============================================================================
# SEMESTER 1 - Total: 29 ECTS, 21 Local Credits
# ============================================================================
# ============================================================================
# SEMESTER 1 - Total: 29 ECTS, 21 Local Credits
# ============================================================================
SEMESTER_1_MANDATORY: List[CourseInfo] = [
    {
        "code": "COMP1007",
        "name_en": "Introduction to Computer and Software Engineering",
        "name_tr": "Bilgisayar ve Yazılım Mühendisliğine Giriş",
        "ects": 1,
        "local_credit": 1,
        "course_type": "mandatory",
        "category": "core"
    },
    {
        "code": "COMP1111",
        "name_en": "Fundamentals of Programming",
        "name_tr": "Programlama Temelleri",
        "ects": 6,
        "local_credit": 4,
        "course_type": "mandatory",
        "category": "core"
    },
    {
        "code": "CORE0101",
        "name_en": "History of Turkish Republic I",
        "name_tr": "Türkiye Cumhuriyeti Tarihi I",
        "ects": 2,
        "local_credit": 2,
        "course_type": "mandatory",
        "category": "general"
    },
    {
        "code": "CORE0103",
        "name_en": "Turkish I",
        "name_tr": "Türkçe I",
        "ects": 2,
        "local_credit": 2,
        "course_type": "mandatory",
        "category": "general"
    },
    {
        "code": "CORE0105",
        "name_en": "Orientation",
        "name_tr": "Oryantasyon",
        "ects": 1,
        "local_credit": 0,
        "course_type": "mandatory",
        "category": "general"
    },
    {
        "code": "CORE0201",
        "name_en": "Nature, Science, Human I",
        "name_tr": "Doğa, Bilim, İnsan I",
        "ects": 5,
        "local_credit": 3,
        "course_type": "mandatory",
        "category": "general"
    },
    {
        "code": "CORE0501",
        "name_en": "Art, Society, Human",
        "name_tr": "Sanat, Toplum, İnsan",
        "ects": 3,
        "local_credit": 2,
        "course_type": "mandatory",
        "category": "general"
    },
    {
        "code": "ENGL1101",
        "name_en": "Academic English 1",
        "name_tr": "Akademik İngilizce 1",
        "ects": 4,
        "local_credit": 3,
        "course_type": "mandatory",
        "category": "general"
    },
    {
        "code": "MATH1111",
        "name_en": "Calculus I",
        "name_tr": "Diferansiyel ve İntegral Hesap I",
        "ects": 5,
        "local_credit": 4,
        "course_type": "mandatory",
        "category": "math"
    }
]

# ============================================================================
# SEMESTER 2 - Total: 36 ECTS, 25 Local Credits
# ============================================================================
SEMESTER_2_MANDATORY: List[CourseInfo] = [
    {
        "code": "MATH1112",
        "name_en": "Calculus II",
        "name_tr": "Diferansiyel ve İntegral Hesap II",
        "ects": 5,
        "local_credit": 4,
        "course_type": "mandatory",
        "category": "math"
    },
    {
        "code": "PHYS1112",
        "name_en": "Physics - Electricity & Magnetism",
        "name_tr": "Fizik - Elektrik ve Manyetizma",
        "ects": 5,
        "local_credit": 4,
        "course_type": "mandatory",
        "category": "physics"
    },
    {
        "code": "PHYS1114",
        "name_en": "Physics Lab",
        "name_tr": "Fizik Laboratuvarı",
        "ects": 1,
        "local_credit": 1,
        "course_type": "mandatory",
        "category": "physics"
    },
    {
        "code": "COMP1112",
        "name_en": "Object Oriented Programming",
        "name_tr": "Nesne Yönelimli Programlama",
        "ects": 6,
        "local_credit": 4,
        "course_type": "mandatory",
        "category": "core"
    },
    {
        "code": "ENGL1102",
        "name_en": "Academic English 2",
        "name_tr": "Akademik İngilizce 2",
        "ects": 3,
        "local_credit": 3,
        "course_type": "mandatory",
        "category": "general"
    },
    {
        "code": "CORE1xx2",
        "name_en": "CORE Courses (TC History II, Turkish II, Numbers-Formulas-Human I, Career Planning)",
        "name_tr": "CORE Dersleri",
        "ects": 11,
        "local_credit": 5,
        "course_type": "mandatory",
        "category": "general"
    }
]

SEMESTER_3_MANDATORY: List[CourseInfo] = [
    {
        "code": "MATH2103",
        "name_en": "Discrete Mathematics",
        "name_tr": "Ayrık Matematik",
        "ects": 6,
        "local_credit": 4,
        "course_type": "mandatory",
        "category": "math"
    },
    {
        "code": "COMP2112",
        "name_en": "Data Structures and Algorithms",
        "name_tr": "Veri Yapıları ve Algoritmalar",
        "ects": 7,
        "local_credit": 4,
        "course_type": "mandatory",
        "category": "core"
    },
    {
        "code": "ELEC2205",
        "name_en": "Electrical Circuits",
        "name_tr": "Elektrik Devreleri",
        "ects": 5,
        "local_credit": 3,
        "course_type": "mandatory",
        "category": "engineering"
    },
    {
        "code": "CORE2xx3",
        "name_en": "CORE Courses (Society-Science-Human, Ethics-Law-Society, Creative Thinking, Major Works)",
        "name_tr": "CORE Dersleri",
        "ects": 13,
        "local_credit": 8,
        "course_type": "mandatory",
        "category": "general"
    }
]

SEMESTER_4_MANDATORY: List[CourseInfo] = [
    {
        "code": "COMP2502",
        "name_en": "Human Computer Interaction",
        "name_tr": "İnsan Bilgisayar Etkileşimi",
        "ects": 5,
        "local_credit": 3,
        "course_type": "mandatory",
        "category": "core"
    },
    {
        "code": "COMP2222",
        "name_en": "Database Systems",
        "name_tr": "Veri Tabanı Sistemleri",
        "ects": 6,
        "local_credit": 3,
        "course_type": "mandatory",
        "category": "core"
    },
    {
        "code": "MATH2201",
        "name_en": "Probability",
        "name_tr": "Olasılık",
        "ects": 6,
        "local_credit": 4,
        "course_type": "mandatory",
        "category": "math"
    },
    {
        "code": "MATH2104",
        "name_en": "Linear Algebra",
        "name_tr": "Lineer Cebir",
        "ects": 5,
        "local_credit": 4,
        "course_type": "mandatory",
        "category": "math"
    },
    {
        "code": "ELEC1411",
        "name_en": "Logic Design & Lab",
        "name_tr": "Mantık Tasarımı ve Laboratuvarı",
        "ects": 7,
        "local_credit": 3,
        "course_type": "mandatory",
        "category": "engineering"
    }
]

SEMESTER_5_MANDATORY: List[CourseInfo] = [
    {
        "code": "COMP3112",
        "name_en": "Analysis of Algorithms",
        "name_tr": "Algoritma Analizi",
        "ects": 5,
        "local_credit": 3,
        "course_type": "mandatory",
        "category": "core"
    },
    {
        "code": "COMP3401",
        "name_en": "Computer Organization",
        "name_tr": "Bilgisayar Organizasyonu",
        "ects": 5,
        "local_credit": 3,
        "course_type": "mandatory",
        "category": "core"
    },
    {
        "code": "SOFT2101",
        "name_en": "Principles of Software Engineering",
        "name_tr": "Yazılım Mühendisliğinin İlkeleri",
        "ects": 5,
        "local_credit": 3,
        "course_type": "mandatory",
        "category": "core"
    },
    {
        "code": "INDE2156",
        "name_en": "Engineering Statistics",
        "name_tr": "Mühendislik İstatistiği",
        "ects": 6,
        "local_credit": 3,
        "course_type": "mandatory",
        "category": "engineering"
    },
    {
        "code": "COMP3920",
        "name_en": "Summer Practice I",
        "name_tr": "Yaz Stajı I",
        "ects": 3,
        "local_credit": 0,
        "course_type": "mandatory",
        "category": "practice"
    },
    {
        "code": "ELEC3305",
        "name_en": "Electronics & Lab",
        "name_tr": "Elektronik ve Laboratuvarı",
        "ects": 6,
        "local_credit": 4,
        "course_type": "mandatory",
        "category": "engineering"
    }
]

SEMESTER_6_MANDATORY: List[CourseInfo] = [
    {
        "code": "COMP3432",
        "name_en": "Operating Systems",
        "name_tr": "İşletim Sistemleri",
        "ects": 6,
        "local_credit": 3,
        "course_type": "mandatory",
        "category": "core"
    },
    {
        "code": "COMP3105",
        "name_en": "Automata and Formal Languages",
        "name_tr": "Otomata ve Biçimsel Diller",
        "ects": 5,
        "local_credit": 3,
        "course_type": "mandatory",
        "category": "core"
    },
    {
        "code": "COMP3402",
        "name_en": "Microprocessors",
        "name_tr": "Mikroişlemciler",
        "ects": 5,
        "local_credit": 3,
        "course_type": "mandatory",
        "category": "core"
    },
    {
        "code": "COMP3334",
        "name_en": "Computer Networks",
        "name_tr": "Bilgisayar Ağları",
        "ects": 6,
        "local_credit": 3,
        "course_type": "mandatory",
        "category": "core"
    },
    {
        "code": "BIOL1101",
        "name_en": "Biology",
        "name_tr": "Biyoloji",
        "ects": 3,
        "local_credit": 3,
        "course_type": "mandatory",
        "category": "general"
    },
    {
        "code": "SOFT3112",
        "name_en": "Software Development Practice",
        "name_tr": "Yazılım Geliştirme Uygulaması",
        "ects": 5,
        "local_credit": 3,
        "course_type": "mandatory",
        "category": "core"
    }
]

SEMESTER_7_STRUCTURE: Dict[str, int] = {
    "area_electives": 3,  # 3 area elective courses
    "general_electives": 2,  # 2 general elective courses
    "mandatory": [
        {
            "code": "ENGR4901",
            "name_en": "Introduction to Design Projects",
            "name_tr": "Tasarım Projelerine Giriş",
            "ects": 3,
            "local_credit": 3,
            "course_type": "mandatory",
            "category": "project"
        },
        {
            "code": "OHES4411",
            "name_en": "Occupational Health and Safety I",
            "name_tr": "İş Sağlığı ve Güvenliği I",
            "ects": 2,
            "local_credit": 2,
            "course_type": "mandatory",
            "category": "general"
        },
        {
            "code": "COMP4920",
            "name_en": "Summer Practice II",
            "name_tr": "Yaz Stajı II",
            "ects": 3,
            "local_credit": 0,
            "course_type": "mandatory",
            "category": "practice"
        }
    ],
    "total_ects": 31
}

SEMESTER_8_STRUCTURE: Dict[str, int] = {
    "area_electives": 2,  # 2 more area elective courses (total 5)
    "general_electives": 2,  # 2 more general electives (total 4)
    "mandatory": [
        {
            "code": "COMP4912",
            "name_en": "Graduation Design Project",
            "name_tr": "Bitirme Tasarım Projesi",
            "ects": 8,
            "local_credit": 4,
            "course_type": "mandatory",
            "category": "project"
        },
        {
            "code": "OHES4412",
            "name_en": "Occupational Health and Safety II",
            "name_tr": "İş Sağlığı ve Güvenliği II",
            "ects": 2,
            "local_credit": 2,
            "course_type": "mandatory",
            "category": "general"
        }
    ],
    "total_ects": 29
}

# Complete curriculum mapping
COMPUTER_ENGINEERING_CURRICULUM: Dict[str, List[CourseInfo]] = {
    "Fall-1": SEMESTER_1_MANDATORY,
    "Spring-1": SEMESTER_2_MANDATORY,
    "Fall-2": SEMESTER_3_MANDATORY,
    "Spring-2": SEMESTER_4_MANDATORY,
    "Fall-3": SEMESTER_5_MANDATORY,
    "Spring-3": SEMESTER_6_MANDATORY,
    "Fall-4": SEMESTER_7_STRUCTURE,
    "Spring-4": SEMESTER_8_STRUCTURE,
}

# Graduation requirements
GRADUATION_REQUIREMENTS = {
    "total_ects": 240,
    "minimum_gpa": 2.00,
    "mandatory_courses": 54,  # Approximate (excluding electives)
    "area_electives": 5,
    "general_electives": 4,
    "summer_practices": 2,
    "graduation_project": 1,
}


def get_semester_courses(semester: str) -> List[CourseInfo]:
    """Get courses for a specific semester."""
    return COMPUTER_ENGINEERING_CURRICULUM.get(semester, [])


def get_total_ects_by_semester(semester: str) -> int:
    """Get total ECTS for a semester."""
    courses = get_semester_courses(semester)
    if isinstance(courses, dict):  # For semesters 7-8
        return courses.get("total_ects", 0)
    return sum(course["ects"] for course in courses)


def get_all_mandatory_courses() -> List[CourseInfo]:
    """Get all mandatory courses across all semesters."""
    all_courses = []
    for semester, courses in COMPUTER_ENGINEERING_CURRICULUM.items():
        if isinstance(courses, list):
            all_courses.extend(courses)
        elif isinstance(courses, dict) and "mandatory" in courses:
            all_courses.extend(courses["mandatory"])
    return all_courses


def get_course_by_code(course_code: str) -> CourseInfo:
    """Find a course by its code."""
    for courses in COMPUTER_ENGINEERING_CURRICULUM.values():
        if isinstance(courses, list):
            for course in courses:
                if course["code"] == course_code:
                    return course
        elif isinstance(courses, dict) and "mandatory" in courses:
            for course in courses["mandatory"]:
                if course["code"] == course_code:
                    return course
    return None


# Example usage
if __name__ == "__main__":
    print("=== Işık University - Computer Engineering Curriculum ===\n")
    
    # Semester 1 courses
    print("Fall-1 Courses:")
    for course in SEMESTER_1_MANDATORY:
        print(f"  {course['code']}: {course['name_en']} ({course['ects']} ECTS)")
    
    print(f"\nTotal ECTS: {get_total_ects_by_semester('Fall-1')}")
    
    # Total mandatory courses
    mandatory = get_all_mandatory_courses()
    print(f"\nTotal mandatory courses: {len(mandatory)}")
    
    # Graduation requirements
    print("\n=== Graduation Requirements ===")
    for key, value in GRADUATION_REQUIREMENTS.items():
        print(f"  {key}: {value}")
