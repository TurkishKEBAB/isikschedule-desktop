"""
Sample academic data for testing Phase 7 features.
"""
from core.models import Grade, Transcript, GraduationRequirement


def create_sample_transcript() -> Transcript:
    """Create a sample transcript for testing."""
    transcript = Transcript(
        student_id="20190123",
        student_name="Ahmet Yılmaz",
        program="Computer Engineering"
    )
    
    # Fall 2023
    transcript.add_grade(Grade(
        course_code="CS101",
        course_name="Introduction to Programming",
        ects=6,
        letter_grade="AA",
        numeric_grade=4.0,
        semester="2023 Fall"
    ))
    transcript.add_grade(Grade(
        course_code="MATH101",
        course_name="Calculus I",
        ects=6,
        letter_grade="BA",
        numeric_grade=3.5,
        semester="2023 Fall"
    ))
    transcript.add_grade(Grade(
        course_code="PHYS101",
        course_name="Physics I",
        ects=5,
        letter_grade="BB",
        numeric_grade=3.0,
        semester="2023 Fall"
    ))
    transcript.add_grade(Grade(
        course_code="ENG101",
        course_name="Academic English",
        ects=3,
        letter_grade="AA",
        numeric_grade=4.0,
        semester="2023 Fall"
    ))
    transcript.add_grade(Grade(
        course_code="HIST101",
        course_name="Principles of Atatürk",
        ects=2,
        letter_grade="BA",
        numeric_grade=3.5,
        semester="2023 Fall"
    ))
    
    # Spring 2024
    transcript.add_grade(Grade(
        course_code="CS102",
        course_name="Data Structures",
        ects=6,
        letter_grade="AA",
        numeric_grade=4.0,
        semester="2024 Spring"
    ))
    transcript.add_grade(Grade(
        course_code="MATH102",
        course_name="Calculus II",
        ects=6,
        letter_grade="BB",
        numeric_grade=3.0,
        semester="2024 Spring"
    ))
    transcript.add_grade(Grade(
        course_code="PHYS102",
        course_name="Physics II",
        ects=5,
        letter_grade="BA",
        numeric_grade=3.5,
        semester="2024 Spring"
    ))
    transcript.add_grade(Grade(
        course_code="CHEM101",
        course_name="General Chemistry",
        ects=4,
        letter_grade="CB",
        numeric_grade=2.5,
        semester="2024 Spring"
    ))
    
    # Fall 2024
    transcript.add_grade(Grade(
        course_code="CS201",
        course_name="Algorithms",
        ects=6,
        letter_grade="AA",
        numeric_grade=4.0,
        semester="2024 Fall"
    ))
    transcript.add_grade(Grade(
        course_code="CS202",
        course_name="Computer Organization",
        ects=6,
        letter_grade="BA",
        numeric_grade=3.5,
        semester="2024 Fall"
    ))
    transcript.add_grade(Grade(
        course_code="MATH201",
        course_name="Linear Algebra",
        ects=5,
        letter_grade="BB",
        numeric_grade=3.0,
        semester="2024 Fall"
    ))
    transcript.add_grade(Grade(
        course_code="ECE201",
        course_name="Digital Logic Design",
        ects=5,
        letter_grade="AA",
        numeric_grade=4.0,
        semester="2024 Fall"
    ))
    
    return transcript


def create_sample_requirement() -> GraduationRequirement:
    """Create sample graduation requirements."""
    return GraduationRequirement(
        program_name="Computer Engineering",
        total_ects_required=240,
        core_courses=[
            "CS101", "CS102", "CS201", "CS202", "CS301", "CS302",
            "CS401", "CS402", "MATH101", "MATH102", "MATH201",
            "PHYS101", "PHYS102", "ECE201", "ECE202"
        ],
        elective_ects_required=60,
        min_gpa=2.0
    )


def add_prerequisites_to_courses(courses):
    """Add sample prerequisites to course list."""
    # This would normally come from a database
    prereq_map = {
        "CS102": ["CS101"],
        "CS201": ["CS102"],
        "CS202": ["CS101"],
        "CS301": ["CS201"],
        "CS302": ["CS201", "CS202"],
        "CS401": ["CS301"],
        "CS402": ["CS302"],
        "MATH102": ["MATH101"],
        "MATH201": ["MATH102"],
        "PHYS102": ["PHYS101"],
        "ECE202": ["ECE201"]
    }
    
    for course in courses:
        if course.main_code in prereq_map:
            course.prerequisites = prereq_map[course.main_code]
    
    return courses
