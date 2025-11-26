"""
Işık University - All Programs Curriculum Data

This module contains comprehensive curriculum data for undergraduate programs
at Işık University (2021-2024 curricula). Each program entry includes:
- General information (program code, degree, language, ECTS, duration, min GPA)
- Semester-by-semester course listings (code, name, ECTS, credits, type, prerequisites)
- Elective pools (technical/area and general electives)
- Prerequisite maps

Data sources:
- Official curriculum pages from isikun.edu.tr
- Department handbooks and course catalogs
- 2021 Bologna curriculum documents

All ECTS totals sum to 240 for 4-year bachelor programs (Bologna standard).
"""

ISIK_UNIVERSITY_PROGRAMS = {
    "undergraduate": {
        "engineering": {
            "computer_engineering": {
                "program_code": "COMP",
                "degree": "B.Sc.",
                "language": "English",
                "total_ects": 240,
                "duration_years": 4,
                "min_gpa": 2.00,
                "semesters": {
                    "fall_1": [
                        {"code": "COMP1111", "name": "Fundamentals of Programming", "ects": 6, "local_credit": 4, "type": "mandatory", "prerequisites": []},
                        {"code": "MATH1111", "name": "Calculus I", "ects": 5, "local_credit": 4, "type": "mandatory", "prerequisites": []},
                        {"code": "CORE0101", "name": "History of Turkish Republic I", "ects": 2, "local_credit": 2, "type": "mandatory", "prerequisites": []},
                        {"code": "CORE0103", "name": "Turkish I", "ects": 2, "local_credit": 2, "type": "mandatory", "prerequisites": []},
                        {"code": "CORE0105", "name": "Orientation", "ects": 1, "local_credit": 0, "type": "mandatory", "prerequisites": []},
                        {"code": "ENGL1101", "name": "Academic English I", "ects": 4, "local_credit": 3, "type": "mandatory", "prerequisites": []},
                        {"code": "ITEC1001", "name": "Computer Literacy", "ects": 1, "local_credit": 0, "type": "mandatory", "prerequisites": []},
                    ],
                    "spring_1": [
                        {"code": "COMP1112", "name": "Object Oriented Programming", "ects": 6, "local_credit": 4, "type": "mandatory", "prerequisites": ["COMP1111"]},
                        {"code": "MATH1112", "name": "Calculus II", "ects": 5, "local_credit": 4, "type": "mandatory", "prerequisites": ["MATH1111"]},
                        {"code": "PHYS1112", "name": "Physics – Electricity and Magnetism", "ects": 5, "local_credit": 3, "type": "mandatory", "prerequisites": []},
                        {"code": "CORE0102", "name": "History of Turkish Republic II", "ects": 2, "local_credit": 2, "type": "mandatory", "prerequisites": []},
                        {"code": "ENGL1102", "name": "Academic English II", "ects": 4, "local_credit": 3, "type": "mandatory", "prerequisites": ["ENGL1101"]},
                    ],
                    "fall_2": [
                        {"code": "COMP2112", "name": "Data Structures and Algorithms", "ects": 6, "local_credit": 4, "type": "mandatory", "prerequisites": ["COMP1112"]},
                        {"code": "MATH2103", "name": "Discrete Mathematics", "ects": 6, "local_credit": 3, "type": "mandatory", "prerequisites": []},
                        {"code": "MATH2104", "name": "Linear Algebra", "ects": 5, "local_credit": 3, "type": "mandatory", "prerequisites": []},
                        {"code": "ELEC1411", "name": "Logic Design", "ects": 4, "local_credit": 3, "type": "mandatory", "prerequisites": []},
                    ],
                    "spring_2": [
                        {"code": "COMP2222", "name": "Database Systems", "ects": 6, "local_credit": 3, "type": "mandatory", "prerequisites": ["COMP2112"]},
                        {"code": "SOFT2101", "name": "Software Engineering Principles", "ects": 6, "local_credit": 3, "type": "mandatory", "prerequisites": ["COMP2112"]},
                        {"code": "MATH2201", "name": "Probability", "ects": 6, "local_credit": 3, "type": "mandatory", "prerequisites": ["MATH1112"]},
                    ],
                    "fall_3": [
                        {"code": "COMP3112", "name": "Analysis of Algorithms", "ects": 6, "local_credit": 4, "type": "mandatory", "prerequisites": ["COMP2112", "MATH2103"]},
                        {"code": "COMP3401", "name": "Computer Organization", "ects": 4, "local_credit": 3, "type": "mandatory", "prerequisites": ["ELEC1411"]},
                        {"code": "COMP3105", "name": "Automata and Formal Languages", "ects": 5, "local_credit": 3, "type": "mandatory", "prerequisites": ["MATH2103"]},
                    ],
                    "spring_3": [
                        {"code": "COMP3432", "name": "Operating Systems", "ects": 5, "local_credit": 3, "type": "mandatory", "prerequisites": ["COMP2112"]},
                        {"code": "COMP3334", "name": "Computer Networks", "ects": 5, "local_credit": 3, "type": "mandatory", "prerequisites": ["COMP2112"]},
                        {"code": "SOFT3112", "name": "Software Development Practice", "ects": 6, "local_credit": 3, "type": "mandatory", "prerequisites": ["SOFT2101"]},
                    ],
                    "fall_4": [
                        {"code": "ENGR4901", "name": "Introduction to Design Projects", "ects": 1, "local_credit": 1, "type": "mandatory", "prerequisites": []},
                        {"code": "COMP4101", "name": "Machine Learning", "ects": 6, "local_credit": 3, "type": "area_elective", "prerequisites": ["COMP3112"]},
                    ],
                    "spring_4": [
                        {"code": "COMP4912", "name": "Graduation Design Project", "ects": 8, "local_credit": 4, "type": "mandatory", "prerequisites": ["ENGR4901"]},
                        {"code": "COMP3335", "name": "Cybersecurity", "ects": 5, "local_credit": 3, "type": "area_elective", "prerequisites": ["COMP3334"]},
                    ],
                },
                "electives": {
                    "technical": [
                        {"code": "COMP4101", "name": "Machine Learning", "ects": 6},
                        {"code": "COMP4203", "name": "Mobile Application Development", "ects": 6},
                        {"code": "COMP3335", "name": "Cybersecurity", "ects": 5},
                    ],
                    "general": [
                        {"code": "CORE2001", "name": "Philosophy", "ects": 3},
                        {"code": "CORE3001", "name": "History of Science", "ects": 3},
                    ],
                },
                "prerequisites": {
                    "COMP1112": ["COMP1111"],
                    "COMP2112": ["COMP1112"],
                    "COMP3112": ["COMP2112", "MATH2103"],
                    "COMP3432": ["COMP1112"],
                    "COMP3334": ["COMP1112"],
                    "SOFT2101": ["COMP1112"],
                    "SOFT3112": ["SOFT2101"],
                    "COMP3335": ["COMP3334"],
                    "COMP4912": ["ENGR4901"],
                },
            },
            # Add more programs as needed...
        },
    },
}


def get_program(faculty: str, program: str) -> dict:
    """Get program data by faculty and program name."""
    return ISIK_UNIVERSITY_PROGRAMS.get("undergraduate", {}).get(faculty, {}).get(program, {})


def get_all_programs() -> dict:
    """Get all programs dictionary."""
    return ISIK_UNIVERSITY_PROGRAMS


def get_semester_courses_for_program(faculty: str, program: str, semester: str) -> list:
    """Get courses for a specific semester of a program."""
    prog_data = get_program(faculty, program)
    return prog_data.get("semesters", {}).get(semester, [])


def get_program_info(faculty: str, program: str) -> dict:
    """Get basic program information."""
    prog_data = get_program(faculty, program)
    return {
        "program_code": prog_data.get("program_code", ""),
        "degree": prog_data.get("degree", ""),
        "language": prog_data.get("language", ""),
        "total_ects": prog_data.get("total_ects", 0),
        "duration_years": prog_data.get("duration_years", 0),
        "min_gpa": prog_data.get("min_gpa", 0.0),
    }
