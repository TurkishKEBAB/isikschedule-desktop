"""
Işık University - Computer Engineering Curriculum Database (REAL DATA)

Source: Official Student Transcript (Provided by User)
Year: Current curriculum
Total ECTS: 240 ECTS (8 semesters)
Total Local Credits: 149

WARNING: This is the REAL curriculum data extracted from actual student records.
Previous curriculum_data.py contained inaccurate ChatGPT-generated data.
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
    category: str


# ============================================================================
# SEMESTER 1 - Total: 29 ECTS, 21 Local Credits
# ============================================================================
SEMESTER_1_MANDATORY: List[CourseInfo] = [
    {"code": "COMP1007", "name_en": "Introduction to Computer and Software Engineering", 
     "name_tr": "Bilgisayar ve Yazılım Mühendisliğine Giriş", "ects": 1, "local_credit": 1,
     "course_type": "mandatory", "category": "core"},
    {"code": "COMP1111", "name_en": "Fundamentals of Programming", 
     "name_tr": "Programlama Temelleri", "ects": 6, "local_credit": 4,
     "course_type": "mandatory", "category": "core"},
    {"code": "CORE0101", "name_en": "History of Turkish Republic I", 
     "name_tr": "Türkiye Cumhuriyeti Tarihi I", "ects": 2, "local_credit": 2,
     "course_type": "mandatory", "category": "general"},
    {"code": "CORE0103", "name_en": "Turkish I", 
     "name_tr": "Türkçe I", "ects": 2, "local_credit": 2,
     "course_type": "mandatory", "category": "general"},
    {"code": "CORE0105", "name_en": "Orientation", 
     "name_tr": "Oryantasyon", "ects": 1, "local_credit": 0,
     "course_type": "mandatory", "category": "general"},
    {"code": "CORE0201", "name_en": "Nature, Science, Human I", 
     "name_tr": "Doğa, Bilim, İnsan I", "ects": 5, "local_credit": 3,
     "course_type": "mandatory", "category": "general"},
    {"code": "CORE0501", "name_en": "Art, Society, Human", 
     "name_tr": "Sanat, Toplum, İnsan", "ects": 3, "local_credit": 2,
     "course_type": "mandatory", "category": "general"},
    {"code": "ENGL1101", "name_en": "Academic English 1", 
     "name_tr": "Akademik İngilizce 1", "ects": 4, "local_credit": 3,
     "course_type": "mandatory", "category": "general"},
    {"code": "MATH1111", "name_en": "Calculus I", 
     "name_tr": "Diferansiyel ve İntegral Hesap I", "ects": 5, "local_credit": 4,
     "course_type": "mandatory", "category": "math"}
]

# ============================================================================
# SEMESTER 2 - Total: 36 ECTS, 25 Local Credits
# ============================================================================
SEMESTER_2_MANDATORY: List[CourseInfo] = [
    {"code": "COMP1112", "name_en": "Object Oriented Programming", 
     "name_tr": "Nesne Yönelimli Programlama", "ects": 6, "local_credit": 3,
     "course_type": "mandatory", "category": "core"},
    {"code": "CORE0102", "name_en": "History of Turkish Republic II", 
     "name_tr": "Türkiye Cumhuriyeti Tarihi II", "ects": 2, "local_credit": 2,
     "course_type": "mandatory", "category": "general"},
    {"code": "CORE0104", "name_en": "Turkish II", 
     "name_tr": "Türkçe II", "ects": 2, "local_credit": 2,
     "course_type": "mandatory", "category": "general"},
    {"code": "CORE0106", "name_en": "Career Planning", 
     "name_tr": "Kariyer Planlama", "ects": 1, "local_credit": 0,
     "course_type": "mandatory", "category": "general"},
    {"code": "CORE0301", "name_en": "Numbers, Formulas, Human I", 
     "name_tr": "Sayılar, Formüller, İnsan I", "ects": 5, "local_credit": 3,
     "course_type": "mandatory", "category": "general"},
    {"code": "ENGL1102", "name_en": "Academic English 2", 
     "name_tr": "Akademik İngilizce 2", "ects": 4, "local_credit": 3,
     "course_type": "mandatory", "category": "general"},
    {"code": "MATH1112", "name_en": "Calculus II", 
     "name_tr": "Diferansiyel ve İntegral Hesap II", "ects": 5, "local_credit": 4,
     "course_type": "mandatory", "category": "math"},
    {"code": "PHYS1112", "name_en": "Electricity and Magnetism", 
     "name_tr": "Elektrik Ve Manyetizma", "ects": 5, "local_credit": 3,
     "course_type": "mandatory", "category": "physics"},
    {"code": "PHYS1114", "name_en": "Electricity and Magnetism Laboratory", 
     "name_tr": "Elektrik Ve Manyetizma Laboratuvarı", "ects": 1, "local_credit": 1,
     "course_type": "mandatory", "category": "physics"}
]

# ============================================================================
# SEMESTER 3 - Total: 31 ECTS, 19 Local Credits
# ============================================================================
SEMESTER_3_MANDATORY: List[CourseInfo] = [
    {"code": "COMP2112", "name_en": "Data Structures and Algorithms", 
     "name_tr": "Veri Yapıları ve Algoritmalar", "ects": 7, "local_credit": 4,
     "course_type": "mandatory", "category": "core"},
    {"code": "CORE0107", "name_en": "Creative Thinking and Problem Solving", 
     "name_tr": "Yaratıcı Düşünme ve Problem Çözme", "ects": 3, "local_credit": 2,
     "course_type": "mandatory", "category": "general"},
    {"code": "CORE0108", "name_en": "Major Works", 
     "name_tr": "BÜYÜK ESERLER", "ects": 3, "local_credit": 2,
     "course_type": "mandatory", "category": "general"},
    {"code": "CORE0401", "name_en": "Society, Science and Human", 
     "name_tr": "Toplum, Bilim ve İnsan", "ects": 4, "local_credit": 3,
     "course_type": "mandatory", "category": "general"},
    {"code": "CORE0402", "name_en": "Ethics, Law, Society", 
     "name_tr": "Etik, Hukuk, Toplum", "ects": 3, "local_credit": 2,
     "course_type": "mandatory", "category": "general"},
    {"code": "ELEC2205", "name_en": "Electrical Circuits", 
     "name_tr": "Elektrik Devreleri", "ects": 5, "local_credit": 3,
     "course_type": "mandatory", "category": "engineering"},
    {"code": "MATH2103", "name_en": "Discrete Mathematics", 
     "name_tr": "Ayrık Matematik", "ects": 6, "local_credit": 3,
     "course_type": "mandatory", "category": "math"},
]

# ============================================================================
# SEMESTER 4 - Total: 29 ECTS, 17 Local Credits
# ============================================================================
SEMESTER_4_MANDATORY: List[CourseInfo] = [
    {"code": "COMP2222", "name_en": "Database Systems", 
     "name_tr": "Veritabanı Sistemleri", "ects": 7, "local_credit": 4,
     "course_type": "mandatory", "category": "core"},
    {"code": "COMP2502", "name_en": "Introduction to Human-Computer Interaction", 
     "name_tr": "İnsan-Bilgisayar Etkileşimine Giriş", "ects": 5, "local_credit": 3,
     "course_type": "mandatory", "category": "core"},
    {"code": "ELEC1402", "name_en": "Logic Design Laboratory", 
     "name_tr": "Mantık Devreleri Tasarımı Laboratuvarı", "ects": 2, "local_credit": 1,
     "course_type": "mandatory", "category": "engineering"},
    {"code": "ELEC1411", "name_en": "Logic Design", 
     "name_tr": "Logic Design", "ects": 4, "local_credit": 3,
     "course_type": "mandatory", "category": "engineering"},
    {"code": "MATH2104", "name_en": "Linear Algebra", 
     "name_tr": "Lineer Cebir", "ects": 5, "local_credit": 3,
     "course_type": "mandatory", "category": "math"},
    {"code": "MATH2201", "name_en": "Probability", 
     "name_tr": "Olasılık", "ects": 6, "local_credit": 3,
     "course_type": "mandatory", "category": "math"},
]

# ============================================================================
# SEMESTER 5 - Total: 30 ECTS, 16 Local Credits
# ============================================================================
SEMESTER_5_MANDATORY: List[CourseInfo] = [
    {"code": "COMP3112", "name_en": "Algorithm Analysis", 
     "name_tr": "Algoritma Analizi", "ects": 5, "local_credit": 3,
     "course_type": "mandatory", "category": "core"},
    {"code": "COMP3401", "name_en": "Computer Organization", 
     "name_tr": "Bilgisayar Organizasyonu", "ects": 5, "local_credit": 3,
     "course_type": "mandatory", "category": "core"},
    {"code": "COMP3920", "name_en": "Summer Practice I", 
     "name_tr": "Yaz Stajı I", "ects": 2, "local_credit": 0,
     "course_type": "mandatory", "category": "general"},
    {"code": "ELEC3305", "name_en": "Electronics", 
     "name_tr": "Elektronik", "ects": 5, "local_credit": 3,
     "course_type": "mandatory", "category": "engineering"},
    {"code": "ELEC3307", "name_en": "Electronics Laboratory", 
     "name_tr": "Elektronik laboratuvarı", "ects": 2, "local_credit": 1,
     "course_type": "mandatory", "category": "engineering"},
    {"code": "INDE2156", "name_en": "Engineering Statistics", 
     "name_tr": "Mühendislik İstatistiği", "ects": 6, "local_credit": 3,
     "course_type": "mandatory", "category": "math"},
    {"code": "SOFT2101", "name_en": "Software Engineering Principles", 
     "name_tr": "Yazılım Mühendisliğinin İlkeleri", "ects": 5, "local_credit": 3,
     "course_type": "mandatory", "category": "core"},
]

# ============================================================================
# SEMESTER 6 - Total: 30 ECTS, 18 Local Credits
# ============================================================================
SEMESTER_6_MANDATORY: List[CourseInfo] = [
    {"code": "BIOL1101", "name_en": "Biology", 
     "name_tr": "Biyoloji", "ects": 5, "local_credit": 3,
     "course_type": "mandatory", "category": "general"},
    {"code": "COMP3105", "name_en": "Automata and Formal Languages", 
     "name_tr": "Özdevinirler ve Biçimsel Diller", "ects": 5, "local_credit": 3,
     "course_type": "mandatory", "category": "core"},
    {"code": "COMP3334", "name_en": "Computer Networks", 
     "name_tr": "Bilgisayar Ağları", "ects": 5, "local_credit": 3,
     "course_type": "mandatory", "category": "core"},
    {"code": "COMP3402", "name_en": "Microprocessors", 
     "name_tr": "Mikroişlemciler", "ects": 6, "local_credit": 3,
     "course_type": "mandatory", "category": "core"},
    {"code": "COMP3432", "name_en": "Operating Systems", 
     "name_tr": "İşletim Sistemleri", "ects": 5, "local_credit": 3,
     "course_type": "mandatory", "category": "core"},
    {"code": "SOFT3112", "name_en": "Software Development Practice", 
     "name_tr": "Yazılım Geliştirme Uygulamaları", "ects": 4, "local_credit": 3,
     "course_type": "mandatory", "category": "core"},
]

# ============================================================================
# SEMESTER 7 - Total: 32 ECTS, 17 Local Credits
# ============================================================================
SEMESTER_7_MANDATORY: List[CourseInfo] = [
    {"code": "COMP4920", "name_en": "Summer Practice II", 
     "name_tr": "Yaz Stajı II", "ects": 3, "local_credit": 0,
     "course_type": "mandatory", "category": "general"},
    {"code": "ENGR4901", "name_en": "Introduction to Design Projects", 
     "name_tr": "Tasarım Projelerine Giriş", "ects": 1, "local_credit": 1,
     "course_type": "mandatory", "category": "core"},
    {"code": "OHES4411", "name_en": "Occupational Health and Safety I", 
     "name_tr": "İş Sağlığı ve Güvenliği I", "ects": 2, "local_credit": 0,
     "course_type": "mandatory", "category": "general"},
]

SEMESTER_7_AREA_ELECTIVES: List[CourseInfo] = [
    {"code": "COMP-AE-I", "name_en": "Area Elective I", 
     "name_tr": "Alan Seçmeli-I", "ects": 5, "local_credit": 3,
     "course_type": "area_elective", "category": "core"},
    {"code": "COMP-AE-II", "name_en": "Area Elective II", 
     "name_tr": "Alan Seçmeli-II", "ects": 5, "local_credit": 3,
     "course_type": "area_elective", "category": "core"},
    {"code": "COMP-AE-III", "name_en": "Area Elective III", 
     "name_tr": "Alan Seçmeli-III", "ects": 5, "local_credit": 3,
     "course_type": "area_elective", "category": "core"},
]

SEMESTER_7_GENERAL_ELECTIVES: List[CourseInfo] = [
    {"code": "COMP-GE-I", "name_en": "General Elective I", 
     "name_tr": "Genel Seçmeli-I", "ects": 5, "local_credit": 3,
     "course_type": "general_elective", "category": "general"},
    {"code": "COMP-GE-II", "name_en": "General Elective II", 
     "name_tr": "Genel Seçmeli-II", "ects": 5, "local_credit": 3,
     "course_type": "general_elective", "category": "general"},
]

# ============================================================================
# SEMESTER 8 - Total: 29 ECTS, 16 Local Credits
# ============================================================================
SEMESTER_8_MANDATORY: List[CourseInfo] = [
    {"code": "COMP4912", "name_en": "Graduation Design Project", 
     "name_tr": "Bitirme Tasarım Projesi", "ects": 7, "local_credit": 4,
     "course_type": "mandatory", "category": "core"},
    {"code": "OHES4412", "name_en": "Occupational Health and Safety II", 
     "name_tr": "İş Sağlığı ve Güvenliği II", "ects": 2, "local_credit": 0,
     "course_type": "mandatory", "category": "general"},
]

SEMESTER_8_AREA_ELECTIVES: List[CourseInfo] = [
    {"code": "COMP-AE-IV", "name_en": "Area Elective IV", 
     "name_tr": "Alan Seçmeli-IV", "ects": 5, "local_credit": 3,
     "course_type": "area_elective", "category": "core"},
    {"code": "COMP-AE-V", "name_en": "Area Elective V", 
     "name_tr": "Alan Seçmeli-V", "ects": 5, "local_credit": 3,
     "course_type": "area_elective", "category": "core"},
]

SEMESTER_8_GENERAL_ELECTIVES: List[CourseInfo] = [
    {"code": "COMP-GE-III", "name_en": "General Elective III", 
     "name_tr": "Genel Seçmeli-III", "ects": 5, "local_credit": 3,
     "course_type": "general_elective", "category": "general"},
    {"code": "COMP-GE-IV", "name_en": "General Elective IV", 
     "name_tr": "Genel Seçmeli-IV", "ects": 5, "local_credit": 3,
     "course_type": "general_elective", "category": "general"},
]

# ============================================================================
# CONSOLIDATED CURRICULUM
# ============================================================================
COMPUTER_ENGINEERING_CURRICULUM: Dict[str, List[CourseInfo]] = {
    "semester_1": SEMESTER_1_MANDATORY,
    "semester_2": SEMESTER_2_MANDATORY,
    "semester_3": SEMESTER_3_MANDATORY,
    "semester_4": SEMESTER_4_MANDATORY,
    "semester_5": SEMESTER_5_MANDATORY,
    "semester_6": SEMESTER_6_MANDATORY,
    "semester_7": SEMESTER_7_MANDATORY + SEMESTER_7_AREA_ELECTIVES + SEMESTER_7_GENERAL_ELECTIVES,
    "semester_8": SEMESTER_8_MANDATORY + SEMESTER_8_AREA_ELECTIVES + SEMESTER_8_GENERAL_ELECTIVES,
}

# Quick access to all mandatory courses
ALL_MANDATORY_COURSES = (
    SEMESTER_1_MANDATORY +
    SEMESTER_2_MANDATORY +
    SEMESTER_3_MANDATORY +
    SEMESTER_4_MANDATORY +
    SEMESTER_5_MANDATORY +
    SEMESTER_6_MANDATORY +
    SEMESTER_7_MANDATORY +
    SEMESTER_8_MANDATORY
)

# Quick access to all electives
ALL_AREA_ELECTIVES = SEMESTER_7_AREA_ELECTIVES + SEMESTER_8_AREA_ELECTIVES
ALL_GENERAL_ELECTIVES = SEMESTER_7_GENERAL_ELECTIVES + SEMESTER_8_GENERAL_ELECTIVES

# Summary statistics
CURRICULUM_SUMMARY = {
    "total_ects": 240,
    "total_local_credits": 149,
    "total_semesters": 8,
    "mandatory_courses": len(ALL_MANDATORY_COURSES),
    "area_electives_required": 5,  # 5 area electives × 5 ECTS = 25 ECTS
    "general_electives_required": 4,  # 4 general electives × 5 ECTS = 20 ECTS
}
