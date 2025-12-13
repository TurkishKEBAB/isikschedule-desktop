"""
Smart Course Advisor Module for SchedularV3.

This module provides intelligent course recommendations based on:
- Student transcript analysis (failed courses, prerequisites)
- GPA-based ECTS limits
- Academic progress tracking
- Sequential course detection (e.g., MATH101 -> MATH102)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from core.models import Course, CourseGroup, Grade, Transcript

logger = logging.getLogger(__name__)

# Try to import Işık University specific data
ISIK_DATA_AVAILABLE = False
ECTS_LIMITS_BY_GPA: Dict[str, int] = {}
PREREQUISITE_MAP: Dict[str, List[str]] = {}

try:
    from core.isik_university_data import ECTS_LIMITS_BY_GPA
    from core.prerequisite_data import PREREQUISITE_MAP  # type: ignore
    ISIK_DATA_AVAILABLE = True
except ImportError:
    pass


@dataclass
class CourseRecommendation:
    """A single course recommendation with reasoning."""

    course_code: str
    course_name: str
    reason: str
    priority: str  # "high", "medium", "low"
    category: str  # "failed_retry", "prerequisite_met", "sequence_next", "elective"
    ects: int = 0

    def __str__(self) -> str:
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(self.priority, "⚪")
        return f"{priority_emoji} {self.course_code} - {self.course_name} ({self.reason})"


@dataclass
class AdvisorReport:
    """Complete advisor analysis report."""

    student_name: str = ""
    current_gpa: float = 0.0
    total_ects_completed: int = 0
    max_ects_allowed: int = 31

    # Recommendations by category
    must_retake: List[CourseRecommendation] = field(default_factory=list)
    recommended: List[CourseRecommendation] = field(default_factory=list)
    available_electives: List[CourseRecommendation] = field(default_factory=list)

    # Warnings and notes
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def all_recommendations(self) -> List[CourseRecommendation]:
        """Get all recommendations sorted by priority."""
        all_recs = self.must_retake + self.recommended + self.available_electives
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(all_recs, key=lambda r: priority_order.get(r.priority, 3))

    def get_mandatory_codes(self) -> Set[str]:
        """Get course codes that should be marked as mandatory."""
        return {r.course_code for r in self.must_retake}

    def get_optional_codes(self) -> Set[str]:
        """Get course codes that should be marked as optional."""
        return {r.course_code for r in self.recommended + self.available_electives}


class SmartCourseAdvisor:
    """
    Intelligent course advisor that analyzes transcripts and suggests courses.

    This advisor considers:
    - Failed courses that must be retaken
    - Prerequisite chains
    - Sequential courses (Part 1 -> Part 2)
    - GPA-based ECTS limits
    - Available courses in the current semester
    """

    def __init__(
        self,
        available_courses: Optional[Dict[str, "CourseGroup"]] = None,
        prerequisite_map: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        """
        Initialize the advisor.

        Args:
            available_courses: Dictionary of available course groups
            prerequisite_map: Custom prerequisite mapping (uses Işık data if not provided)
        """
        self._available_courses = available_courses or {}
        self._prerequisite_map = prerequisite_map or PREREQUISITE_MAP
        self._course_names: Dict[str, str] = {}
        self._course_ects: Dict[str, int] = {}

        # Build course info cache
        for main_code, group in self._available_courses.items():
            if group.courses:
                first_course = group.courses[0]
                self._course_names[main_code] = first_course.name
                self._course_ects[main_code] = first_course.ects

    def set_available_courses(self, courses: Dict[str, "CourseGroup"]) -> None:
        """Update available courses for the current semester."""
        self._available_courses = courses
        self._course_names.clear()
        self._course_ects.clear()

        for main_code, group in courses.items():
            if group.courses:
                first_course = group.courses[0]
                self._course_names[main_code] = first_course.name
                self._course_ects[main_code] = first_course.ects

    def analyze_transcript(self, transcript: "Transcript") -> AdvisorReport:
        """
        Analyze a student transcript and generate recommendations.

        Args:
            transcript: Student transcript with grades

        Returns:
            AdvisorReport with recommendations and warnings
        """
        report = AdvisorReport()

        # Calculate current GPA
        report.current_gpa = self._calculate_gpa(transcript.grades)
        report.total_ects_completed = sum(
            g.ects for g in transcript.grades if self._is_passing_grade(g.letter_grade)
        )

        # Determine ECTS limit based on GPA
        report.max_ects_allowed = self._get_ects_limit(report.current_gpa)

        # Add GPA-related notes
        if report.current_gpa < 2.0:
            report.warnings.append(
                f"⚠️ Ortalaman {report.current_gpa:.2f} < 2.00 olduğu için "
                f"ECTS limitin {report.max_ects_allowed} olarak belirlendi."
            )

        # Find failed courses
        failed_codes = self._find_failed_courses(transcript.grades)
        passed_codes = self._find_passed_courses(transcript.grades)

        # Generate recommendations
        self._add_failed_course_recommendations(report, failed_codes)
        self._add_prerequisite_recommendations(report, passed_codes, failed_codes)
        self._add_sequence_recommendations(report, passed_codes, failed_codes)

        return report

    def _calculate_gpa(self, grades: List["Grade"]) -> float:
        """Calculate GPA from grades."""
        if not grades:
            return 0.0

        grade_points = {
            "AA": 4.0, "BA": 3.5, "BB": 3.0, "CB": 2.5, "CC": 2.0,
            "DC": 1.5, "DD": 1.0, "FD": 0.5, "FF": 0.0,
            "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
            "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "F": 0.0,
        }

        total_points = 0.0
        total_credits = 0

        for grade in grades:
            letter = grade.letter_grade.upper().strip()
            if letter in grade_points and grade.ects > 0:
                total_points += grade_points[letter] * grade.ects
                total_credits += grade.ects

        return total_points / total_credits if total_credits > 0 else 0.0

    def _is_passing_grade(self, letter_grade: str) -> bool:
        """Check if a grade is passing."""
        passing = {"AA", "BA", "BB", "CB", "CC", "DC", "DD", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D"}
        return letter_grade.upper().strip() in passing

    def _get_ects_limit(self, gpa: float) -> int:
        """Get ECTS limit based on GPA."""
        if not ISIK_DATA_AVAILABLE:
            return 31  # Default

        if gpa >= 3.50:
            return ECTS_LIMITS_BY_GPA.get("high", 45)
        elif gpa >= 2.50:
            return ECTS_LIMITS_BY_GPA.get("medium", 37)
        else:
            return ECTS_LIMITS_BY_GPA.get("low", 31)

    def _find_failed_courses(self, grades: List["Grade"]) -> Set[str]:
        """Find courses that were failed and need retaking."""
        failed = set()
        for grade in grades:
            if not self._is_passing_grade(grade.letter_grade):
                failed.add(grade.course_code)
        return failed

    def _find_passed_courses(self, grades: List["Grade"]) -> Set[str]:
        """Find courses that were passed."""
        passed = set()
        for grade in grades:
            if self._is_passing_grade(grade.letter_grade):
                passed.add(grade.course_code)
        return passed

    def _add_failed_course_recommendations(
        self, report: AdvisorReport, failed_codes: Set[str]
    ) -> None:
        """Add recommendations for failed courses that must be retaken."""
        for code in failed_codes:
            if code in self._available_courses:
                name = self._course_names.get(code, "Unknown Course")
                ects = self._course_ects.get(code, 0)

                report.must_retake.append(CourseRecommendation(
                    course_code=code,
                    course_name=name,
                    reason="FF aldın, bu dersi tekrar almalısın",
                    priority="high",
                    category="failed_retry",
                    ects=ects,
                ))

    def _add_prerequisite_recommendations(
        self, report: AdvisorReport, passed_codes: Set[str], failed_codes: Set[str]
    ) -> None:
        """Add recommendations for courses whose prerequisites are now met."""
        for course_code, prerequisites in self._prerequisite_map.items():
            if course_code not in self._available_courses:
                continue
            if course_code in passed_codes or course_code in failed_codes:
                continue

            # Check if all prerequisites are passed
            prereqs_met = all(prereq in passed_codes for prereq in prerequisites)
            if prereqs_met and prerequisites:
                name = self._course_names.get(course_code, "Unknown Course")
                ects = self._course_ects.get(course_code, 0)
                prereq_str = ", ".join(prerequisites)

                report.recommended.append(CourseRecommendation(
                    course_code=course_code,
                    course_name=name,
                    reason=f"Ön koşulları tamamladın: {prereq_str}",
                    priority="medium",
                    category="prerequisite_met",
                    ects=ects,
                ))

    def _add_sequence_recommendations(
        self, report: AdvisorReport, passed_codes: Set[str], failed_codes: Set[str]
    ) -> None:
        """Add recommendations for sequential courses (e.g., MATH101 -> MATH102)."""
        # Pattern: Course codes often follow sequences like XXX101 -> XXX102
        sequence_patterns = [
            (1, 2), (101, 102), (1001, 1002), (1101, 1102),
            (2, 3), (102, 103), (1002, 1003), (1102, 1103),
        ]

        already_recommended = {r.course_code for r in report.recommended}

        for passed_code in passed_codes:
            # Try to find sequence patterns
            base_part = ""
            num_part = ""

            # Extract numeric suffix
            for i, char in enumerate(reversed(passed_code)):
                if not char.isdigit():
                    base_part = passed_code[:len(passed_code) - i]
                    num_part = passed_code[len(passed_code) - i:]
                    break

            if not num_part:
                continue

            try:
                current_num = int(num_part)
            except ValueError:
                continue

            # Check for next in sequence
            for seq_current, seq_next in sequence_patterns:
                if current_num == seq_current:
                    next_code = f"{base_part}{seq_next}"

                    if (
                        next_code in self._available_courses
                        and next_code not in passed_codes
                        and next_code not in failed_codes
                        and next_code not in already_recommended
                    ):
                        name = self._course_names.get(next_code, "Unknown Course")
                        ects = self._course_ects.get(next_code, 0)

                        report.recommended.append(CourseRecommendation(
                            course_code=next_code,
                            course_name=name,
                            reason=f"{passed_code} dersinin devamı",
                            priority="medium",
                            category="sequence_next",
                            ects=ects,
                        ))
                        already_recommended.add(next_code)
                    break


def create_quick_schedule_config(
    lifestyle_mode: str = "balanced",
    morning_person: bool = False,
    prefer_gaps: bool = False,
    free_day_preference: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create algorithm configuration based on lifestyle preferences.

    Args:
        lifestyle_mode: "minimal" (light load), "balanced", "intensive" (heavy load)
        morning_person: Prefer early classes if True
        prefer_gaps: Prefer gaps between classes if True
        free_day_preference: Preferred free day (e.g., "Friday")

    Returns:
        Configuration dictionary for the scheduler
    """
    from utils.schedule_metrics import SchedulerPrefs

    # Base preferences
    prefs = {
        "compress_classes": not prefer_gaps,
        "prefer_morning": morning_person,
        "desired_free_days": [free_day_preference] if free_day_preference else [],
        "strict_free_days": free_day_preference is not None,
    }

    # Algorithm selection based on mode
    if lifestyle_mode == "minimal":
        config = {
            "algorithm": "Greedy",
            "max_results": 5,
            "max_ects": 25,
            "params": {"timeout_seconds": 60},
        }
    elif lifestyle_mode == "intensive":
        config = {
            "algorithm": "Genetic",
            "max_results": 10,
            "max_ects": 40,
            "params": {
                "population_size": 30,
                "generations": 50,
                "timeout_seconds": 180,
            },
        }
    else:  # balanced
        config = {
            "algorithm": "DFS",
            "max_results": 10,
            "max_ects": 31,
            "params": {"timeout_seconds": 120},
        }

    config["scheduler_prefs"] = SchedulerPrefs(**prefs)
    return config


__all__ = [
    "SmartCourseAdvisor",
    "CourseRecommendation",
    "AdvisorReport",
    "create_quick_schedule_config",
]
