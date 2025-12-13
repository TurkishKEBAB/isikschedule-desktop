"""
Simulated Annealing optimization for course schedules.

This module provides a simulated annealing implementation to optimize
course schedules by minimizing conflicts and maximizing credits.
"""
import random
import math
from typing import List, Dict, Optional
from core.models import Course, Schedule
from utils.schedule_metrics import (
    SchedulerPrefs, score_schedule, meets_weekly_hours_constraint,
    meets_daily_hours_constraint, meets_free_day_constraint
)


class AnnealingOptimizer:
    """
    Optimizes course schedules using Simulated Annealing algorithm.

    Simulated annealing is a probabilistic technique used to find an
    approximate global optimum in a large search space. It's especially
    useful for schedule optimization where small changes can be made
    incrementally to improve the overall schedule quality.
    """

    def __init__(self,
                 temp0: float = 100.0,
                 alpha: float = 0.95,
                 iterations: int = 1000,
                 max_ects: int = 31,
                 scheduler_prefs: Optional[SchedulerPrefs] = None,
                 enable_reheating: bool = True,
                 stagnation_threshold: int = 50):
        """
        Initialize the annealing optimizer.

        Args:
            temp0: Initial temperature
            alpha: Cooling rate
            iterations: Maximum number of iterations
            max_ects: Maximum ECTS credits allowed
            scheduler_prefs: Advanced scheduler preferences
            enable_reheating: Enable reheating when stuck
            stagnation_threshold: Number of iterations without improvement before reheating
        """
        self.temp0 = temp0
        self.alpha = alpha
        self.iterations = iterations
        self.max_ects = max_ects
        self.scheduler_prefs = scheduler_prefs or SchedulerPrefs()
        self.enable_reheating = enable_reheating
        self.stagnation_threshold = stagnation_threshold

    def optimize(self,
                 schedule: Schedule,
                 group_keys: List[str],
                 group_options: Dict[str, List[Optional[List[Course]]]]) -> Schedule:
        """
        Optimize a schedule using simulated annealing.

        Args:
            schedule: Initial schedule to optimize
            group_keys: List of course group keys (main codes)
            group_options: Dictionary mapping group keys to lists of possible course selections

        Returns:
            Optimized schedule
        """
        current_schedule = schedule.courses.copy()

        def fitness(sched: List[Course], total: int) -> float:
            """
            Calculate fitness score (lower is better).

            Args:
                sched: Course schedule to evaluate
                total: Total ECTS credits

            Returns:
                Fitness score (lower is better)
            """
            return self._calculate_fitness(sched, total)

        current_fitness = fitness(current_schedule, sum(c.ects for c in current_schedule))
        best_schedule = current_schedule.copy()
        best_fitness = current_fitness

        T = self.temp0
        iterations_without_improvement = 0

        for _ in range(self.iterations):
            if not group_keys:
                break

            current_schedule, current_fitness, best_schedule, best_fitness, improved = self._annealing_step(
                current_schedule, current_fitness, best_schedule, best_fitness,
                group_keys, group_options, fitness, T
            )

            if improved:
                iterations_without_improvement = 0
            else:
                iterations_without_improvement += 1

            # Reheating: if stuck for too long, increase temperature
            if (self.enable_reheating and
                iterations_without_improvement >= self.stagnation_threshold and
                T < self.temp0 * 0.1):
                T = self.temp0 * 0.5  # Reheat to 50% of initial temperature
                iterations_without_improvement = 0

            T *= self.alpha

            # Early termination if temperature is too low
            if T < 1e-3 and iterations_without_improvement > 20:
                break

        return Schedule(best_schedule)

    def _calculate_fitness(self, sched: List[Course], total: int) -> float:
        """Calculate fitness score for a schedule."""
        temp_schedule = Schedule(sched)

        if self.scheduler_prefs:
            return self._calculate_prefs_fitness(temp_schedule, total)
        else:
            # Original fitness function for backward compatibility
            ects_penalty = (self.max_ects - total) ** 2
            conflict_penalty = temp_schedule.conflict_count * 100
            return ects_penalty + conflict_penalty

    def _calculate_prefs_fitness(self, temp_schedule: Schedule, total: int) -> float:
        """Calculate fitness using preferences."""
        base_score = -score_schedule(temp_schedule, self.scheduler_prefs)

        # Add penalties for constraint violations
        if self.scheduler_prefs.max_weekly_slots < 60:
            if not meets_weekly_hours_constraint(temp_schedule, self.scheduler_prefs.max_weekly_slots):
                return 10000.0

        if self.scheduler_prefs.max_daily_slots is not None:
            if not meets_daily_hours_constraint(temp_schedule, self.scheduler_prefs.max_daily_slots):
                return 10000.0

        if (self.scheduler_prefs.compress_classes and
                self.scheduler_prefs.desired_free_days and
                self.scheduler_prefs.strict_free_days and
                not meets_free_day_constraint(
                    temp_schedule,
                    self.scheduler_prefs.desired_free_days,
                    strict=True
                )):
            return 10000.0

        # Add penalty for deviation from target ECTS
        ects_penalty = (self.max_ects - total) ** 2

        # Add penalty for conflicts
        conflict_penalty = temp_schedule.conflict_count * 100

        return base_score + ects_penalty + conflict_penalty

    def _annealing_step(
            self,
            current_schedule: List[Course],
            current_fitness: float,
            best_schedule: List[Course],
            best_fitness: float,
            group_keys: List[str],
            group_options: Dict[str, List[Optional[List[Course]]]],
            fitness_fn,
            temperature: float,
    ) -> tuple:
        """
        Perform one simulated annealing step.

        Returns:
            Tuple of (current_schedule, current_fitness, best_schedule, best_fitness, improved)
            where improved is True if best_fitness was improved
        """
        import random
        import math

        group = random.choice(group_keys)
        valid_options = group_options.get(group, [])

        if len(valid_options) <= 1:
            return current_schedule, current_fitness, best_schedule, best_fitness, False

        new_schedule = [c for c in current_schedule if c.main_code != group]
        non_none_options = [opt for opt in valid_options if opt is not None]

        if not non_none_options:
            return current_schedule, current_fitness, best_schedule, best_fitness, False

        new_option = random.choice(non_none_options)
        new_schedule.extend(new_option)

        new_total = sum(c.ects for c in new_schedule)
        new_fitness = fitness_fn(new_schedule, new_total)

        delta = new_fitness - current_fitness
        improved = False

        if delta < 0 or random.random() < math.exp(-delta / temperature):
            current_schedule = new_schedule
            current_fitness = new_fitness

            if current_fitness < best_fitness:
                best_schedule = current_schedule.copy()
                best_fitness = current_fitness
                improved = True

        return current_schedule, current_fitness, best_schedule, best_fitness, improved

    def repair_schedule_with_priority(self,
                                      schedule: Schedule,
                                      group_valid_selections: Dict[str, List[List[Course]]],
                                      priority_order: List[str]) -> Schedule:
        """
        Repair a schedule by prioritizing certain course types.

        Args:
            schedule: Schedule to repair
            group_valid_selections: Dictionary mapping main codes to valid course selections
            priority_order: List of course types in order of priority ("lecture", "ps", "lab")

        Returns:
            Repaired schedule
        """
        # Group courses by main code
        current = {}
        for course in schedule.courses:
            if course.main_code not in current:
                current[course.main_code] = []
            current[course.main_code].append(course)

        best_schedule = schedule.courses.copy()
        best_cost = schedule.conflict_count

        for _ in range(10):
            improved = self._try_priority_improvements(
                current, best_schedule, best_cost, group_valid_selections, priority_order
            )
            if not improved:
                break

        return Schedule(best_schedule)

    def _try_priority_improvements(
            self,
            current: Dict,
            best_schedule: List[Course],
            best_cost: int,
            group_valid_selections: Dict[str, List[List[Course]]],
            priority_order: List[str],
    ) -> bool:
        """Try improvements for priority types. Returns True if improved."""
        for p_type in priority_order:
            for group in current.keys():
                current_selection = current[group]

                # Skip if no courses of this type
                if not any(course.course_type == p_type for course in current_selection):
                    continue

                # Try alternatives for this group
                alternatives = group_valid_selections.get(group, [])
                for alternative in alternatives:
                    if self._try_alternative(
                            current, group, alternative, current_selection,
                            best_schedule, best_cost, p_type
                    ):
                        return True

        return False

    def _try_alternative(
            self,
            current: Dict,
            group: str,
            alternative: List[Course],
            current_selection: List[Course],
            best_schedule: List[Course],
            best_cost: int,
            p_type: str,
    ) -> bool:
        """Try an alternative course selection. Returns True if improved."""
        alt_has_priority = any(course.course_type == p_type for course in alternative)
        cur_has_priority = any(course.course_type == p_type for course in current_selection)

        if alt_has_priority == cur_has_priority:
            return False

        # Generate new schedule with this alternative
        new_schedule = []
        for g in current:
            if g == group:
                new_schedule.extend(alternative)
            else:
                new_schedule.extend(current[g])

        # Check if it's an improvement
        temp_schedule = Schedule(new_schedule)
        new_cost = temp_schedule.conflict_count

        if new_cost < best_cost:
            best_schedule[:] = new_schedule
            current[group] = alternative
            return True

        return False

    def global_repair_schedule(self, schedule: Schedule, all_courses: List[Course]) -> Schedule:
        """
        Attempt global repair by substituting individual courses.

        Args:
            schedule: Schedule to repair
            all_courses: List of all available courses

        Returns:
            Repaired schedule
        """
        best_schedule = schedule.courses.copy()
        best_cost = schedule.conflict_count

        for i in range(len(best_schedule)):
            # Try removing one course
            candidate_removed = best_schedule[:i] + best_schedule[i + 1:]

            # Try substituting with each available course
            for course in all_courses:
                # Skip if already in the schedule
                if course.code in [c.code for c in candidate_removed]:
                    continue

                # Check for conflicts
                temp_schedule = Schedule(candidate_removed)
                if not temp_schedule.has_conflict_with([course]):
                    new_schedule = candidate_removed + [course]
                    temp_schedule = Schedule(new_schedule)
                    new_cost = temp_schedule.conflict_count

                    # Update if better
                    if new_cost < best_cost:
                        best_cost = new_cost
                        best_schedule = new_schedule

        return Schedule(best_schedule)

    def multi_objective_optimize(self,
                                 schedule: Schedule,
                                 group_keys: List[str],
                                 group_options: Dict[str, List[Optional[List[Course]]]],
                                 objectives: Dict[str, float]) -> Schedule:
        """
        Optimize schedule for multiple objectives with weights.

        Args:
            schedule: Initial schedule
            group_keys: List of course group keys
            group_options: Dictionary of group options
            objectives: Dictionary of objective weights (e.g., {"conflicts": 2.0, "ects": 1.0, "gaps": 0.5})

        Returns:
            Optimized schedule
        """
        from utils.schedule_metrics import compute_schedule_stats

        current_schedule = schedule.courses.copy()

        def multi_objective_fitness(sched: List[Course]) -> float:
            """Calculate weighted multi-objective fitness."""
            return self._calc_multi_objective_fitness(sched, objectives)

        current_fitness = multi_objective_fitness(current_schedule)
        best_schedule = current_schedule.copy()
        best_fitness = current_fitness

        T = self.temp0
        for _ in range(self.iterations):
            if not group_keys:
                break

            current_schedule, current_fitness, best_schedule, best_fitness = self._multi_obj_step(
                current_schedule, current_fitness, best_schedule, best_fitness,
                group_keys, group_options, multi_objective_fitness, T
            )

            T *= self.alpha

            if T < 1e-3:
                break

        return Schedule(best_schedule)

    def _calc_multi_objective_fitness(self, sched: List[Course], objectives: Dict[str, float]) -> float:
        """Calculate weighted multi-objective fitness."""
        from utils.schedule_metrics import compute_schedule_stats

        temp_schedule = Schedule(sched)
        stats = compute_schedule_stats(temp_schedule)

        fitness = 0.0

        # Conflict objective (lower is better)
        if "conflicts" in objectives:
            fitness += objectives["conflicts"] * temp_schedule.conflict_count * 100

        # ECTS objective (closer to max is better)
        if "ects" in objectives:
            ects_diff = abs(self.max_ects - temp_schedule.total_credits)
            fitness += objectives["ects"] * ects_diff * 10

        # Gaps objective (fewer gaps is better)
        if "gaps" in objectives:
            total_gaps = sum(stats.gaps_per_day.values())
            fitness += objectives["gaps"] * total_gaps * 50

        # Day compression objective (fewer days is better)
        if "compression" in objectives:
            fitness += objectives["compression"] * stats.days_used * 20

        return fitness

    def _multi_obj_step(
            self,
            current_schedule: List[Course],
            current_fitness: float,
            best_schedule: List[Course],
            best_fitness: float,
            group_keys: List[str],
            group_options: Dict[str, List[Optional[List[Course]]]],
            fitness_fn,
            temperature: float,
    ) -> tuple:
        """Perform one multi-objective annealing step."""
        group = random.choice(group_keys)
        valid_options = group_options.get(group, [])

        if len(valid_options) <= 1:
            return current_schedule, current_fitness, best_schedule, best_fitness

        new_schedule = [c for c in current_schedule if c.main_code != group]
        non_none_options = [opt for opt in valid_options if opt is not None]

        if not non_none_options:
            return current_schedule, current_fitness, best_schedule, best_fitness

        new_option = random.choice(non_none_options)
        new_schedule.extend(new_option)

        new_fitness = fitness_fn(new_schedule)

        delta = new_fitness - current_fitness
        if delta < 0 or random.random() < math.exp(-delta / temperature):
            current_schedule = new_schedule
            current_fitness = new_fitness

            if current_fitness < best_fitness:
                best_schedule = current_schedule.copy()
                best_fitness = current_fitness

        return current_schedule, current_fitness, best_schedule, best_fitness
