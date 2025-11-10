"""A* search scheduler leveraging heuristic guidance."""

from __future__ import annotations

import heapq
import itertools
import time
from typing import List, Optional, Set, Tuple

from core.models import Course, Schedule
from utils.schedule_metrics import SchedulerPrefs
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
        open_set: List[Tuple[float, int, int, List[Course], int]] = []
        heapq.heappush(open_set, (0.0, next(counter), 0, [], 0))

        results: List[Schedule] = []
        visited: Set[Tuple[int, Tuple[str, ...]]] = set()
        start = time.time()

        while open_set and len(results) < self.max_results:
            if time.time() - start >= self.timeout_seconds:
                self._last_run_stats["timeout_reached"] = True
                break

            priority, _, group_index, current_courses, current_ects = heapq.heappop(open_set)
            self._last_run_stats["nodes_explored"] += 1

            signature = (
                group_index,
                tuple(sorted(course.code for course in current_courses)),
            )
            if signature in visited:
                continue
            visited.add(signature)

            if group_index >= len(search.group_keys):
                if current_courses:
                    schedule = Schedule(current_courses.copy())
                    if self._is_valid_final_schedule(schedule):
                        results.append(schedule)
                continue

            group_key = search.group_keys[group_index]
            options = search.group_options.get(group_key, [])

            remaining = len(search.group_keys) - (group_index + 1)
            heuristic_penalty = estimate_remaining_group_penalty(remaining)

            for option in options:
                if option is None:
                    new_courses = current_courses.copy()
                    new_ects = current_ects
                else:
                    new_courses = current_courses + option
                    new_ects = current_ects + sum(course.ects for course in option)

                if not self._is_valid_partial_selection(new_courses):
                    self._last_run_stats["branches_pruned"] += 1
                    continue

                schedule = Schedule(new_courses)
                cost = estimate_conflict_penalty(schedule)
                total_priority = cost + heuristic_penalty

                heapq.heappush(
                    open_set,
                    (total_priority, next(counter), group_index + 1, new_courses, new_ects),
                )

        return results


__all__ = ["AStarScheduler"]
