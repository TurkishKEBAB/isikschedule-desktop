"""Tabu search scheduler implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from core.models import Course, Schedule
    from utils.schedule_metrics import SchedulerPrefs

# Runtime imports
try:
    from core.models import Course, Schedule
except ImportError as e:
    raise ImportError(f"Required module core.models not found: {e}")

try:
    from utils.schedule_metrics import SchedulerPrefs, score_schedule
except ImportError as e:
    raise ImportError(f"Required module utils.schedule_metrics not found: {e}")

from . import register_scheduler
from .base_scheduler import AlgorithmMetadata, BaseScheduler, PreparedSearch
from .heuristics import estimate_conflict_penalty


@register_scheduler
class TabuSearchScheduler(BaseScheduler):
    """Local search with memory to avoid cycling between similar schedules."""

    metadata = AlgorithmMetadata(
        name="TabuSearch",
        category="local-search",
        complexity="O(iterations * neighbourhood)",
        description="Tabu search optimisation with adaptive tenure",
        optimal=False,
        supports_preferences=True,
        is_optimizer=True,
    )

    def __init__(
        self,
        max_results: int = 10,
        max_ects: int = 31,
        allow_conflicts: bool = False,
        max_conflicts: int = 1,
        scheduler_prefs: Optional[SchedulerPrefs] = None,
        timeout_seconds: int = 180,
        max_iterations: int = 100,
        tabu_tenure: int = 10,
    ) -> None:
        super().__init__(
            max_results=max_results,
            max_ects=max_ects,
            allow_conflicts=allow_conflicts,
            max_conflicts=max_conflicts,
            scheduler_prefs=scheduler_prefs,
            timeout_seconds=timeout_seconds,
        )
        self.max_iterations = max_iterations
        self.tabu_tenure = max(3, tabu_tenure)

    def _run_algorithm(self, search):
        initial_courses = self._build_initial_solution(search)

        if not initial_courses:
            return []

        current_schedule = Schedule(initial_courses)
        if not self._is_valid_final_schedule(current_schedule):
            return []

        best_schedule = current_schedule
        best_cost = self._cost(best_schedule)

        tabu_list = []

        for _ in range(self.max_iterations):
            best_candidate, best_candidate_cost = self._find_best_neighbor(
                search, current_schedule, tabu_list
            )

            if best_candidate is None:
                break

            current_schedule = best_candidate
            signature = tuple(sorted(course.code for course in current_schedule.courses))
            tabu_list.append(signature)
            if len(tabu_list) > self.tabu_tenure:
                tabu_list.pop(0)

            if best_candidate_cost < best_cost:
                best_schedule = current_schedule
                best_cost = best_candidate_cost

        return [best_schedule]

    def _build_initial_solution(self, search):
        """Build initial feasible solution greedily."""
        initial_courses = []
        for group_key in search.group_keys:
            options = search.group_options.get(group_key, [])
            for option in options:
                if option is None:
                    continue
                tentative = initial_courses + option
                if self._is_valid_partial_selection(tentative):
                    initial_courses.extend(option)
                    break
        return initial_courses

    def _find_best_neighbor(self, search, current_schedule, tabu_list):
        """Find best neighbor not in tabu list."""
        best_candidate = None
        best_candidate_cost = float("inf")

        for group_key in search.group_keys:
            options = search.group_options.get(group_key, [])
            for option in options:
                if option is None:
                    continue

                candidate, cost = self._check_option(
                    current_schedule, group_key, option, tabu_list
                )

                if candidate and cost < best_candidate_cost:
                    best_candidate = candidate
                    best_candidate_cost = cost

        return best_candidate, best_candidate_cost

    def _check_option(self, current_schedule, group_key, option, tabu_list):
        """Check if an option is valid and return candidate schedule and cost."""
        filtered = [
            course
            for course in current_schedule.courses
            if course.main_code != group_key
        ]
        tentative_courses = filtered + option

        if not self._is_valid_partial_selection(tentative_courses):
            self._last_run_stats["branches_pruned"] += 1
            return None, float("inf")

        tentative_schedule = Schedule(tentative_courses)
        signature = tuple(sorted(course.code for course in tentative_schedule.courses))
        if signature in tabu_list:
            return None, float("inf")

        cost = self._cost(tentative_schedule)
        self._last_run_stats["nodes_explored"] += 1

        if self._is_valid_final_schedule(tentative_schedule):
            return tentative_schedule, cost

        return None, float("inf")

    def _cost(self, schedule):
        if self.scheduler_prefs and score_schedule:
            return -score_schedule(schedule, self.scheduler_prefs)
        return estimate_conflict_penalty(schedule)
__all__ = ["TabuSearchScheduler"]
