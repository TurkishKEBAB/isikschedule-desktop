"""Dijkstra-based scheduler treating each partial selection as a graph node."""

from __future__ import annotations

import heapq
import time
from typing import Dict, List, Optional, Tuple

from core.models import Course, Schedule
from utils.schedule_metrics import SchedulerPrefs
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
        scheduler_prefs: Optional[SchedulerPrefs] = None,
        timeout_seconds: int = 180,
    ) -> None:
        super().__init__(
            max_results=max_results,
            max_ects=max_ects,
            allow_conflicts=allow_conflicts,
            scheduler_prefs=scheduler_prefs,
            timeout_seconds=timeout_seconds,
        )

    def _run_algorithm(self, search: PreparedSearch) -> List[Schedule]:
        queue: List[Tuple[float, int, int, List[Course], int]] = []
        heapq.heappush(queue, (0.0, 0, 0, [], 0))

        results: List[Schedule] = []
        distances: Dict[Tuple[int, Tuple[str, ...]], float] = {}
        start = time.time()

        while queue and len(results) < self.max_results:
            if time.time() - start >= self.timeout_seconds:
                self._last_run_stats["timeout_reached"] = True
                break

            cost, _, group_index, current_courses, current_ects = heapq.heappop(queue)
            self._last_run_stats["nodes_explored"] += 1

            signature = (
                group_index,
                tuple(sorted(course.code for course in current_courses)),
            )

            if signature in distances and distances[signature] <= cost:
                continue
            distances[signature] = cost

            if group_index >= len(search.group_keys):
                if current_courses:
                    schedule = Schedule(current_courses.copy())
                    if self._is_valid_final_schedule(schedule):
                        results.append(schedule)
                continue

            group_key = search.group_keys[group_index]
            options = search.group_options.get(group_key, [])

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
                new_cost = cost + estimate_conflict_penalty(schedule)

                heapq.heappush(queue, (new_cost, group_index + 1, group_index + 1, new_courses, new_ects))

        return results


__all__ = ["DijkstraScheduler"]
