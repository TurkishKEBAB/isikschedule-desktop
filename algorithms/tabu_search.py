"""Tabu search scheduler implementation."""

from __future__ import annotations

from typing import List, Optional, Tuple

from core.models import Course, Schedule
from utils.schedule_metrics import SchedulerPrefs, score_schedule
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

    def _run_algorithm(self, search: PreparedSearch) -> List[Schedule]:
        initial_courses: List[Course] = []
        for group_key in search.group_keys:
            options = search.group_options.get(group_key, [])
            for option in options:
                if option is None:
                    continue
                tentative = initial_courses + option
                if self._is_valid_partial_selection(tentative):
                    initial_courses.extend(option)
                    break

        if not initial_courses:
            return []

        current_schedule = Schedule(initial_courses)
        if not self._is_valid_final_schedule(current_schedule):
            return []

        best_schedule = current_schedule
        best_cost = self._cost(best_schedule)

        tabu_list: List[Tuple[str, ...]] = []

        for _ in range(self.max_iterations):
            best_candidate = None
            best_candidate_cost = float("inf")

            for group_key in search.group_keys:
                options = search.group_options.get(group_key, [])
                for option in options:
                    if option is None:
                        continue

                    filtered = [
                        course
                        for course in current_schedule.courses
                        if course.main_code != group_key
                    ]
                    tentative_courses = filtered + option

                    if not self._is_valid_partial_selection(tentative_courses):
                        self._last_run_stats["branches_pruned"] += 1
                        continue

                    tentative_schedule = Schedule(tentative_courses)
                    signature = tuple(sorted(course.code for course in tentative_schedule.courses))
                    if signature in tabu_list:
                        continue

                    cost = self._cost(tentative_schedule)
                    self._last_run_stats["nodes_explored"] += 1

                    if self._is_valid_final_schedule(tentative_schedule) and cost < best_candidate_cost:
                        best_candidate = tentative_schedule
                        best_candidate_cost = cost

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

    def _cost(self, schedule: Schedule) -> float:
        if self.scheduler_prefs:
            return -score_schedule(schedule, self.scheduler_prefs)
        return estimate_conflict_penalty(schedule)


__all__ = ["TabuSearchScheduler"]
