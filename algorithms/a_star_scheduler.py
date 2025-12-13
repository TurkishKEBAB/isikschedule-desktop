"""A* search scheduler leveraging heuristic guidance."""

from __future__ import annotations

import heapq
import itertools
import time
from typing import TYPE_CHECKING, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from core.models import Course, Schedule
    from utils.schedule_metrics import SchedulerPrefs

# Runtime imports
try:
    from core.models import Course, Schedule
except ImportError as e:
    raise ImportError(f"Required module core.models not found: {e}")

try:
    from utils.schedule_metrics import SchedulerPrefs
except ImportError as e:
    raise ImportError(f"Required module utils.schedule_metrics not found: {e}")

from . import register_scheduler
from .base_scheduler import AlgorithmMetadata, BaseScheduler, PreparedSearch
from .heuristics import estimate_conflict_penalty, estimate_remaining_group_penalty


@register_scheduler
class AStarScheduler(BaseScheduler):
    """Heuristic-informed search that favours promising partial schedules."""

    metadata = AlgorithmMetadata(
        name="A*",
        category="informed-search",
        complexity="O(b^d)",
        description="A* search with conflict-based heuristics",
        optimal=True,
        supports_preferences=True,
    )

    def __init__(
        self,
        max_results: int = 10,
        max_ects: int = 31,
        allow_conflicts: bool = False,
        max_conflicts: int = 1,
        scheduler_prefs: Optional[SchedulerPrefs] = None,
        timeout_seconds: int = 180,
    ) -> None:
        super().__init__(
            max_results=max_results,
            max_ects=max_ects,
            allow_conflicts=allow_conflicts,
            max_conflicts=max_conflicts,
            scheduler_prefs=scheduler_prefs,
            timeout_seconds=timeout_seconds,
        )

    def _run_algorithm(self, search: PreparedSearch) -> List[Schedule]:
        counter = itertools.count()
        open_set = []  # type: List[Tuple[float, int, int, List[Course], int]]
        heapq.heappush(open_set, (0.0, next(counter), 0, [], 0))

        results = []  # type: List[Schedule]
        visited: Set[Tuple[int, frozenset]] = set()
        start = time.time()

        while open_set and len(results) < self.max_results:
            if self._check_timeout(start):
                break

            _, _, group_index, current_courses, current_ects = heapq.heappop(open_set)
            self._last_run_stats["nodes_explored"] += 1

            signature = self._create_signature(group_index, current_courses)
            if signature in visited:
                continue
            visited.add(signature)

            if self._is_complete_schedule(group_index, search, current_courses, results):
                continue

            self._expand_node(
                search, group_index, current_courses, current_ects,
                open_set, counter
            )

        return results

    def _check_timeout(self, start: float) -> bool:
        """Check if algorithm has exceeded timeout."""
        if time.time() - start >= self.timeout_seconds:
            self._last_run_stats["timeout_reached"] = True
            return True
        return False

    @staticmethod
    def _create_signature(
        group_index: int, current_courses: List[Course]
    ) -> Tuple[int, frozenset]:
        """Create a unique signature for state deduplication using frozenset."""
        return (
            group_index,
            frozenset(course.code for course in current_courses),
        )

    def _is_complete_schedule(
        self,
        group_index: int,
        search: PreparedSearch,
        current_courses: List[Course],
        results: List[Schedule]
    ) -> bool:
        """Check if we've processed all groups and add valid schedule to results."""
        if group_index >= len(search.group_keys):
            if current_courses:
                schedule = Schedule(current_courses.copy())
                if self._is_valid_final_schedule(schedule):
                    results.append(schedule)
            return True
        return False

    def _expand_node(
        self,
        search: PreparedSearch,
        group_index: int,
        current_courses: List[Course],
        current_ects: int,
        open_set: List[Tuple[float, int, int, List[Course], int]],
        counter: itertools.count
    ) -> None:
        """Expand current node by trying all options for the current group."""
        group_key = search.group_keys[group_index]
        options = search.group_options.get(group_key, [])

        remaining = len(search.group_keys) - (group_index + 1)
        heuristic_penalty = estimate_remaining_group_penalty(remaining)

        for option in options:
            new_courses, new_ects = self._apply_option(
                option, current_courses, current_ects
            )

            if not self._is_valid_partial_selection(new_courses):
                self._last_run_stats["branches_pruned"] += 1
                continue

            self._add_to_open_set(
                open_set, counter, new_courses, new_ects,
                group_index, heuristic_penalty
            )

    @staticmethod
    def _apply_option(
        option: Optional[List[Course]],
        current_courses: List[Course],
        current_ects: int
    ) -> Tuple[List[Course], int]:
        """Apply an option (skip or add courses) to current state."""
        if option is None:
            return current_courses.copy(), current_ects

        new_courses = current_courses + option
        new_ects = current_ects + sum(course.ects for course in option)
        return new_courses, new_ects

    @staticmethod
    def _add_to_open_set(
        open_set: List[Tuple[float, int, int, List[Course], int]],
        counter: itertools.count,
        new_courses: List[Course],
        new_ects: int,
        group_index: int,
        heuristic_penalty: float
    ) -> None:
        """Calculate priority and add new state to open set."""
        schedule = Schedule(new_courses)
        cost = estimate_conflict_penalty(schedule)
        total_priority = cost + heuristic_penalty

        heapq.heappush(
            open_set,
            (total_priority, next(counter), group_index + 1, new_courses, new_ects),
        )



__all__ = ["AStarScheduler"]
