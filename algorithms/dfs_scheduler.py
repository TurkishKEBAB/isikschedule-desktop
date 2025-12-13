"""
Depth-First Search scheduler implementation.

This module provides a comprehensive DFS-based scheduling algorithm that systematically
explores all possible course combinations to find valid schedules while respecting
constraints and user preferences.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set
import logging
import time
from collections import defaultdict

if TYPE_CHECKING:
    from core.models import Course, Schedule, CourseGroup
    from utils.schedule_metrics import SchedulerPrefs

# Runtime imports
try:
    from core.models import Course, Schedule, CourseGroup
except ImportError as e:
    raise ImportError(f"Required module core.models not found: {e}")

try:
    from utils.schedule_metrics import SchedulerPrefs, score_schedule
except ImportError as e:
    raise ImportError(f"Required module utils.schedule_metrics not found: {e}")

from .base_scheduler import AlgorithmMetadata, BaseScheduler, PreparedSearch
from . import register_scheduler

# Set up logging
logger = logging.getLogger(__name__)


@register_scheduler
class DFSScheduler(BaseScheduler):
    """
    Advanced Depth-First Search scheduler for generating course schedules.

    This scheduler uses a systematic DFS approach to explore all possible
    combinations of course selections while respecting constraints and
    optimizing for user preferences.

    Features:
    - Constraint-aware scheduling
    - User preference optimization
    - Early pruning for efficiency
    - Conflict detection and handling
    - Progress tracking and statistics
    """

    metadata = AlgorithmMetadata(
        name="DFS",
        category="complete-search",
        complexity="O(b^d)",
        description="Depth-first search with pruning and preference scoring",
        optimal=False,
        supports_preferences=True,
        supports_constraints=True,
    )

    def __init__(
        self,
        max_results: int = 10,
        max_ects: int = 31,
        allow_conflicts: bool = False,
        max_conflicts: int = 1,
        scheduler_prefs: Optional[SchedulerPrefs] = None,
        timeout_seconds: int = 300,
    ):
        """
        Initialize the DFS scheduler.

        Args:
            max_results: Maximum number of schedules to generate
            max_ects: Maximum ECTS credits allowed
            allow_conflicts: Whether to allow schedule conflicts
            max_conflicts: Maximum number of conflicts allowed
            scheduler_prefs: Advanced scheduler preferences for optimization
            timeout_seconds: Maximum time to spend searching (in seconds)
        """
        super().__init__(
            max_results=max_results,
            max_ects=max_ects,
            allow_conflicts=allow_conflicts,
            max_conflicts=max_conflicts,
            scheduler_prefs=scheduler_prefs,
            timeout_seconds=timeout_seconds,
        )

        self._start_time = 0.0
        self._nodes_explored = 0
        self._pruned_branches = 0
        self._best_score = float("-inf")
        self._active_mandatory_codes: Set[str] = set()

    # ------------------------------------------------------------------
    # BaseScheduler contract
    # ------------------------------------------------------------------
    def _run_algorithm(self, search: PreparedSearch) -> List[Schedule]:
        self._start_time = time.time()
        self._nodes_explored = 0
        self._pruned_branches = 0
        self._best_score = float("-inf")
        self._active_mandatory_codes = set(search.mandatory_codes)

        results: List[Schedule] = []

        self._dfs_search(
            search,
            current_courses=[],
            current_ects=0,
            group_index=0,
            results=results,
        )

        elapsed_time = time.time() - self._start_time
        self._last_run_stats.update(
            {
                "total_time": elapsed_time,
                "nodes_explored": self._nodes_explored,
                "pruned_branches": self._pruned_branches,
                "best_score": self._best_score if results else 0,
                "timeout_reached": elapsed_time >= self.timeout_seconds,
            }
        )

        return results

    # ------------------------------------------------------------------
    # DFS implementation
    # ------------------------------------------------------------------
    def _dfs_search(
        self,
        search: PreparedSearch,
        current_courses: List[Course],
        current_ects: int,
        group_index: int,
        results: List[Schedule],
    ) -> None:
        self._nodes_explored += 1

        if time.time() - self._start_time >= self.timeout_seconds:
            logger.warning("DFS search timeout reached")
            return

        if group_index >= len(search.group_keys):
            self._handle_dfs_base_case(current_courses, results)
            return

        if len(results) >= self.max_results:
            return

        group_key = search.group_keys[group_index]
        options = search.group_options.get(group_key, [])

        for option in options:
            self._process_dfs_option(
                search, current_courses, current_ects, group_index, results, group_key, option
            )

    def _handle_dfs_base_case(self, current_courses: List[Course], results: List[Schedule]) -> None:
        """Handle the base case when all groups have been processed."""
        if not current_courses:
            return

        schedule = Schedule(current_courses.copy())
        if self._is_valid_final_schedule(schedule):
            if self.scheduler_prefs:
                score = score_schedule(schedule, self.scheduler_prefs)
                self._best_score = max(self._best_score, score)
            results.append(schedule)

    def _process_dfs_option(
        self,
        search: PreparedSearch,
        current_courses: List[Course],
        current_ects: int,
        group_index: int,
        results: List[Schedule],
        group_key: str,
        option: Optional[List[Course]],
    ) -> None:
        """Process a single option for the current group."""
        if self._should_prune_branch(option, current_courses, current_ects, group_key):
            self._pruned_branches += 1
            return

        if option is None:
            self._dfs_search(
                search,
                current_courses=current_courses,
                current_ects=current_ects,
                group_index=group_index + 1,
                results=results,
            )
        else:
            new_courses = current_courses + option
            new_ects = current_ects + sum(course.ects for course in option)
            self._dfs_search(
                search,
                current_courses=new_courses,
                current_ects=new_ects,
                group_index=group_index + 1,
                results=results,
            )

    def _should_prune_branch(
        self,
        option: Optional[List[Course]],
        current_courses: List[Course],
        current_ects: int,
        group_key: str,
    ) -> bool:
        """
        Determine if a branch should be pruned for efficiency.

        Args:
            option: Current option being considered
            current_courses: Current course selection
            current_ects: Current ECTS total
            group_key: Current group key

        Returns:
            True if branch should be pruned
        """
        if option is None:
            return group_key in self._active_mandatory_codes

        new_ects = current_ects + sum(course.ects for course in option)

        # Prune if ECTS limit exceeded
        if new_ects > self.max_ects:
            return True

        # Check conflicts based on allow_conflicts setting
        temp_schedule = Schedule(current_courses + option)

        if not self.allow_conflicts:
            return temp_schedule.conflict_count > 0

        if self.scheduler_prefs and self.scheduler_prefs.max_conflict_hours > 0:
            if temp_schedule.conflict_count > self.scheduler_prefs.max_conflict_hours:
                return True

        # Advanced pruning based on preferences
        if self.scheduler_prefs:
            return self._check_preference_constraints(temp_schedule)

        return False

    def _check_preference_constraints(self, temp_schedule: Schedule) -> bool:
        """Check if schedule violates preference constraints."""
        if not self.scheduler_prefs:
            return False

        # Prune if hard constraints violated
        if self.scheduler_prefs.max_weekly_slots < 60:  # 60 is effectively no limit
            weekly_slots = len({(day, slot) for course in temp_schedule.courses for day, slot in course.schedule})
            if weekly_slots > self.scheduler_prefs.max_weekly_slots:
                return True

        if self.scheduler_prefs.max_daily_slots:
            # Check daily slot limits
            daily_slots = defaultdict(set)
            for course in temp_schedule.courses:
                for day, slot in course.schedule:
                    daily_slots[day].add(slot)

            if any(len(slots) > self.scheduler_prefs.max_daily_slots for slots in daily_slots.values()):
                return True

        return False

    # ------------------------------------------------------------------
    # Reporting helpers
    # ------------------------------------------------------------------
    def get_search_statistics(self) -> Dict[str, float]:
        """Maintain backwards-compatible statistics accessor."""

        return {
            "total_time": self._last_run_stats.get("total_time", 0.0),
            "nodes_explored": self._last_run_stats.get("nodes_explored", 0),
            "pruned_branches": self._last_run_stats.get("pruned_branches", 0),
            "schedules_found": self._last_run_stats.get("generated", 0),
            "best_score": self._last_run_stats.get("best_score", 0.0),
            "timeout_reached": self._last_run_stats.get("timeout_reached", False),
        }

    def get_optimization_report(self) -> Dict[str, Any]:
        """
        Generate a detailed optimization report.

        Returns:
            Dictionary with optimization analysis
        """
        if not self._results:
            return {"status": "No schedules generated"}

        # Analyze results
        total_credits = [s.total_credits for s in self._results]
        conflict_counts = [s.conflict_count for s in self._results]

        report = {
            "total_schedules": len(self._results),
            "search_statistics": self.get_search_statistics(),
            "credit_analysis": {
                "min_credits": min(total_credits),
                "max_credits": max(total_credits),
                "avg_credits": sum(total_credits) / len(total_credits),
                "target_credits": self.max_ects
            },
            "conflict_analysis": {
                "conflict_free_schedules": sum(1 for count in conflict_counts if count == 0),
                "min_conflicts": min(conflict_counts),
                "max_conflicts": max(conflict_counts),
                "avg_conflicts": sum(conflict_counts) / len(conflict_counts)
            }
        }

        # Add preference-based analysis if available
        if self.scheduler_prefs:
            scores = [score_schedule(s, self.scheduler_prefs) for s in self._results]
            report["score_analysis"] = {
                "best_score": max(scores),
                "worst_score": min(scores),
                "avg_score": sum(scores) / len(scores),
                "score_range": max(scores) - min(scores)
            }

        return report

    def analyze_schedule_failure(
        self,
        course_groups: Dict[str, CourseGroup],
        mandatory_codes: Set[str],
    ) -> List[str]:
        """
        Analyze why schedule generation might have failed.

        Args:
            course_groups: Dictionary of course groups
            mandatory_codes: Set of mandatory course codes

        Returns:
            List of potential failure reasons
        """
        reasons = []

        # Check for invalid mandatory courses
        for code in mandatory_codes:
            if code not in course_groups:
                reasons.append(f"Mandatory course '{code}' not found in available courses")
                continue

            group = course_groups[code]
            if not group.lecture_courses:
                reasons.append(f"Mandatory course '{code}' has no lecture sections")

        # Check total minimum ECTS
        min_total_ects = sum(
            min(course.ects for course in course_groups[code].lecture_courses)
            for code in mandatory_codes
            if code in course_groups and course_groups[code].lecture_courses
        )

        if min_total_ects > self.max_ects:
            reasons.append(f"Minimum required ECTS ({min_total_ects}) exceeds limit ({self.max_ects})")

        # Check for constraint conflicts
        if self.scheduler_prefs:
            if self.scheduler_prefs.max_weekly_slots < len(mandatory_codes) * 2:
                reasons.append("Weekly hour limit too restrictive for mandatory courses")

        # Check timeout issues
        if self._last_run_stats.get("timeout_reached"):
            reasons.append("Search timeout reached - try increasing time limit or reducing course options")

        if not reasons:
            reasons.append("Unknown scheduling failure - check course data and constraints")

        return reasons
