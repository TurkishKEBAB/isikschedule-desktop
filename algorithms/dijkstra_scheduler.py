"""Dijkstra-based scheduler treating each partial selection as a graph node."""

from __future__ import annotations

import heapq
import itertools
import time
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple

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
from .heuristics import estimate_conflict_penalty


@register_scheduler
class DijkstraScheduler(BaseScheduler):
    """Weighted shortest-path search to minimise conflicts and dispersion."""

    metadata = AlgorithmMetadata(
        name="Dijkstra",
        category="informed-search",
        complexity="O(E log V)",
        description="Dijkstra search minimising conflict penalties",
        optimal=True,
        supports_preferences=True,
    )

    def __init__(
        self,
        max_results: int = 5,
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
        queue: List[Tuple[float, int, int, List[Course], int]] = []
        heapq.heappush(queue, (0.0, next(counter), 0, [], 0))

        results: List[Schedule] = []
        distances: Dict[Tuple[int, Tuple[str, ...]], float] = {}
        start = time.time()

        while queue and len(results) < self.max_results:
            if time.time() - start >= self.timeout_seconds:
                self._last_run_stats["timeout_reached"] = True
                break

            cost, _, group_index, current_courses, current_ects = heapq.heappop(queue)
            self._last_run_stats["nodes_explored"] += 1

            signature = self._compute_signature(group_index, current_courses)

            if self._should_skip_node(signature, distances, cost):
                continue

            distances[signature] = cost

            if group_index >= len(search.group_keys):
                self._try_add_result(current_courses, results)
                continue

            self._expand_node(
                queue, counter, group_index, current_courses, current_ects, search, results
            )

        return results

    def _compute_signature(self, group_index: int, current_courses: List[Course]) -> Tuple[int, Tuple[str, ...]]:
        """Compute node signature for visited tracking."""
        return (group_index, tuple(sorted(course.code for course in current_courses)))

    def _should_skip_node(
        self,
        signature: Tuple[int, Tuple[str, ...]],
        distances: Dict[Tuple[int, Tuple[str, ...]], float],
        cost: float,
    ) -> bool:
        """Check if node should be skipped (already visited with better cost)."""
        return signature in distances and distances[signature] <= cost

    def _try_add_result(self, current_courses: List[Course], results: List[Schedule]) -> None:
        """Try to add current course selection to results."""
        if current_courses:
            schedule = Schedule(current_courses.copy())
            if self._is_valid_final_schedule(schedule):
                results.append(schedule)

    def _expand_node(
        self,
        queue: List[Tuple[float, int, int, List[Course], int]],
        counter: itertools.count,
        group_index: int,
        current_courses: List[Course],
        current_ects: int,
        search: PreparedSearch,
        results: List[Schedule],
    ) -> None:
        """Expand a node by adding its children to the queue."""
        group_key = search.group_keys[group_index]
        options = search.group_options.get(group_key, [])

        for option in options:
            new_courses, new_ects = self._compute_option_values(
                current_courses, current_ects, option
            )

            if not self._is_valid_partial_selection(new_courses):
                self._last_run_stats["branches_pruned"] += 1
                continue

            schedule = Schedule(new_courses)
            new_cost = self._compute_cost(schedule)

            heapq.heappush(
                queue,
                (new_cost, next(counter), group_index + 1, new_courses, new_ects),
            )

    def _compute_option_values(
        self, current_courses: List[Course], current_ects: int, option: Optional[List[Course]]
    ) -> Tuple[List[Course], int]:
        """Compute new courses and ECTS for an option."""
        if option is None:
            return current_courses.copy(), current_ects
        return current_courses + option, current_ects + sum(course.ects for course in option)

    def _compute_cost(self, schedule: Schedule) -> float:
        """Compute cost of a schedule."""
        return estimate_conflict_penalty(schedule)


__all__ = ["DijkstraScheduler"]
