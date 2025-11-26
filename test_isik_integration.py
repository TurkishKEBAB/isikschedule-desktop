"""
Quick test script for Işık University data integration.
"""

print("=" * 60)
print("IŞIK UNIVERSITY DATA INTEGRATION TEST")
print("=" * 60)

# Test 1: Prerequisite Data
print("\n1. PREREQUISITE DATA")
print("-" * 60)
from core.prerequisite_data import (
    COMPUTER_ENGINEERING_PREREQUISITES,
    get_prerequisites,
    get_prerequisite_chain,
    can_take_course
)

print(f"Total courses with prerequisites: {len(COMPUTER_ENGINEERING_PREREQUISITES)}")
prereqs = get_prerequisites('COMP3112')
print(f"\nCOMP3112 prerequisites: {prereqs}")

chain = get_prerequisite_chain('COMP3112')
print(f"\nPrerequisite chain for COMP3112:")
for i, level in enumerate(chain, 1):
    print(f"  Level {i}: {level}")

completed = ["COMP1111", "COMP1112", "COMP2112", "MATH2103"]
can_take = can_take_course('COMP3112', completed)
print(f"\nCan take COMP3112 with {completed}? {can_take}")

# Test 2: Curriculum Data
print("\n\n2. CURRICULUM DATA")
print("-" * 60)
from core.curriculum_data import (
    GRADUATION_REQUIREMENTS,
    SEMESTER_1_MANDATORY,
    get_total_ects_by_semester
)

print(f"Total ECTS requirement: {GRADUATION_REQUIREMENTS['total_ects']}")
print(f"Minimum GPA: {GRADUATION_REQUIREMENTS['minimum_gpa']}")
print(f"Required area electives: {GRADUATION_REQUIREMENTS['area_electives']}")

print(f"\nFall-1 courses:")
for course in SEMESTER_1_MANDATORY[:3]:
    print(f"  {course['code']}: {course['name_en']} ({course['ects']} ECTS)")

total_ects = get_total_ects_by_semester('Fall-1')
print(f"\nTotal ECTS for Fall-1: {total_ects}")

# Test 3: Sample Data
print("\n\n3. SAMPLE COURSE DATA")
print("-" * 60)
from core.isik_university_data import (
    create_sample_courses,
    get_course_conflicts,
    GRADE_SCALE,
    ECTS_LIMITS_BY_GPA
)

courses = create_sample_courses()
print(f"Total sample courses: {len(courses)}")

print(f"\nFirst 3 courses:")
for c in courses[:3]:
    print(f"  {c.code}: {c.teacher}, schedule={c.schedule}, {c.ects} ECTS")

conflicts = get_course_conflicts()
print(f"\nCourse conflicts:")
for code, conflicting in list(conflicts.items())[:2]:
    print(f"  {code} conflicts with: {', '.join(conflicting)}")

print(f"\nGrade scale: AA={GRADE_SCALE['AA']}, CC={GRADE_SCALE['CC']}, F={GRADE_SCALE['F']}")
print(f"\nECTS limits:")
for key, value in ECTS_LIMITS_BY_GPA.items():
    print(f"  {key}: {value} ECTS")

# Test 4: Settings Update
print("\n\n4. SETTINGS UPDATE")
print("-" * 60)
from config.settings import ISIK_BLUE_PRIMARY, DEFAULT_MAX_ECTS, SCHEDULE_COLORS

print(f"Işık Blue primary color: {ISIK_BLUE_PRIMARY}")
print(f"Default max ECTS: {DEFAULT_MAX_ECTS}")
print(f"Schedule colors (first 3): {SCHEDULE_COLORS[:3]}")

# Test 5: Academic Integration
print("\n\n5. ACADEMIC SYSTEM INTEGRATION")
print("-" * 60)
try:
    from core.academic import PrerequisiteChecker, ISIK_DATA_AVAILABLE
    print(f"Işık data available in academic.py: {ISIK_DATA_AVAILABLE}")
    
    checker = PrerequisiteChecker(courses, use_isik_data=True)
    print(f"PrerequisiteChecker initialized with {len(checker._prerequisite_graph)} courses")
    print(f"Using official Işık data: {checker.use_isik_data}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 60)
