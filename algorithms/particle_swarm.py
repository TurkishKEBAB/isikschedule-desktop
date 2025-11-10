"""Particle swarm optimisation for schedule generation."""

from __future__ import annotations

import random
from typing import Dict, List, Optional

from core.models import Course, Schedule
from utils.schedule_metrics import SchedulerPrefs, score_schedule
from . import register_scheduler
from .base_scheduler import AlgorithmMetadata, BaseScheduler, PreparedSearch
from .heuristics import estimate_conflict_penalty


class Particle:
    def __init__(self, position: Dict[str, int]):
        self.position = position
        self.best_position = position.copy()
        self.best_cost = float("inf")


@register_scheduler
class ParticleSwarmScheduler(BaseScheduler):
    """Discrete PSO variant tailored for course selection problems."""

    metadata = AlgorithmMetadata(
        name="PSO",
        category="population",
        complexity="O(swarm * iterations)",
        description="Particle swarm optimisation over course combinations",
        optimal=False,
        supports_preferences=True,
        supports_parallel=True,
        is_optimizer=True,
    )

    def __init__(
        self,
        max_results: int = 1,
        max_ects: int = 31,
        allow_conflicts: bool = False,
        scheduler_prefs: Optional[SchedulerPrefs] = None,
        timeout_seconds: int = 120,
        swarm_size: int = 15,
        iterations: int = 25,
        inertia: float = 0.4,
        social: float = 0.4,
        cognitive: float = 0.4,
    ) -> None:
        super().__init__(
            max_results=max_results,
            max_ects=max_ects,
            allow_conflicts=allow_conflicts,
            scheduler_prefs=scheduler_prefs,
            timeout_seconds=timeout_seconds,
        )
        self.swarm_size = max(5, swarm_size)
        self.iterations = max(10, iterations)
        self.inertia = inertia
        self.social = social
        self.cognitive = cognitive

    def _run_algorithm(self, search: PreparedSearch) -> List[Schedule]:
        options_map: Dict[str, List[Optional[List[Course]]]] = {
            key: search.group_options.get(key, []) for key in search.group_keys
        }

        index_map: Dict[str, List[Optional[List[Course]]]] = {
            key: options for key, options in options_map.items() if options
        }

        if not index_map:
            return []

        particles = [self._create_particle(index_map, search) for _ in range(self.swarm_size)]
        global_best_position = particles[0].position.copy()
        global_best_cost = float("inf")
        global_best_schedule: Optional[Schedule] = None

        for _ in range(self.iterations):
            for particle in particles:
                schedule = self._decode(particle.position, index_map)
                if schedule is None:
                    continue

                cost = self._fitness(schedule)
                self._last_run_stats["nodes_explored"] += 1

                if cost < particle.best_cost and self._is_valid_final_schedule(schedule):
                    particle.best_cost = cost
                    particle.best_position = particle.position.copy()

                if cost < global_best_cost and self._is_valid_final_schedule(schedule):
                    global_best_cost = cost
                    global_best_position = particle.position.copy()
                    global_best_schedule = schedule

            for particle in particles:
                for key, options in index_map.items():
                    if not options:
                        continue

                    rand = random.random()
                    if rand < self.cognitive and key in particle.best_position:
                        particle.position[key] = particle.best_position[key]
                    elif rand < self.cognitive + self.social and key in global_best_position:
                        particle.position[key] = global_best_position[key]
                    elif rand > self.inertia:
                        particle.position[key] = random.randrange(len(options))

        return [global_best_schedule] if global_best_schedule else []

    def _create_particle(
        self,
        index_map: Dict[str, List[Optional[List[Course]]]],
        search: PreparedSearch,
    ) -> Particle:
        position: Dict[str, int] = {}
        for key, options in index_map.items():
            if key in search.mandatory_codes:
                valid_indices = [idx for idx, opt in enumerate(options) if opt is not None]
                position[key] = random.choice(valid_indices or [0])
            else:
                position[key] = random.randrange(len(options))
        return Particle(position)

    def _decode(
        self,
        position: Dict[str, int],
        index_map: Dict[str, List[Optional[List[Course]]]],
    ) -> Optional[Schedule]:
        courses: List[Course] = []
        for key, index in position.items():
            options = index_map.get(key)
            if not options:
                continue
            index = max(0, min(index, len(options) - 1))
            option = options[index]
            if option:
                tentative = courses + option
                if not self._is_valid_partial_selection(tentative):
                    return None
                courses.extend(option)
        if not courses:
            return None
        return Schedule(courses)

    def _fitness(self, schedule: Schedule) -> float:
        if self.scheduler_prefs:
            return -score_schedule(schedule, self.scheduler_prefs)
        return estimate_conflict_penalty(schedule)


__all__ = ["ParticleSwarmScheduler"]
