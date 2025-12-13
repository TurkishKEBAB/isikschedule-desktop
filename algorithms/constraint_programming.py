"""Constraint programming inspired backtracking scheduler."""

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
        ordered_groups = self._order_groups(search)
        results: List[Schedule] = []
        start = time.time()
        self._cp_backtrack(search, ordered_groups, 0, [], results, start)
        return results

    def _order_groups(self, search: PreparedSearch) -> List[str]:
        """Order groups by number of options (MRV heuristic)."""
        return sorted(
            search.group_keys,
            key=lambda key: len(search.group_options.get(key, [])) or 999,
        )

    def _cp_backtrack(
        self,
        search: PreparedSearch,
        ordered_groups: List[str],
        index: int,
        current_courses: List[Course],
        results: List[Schedule],
        start: float,
    ) -> None:
        if self._should_terminate_search(results, start):
            return

        self._last_run_stats["nodes_explored"] += 1

        if index >= len(ordered_groups):
            self._finalize_schedule(current_courses, results)
            return

        self._process_group(search, ordered_groups, index, current_courses, results, start)

    def _should_terminate_search(self, results: List[Schedule], start: float) -> bool:
        """Check if search should terminate early."""
        if len(results) >= self.max_results:
            return True
        if time.time() - start >= self.timeout_seconds:
            self._last_run_stats["timeout_reached"] = True
            return True
        return False

    def _finalize_schedule(self, current_courses: List[Course], results: List[Schedule]) -> None:
        """Finalize and store a valid schedule."""
        schedule = Schedule(current_courses.copy())
        if self._is_valid_final_schedule(schedule):
            results.append(schedule)

    def _process_group(
        self,
        search: PreparedSearch,
        ordered_groups: List[str],
        index: int,
        current_courses: List[Course],
        results: List[Schedule],
        start: float,
    ) -> None:
        """Process all options for the current group."""
        group_key = ordered_groups[index]
        options = search.group_options.get(group_key, [])
        ranked = sorted(options, key=lambda opt: len(opt) if opt else float('inf'))

        for option in ranked:
            self._try_option(search, ordered_groups, index, option, current_courses, results, start)

    def _try_option(
        self,
        search: PreparedSearch,
        ordered_groups: List[str],
        index: int,
        option: Optional[List[Course]],
        current_courses: List[Course],
        results: List[Schedule],
        start: float,
    ) -> None:
        """Try a single option for the current group."""
        if option is None:
            self._try_skip_option(search, ordered_groups, index, current_courses, results, start)
            return

        tentative = current_courses + option
        if not self._is_valid_partial_selection(tentative):
            self._last_run_stats["branches_pruned"] += 1
            return

        if not self._forward_check(search, ordered_groups[index + 1 :], tentative):
            self._last_run_stats["branches_pruned"] += 1
            return

        self._cp_backtrack(search, ordered_groups, index + 1, tentative, results, start)

    def _try_skip_option(
        self,
        search: PreparedSearch,
        ordered_groups: List[str],
        index: int,
        current_courses: List[Course],
        results: List[Schedule],
        start: float,
    ) -> None:
        """Try skipping the current group (if optional)."""
        group_key = ordered_groups[index]
        if group_key not in search.mandatory_codes:
            self._cp_backtrack(
                search,
                ordered_groups,
                index + 1,
                current_courses,
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
