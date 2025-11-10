"""Breadth-first search scheduler implementation."""

from __future__ import annotations

from collections import deque
import time
from typing import List, Optional

from core.models import Course, Schedule
from utils.schedule_metrics import SchedulerPrefs
from . import register_scheduler
from .base_scheduler import AlgorithmMetadata, BaseScheduler, PreparedSearch


@register_scheduler
class BFSScheduler(BaseScheduler):
    """Systematically explores schedules level-by-level."""

    metadata = AlgorithmMetadata(
        name="BFS",
        category="complete-search",
        complexity="O(b^d)",
        description="Breadth-first exploration of course combinations",
        optimal=True,
        supports_parallel=True,
    )

    def __init__(
        self,
        max_results: int = 10,
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
        queue = deque([(0, [], 0)])  # (group_index, courses, ects)
        results: List[Schedule] = []
        start = time.time()

        while queue and len(results) < self.max_results:
            if time.time() - start >= self.timeout_seconds:
                self._last_run_stats["timeout_reached"] = True
                break

            group_index, current_courses, current_ects = queue.popleft()
            self._last_run_stats["nodes_explored"] += 1

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
                    queue.append((group_index + 1, current_courses, current_ects))
                    continue

                new_courses = current_courses + option
                new_ects = current_ects + sum(course.ects for course in option)

                if not self._is_valid_partial_selection(new_courses):
                    self._last_run_stats["branches_pruned"] += 1
                    continue

                queue.append((group_index + 1, new_courses, new_ects))

        return results


__all__ = ["BFSScheduler"]
