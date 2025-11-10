"""Constraint programming inspired backtracking scheduler."""

from __future__ import annotations

import time
from typing import List, Optional

from core.models import Course, Schedule
from utils.schedule_metrics import SchedulerPrefs
from . import register_scheduler
from .base_scheduler import AlgorithmMetadata, BaseScheduler, PreparedSearch
from .heuristics import rank_options_by_score


@register_scheduler
class ConstraintProgrammingScheduler(BaseScheduler):
    """Applies MRV + forward checking to prune the search space aggressively."""

    metadata = AlgorithmMetadata(
        name="ConstraintProgramming",
        category="constraint-programming",
        complexity="O(b^d)",
        description="Backtracking with MRV and forward checking",
        optimal=True,
        supports_preferences=True,
        supports_parallel=False,
    )

    def __init__(
        self,
        max_results: int = 10,
        max_ects: int = 31,
        allow_conflicts: bool = False,
        scheduler_prefs: Optional[SchedulerPrefs] = None,
        timeout_seconds: int = 300,
    ) -> None:
        super().__init__(
            max_results=max_results,
            max_ects=max_ects,
            allow_conflicts=allow_conflicts,
            scheduler_prefs=scheduler_prefs,
            timeout_seconds=timeout_seconds,
        )

    def _run_algorithm(self, search: PreparedSearch) -> List[Schedule]:
        ordered_groups = sorted(
            search.group_keys,
            key=lambda key: len(search.group_options.get(key, [])) or 999,
        )
        results: List[Schedule] = []
        start = time.time()
        self._cp_backtrack(search, ordered_groups, 0, [], results, start)
        return results

    def _cp_backtrack(
        self,
        search: PreparedSearch,
        ordered_groups: List[str],
        index: int,
        current_courses: List[Course],
        results: List[Schedule],
        start: float,
    ) -> None:
        if len(results) >= self.max_results:
            return

        if time.time() - start >= self.timeout_seconds:
            self._last_run_stats["timeout_reached"] = True
            return

        self._last_run_stats["nodes_explored"] += 1

        if index >= len(ordered_groups):
            schedule = Schedule(current_courses.copy())
            if self._is_valid_final_schedule(schedule):
                results.append(schedule)
            return

        group_key = ordered_groups[index]
        options = search.group_options.get(group_key, [])
        ranked = rank_options_by_score(options, current_courses, self.scheduler_prefs)

        for option in ranked:
            if option is None:
                # forward checking: only allow skipping optional courses
                if group_key in search.mandatory_codes:
                    continue
                self._cp_backtrack(
                    search,
                    ordered_groups,
                    index + 1,
                    current_courses,
                    results,
                    start,
                )
                continue

            tentative = current_courses + option
            if not self._is_valid_partial_selection(tentative):
                self._last_run_stats["branches_pruned"] += 1
                continue

            # Forward checking: ensure future mandatory groups still have options
            if not self._forward_check(search, ordered_groups[index + 1 :], tentative):
                self._last_run_stats["branches_pruned"] += 1
                continue

            self._cp_backtrack(
                search,
                ordered_groups,
                index + 1,
                tentative,
                results,
                start,
            )

    def _forward_check(
        self,
        search: PreparedSearch,
        remaining_groups: List[str],
        tentative_courses: List[Course],
    ) -> bool:
        for group in remaining_groups:
            options = search.group_options.get(group, [])
            if not options:
                return False

            if group not in search.mandatory_codes:
                continue

            has_valid = False
            for option in options:
                if option is None:
                    continue
                if self._is_valid_partial_selection(tentative_courses + option):
                    has_valid = True
                    break
            if not has_valid:
                return False

        return True


__all__ = ["ConstraintProgrammingScheduler"]
