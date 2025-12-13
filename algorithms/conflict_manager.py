"""
Conflict Manager with Bitmask optimization for fast conflict detection.

This module provides an efficient conflict detection system using bitmasks
to replace O(N^2) nested loops with O(1) bitwise operations.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Set

if TYPE_CHECKING:
    from core.models import Course


class ConflictManager:
    """
    Manages course conflicts using bitmask optimization.

    Instead of checking each course pair individually (O(N^2)),
    this manager pre-computes conflicts as bitmasks and uses
    bitwise operations for instant conflict detection (O(1)).
    """

    def __init__(self, all_courses: List[Course]):
        """
        Initialize conflict manager with all available courses.

        Args:
            all_courses: Complete list of courses to manage
        """
        self.courses = all_courses
        self.course_to_id: Dict[str, int] = {
            course.code: idx for idx, course in enumerate(all_courses)
        }
        self.id_to_course: Dict[int, Course] = dict(enumerate(all_courses))
        self.conflict_masks: List[int] = [0] * len(all_courses)
        self._precompute_conflicts()

    def _precompute_conflicts(self) -> None:
        """
        Pre-compute all conflicts as bitmasks.

        For each course i, creates a bitmask where bit j is set to 1
        if course i conflicts with course j.
        """
        for i, course1 in enumerate(self.courses):
            conflict_mask = 0
            for j, course2 in enumerate(self.courses):
                if i != j and course1.conflicts_with(course2):
                    conflict_mask |= (1 << j)
            self.conflict_masks[i] = conflict_mask

    def has_conflict(self, current_mask: int, new_course_code: str) -> bool:
        """
        Check if adding a new course creates conflict.

        Args:
            current_mask: Bitmask representing currently selected courses
            new_course_code: Code of the course to add

        Returns:
            True if adding the course creates a conflict
        """
        if new_course_code not in self.course_to_id:
            return False

        new_course_id = self.course_to_id[new_course_code]
        return (current_mask & self.conflict_masks[new_course_id]) != 0

    def get_schedule_mask(self, course_codes: List[str]) -> int:
        """
        Convert a list of course codes to a bitmask.

        Args:
            course_codes: List of course codes

        Returns:
            Bitmask with bits set for each course
        """
        mask = 0
        for code in course_codes:
            if code in self.course_to_id:
                mask |= (1 << self.course_to_id[code])
        return mask

    def count_conflicts(self, course_codes: List[str]) -> int:
        """
        Count total conflicts in a schedule.

        Args:
            course_codes: List of course codes in schedule

        Returns:
            Number of conflicting course pairs
        """
        conflicts = 0
        schedule_mask = 0

        for code in course_codes:
            if code not in self.course_to_id:
                continue

            course_id = self.course_to_id[code]
            # Check if this course conflicts with any already selected
            if (schedule_mask & self.conflict_masks[course_id]) != 0:
                # Count how many conflicts
                conflicts += bin(schedule_mask & self.conflict_masks[course_id]).count('1')

            # Add this course to the mask
            schedule_mask |= (1 << course_id)

        return conflicts

    def get_conflicting_courses(self, current_mask: int, new_course_code: str) -> Set[str]:
        """
        Get the set of courses that conflict with a new course.

        Args:
            current_mask: Bitmask of currently selected courses
            new_course_code: Code of the course to check

        Returns:
            Set of course codes that conflict with the new course
        """
        if new_course_code not in self.course_to_id:
            return set()

        new_course_id = self.course_to_id[new_course_code]
        conflict_mask = current_mask & self.conflict_masks[new_course_id]

        conflicting = set()
        for course_id, course in self.id_to_course.items():
            if (conflict_mask >> course_id) & 1:
                conflicting.add(course.code)

        return conflicting

    def add_course_to_mask(self, current_mask: int, course_code: str) -> int:
        """
        Add a course to the current mask.

        Args:
            current_mask: Current schedule bitmask
            course_code: Code of course to add

        Returns:
            New mask with the course added
        """
        if course_code not in self.course_to_id:
            return current_mask

        course_id = self.course_to_id[course_code]
        return current_mask | (1 << course_id)

    def remove_course_from_mask(self, current_mask: int, course_code: str) -> int:
        """
        Remove a course from the current mask.

        Args:
            current_mask: Current schedule bitmask
            course_code: Code of course to remove

        Returns:
            New mask with the course removed
        """
        if course_code not in self.course_to_id:
            return current_mask

        course_id = self.course_to_id[course_code]
        return current_mask & ~(1 << course_id)


__all__ = ["ConflictManager"]
