"""Iterative deepening depth-first search scheduler."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, List, Optional

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


@register_scheduler
class IDDFSScheduler(BaseScheduler):
    """Combines DFS depth precision with BFS completeness guarantees."""

    metadata = AlgorithmMetadata(
        name="IDDFS",
        category="complete-search",
        complexity="O(b^d)",
        description="Iterative deepening DFS scheduler",
        optimal=True,
    )

    def __init__(
        self,
        max_results: int = 10,
        max_ects: int = 31,
        allow_conflicts: bool = False,
        max_conflicts: int = 1,
        scheduler_prefs: Optional[SchedulerPrefs] = None,
        timeout_seconds: int = 240,
        depth_increment: int = 1,
    ) -> None:
        super().__init__(
            max_results=max_results,
            max_ects=max_ects,
            allow_conflicts=allow_conflicts,
            max_conflicts=max_conflicts,
            scheduler_prefs=scheduler_prefs,
            timeout_seconds=timeout_seconds,
        )
        self.depth_increment = max(1, depth_increment)

    def _run_algorithm(self, search: PreparedSearch) -> List[Schedule]:
        results: List[Schedule] = []
        max_depth = len(search.group_keys)
        depth_limit = self.depth_increment
        start = time.time()

        while depth_limit <= max_depth and len(results) < self.max_results:
            self._iddfs(
                search,
                depth_limit=depth_limit,
                group_index=0,
                current_courses=[],
                current_ects=0,
                results=results,
                start=start,
            )

            if self._last_run_stats.get("timeout_reached"):
                break

            depth_limit += self.depth_increment

        return results

    def _iddfs(
        self,
        search: PreparedSearch,
        *,
        depth_limit: int,
        group_index: int,
        current_courses: List[Course],
        current_ects: int,
        results: List[Schedule],
        start: float,
    ) -> None:
        if time.time() - start >= self.timeout_seconds:
            self._last_run_stats["timeout_reached"] = True
            return

        self._last_run_stats["nodes_explored"] += 1

        if group_index >= len(search.group_keys) or group_index >= depth_limit:
            if group_index >= len(search.group_keys) and current_courses:
                schedule = Schedule(current_courses.copy())
                if self._is_valid_final_schedule(schedule):
                    results.append(schedule)
            return

        group_key = search.group_keys[group_index]
        options = search.group_options.get(group_key, [])

        for option in options:
            if option is None:
                self._iddfs(
                    search,
                    depth_limit=depth_limit,
                    group_index=group_index + 1,
                    current_courses=current_courses,
                    current_ects=current_ects,
                    results=results,
                    start=start,
                )
                continue

            new_courses = current_courses + option
            new_ects = current_ects + sum(course.ects for course in option)

            if not self._is_valid_partial_selection(new_courses):
                self._last_run_stats["branches_pruned"] += 1
                continue

            self._iddfs(
                search,
                depth_limit=depth_limit,
                group_index=group_index + 1,
                current_courses=new_courses,
                current_ects=new_ects,
                results=results,
                start=start,
            )


__all__ = ["IDDFSScheduler"]
