"""Hill climbing local search scheduler."""

from __future__ import annotations

from typing import List, Optional

from core.models import Course, Schedule
from utils.schedule_metrics import SchedulerPrefs, score_schedule
from . import register_scheduler
from .base_scheduler import AlgorithmMetadata, BaseScheduler, PreparedSearch
from .heuristics import estimate_conflict_penalty


@register_scheduler
class HillClimbingScheduler(BaseScheduler):
    """Iteratively improves a single schedule using local changes."""

    metadata = AlgorithmMetadata(
        name="HillClimbing",
        category="local-search",
        complexity="O(iterations * groups)",
        description="Gradient-free hill climbing optimisation",
        optimal=False,
        supports_preferences=True,
        is_optimizer=True,
    )

    def __init__(
        self,
        max_results: int = 1,
        max_ects: int = 31,
        allow_conflicts: bool = False,
        scheduler_prefs: Optional[SchedulerPrefs] = None,
        timeout_seconds: int = 120,
        max_iterations: int = 30,
    ) -> None:
        super().__init__(
            max_results=max_results,
            max_ects=max_ects,
            allow_conflicts=allow_conflicts,
            scheduler_prefs=scheduler_prefs,
            timeout_seconds=timeout_seconds,
        )
        self.max_iterations = max_iterations

    def _run_algorithm(self, search: PreparedSearch) -> List[Schedule]:
        current_courses: List[Course] = []

        # Build an initial feasible solution by picking the first valid option per group
        for group_key in search.group_keys:
            options = search.group_options.get(group_key, [])
            chosen = None
            for option in options:
                if option is None:
                    continue
                tentative = current_courses + option
                if self._is_valid_partial_selection(tentative):
                    chosen = option
                    break
            if chosen:
                current_courses.extend(chosen)

        if not current_courses:
            return []

        best_schedule = Schedule(current_courses)
        if not self._is_valid_final_schedule(best_schedule):
            return []

        best_cost = self._cost(best_schedule)

        for iteration in range(self.max_iterations):
            improved = False

            for group_key in search.group_keys:
                options = search.group_options.get(group_key, [])
                for option in options:
                    if option is None:
                        continue

                    filtered = [
                        course
                        for course in best_schedule.courses
                        if course.main_code != group_key
                    ]
                    tentative_courses = filtered + option

                    if not self._is_valid_partial_selection(tentative_courses):
                        self._last_run_stats["branches_pruned"] += 1
                        continue

                    tentative_schedule = Schedule(tentative_courses)
                    tentative_cost = self._cost(tentative_schedule)
                    self._last_run_stats["nodes_explored"] += 1

                    if tentative_cost < best_cost and self._is_valid_final_schedule(
                        tentative_schedule
                    ):
                        best_schedule = tentative_schedule
                        best_cost = tentative_cost
                        improved = True
                        break

                if improved:
                    break

            if not improved:
                break

        return [best_schedule]

    def _cost(self, schedule: Schedule) -> float:
        if self.scheduler_prefs:
            return -score_schedule(schedule, self.scheduler_prefs)
        return estimate_conflict_penalty(schedule)


__all__ = ["HillClimbingScheduler"]
