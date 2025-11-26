"""
Academic utilities for SchedularV3 - Phase 7.

Includes:
- PrerequisiteChecker: Validate prerequisites and detect circular dependencies
- GPACalculator: Calculate GPA/CGPA
- GraduationPlanner: Track graduation progress

Updated with Işık University official data.
"""
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass
import logging
from collections import deque

from .models import Course, Schedule, Grade, Transcript, GraduationRequirement

# Import Işık University official data
try:
    from .prerequisite_data import (
        COMPUTER_ENGINEERING_PREREQUISITES,
        get_prerequisites,
        can_take_course,
        get_missing_prerequisites,
        get_courses_unlocked_by,
        get_prerequisite_chain
    )
    ISIK_DATA_AVAILABLE = True
except ImportError:
    ISIK_DATA_AVAILABLE = False
    logger.warning("Işık University prerequisite data not available")

logger = logging.getLogger(__name__)


class PrerequisiteChecker:
    """
    Validates course prerequisites and detects circular dependencies.
    Updated to use Işık University official prerequisite data when available.
    """
    
    def __init__(self, courses: List[Course], use_isik_data: bool = True):
        """
        Initialize with a list of courses.
        
        Args:
            courses: List of all available courses
            use_isik_data: If True, use Işık University official data when available
        """
        self.courses = {c.main_code: c for c in courses}
        self._prerequisite_graph: Dict[str, List[str]] = {}
        self.use_isik_data = use_isik_data and ISIK_DATA_AVAILABLE
        self._build_graph()
    
    def _build_graph(self) -> None:
        """Build prerequisite dependency graph."""
        if self.use_isik_data:
            # Use official Işık University prerequisite data
            self._prerequisite_graph = COMPUTER_ENGINEERING_PREREQUISITES.copy()
            logger.info("Using Işık University official prerequisite data")
        else:
            # Fallback to course-defined prerequisites
            for code, course in self.courses.items():
                self._prerequisite_graph[code] = course.prerequisites.copy()
            logger.info("Using course-defined prerequisites")
    
    def check_prerequisites(
        self, 
        course_code: str, 
        completed_courses: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Check if prerequisites are satisfied for a course.
        Uses Işık University official data when available.
        
        Args:
            course_code: Course code to check
            completed_courses: List of completed course codes
            
        Returns:
            Tuple of (requirements_met, missing_prerequisites)
        """
        if course_code not in self.courses:
            logger.warning(f"Course {course_code} not found")
            return True, []
        
        course = self.courses[course_code]
        missing = [p for p in course.prerequisites if p not in completed_courses]
        
        return len(missing) == 0, missing
    
    def get_prerequisite_chain(self, course_code: str) -> List[List[str]]:
        """
        Get full prerequisite chain (all levels) for a course.
        
        Args:
            course_code: Course code
            
        Returns:
            List of prerequisite levels (innermost to outermost)
            
        Example:
            CS301 requires [CS201, CS202]
            CS201 requires [CS101]
            CS202 requires [CS101]
            
            Returns: [[CS101], [CS201, CS202], [CS301]]
        """
        if course_code not in self.courses:
            return []
        
        visited = set()
        levels: List[Set[str]] = []
        current_level = {course_code}
        
        while current_level:
            next_level = set()
            for code in current_level:
                if code in visited:
                    continue
                visited.add(code)
                
                if code in self._prerequisite_graph:
                    for prereq in self._prerequisite_graph[code]:
                        if prereq not in visited:
                            next_level.add(prereq)
            
            if next_level:
                levels.insert(0, next_level)
            current_level = next_level
        
        return [list(level) for level in levels]
    
    def detect_circular_dependency(self) -> Optional[List[str]]:
        """
        Detect circular dependencies in prerequisite graph using DFS.
        
        Returns:
            Cycle path if found, None otherwise
            
        Example:
            If CS301 -> CS201 -> CS101 -> CS301 (circular)
            Returns: ['CS301', 'CS201', 'CS101', 'CS301']
        """
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> Optional[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            if node in self._prerequisite_graph:
                for neighbor in self._prerequisite_graph[node]:
                    if neighbor not in visited:
                        result = dfs(neighbor, path.copy())
                        if result:
                            return result
                    elif neighbor in rec_stack:
                        # Found cycle
                        cycle_start = path.index(neighbor)
                        return path[cycle_start:] + [neighbor]
            
            rec_stack.remove(node)
            return None
        
        # Check all nodes
        for node in self._prerequisite_graph:
            if node not in visited:
                result = dfs(node, [])
                if result:
                    return result
        
        return None
    
    def get_available_courses(
        self, 
        completed_courses: List[str],
        all_courses: Optional[List[Course]] = None
    ) -> List[Course]:
        """
        Get list of courses that can be taken given completed courses.
        
        Args:
            completed_courses: List of completed course codes
            all_courses: Optional list to filter from (uses self.courses if None)
            
        Returns:
            List of available courses
        """
        courses_to_check = all_courses if all_courses else list(self.courses.values())
        available = []
        
        for course in courses_to_check:
            can_take, _ = self.check_prerequisites(course.main_code, completed_courses)
            if can_take and course.main_code not in completed_courses:
                available.append(course)
        
        return available
    
    def validate_schedule(
        self, 
        schedule: Schedule, 
        completed_courses: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all courses in schedule have prerequisites met.
        
        Args:
            schedule: Schedule to validate
            completed_courses: List of completed course codes
            
        Returns:
            Tuple of (is_valid, list_of_courses_with_missing_prereqs)
        """
        invalid_courses = []
        
        for course in schedule.courses:
            can_take, missing = self.check_prerequisites(
                course.main_code, 
                completed_courses
            )
            if not can_take:
                invalid_courses.append(course.main_code)
                logger.warning(
                    f"Course {course.main_code} has missing prerequisites: {missing}"
                )
        
        return len(invalid_courses) == 0, invalid_courses


class GPACalculator:
    """
    GPA calculation utilities and GPA simulation.
    """
    
    @staticmethod
    def calculate_gpa(grades: List[Grade]) -> float:
        """
        Calculate GPA from list of grades.
        
        Args:
            grades: List of Grade objects
            
        Returns:
            GPA (0.0 - 4.0)
        """
        total_points = 0.0
        total_credits = 0
        
        for grade in grades:
            if grade.letter_grade != "P":  # Don't count Pass/Fail
                total_points += grade.numeric_grade * grade.ects
                total_credits += grade.ects
        
        return total_points / total_credits if total_credits > 0 else 0.0
    
    @staticmethod
    def simulate_gpa(
        current_transcript: Transcript,
        planned_courses: List[Tuple[str, int, str]]
    ) -> Dict[str, float]:
        """
        Simulate "what-if" GPA scenarios.
        
        Args:
            current_transcript: Current transcript
            planned_courses: List of (course_code, ects, letter_grade) tuples
            
        Returns:
            Dictionary with simulated GPA statistics
            
        Example:
            simulate_gpa(transcript, [
                ("CS301", 6, "AA"),
                ("CS302", 6, "BA")
            ])
        """
        # Create simulated grades
        simulated_grades = current_transcript.grades.copy()
        
        for course_code, ects, letter_grade in planned_courses:
            simulated_grades.append(Grade(
                course_code=course_code,
                course_name="Simulated Course",
                ects=ects,
                letter_grade=letter_grade,
                numeric_grade=Grade.letter_to_numeric(letter_grade),
                semester="Simulated",
                is_retake=False
            ))
        
        # Calculate new GPA
        new_gpa = GPACalculator.calculate_gpa(simulated_grades)
        
        # Calculate change
        gpa_change = new_gpa - current_transcript.gpa
        
        # Calculate new ECTS
        new_ects = sum(g.ects for g in simulated_grades if Grade.is_passing_grade(g.letter_grade))
        
        return {
            "current_gpa": current_transcript.gpa,
            "simulated_gpa": new_gpa,
            "gpa_change": gpa_change,
            "current_ects": current_transcript.total_ects_earned,
            "simulated_ects": new_ects,
            "ects_change": new_ects - current_transcript.total_ects_earned
        }
    
    @staticmethod
    def calculate_required_gpa(
        current_transcript: Transcript,
        target_gpa: float,
        remaining_ects: int
    ) -> Optional[float]:
        """
        Calculate required GPA in remaining courses to reach target.
        
        Args:
            current_transcript: Current transcript
            target_gpa: Desired GPA
            remaining_ects: ECTS credits remaining
            
        Returns:
            Required GPA for remaining courses (None if impossible)
        """
        current_points = current_transcript.gpa * current_transcript.total_ects_taken
        total_ects = current_transcript.total_ects_taken + remaining_ects
        
        required_total_points = target_gpa * total_ects
        required_points = required_total_points - current_points
        required_gpa = required_points / remaining_ects if remaining_ects > 0 else 0.0
        
        # Check if achievable (max GPA is 4.0)
        if required_gpa > 4.0:
            return None
        
        return max(0.0, required_gpa)


class GraduationPlanner:
    """
    Graduation planning and progress tracking.
    """
    
    def __init__(
        self, 
        requirement: GraduationRequirement,
        transcript: Transcript
    ):
        """
        Initialize graduation planner.
        
        Args:
            requirement: Graduation requirements
            transcript: Student transcript
        """
        self.requirement = requirement
        self.transcript = transcript
    
    def get_progress_report(self) -> Dict[str, Any]:
        """
        Get detailed graduation progress report.
        
        Returns:
            Dictionary with progress information
        """
        completion = self.requirement.check_completion(self.transcript)
        completed_courses = self.transcript.get_completed_courses()

        # Calculate semesters to graduation (assuming 30 ECTS/semester)
        remaining_ects = completion["ects_remaining"]
        ects_limit = self.transcript.get_ects_limit()
        semesters_remaining = (remaining_ects + ects_limit - 1) // ects_limit  # Ceiling division

        return {
            "can_graduate": completion["can_graduate"],
            "completion_percentage": (
                completion["ects_earned"] / completion["ects_required"] * 100
            ) if completion["ects_required"] > 0 else 0.0,
            "core_courses": {
                "total": len(self.requirement.core_courses),
                "completed": len(self.requirement.core_courses) - len(completion["missing_core_courses"]),
                "missing": completion["missing_core_courses"]
            },
            "ects": {
                "earned": completion["ects_earned"],
                "required": completion["ects_required"],
                "remaining": remaining_ects,
                "percentage": (completion["ects_earned"] / completion["ects_required"] * 100)
                    if completion["ects_required"] > 0 else 0.0
            },
            "gpa": {
                "current": completion["current_gpa"],
                "required": completion["min_gpa"],
                "meets_requirement": completion["gpa_complete"]
            },
            "electives": {
                "earned": completion["elective_ects_earned"],
                "required": completion["elective_ects_required"],
                "complete": completion["elective_complete"]
            },
            "timeline": {
                "semesters_remaining": semesters_remaining,
                "ects_per_semester_limit": ects_limit
            }
        }
    
    def suggest_next_semester(
        self,
        available_courses: List[Course],
        max_ects: Optional[int] = None
    ) -> List[Course]:
        """
        Suggest courses for next semester based on graduation requirements.
        
        Args:
            available_courses: List of available courses
            max_ects: Maximum ECTS to take (uses limit from GPA if None)
            
        Returns:
            List of suggested courses
        """
        if max_ects is None:
            max_ects = self.transcript.get_ects_limit()
        
        completed = self.transcript.get_completed_courses()
        completion = self.requirement.check_completion(self.transcript)
        
        # Prioritize missing core courses
        suggestions = []
        current_ects = 0
        
        # First, add missing core courses
        for course_code in completion["missing_core_courses"]:
            for course in available_courses:
                if course.main_code == course_code and current_ects + course.ects <= max_ects:
                    suggestions.append(course)
                    current_ects += course.ects
                    break
        
        # Then, add electives if ECTS limit not reached
        if not completion["elective_complete"]:
            for course in available_courses:
                if (course.main_code not in self.requirement.core_courses and
                    course.main_code not in completed and
                    course not in suggestions and
                    current_ects + course.ects <= max_ects):
                    suggestions.append(course)
                    current_ects += course.ects
        
        return suggestions
    
    def estimate_graduation_date(
        self, 
        current_semester: str,
        semesters_per_year: int = 2
    ) -> str:
        """
        Estimate graduation semester.
        
        Args:
            current_semester: Current semester (e.g., "2024 Fall")
            semesters_per_year: Number of semesters per year
            
        Returns:
            Estimated graduation semester
        """
        progress = self.get_progress_report()
        semesters_remaining = progress["timeline"]["semesters_remaining"]
        
        # Parse current semester
        parts = current_semester.split()
        if len(parts) != 2:
            return "Unknown"
        
        year = int(parts[0])
        season = parts[1]
        
        # Calculate graduation semester
        season_order = ["Spring", "Fall"] if semesters_per_year == 2 else ["Spring", "Summer", "Fall"]
        current_index = season_order.index(season) if season in season_order else 0
        
        for _ in range(semesters_remaining):
            current_index = (current_index + 1) % len(season_order)
            if current_index == 0:
                year += 1
        
        return f"{year} {season_order[current_index]}"
