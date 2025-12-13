"""Greedy best-first scheduler implementation."""

from __future__ import annotations

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
class GreedyScheduler(BaseScheduler):
    """Selects locally optimal course options step-by-step."""

    metadata = AlgorithmMetadata(
        name="Greedy",
        category="informed-search",
        complexity="O(n * m)",
        description="Greedy best-first selection using heuristic scoring",
        optimal=False,
        supports_preferences=True,
    )

    def __init__(
        self,
        max_results: int = 5,
        max_ects: int = 31,
        allow_conflicts: bool = False,
        max_conflicts: int = 1,
        scheduler_prefs: Optional[SchedulerPrefs] = None,
        timeout_seconds: int = 60,
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
        current_courses: List[Course] = []

        for group_key in search.group_keys:
            options = search.group_options.get(group_key, [])
            ranked = rank_options_by_score(options, current_courses, self.scheduler_prefs)

            chosen: Optional[List[Course]] = None
            for option in ranked:
                if option is None:
                    # Skip optional group entirely
                    chosen = None
                    break

                tentative = current_courses + option
                if self._is_valid_partial_selection(tentative):
                    chosen = option
                    break
                else:
                    self._last_run_stats["branches_pruned"] += 1

            if chosen:
                current_courses.extend(chosen)

            self._last_run_stats["nodes_explored"] += 1

        schedule = Schedule(current_courses)
        if self._is_valid_final_schedule(schedule):
            return [schedule]
        return []


__all__ = ["GreedyScheduler"]
