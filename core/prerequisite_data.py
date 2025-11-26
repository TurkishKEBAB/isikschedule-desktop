"""
Işık University - Computer Engineering Prerequisites Database

Source: Official Course Prerequisites Table
Date: 2024-2025 Academic Year
URL: isikun.edu.tr

This module contains prerequisite relationships for Computer Engineering courses.
"""

from typing import Dict, List

# Prerequisite mappings: {course_code: [list_of_prerequisite_codes]}
COMPUTER_ENGINEERING_PREREQUISITES: Dict[str, List[str]] = {
    # 1st Year - Foundational Courses
    "MATH1112": ["MATH1111"],  # Calculus II requires Calculus I
    "COMP1112": ["COMP1111"],  # Object Oriented Programming requires Fundamentals of Programming
    "ENGL1102": ["ENGL1101"],  # Academic English 2 requires Academic English 1
    
    # 2nd Year - Core Courses
    "COMP2112": ["COMP1112"],  # Data Structures and Algorithms requires OOP
    "COMP2222": ["COMP1112"],  # Database Systems requires OOP
    "MATH2201": ["MATH1112"],  # Probability requires Calculus II
    
    # 3rd Year - Advanced Courses
    "COMP3112": ["COMP2112", "MATH2103"],  # Analysis of Algorithms requires DS&A and Discrete Math
    "COMP3401": ["ELEC1411"],  # Computer Organization requires Logic Design
    "SOFT2101": ["COMP1112"],  # Software Engineering Principles requires OOP
    "INDE2156": ["MATH2201"],  # Engineering Statistics requires Probability
    "COMP3432": ["COMP1112"],  # Operating Systems requires OOP
    "COMP3334": ["COMP1112"],  # Computer Networks requires OOP
    "COMP3105": ["MATH2103"],  # Automata & Formal Languages requires Discrete Math
    "COMP3402": ["ELEC1411"],  # Microprocessors requires Logic Design
    
    # Courses with no prerequisites
    "COMP1007": [],  # Introduction to Computer and Software Engineering
    "COMP1111": [],  # Fundamentals of Programming
    "MATH1111": [],  # Calculus I
    "MATH2103": [],  # Discrete Mathematics
    "ENGL1101": [],  # Academic English 1
    "PHYS1112": [],  # Physics - Electricity & Magnetism
    "ELEC1411": [],  # Logic Design
}

# Course groups (related courses that should be taken together or in sequence)
COURSE_GROUPS: Dict[str, List[str]] = {
    "calculus_sequence": ["MATH1111", "MATH1112"],
    "programming_sequence": ["COMP1111", "COMP1112", "COMP2112"],
    "english_sequence": ["ENGL1101", "ENGL1102"],
    "math_foundation": ["MATH1111", "MATH1112", "MATH2103", "MATH2201"],
    "core_cs": ["COMP1111", "COMP1112", "COMP2112", "COMP3112"],
    "systems_courses": ["COMP3401", "COMP3432", "COMP3402"],
}

# Recommended course order (semester suggestions)
RECOMMENDED_SEMESTER: Dict[str, int] = {
    # Fall 1
    "MATH1111": 1,
    "COMP1007": 1,
    "COMP1111": 1,
    "ENGL1101": 1,
    
    # Spring 1
    "MATH1112": 2,
    "PHYS1112": 2,
    "COMP1112": 2,
    "ENGL1102": 2,
    
    # Fall 2
    "MATH2103": 3,
    "COMP2112": 3,
    "ELEC2205": 3,
    
    # Spring 2
    "COMP2502": 4,
    "COMP2222": 4,
    "MATH2201": 4,
    "MATH2104": 4,
    "ELEC1411": 4,
    
    # Fall 3
    "COMP3112": 5,
    "COMP3401": 5,
    "SOFT2101": 5,
    "INDE2156": 5,
    
    # Spring 3
    "COMP3432": 6,
    "COMP3105": 6,
    "COMP3402": 6,
    "COMP3334": 6,
}


def get_prerequisites(course_code: str) -> List[str]:
    """
    Get the list of prerequisite courses for a given course.
    
    Args:
        course_code: Course code (e.g., "COMP3112")
        
    Returns:
        List of prerequisite course codes
    """
    return COMPUTER_ENGINEERING_PREREQUISITES.get(course_code, [])


def has_prerequisites(course_code: str) -> bool:
    """Check if a course has any prerequisites."""
    return len(get_prerequisites(course_code)) > 0


def can_take_course(course_code: str, completed_courses: List[str]) -> bool:
    """
    Check if a student can take a course based on completed courses.
    
    Args:
        course_code: Course to check
        completed_courses: List of course codes the student has completed
        
    Returns:
        True if all prerequisites are met, False otherwise
    """
    prerequisites = get_prerequisites(course_code)
    return all(prereq in completed_courses for prereq in prerequisites)


def get_missing_prerequisites(course_code: str, completed_courses: List[str]) -> List[str]:
    """
    Get the list of missing prerequisites for a course.
    
    Args:
        course_code: Course to check
        completed_courses: List of completed course codes
        
    Returns:
        List of missing prerequisite course codes
    """
    prerequisites = get_prerequisites(course_code)
    return [prereq for prereq in prerequisites if prereq not in completed_courses]


def get_courses_unlocked_by(course_code: str) -> List[str]:
    """
    Get courses that become available after completing a given course.
    
    Args:
        course_code: Completed course code
        
    Returns:
        List of course codes that require this course as a prerequisite
    """
    unlocked = []
    for course, prereqs in COMPUTER_ENGINEERING_PREREQUISITES.items():
        if course_code in prereqs:
            unlocked.append(course)
    return unlocked


def get_prerequisite_chain(course_code: str) -> List[List[str]]:
    """
    Get the complete prerequisite chain for a course (all levels).
    
    Args:
        course_code: Course code
        
    Returns:
        List of lists, where each list is a level in the prerequisite tree
        
    Example:
        COMP3112 → [[COMP2112, MATH2103], [COMP1112], [COMP1111]]
    """
    if course_code not in COMPUTER_ENGINEERING_PREREQUISITES:
        return []
    
    chain = []
    current_level = [course_code]
    visited = set()
    
    while current_level:
        next_level = []
        for course in current_level:
            if course in visited:
                continue
            visited.add(course)
            
            prereqs = get_prerequisites(course)
            next_level.extend(prereqs)
        
        if next_level:
            chain.append(next_level)
        current_level = next_level
    
    return chain


def get_recommended_semester(course_code: str) -> int:
    """
    Get the recommended semester for taking a course.
    
    Args:
        course_code: Course code
        
    Returns:
        Recommended semester number (1-8), or 0 if not found
    """
    return RECOMMENDED_SEMESTER.get(course_code, 0)


# Example usage
if __name__ == "__main__":
    print("=== Işık University - Computer Engineering Prerequisites ===\n")
    
    # Example 1: Check prerequisites for Analysis of Algorithms
    course = "COMP3112"
    prereqs = get_prerequisites(course)
    print(f"{course} prerequisites: {prereqs}")
    
    # Example 2: Check if student can take a course
    completed = ["COMP1111", "COMP1112", "COMP2112", "MATH2103"]
    can_take = can_take_course(course, completed)
    print(f"Can take {course}? {can_take}")
    
    # Example 3: Get missing prerequisites
    completed_partial = ["COMP1111", "COMP1112", "COMP2112"]
    missing = get_missing_prerequisites(course, completed_partial)
    print(f"Missing prerequisites for {course}: {missing}")
    
    # Example 4: Get prerequisite chain
    chain = get_prerequisite_chain(course)
    print(f"\nPrerequisite chain for {course}:")
    for i, level in enumerate(chain, 1):
        print(f"  Level {i}: {level}")
    
    # Example 5: Courses unlocked by completing COMP1112
    unlocked = get_courses_unlocked_by("COMP1112")
    print(f"\nCourses unlocked by COMP1112: {unlocked}")
