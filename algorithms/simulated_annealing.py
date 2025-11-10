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
                 scheduler_prefs: Optional[SchedulerPrefs] = None):
        """
        Initialize the annealing optimizer.

        Args:
            temp0: Initial temperature
            alpha: Cooling rate
            iterations: Maximum number of iterations
            max_ects: Maximum ECTS credits allowed
            scheduler_prefs: Advanced scheduler preferences
        """
        self.temp0 = temp0
        self.alpha = alpha
        self.iterations = iterations
        self.max_ects = max_ects
        self.scheduler_prefs = scheduler_prefs or SchedulerPrefs()

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
        current_total = sum(c.ects for c in current_schedule)

        def fitness(sched: List[Course], total: int) -> float:
            """
            Calculate fitness score (lower is better).

            Args:
                sched: Course schedule to evaluate
                total: Total ECTS credits

            Returns:
                Fitness score (lower is better)
            """
            temp_schedule = Schedule(sched)

            # If using advanced preferences, use the schedule_metrics scoring
            if self.scheduler_prefs:
                # Apply advanced scoring (higher score = better, so negate for lower=better)
                base_score = -score_schedule(temp_schedule, self.scheduler_prefs)

                # Add penalties for constraint violations
                if self.scheduler_prefs.max_weekly_slots < 60:  # 60 is effectively no limit
                    if not meets_weekly_hours_constraint(temp_schedule, self.scheduler_prefs.max_weekly_slots):
                        return 10000.0  # Hard constraint violation

                # Check daily hours constraint if set
                if self.scheduler_prefs.max_daily_slots is not None:
                    if not meets_daily_hours_constraint(temp_schedule, self.scheduler_prefs.max_daily_slots):
                        return 10000.0  # Hard constraint violation

                # Check free day constraint if strict mode is enabled
                if (self.scheduler_prefs.compress_classes and
                    self.scheduler_prefs.desired_free_days and
                    self.scheduler_prefs.strict_free_days):
                    if not meets_free_day_constraint(
                        temp_schedule,
                        self.scheduler_prefs.desired_free_days,
                        strict=True
                    ):
                        return 10000.0  # Hard constraint violation

                # Add penalty for deviation from target ECTS
                ects_penalty = (self.max_ects - total) ** 2

                # Add penalty for conflicts
                conflict_penalty = temp_schedule.conflict_count * 100

                return base_score + ects_penalty + conflict_penalty
            else:
                # Original fitness function for backward compatibility
                # Penalty for deviation from target ECTS
                ects_penalty = (self.max_ects - total) ** 2

                # Penalty for conflicts
                conflict_penalty = temp_schedule.conflict_count * 100

                return ects_penalty + conflict_penalty

        current_fitness = fitness(current_schedule, current_total)
        best_schedule = current_schedule.copy()
        best_fitness = current_fitness

        T = self.temp0
        for iteration in range(self.iterations):
            # Randomly select a course group to modify
            if not group_keys:
                break

            group = random.choice(group_keys)
            valid_options = group_options.get(group, [])

            # Skip if there's only one or no options
            if len(valid_options) <= 1:
                continue

            # Remove current courses of this group from schedule
            new_schedule = [c for c in current_schedule if c.main_code != group]

            # Select a random new option (only from non-None options)
            non_none_options = [opt for opt in valid_options if opt is not None]
            if not non_none_options:
                continue

            new_option = random.choice(non_none_options)

            # Add new option courses to schedule
            new_schedule.extend(new_option)

            # Calculate new credits and fitness
            new_total = sum(c.ects for c in new_schedule)
            new_fitness = fitness(new_schedule, new_total)

            # Determine whether to accept the new solution
            delta = new_fitness - current_fitness
            if delta < 0 or random.random() < math.exp(-delta / T):
                current_schedule = new_schedule
                current_total = new_total
                current_fitness = new_fitness

                # Update best if this is an improvement
                if current_fitness < best_fitness:
                    best_schedule = current_schedule.copy()
                    best_fitness = current_fitness

            # Cool down temperature
            T *= self.alpha

            # Early termination if temperature is too low
            if T < 1e-3:
                break

        return Schedule(best_schedule)

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
        improved = True
        iteration = 0
        max_iter = 10

        while improved and iteration < max_iter:
            improved = False

            # Try improvements for each priority type
            for p_type in priority_order:
                for group in list(current.keys()):
                    current_selection = current[group]

                    # Skip if no courses of this type
                    if not any(course.course_type == p_type for course in current_selection):
                        continue

                    # Try alternatives for this group
                    alternatives = group_valid_selections.get(group, [])
                    for alternative in alternatives:
                        # Check if priority changed
                        alt_has_priority = any(course.course_type == p_type for course in alternative)
                        cur_has_priority = any(course.course_type == p_type for course in current_selection)

                        if alt_has_priority == cur_has_priority:
                            continue

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
                            best_cost = new_cost
                            best_schedule = new_schedule
                            current[group] = alternative
                            improved = True

            iteration += 1

        return Schedule(best_schedule)

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
            candidate_removed = best_schedule[:i] + best_schedule[i+1:]

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

        current_fitness = multi_objective_fitness(current_schedule)
        best_schedule = current_schedule.copy()
        best_fitness = current_fitness

        T = self.temp0
        for iteration in range(self.iterations):
            if not group_keys:
                break

            group = random.choice(group_keys)
            valid_options = group_options.get(group, [])

            if len(valid_options) <= 1:
                continue

            new_schedule = [c for c in current_schedule if c.main_code != group]
            non_none_options = [opt for opt in valid_options if opt is not None]
            
            if not non_none_options:
                continue

            new_option = random.choice(non_none_options)
            new_schedule.extend(new_option)

            new_fitness = multi_objective_fitness(new_schedule)

            delta = new_fitness - current_fitness
            if delta < 0 or random.random() < math.exp(-delta / T):
                current_schedule = new_schedule
                current_fitness = new_fitness

                if current_fitness < best_fitness:
                    best_schedule = current_schedule.copy()
                    best_fitness = current_fitness

            T *= self.alpha

            if T < 1e-3:
                break

        return Schedule(best_schedule)
