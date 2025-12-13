"""Hill climbing local search scheduler."""

from __future__ import annotations

from typing import Dict, List, Optional

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
        current_courses = self._build_initial_solution(search)
        if not current_courses:
            return []

        best_schedule = Schedule(current_courses)
        if not self._is_valid_final_schedule(best_schedule):
            return []

        best_cost = self._cost(best_schedule)

        for _ in range(self.max_iterations):
            best_candidate = self._find_best_neighbor(search, best_schedule, best_cost)
            if best_candidate is None:
                break

            best_schedule = best_candidate["schedule"]
            best_cost = best_candidate["cost"]

        return [best_schedule]

    def _build_initial_solution(self, search: PreparedSearch) -> List[Course]:
        """Build initial feasible solution by picking first valid option per group."""
        current_courses: List[Course] = []

        for group_key in search.group_keys:
            options = search.group_options.get(group_key, [])
            chosen = self._select_first_valid_option(options, current_courses)
            if chosen:
                current_courses.extend(chosen)

        return current_courses

    def _select_first_valid_option(
        self, options: List[Optional[List[Course]]], current_courses: List[Course]
    ) -> Optional[List[Course]]:
        """Select first valid option from list."""
        for option in options:
            if option is None:
                continue
            tentative = current_courses + option
            if self._is_valid_partial_selection(tentative):
                return option
        return None

    def _find_best_neighbor(
        self,
        search: PreparedSearch,
        current_schedule: Schedule,
        current_cost: float,
    ) -> Optional[Dict]:
        """Find the best neighbor to current schedule."""
        best_candidate = None
        best_candidate_cost = current_cost

        for group_key in search.group_keys:
            options = search.group_options.get(group_key, [])
            for option in options:
                candidate = self._evaluate_neighbor(
                    group_key, option, current_schedule, best_candidate_cost
                )
                if candidate:
                    best_candidate = candidate
                    best_candidate_cost = candidate["cost"]

        return best_candidate

    def _evaluate_neighbor(
        self,
        group_key: str,
        option: Optional[List[Course]],
        current_schedule: Schedule,
        best_cost_so_far: float,
    ) -> Optional[Dict]:
        """Evaluate a single neighbor option."""
        if option is None:
            return None

        filtered = [
            course
            for course in current_schedule.courses
            if course.main_code != group_key
        ]
        tentative_courses = filtered + option

        if not self._is_valid_partial_selection(tentative_courses):
            self._last_run_stats["branches_pruned"] += 1
            return None

        tentative_schedule = Schedule(tentative_courses)
        tentative_cost = self._cost(tentative_schedule)
        self._last_run_stats["nodes_explored"] += 1

        if tentative_cost < best_cost_so_far and self._is_valid_final_schedule(
            tentative_schedule
        ):
            return {"schedule": tentative_schedule, "cost": tentative_cost}

        return None

    def _cost(self, schedule: Schedule) -> float:
        if self.scheduler_prefs:
            return -score_schedule(schedule, self.scheduler_prefs)
        return estimate_conflict_penalty(schedule)


__all__ = ["HillClimbingScheduler"]
