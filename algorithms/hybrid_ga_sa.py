"""Hybrid genetic algorithm + simulated annealing scheduler."""

from __future__ import annotations

from typing import Any, List, Optional, cast

from core.models import Schedule
from utils.schedule_metrics import SchedulerPrefs
from . import register_scheduler
from .base_scheduler import AlgorithmMetadata, BaseScheduler, PreparedSearch
from .genetic_algorithm import GeneticAlgorithmScheduler
from .simulated_annealing import AnnealingOptimizer


@register_scheduler
class HybridGASAScheduler(BaseScheduler):
    """Runs GA to explore globally, then annealing for fine-tuning."""

    metadata = AlgorithmMetadata(
        name="HybridGA+SA",
        category="hybrid",
        complexity="O(population * generations) + O(annealing)",
        description="Hybrid genetic + simulated annealing optimisation",
        optimal=False,
        supports_preferences=True,
        supports_parallel=True,
        is_optimizer=True,
    )

    def __init__(
        self,
        max_results: int = 10,
        max_ects: int = 31,
        allow_conflicts: bool = False,
        max_conflicts: int = 1,
        scheduler_prefs: Optional[SchedulerPrefs] = None,
        timeout_seconds: int = 240,
        population_size: int = 30,
        generations: int = 50,
        annealing_iterations: int = 20,
    ) -> None:
        super().__init__(
            max_results=max_results,
            max_ects=max_ects,
            allow_conflicts=allow_conflicts,
            max_conflicts=max_conflicts,
            scheduler_prefs=scheduler_prefs,
            timeout_seconds=timeout_seconds,
        )
        self.population_size = population_size
        self.generations = generations
        self.annealing_iterations = annealing_iterations

    def _run_algorithm(self, search: PreparedSearch) -> List[Schedule]:
        ga_ctor = cast(Any, GeneticAlgorithmScheduler)
        ga = ga_ctor(
            max_results=self.max_results,
            max_ects=self.max_ects,
            allow_conflicts=self.allow_conflicts,
            scheduler_prefs=self.scheduler_prefs,
            timeout_seconds=self.timeout_seconds,
            population_size=self.population_size,
            generations=self.generations,
        )
        ga._active_mandatory_codes = self._active_mandatory_codes
        ga_results = ga._run_algorithm(search)

        if not ga_results:
            return []

        optimizer = AnnealingOptimizer(
            max_ects=self.max_ects,
            scheduler_prefs=self.scheduler_prefs,
            iterations=self.annealing_iterations,
        )

        optimized_results: List[Schedule] = []
        for schedule in ga_results[: self.max_results * 2]:
            refined = optimizer.optimize(schedule, search.group_keys, search.group_options)
            if self._is_valid_final_schedule(refined):
                optimized_results.append(refined)

        return optimized_results[: self.max_results]


__all__ = ["HybridGASAScheduler"]
