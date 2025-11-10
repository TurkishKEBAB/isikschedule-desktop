"""
Constraint generation and handling for the course scheduler.

This module provides functionality for generating and managing course constraints,
such as mandatory PS/lab sections and dependencies between course sections.
"""
from typing import Dict, List, Set, Optional, Any
from core.models import Course, CourseGroup


class ConstraintUtils:
    """Utilities for generating and managing course constraints."""

    @staticmethod
    def auto_generate_constraints(courses: List[Course]) -> Dict[str, Dict[str, bool]]:
        """
        Automatically generate constraints from course data.

        Args:
            courses: List of Course objects

        Returns:
            Dictionary mapping main course codes to constraint dictionaries
        """
        groups = {}
        for course in courses:
            if course.main_code not in groups:
                groups[course.main_code] = []
            groups[course.main_code].append(course)

        constraints = {}
        for main_code, group in groups.items():
            constraints[main_code] = {
                "must_ps": any(c.course_type == "ps" for c in group),
                "must_lab": any(c.course_type == "lab" for c in group)
            }

        return constraints

    @staticmethod
    def generate_valid_group_selections(course_group: List[Course],
                                       constraints: Dict[str, Dict[str, bool]]) -> List[List[Course]]:
        """
        Generate all valid combinations of lecture, PS, and lab sections for a course group.

        Args:
            course_group: List of related Course objects sharing the same main_code
            constraints: Dictionary of constraints

        Returns:
            List of valid course selections (each a list of Course objects)
        """
        # Filter courses by type
        lectures = [c for c in course_group if c.course_type == "lecture"]
        if not lectures:
            return []

        ps_sections = [c for c in course_group if c.course_type == "ps"]
        lab_sections = [c for c in course_group if c.course_type == "lab"]

        valid_selections = []
        for lec in lectures:
            base_selection = [lec]

            # Get constraint for this main code
            constraint = constraints.get(lec.main_code, {"must_ps": False, "must_lab": False})
            must_ps = constraint.get("must_ps", False)
            must_lab = constraint.get("must_lab", False)

            # Determine options based on constraints
            ps_options = ps_sections if must_ps else [None] + ps_sections
            lab_options = lab_sections if must_lab else [None] + lab_sections

            # Skip if constraints cannot be satisfied
            if must_ps and not ps_sections:
                continue
            if must_lab and not lab_sections:
                continue

            # Generate all valid combinations
            for ps in ps_options:
                for lab in lab_options:
                    sel = base_selection.copy()
                    if ps is not None:
                        sel.append(ps)
                    if lab is not None:
                        sel.append(lab)
                    valid_selections.append(sel)

        return valid_selections

    @staticmethod
    def build_group_options(course_groups: Dict[str, CourseGroup],
                           mandatory_codes: Set[str],
                           replacement_target: str = "sections") -> tuple:
        """
        Build options for each course group based on constraints and mandatory requirements.

        Args:
            course_groups: Dictionary mapping main codes to CourseGroup objects
            mandatory_codes: Set of main codes that are mandatory
            replacement_target: Target mode for replacements ("sections" or "course")

        Returns:
            Tuple of (group_valid_selections, group_options)
        """
        # First, auto-generate constraints
        all_courses = []
        for group in course_groups.values():
            all_courses.extend(group.courses)

        constraints = ConstraintUtils.auto_generate_constraints(all_courses)

        # Generate valid selections for each group
        group_valid_selections = {}
        group_options = {}

        for main_code, group in course_groups.items():
            selections = ConstraintUtils.generate_valid_group_selections(group.courses, constraints)
            group_valid_selections[main_code] = selections

            # For mandatory courses, all valid selections are options
            if main_code in mandatory_codes:
                group_options[main_code] = selections
            # For optional courses, add None (not taking the course) as an option
            else:
                group_options[main_code] = [None] + (selections if selections else [])

            # If replacement target is "course", restrict to first valid option only
            if replacement_target == "course":
                if group_options[main_code] and group_options[main_code][0] is not None:
                    group_options[main_code] = [group_options[main_code][0]]

        return group_valid_selections, group_options

    @staticmethod
    def analyze_schedule_failure(group_valid_selections: Dict[str, List[List[Course]]],
                                mandatory_set: Set[str]) -> List[str]:
        """
        Analyze and provide reasons for scheduling failure.

        Args:
            group_valid_selections: Dictionary of valid selections for each course group
            mandatory_set: Set of mandatory course codes

        Returns:
            List of reasons for scheduling failure
        """
        reasons = []

        for code in mandatory_set:
            if not group_valid_selections.get(code):
                reasons.append(f"{code}: No valid sections available (missing lecture, PS, or lab).")
            else:
                reasons.append(f"{code}: Check for conflicts in available sections.")

        return reasons

    @staticmethod
    def validate_course_group(course_group: CourseGroup) -> Dict[str, Any]:
        """
        Validate a course group for completeness and consistency.

        Args:
            course_group: CourseGroup to validate

        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []

        # Check for lectures
        if not course_group.lecture_courses:
            issues.append("No lecture sections available")

        # Check for required components
        has_ps = bool(course_group.ps_courses)
        has_lab = bool(course_group.lab_courses)

        if has_ps and not has_lab:
            warnings.append("Has PS sections but no lab sections")
        elif has_lab and not has_ps:
            warnings.append("Has lab sections but no PS sections")

        # Check for ECTS consistency
        if course_group.lecture_courses:
            ects_values = set(c.ects for c in course_group.lecture_courses)
            if len(ects_values) > 1:
                warnings.append(f"Inconsistent ECTS values in lectures: {ects_values}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "has_ps": has_ps,
            "has_lab": has_lab,
            "lecture_count": len(course_group.lecture_courses),
            "ps_count": len(course_group.ps_courses),
            "lab_count": len(course_group.lab_courses)
        }

    @staticmethod
    def get_conflict_matrix(courses: List[Course]) -> Dict[str, Set[str]]:
        """
        Generate a conflict matrix showing which courses conflict with each other.

        Args:
            courses: List of courses to analyze

        Returns:
            Dictionary mapping course codes to set of conflicting course codes
        """
        conflict_matrix = {}

        for i, course1 in enumerate(courses):
            conflicts = set()
            for j, course2 in enumerate(courses):
                if i != j and course1.conflicts_with(course2):
                    conflicts.add(course2.code)

            conflict_matrix[course1.code] = conflicts

        return conflict_matrix

    @staticmethod
    def find_independent_sets(courses: List[Course]) -> List[List[Course]]:
        """
        Find maximal independent sets of courses (courses that don't conflict).

        Args:
            courses: List of courses

        Returns:
            List of independent course sets
        """
        # Simple greedy algorithm to find independent sets
        conflict_matrix = ConstraintUtils.get_conflict_matrix(courses)

        independent_sets = []
        remaining = set(c.code for c in courses)

        while remaining:
            # Start new independent set with a course
            current_set = []
            code = remaining.pop()
            course = next(c for c in courses if c.code == code)
            current_set.append(course)

            # Add compatible courses
            for other_code in list(remaining):
                other_course = next(c for c in courses if c.code == other_code)

                # Check if compatible with all in current set
                compatible = True
                for set_course in current_set:
                    if other_course.conflicts_with(set_course):
                        compatible = False
                        break

                if compatible:
                    current_set.append(other_course)
                    remaining.remove(other_code)

            independent_sets.append(current_set)

        return independent_sets
