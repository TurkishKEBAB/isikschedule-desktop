"""Genetic algorithm based scheduler."""

from __future__ import annotations

import random
from typing import Dict, List, Optional

from core.models import Course, Schedule
from utils.schedule_metrics import SchedulerPrefs, score_schedule
from . import register_scheduler
from .base_scheduler import AlgorithmMetadata, BaseScheduler, PreparedSearch
from .heuristics import estimate_conflict_penalty


Individual = Dict[str, Optional[List[Course]]]


@register_scheduler
class GeneticAlgorithmScheduler(BaseScheduler):
    """Evolutionary approach for exploring large search spaces."""

    metadata = AlgorithmMetadata(
        name="Genetic",
        category="evolutionary",
        complexity="O(population * generations)",
        description="Genetic algorithm with crossover and mutation",
        optimal=False,
        supports_preferences=True,
        supports_parallel=True,
        is_optimizer=True,
    )

    def __init__(
        self,
        max_results: int = 3,
        max_ects: int = 31,
        allow_conflicts: bool = False,
        scheduler_prefs: Optional[SchedulerPrefs] = None,
        timeout_seconds: int = 180,
        population_size: int = 20,
        generations: int = 30,
        crossover_rate: float = 0.7,
        mutation_rate: float = 0.2,
    ) -> None:
        super().__init__(
            max_results=max_results,
            max_ects=max_ects,
            allow_conflicts=allow_conflicts,
            scheduler_prefs=scheduler_prefs,
            timeout_seconds=timeout_seconds,
        )
        self.population_size = max(6, population_size)
        self.generations = max(5, generations)
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate

    def _run_algorithm(self, search: PreparedSearch) -> List[Schedule]:
        options_map: Dict[str, List[Optional[List[Course]]]] = {
            key: search.group_options.get(key, []) for key in search.group_keys
        }

        population = [self._create_individual(search, options_map) for _ in range(self.population_size)]
        best_schedule: Optional[Schedule] = None
        best_cost = float("inf")

        for _ in range(self.generations):
            evaluated = [(individual, self._fitness(individual, search)) for individual in population]
            evaluated.sort(key=lambda item: item[1])

            for individual, cost in evaluated[: self.max_results * 2]:
                schedule = self._to_schedule(individual)
                if schedule and self._is_valid_final_schedule(schedule):
                    if cost < best_cost:
                        best_schedule = schedule
                        best_cost = cost

            next_population: List[Individual] = []

            # Elitism: carry best individuals forward
            elite_count = max(1, self.population_size // 5)
            next_population.extend(individual for individual, _ in evaluated[:elite_count])

            while len(next_population) < self.population_size:
                parent_a = self._tournament_selection(evaluated)
                parent_b = self._tournament_selection(evaluated)

                if random.random() < self.crossover_rate:
                    child_a, child_b = self._crossover(parent_a, parent_b)
                else:
                    child_a, child_b = parent_a.copy(), parent_b.copy()

                self._mutate(child_a, options_map)
                self._mutate(child_b, options_map)

                next_population.extend([child_a, child_b])

            population = next_population[: self.population_size]

        return [best_schedule] if best_schedule else []

    # ------------------------------------------------------------------
    # Genetic primitives
    # ------------------------------------------------------------------
    def _create_individual(
        self,
        search: PreparedSearch,
        options_map: Dict[str, List[Optional[List[Course]]]],
    ) -> Individual:
        individual: Individual = {}
        current_courses: List[Course] = []

        for group_key in search.group_keys:
            options = options_map.get(group_key, [])

            if not options:
                individual[group_key] = None
                continue

            attempt_options = options.copy()
            random.shuffle(attempt_options)

            chosen: Optional[List[Course]] = None
            for option in attempt_options:
                if option is None:
                    chosen = None
                    break

                tentative = current_courses + option
                if self._is_valid_partial_selection(tentative):
                    chosen = option
                    current_courses.extend(option)
                    break

            if chosen is None and group_key in search.mandatory_codes and attempt_options:
                # fallback to first option even if conflicts (will be penalised)
                fallback = next(opt for opt in attempt_options if opt is not None)
                current_courses.extend(fallback)
                chosen = fallback

            individual[group_key] = chosen

        return individual

    def _to_schedule(self, individual: Individual) -> Optional[Schedule]:
        courses: List[Course] = []
        for option in individual.values():
            if option:
                courses.extend(option)
        if not courses:
            return None
        return Schedule(courses)

    def _fitness(self, individual: Individual, search: PreparedSearch) -> float:
        schedule = self._to_schedule(individual)
        if schedule is None:
            return 1e6

        included = {course.main_code for course in schedule.courses}
        if not search.mandatory_codes.issubset(included):
            return 5e5

        if not self._is_valid_final_schedule(schedule):
            return 1e5 + estimate_conflict_penalty(schedule)

        if self.scheduler_prefs:
            return -score_schedule(schedule, self.scheduler_prefs)
        return estimate_conflict_penalty(schedule)

    def _tournament_selection(self, evaluated: List[tuple]) -> Individual:
        contenders = random.sample(evaluated, k=2)
        winner = min(contenders, key=lambda item: item[1])
        return winner[0].copy()

    def _crossover(self, parent_a: Individual, parent_b: Individual) -> tuple:
        child_a: Individual = {}
        child_b: Individual = {}

        for key in parent_a.keys():
            if random.random() < 0.5:
                child_a[key] = parent_a.get(key)
                child_b[key] = parent_b.get(key)
            else:
                child_a[key] = parent_b.get(key)
                child_b[key] = parent_a.get(key)

        return child_a, child_b

    def _mutate(self, individual: Individual, options_map: Dict[str, List[Optional[List[Course]]]]) -> None:
        if random.random() >= self.mutation_rate:
            return

        group_key = random.choice(list(individual.keys()))
        options = options_map.get(group_key, [])
        if not options:
            return

        individual[group_key] = random.choice(options)


__all__ = ["GeneticAlgorithmScheduler"]
