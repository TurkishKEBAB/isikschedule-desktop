"""Scheduler adapter for the simulated annealing optimizer."""

from __future__ import annotations

from typing import List, Optional

from core.models import Course, Schedule
from utils.schedule_metrics import SchedulerPrefs
from . import register_scheduler
from .base_scheduler import AlgorithmMetadata, BaseScheduler, PreparedSearch
from .simulated_annealing import AnnealingOptimizer


@register_scheduler
class SimulatedAnnealingScheduler(BaseScheduler):
    metadata = AlgorithmMetadata(
        name="SimulatedAnnealing",
        category="local-search",
        complexity="O(iterations)",
        description="Simulated annealing optimisation",
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
        iterations: int = 500,
        annealing_iterations: Optional[int] = None,  # Eski parametre için backward compatibility
    ) -> None:
        super().__init__(
            max_results=max_results,
            max_ects=max_ects,
            allow_conflicts=allow_conflicts,
            max_conflicts=max_conflicts,
            scheduler_prefs=scheduler_prefs,
            timeout_seconds=timeout_seconds,
        )
        # annealing_iterations parametresi verilmişse onu kullan
        if annealing_iterations is not None:
            self.annealing_iterations = annealing_iterations
        else:
            self.annealing_iterations = iterations

    def _run_algorithm(self, search: PreparedSearch) -> List[Schedule]:
        initial_schedule = self._initial_schedule(search)
        if initial_schedule is None:
            return []

        optimizer = AnnealingOptimizer(
            iterations=self.annealing_iterations,
            max_ects=self.max_ects,
            scheduler_prefs=self.scheduler_prefs,
        )

        optimized = optimizer.optimize(initial_schedule, search.group_keys, search.group_options)
        if self._is_valid_final_schedule(optimized):
            return [optimized]
        return []

    def _initial_schedule(self, search: PreparedSearch) -> Optional[Schedule]:
        courses: List[Course] = []
        for group_key in search.group_keys:
            options = search.group_options.get(group_key, [])
            for option in options:
                if option is None:
                    continue
                tentative = courses + option
                if self._is_valid_partial_selection(tentative):
                    courses.extend(option)
                    break

        if not courses:
            return None

        schedule = Schedule(courses)
        return schedule if self._is_valid_final_schedule(schedule) else None


__all__ = ["SimulatedAnnealingScheduler"]
