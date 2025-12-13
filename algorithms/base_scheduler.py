"""Common scheduling algorithm infrastructure.

This module provides reusable primitives for all scheduling algorithms in
SchedularV3:

- ``AlgorithmMetadata``: rich metadata about an algorithm implementation.
- ``track_performance``: decorator that records execution duration.
- ``BaseScheduler``: abstract base class supplying utility helpers such as
  constraint preparation, result management, and preference-aware sorting.

The goal is to give every algorithm a consistent surface area so they can be
benchmarked, auto-selected, and executed interchangeably.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import functools
import time
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Optional, Sequence, Set

if TYPE_CHECKING:
    from core.models import Course, CourseGroup, Schedule, Transcript
    from utils.schedule_metrics import SchedulerPrefs

# Runtime imports
try:
    from core.models import Course, CourseGroup, Schedule, Transcript
except ImportError as e:
    raise ImportError(f"Required module core.models not found: {e}")

try:
    from utils.schedule_metrics import SchedulerPrefs, score_schedule
except ImportError as e:
    raise ImportError(f"Required module utils.schedule_metrics not found: {e}")

from .constraints import ConstraintUtils

# Işık University smart filtering (optional)
ISIK_FILTERING_AVAILABLE = False
can_take_course = None
get_prerequisites = None
ECTS_LIMITS_BY_GPA: Dict[str, int] = {}
try:
    from core.prerequisite_data import can_take_course, get_prerequisites
    from core.isik_university_data import ECTS_LIMITS_BY_GPA
    ISIK_FILTERING_AVAILABLE = True
except ImportError:
    pass  # Işık University features will be disabled


@dataclass(frozen=True)
class AlgorithmMetadata:
    """Descriptive metadata for a scheduler or optimizer implementation."""

    name: str
    category: str
    complexity: str
    description: str
    optimal: bool = False
    supports_preferences: bool = True
    supports_constraints: bool = True
    supports_parallel: bool = False
    is_optimizer: bool = False


def track_performance(method: Callable) -> Callable:
    """Decorator that records execution duration on the scheduler instance."""

    @functools.wraps(method)
    def wrapper(self: "BaseScheduler", *args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = method(self, *args, **kwargs)
        duration = time.perf_counter() - start
        self._performance_history.append(
            {
                "method": method.__name__,
                "duration": duration,
                "timestamp": time.time(),
            }
        )
        self._last_run_stats.setdefault("call_durations", []).append(duration)
        return result

    return wrapper


@dataclass
class PreparedSearch:
    """Container for pre-processed search data used by schedulers."""

    group_keys: List[str]
    mandatory_keys: List[str]
    optional_keys: List[str]
    group_options: Dict[str, List[Optional[List[Course]]]]
    valid_selections: Dict[str, List[List[Course]]]
    mandatory_codes: Set[str]
    optional_codes: Set[str]


class BaseScheduler(ABC):
    """Abstract base class for all scheduling algorithms."""

    metadata: AlgorithmMetadata = AlgorithmMetadata(
        name="base",
        category="infrastructure",
        complexity="O(1)",
        description="Base scheduler – should be subclassed",
        optimal=False,
    )

    def __init__(
        self,
        *,
        max_results: int = 10,
        max_ects: int = 31,
        allow_conflicts: bool = False,
        max_conflicts: int = 1,
        scheduler_prefs: Optional[SchedulerPrefs] = None,
        timeout_seconds: int = 120,
        transcript: Optional[Transcript] = None,
        enable_smart_filtering: bool = True,
    ) -> None:
        self.max_results = max_results
        self.max_ects = max_ects
        self.allow_conflicts = allow_conflicts
        self.max_conflicts = max_conflicts
        self.transcript = transcript
        self.enable_smart_filtering = enable_smart_filtering and ISIK_FILTERING_AVAILABLE
        self.scheduler_prefs = scheduler_prefs or SchedulerPrefs()
        self.timeout_seconds = timeout_seconds

        self._performance_history = []  # type: List[Dict[str, Any]]
        self._last_run_stats = {}  # type: Dict[str, Any]
        self._results = []  # type: List[Schedule]
        self._active_mandatory_codes = set()  # type: Set[str]

    # ------------------------------------------------------------------
    # Abstract behaviour
    # ------------------------------------------------------------------
    @abstractmethod
    def _run_algorithm(self, search: PreparedSearch) -> List[Schedule]:
        """Execute the concrete scheduling strategy.

        Subclasses receive the pre-computed search container and must return a
        list of ``Schedule`` instances that respect the configured limits.
        """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @track_performance
    def generate_schedules(
        self,
        course_groups: Dict[str, CourseGroup],
        mandatory_codes: Set[str],
        optional_codes: Optional[Set[str]] = None,
    ) -> List[Schedule]:
        """Shared entry point used by every scheduler implementation."""

        self._results.clear()
        self._last_run_stats = {
            "nodes_explored": 0,
            "branches_pruned": 0,
            "generated": 0,
        }

        if not course_groups or not mandatory_codes:
            self._last_run_stats["status"] = "invalid-input"
            return []

        search = self._prepare_search_space(course_groups, mandatory_codes, optional_codes)
        if search is None:
            self._last_run_stats["status"] = "no-valid-selections"
            return []

        raw_results = self._run_algorithm(search)
        self._results = self._finalize_results(raw_results)
        self._last_run_stats["generated"] = len(self._results)
        self._last_run_stats["status"] = "ok"
        return self._results

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _prepare_search_space(
        self,
        course_groups: Dict[str, CourseGroup],
        mandatory_codes: Set[str],
        optional_codes: Optional[Set[str]] = None,
    ) -> Optional[PreparedSearch]:
        """Build constraint-aware search structures shared across algorithms."""

        valid_selections, group_options = ConstraintUtils.build_group_options(
            course_groups, mandatory_codes
        )

        invalid_mandatory = [code for code in mandatory_codes if not valid_selections.get(code)]
        if invalid_mandatory:
            self._last_run_stats["invalid_mandatory"] = invalid_mandatory
            return None

        all_keys = list(course_groups.keys())

        # If optional_codes is None, treat it as empty (no optional courses)
        if optional_codes is None:
            optional_codes = set()

        # Filter out excluded courses (courses that are neither mandatory nor optional)
        included_codes = mandatory_codes | optional_codes
        filtered_keys = [key for key in all_keys if key in included_codes]

        mandatory_keys = [key for key in filtered_keys if key in mandatory_codes]
        optional_keys = [key for key in filtered_keys if key in optional_codes]

        mandatory_keys.sort(key=lambda k: len(group_options.get(k, [])))
        optional_keys.sort(key=lambda k: len(group_options.get(k, [])))

        self._active_mandatory_codes = set(mandatory_codes)

        return PreparedSearch(
            group_keys=mandatory_keys + optional_keys,
            mandatory_keys=mandatory_keys,
            optional_keys=optional_keys,
            group_options=group_options,
            valid_selections=valid_selections,
            mandatory_codes=set(mandatory_codes),
            optional_codes=set(optional_codes),
        )

    def _finalize_results(self, results: Iterable[Schedule]) -> List[Schedule]:
        """Sort schedules based on preferences and apply result limits."""

        filtered = []  # type: List[Schedule]
        for schedule in results:
            if not self._is_valid_final_schedule(schedule):
                continue

            if len(filtered) < self.max_results:
                filtered.append(schedule)
            else:
                # Replace worst schedule if this one is better
                worst = self._select_worst_schedule(filtered)
                if self._is_schedule_better(schedule, worst):
                    filtered.remove(worst)
                    filtered.append(schedule)

        self._sort_schedules(filtered)
        return filtered

    def filter_courses_by_prerequisites(
        self, courses: List[Course]
    ) -> List[Course]:
        """
        Filter courses based on prerequisites (Işık University smart filtering).

        Args:
            courses: List of courses to filter

        Returns:
            Filtered list of courses that prerequisites are met
        """
        if not self.enable_smart_filtering or not self.transcript or not ISIK_FILTERING_AVAILABLE:
            return courses

        # Get completed courses from transcript
        completed = {grade.course_code for grade in self.transcript.grades}

        # Filter courses
        available = []
        for course in courses:
            if can_take_course(course.main_code, list(completed)) if can_take_course else True:
                available.append(course)

        return available

    def adjust_max_ects_by_gpa(self) -> int:
        """
        Adjust max ECTS based on GPA (Işık University rules).

        Returns:
            Adjusted max ECTS value
        """
        if not self.enable_smart_filtering or not self.transcript or not ISIK_FILTERING_AVAILABLE:
            return self.max_ects

        # Calculate current GPA
        try:
            from core.academic import GPACalculator
            calculator = GPACalculator()
            current_gpa = calculator.calculate_gpa(self.transcript.grades)
        except ImportError:
            return self.max_ects

        # Apply Işık University rules
        if current_gpa >= 3.50:
            return min(ECTS_LIMITS_BY_GPA.get("high", self.max_ects), self.max_ects)  # 43
        elif current_gpa >= 2.50:
            return min(ECTS_LIMITS_BY_GPA.get("medium", self.max_ects), self.max_ects)  # 37
        else:
            return min(ECTS_LIMITS_BY_GPA.get("low", self.max_ects), self.max_ects)  # 31

    def _sort_schedules(self, schedules: List[Schedule]) -> None:
        if not schedules:
            return

        if self.scheduler_prefs:
            schedules.sort(key=lambda s: score_schedule(s, self.scheduler_prefs), reverse=True)
        else:
            schedules.sort(key=lambda s: (s.conflict_count, -s.total_credits))

    def _select_worst_schedule(self, schedules: Sequence[Schedule]) -> Schedule:
        """Select the worst schedule from the given list based on quality metrics."""
        if self.scheduler_prefs:
            return min(schedules, key=lambda s: score_schedule(s, self.scheduler_prefs))
        return max(schedules, key=lambda s: (s.conflict_count, -s.total_credits))

    def _is_schedule_better(self, candidate: Schedule, incumbent: Schedule) -> bool:
        if self.scheduler_prefs:
            return score_schedule(candidate, self.scheduler_prefs) > score_schedule(
                incumbent, self.scheduler_prefs
            )
        return (
            candidate.conflict_count < incumbent.conflict_count
            or (
                candidate.conflict_count == incumbent.conflict_count
                and candidate.total_credits > incumbent.total_credits
            )
        )

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    def _is_valid_partial_selection(self, courses: List[Course]) -> bool:
        total_ects = sum(course.ects for course in courses)
        if total_ects > self.max_ects:
            return False

        schedule = Schedule(courses)
        if self.allow_conflicts:
            return schedule.conflict_count <= self.max_conflicts

        return schedule.conflict_count == 0

    def _is_valid_final_schedule(self, schedule: Schedule) -> bool:
        """
        Validate that a schedule meets all hard constraints.

        Args:
            schedule: Schedule to validate

        Returns:
            True if schedule is valid, False otherwise
        """
        if schedule.total_credits > self.max_ects:
            return False

        if not self.allow_conflicts:
            if schedule.conflict_count > 0:
                return False
        elif schedule.conflict_count > self.max_conflicts:
            return False

        if self._active_mandatory_codes:
            included_main_codes = {course.main_code for course in schedule.courses}
            if not self._active_mandatory_codes.issubset(included_main_codes):
                return False

        # Respect strict free day constraints if configured
        if (
            self.scheduler_prefs
            and self.scheduler_prefs.strict_free_days
            and self.scheduler_prefs.desired_free_days
        ):
            try:
                from utils.schedule_metrics import meets_free_day_constraint as check_free_days

                if not check_free_days(
                    schedule, self.scheduler_prefs.desired_free_days, strict=True
                ):
                    return False
            except ImportError:
                pass  # Skip free day constraint if not available

        return True

    # ------------------------------------------------------------------
    # Statistics & diagnostics
    # ------------------------------------------------------------------
    @property
    def last_run_stats(self) -> Dict[str, Any]:
        return dict(self._last_run_stats)

    @property
    def performance_history(self) -> List[Dict[str, Any]]:
        return list(self._performance_history)

    @property
    def results(self) -> List[Schedule]:
        return list(self._results)

    def get_search_statistics(self) -> Dict[str, Any]:
        return self.last_run_stats

    def get_optimization_report(self) -> Dict[str, Any]:
        total = len(self._results)
        credit_values = [schedule.total_credits for schedule in self._results]
        conflicts = [schedule.conflict_count for schedule in self._results]
        preference_scores = []  # type: List[float]
        if self.scheduler_prefs:
            preference_scores = [score_schedule(schedule, self.scheduler_prefs) for schedule in self._results]

        def _summary(values: List[float]) -> Dict[str, float]:
            if not values:
                return {"min": 0.0, "max": 0.0, "average": 0.0}
            return {
                "min": float(min(values)),
                "max": float(max(values)),
                "average": float(sum(values) / len(values)),
            }

        return {
            "total_schedules": total,
            "credit_analysis": _summary([float(value) for value in credit_values]),
            "conflict_analysis": _summary([float(value) for value in conflicts]),
            "preference_scores": preference_scores,
        }

    def analyze_failure(self, course_groups: Optional[Dict[str, CourseGroup]] = None) -> List[str]:
        """
        Provide generic failure diagnostics for subclasses to extend.

        Args:
            course_groups: Optional course groups dictionary (for future use)

        Returns:
            List of diagnostic messages about why schedule generation failed
        """
        # Note: course_groups parameter is kept for API compatibility but not currently used
        issues = []  # type: List[str]
        invalid = self._last_run_stats.get("invalid_mandatory", [])
        if invalid:
            issues.append(
                "Mandatory course(s) missing valid combinations: " + ", ".join(sorted(invalid))
            )

        if not issues:
            issues.append("No schedules generated – check constraints or increase limits")
        return issues


__all__ = [
    "AlgorithmMetadata",
    "BaseScheduler",
    "PreparedSearch",
    "track_performance",
]
