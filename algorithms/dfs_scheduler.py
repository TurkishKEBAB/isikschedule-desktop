"""
Depth-First Search scheduler implementation.

This module provides a comprehensive DFS-based scheduling algorithm that systematically
explores all possible course combinations to find valid schedules while respecting
constraints and user preferences.
"""
from typing import List, Dict, Set, Optional, Any
import logging
import time
from collections import defaultdict

from core.models import Course, Schedule, CourseGroup
from algorithms.constraints import ConstraintUtils
from utils.schedule_metrics import SchedulerPrefs, score_schedule

# Set up logging
logger = logging.getLogger(__name__)


class DFSScheduler:
    """
    Advanced Depth-First Search scheduler for generating course schedules.

    This scheduler uses a systematic DFS approach to explore all possible
    combinations of course selections while respecting constraints and
    optimizing for user preferences.

    Features:
    - Constraint-aware scheduling
    - User preference optimization
    - Early pruning for efficiency
    - Conflict detection and handling
    - Progress tracking and statistics
    """

    def __init__(self,
                 max_results: int = 10,
                 max_ects: int = 31,
                 allow_conflicts: bool = False,
                 scheduler_prefs: Optional[SchedulerPrefs] = None,
                 timeout_seconds: int = 300):
        """
        Initialize the DFS scheduler.

        Args:
            max_results: Maximum number of schedules to generate
            max_ects: Maximum ECTS credits allowed
            allow_conflicts: Whether to allow schedule conflicts
            scheduler_prefs: Advanced scheduler preferences for optimization
            timeout_seconds: Maximum time to spend searching (in seconds)
        """
        self.max_results = max_results
        self.max_ects = max_ects
        self.allow_conflicts = allow_conflicts
        self.scheduler_prefs = scheduler_prefs or SchedulerPrefs()
        self.timeout_seconds = timeout_seconds

        # Internal state
        self.results = []
        self.start_time = 0
        self.nodes_explored = 0
        self.pruned_branches = 0
        self.best_score = float('-inf')
        self.search_statistics = {}

    def generate_schedules(self,
                          course_groups: Dict[str, CourseGroup],
                          mandatory_codes: Set[str],
                          optional_codes: Optional[Set[str]] = None) -> List[Schedule]:
        """
        Generate schedules using depth-first search.

        Args:
            course_groups: Dictionary mapping main codes to CourseGroup objects
            mandatory_codes: Set of mandatory course codes
            optional_codes: Set of optional course codes (if None, all non-mandatory are optional)

        Returns:
            List of valid Schedule objects sorted by quality
        """
        logger.info(f"Starting DFS scheduling with {len(course_groups)} course groups")
        logger.info(f"Mandatory courses: {len(mandatory_codes)}, Max results: {self.max_results}")

        self.start_time = time.time()
        self.results = []
        self.nodes_explored = 0
        self.pruned_branches = 0
        self.best_score = float('-inf')

        # Validate input
        if not course_groups:
            logger.warning("No course groups provided")
            return []

        if not mandatory_codes:
            logger.warning("No mandatory courses specified")
            return []

        # Build group options with constraints
        group_valid_selections, group_options = ConstraintUtils.build_group_options(
            course_groups, mandatory_codes, "sections"
        )

        # Validate mandatory courses have valid selections
        invalid_mandatory = []
        for code in mandatory_codes:
            if not group_valid_selections.get(code):
                invalid_mandatory.append(code)

        if invalid_mandatory:
            logger.error(f"Invalid mandatory courses (no valid selections): {invalid_mandatory}")
            return []

        # Prepare search parameters
        all_group_keys = list(course_groups.keys())
        mandatory_keys = [key for key in all_group_keys if key in mandatory_codes]
        optional_keys = [key for key in all_group_keys if key not in mandatory_codes]

        # Sort groups by complexity (fewer options first for better pruning)
        mandatory_keys.sort(key=lambda k: len(group_options.get(k, [])))
        optional_keys.sort(key=lambda k: len(group_options.get(k, [])))

        # Combine with mandatory first for better early constraint checking
        search_order = mandatory_keys + optional_keys

        logger.info(f"Search order: {len(mandatory_keys)} mandatory + {len(optional_keys)} optional")

        # Start DFS search
        self._dfs_search(
            search_order,
            group_options,
            group_valid_selections,
            mandatory_codes,
            [],  # current_courses
            0,   # current_ects
            0    # group_index
        )

        # Calculate search statistics
        elapsed_time = time.time() - self.start_time
        self.search_statistics = {
            "total_time": elapsed_time,
            "nodes_explored": self.nodes_explored,
            "pruned_branches": self.pruned_branches,
            "schedules_found": len(self.results),
            "best_score": self.best_score if self.results else 0,
            "timeout_reached": elapsed_time >= self.timeout_seconds
        }

        logger.info(f"DFS search completed in {elapsed_time:.2f}s")
        logger.info(f"Explored {self.nodes_explored} nodes, pruned {self.pruned_branches} branches")
        logger.info(f"Found {len(self.results)} valid schedules")

        # Sort results by quality
        if self.scheduler_prefs and self.results:
            self.results.sort(key=lambda s: score_schedule(s, self.scheduler_prefs), reverse=True)
        else:
            # Default sorting: least conflicts, then highest credits
            self.results.sort(key=lambda s: (s.conflict_count, -s.total_credits))

        return self.results

    def _dfs_search(self,
                   group_keys: List[str],
                   group_options: Dict[str, List[Optional[List[Course]]]],
                   group_valid_selections: Dict[str, List[List[Course]]],
                   mandatory_codes: Set[str],
                   current_courses: List[Course],
                   current_ects: int,
                   group_index: int) -> None:
        """
        Recursive depth-first search implementation.

        Args:
            group_keys: Ordered list of course group keys to process
            group_options: Dictionary of available options for each group
            group_valid_selections: Dictionary of valid selections for each group
            mandatory_codes: Set of mandatory course codes
            current_courses: Current course selection
            current_ects: Current total ECTS
            group_index: Current group being processed
        """
        self.nodes_explored += 1

        # Check timeout
        if time.time() - self.start_time >= self.timeout_seconds:
            logger.warning("DFS search timeout reached")
            return

        # Base case: processed all groups
        if group_index >= len(group_keys):
            if current_courses:  # Only add non-empty schedules
                schedule = Schedule(current_courses.copy())

                # Validate and score the schedule
                if self._is_valid_final_schedule(schedule, current_ects, mandatory_codes):
                    self._add_schedule_if_good(schedule)
            return

        # Early termination if we have enough good results
        if len(self.results) >= self.max_results:
            return

        # Get current group
        group_key = group_keys[group_index]
        options = group_options.get(group_key, [])

        # Try each option for this group
        for option in options:
            # Check if we should prune this branch
            if self._should_prune_branch(option, current_courses, current_ects, group_key, mandatory_codes):
                self.pruned_branches += 1
                continue

            if option is None:
                # Skip this group (don't take any courses from it)
                # Only allowed if not mandatory
                if group_key not in mandatory_codes:
                    self._dfs_search(
                        group_keys, group_options, group_valid_selections,
                        mandatory_codes, current_courses, current_ects, group_index + 1
                    )
            else:
                # Try this course selection
                new_courses = current_courses + option
                new_ects = current_ects + sum(course.ects for course in option)

                # Continue search with this selection
                self._dfs_search(
                    group_keys, group_options, group_valid_selections,
                    mandatory_codes, new_courses, new_ects, group_index + 1
                )

    def _should_prune_branch(self,
                           option: Optional[List[Course]],
                           current_courses: List[Course],
                           current_ects: int,
                           group_key: str,
                           mandatory_codes: Set[str]) -> bool:
        """
        Determine if a branch should be pruned for efficiency.

        Args:
            option: Current option being considered
            current_courses: Current course selection
            current_ects: Current ECTS total
            group_key: Current group key
            mandatory_codes: Set of mandatory codes

        Returns:
            True if branch should be pruned
        """
        if option is None:
            # Pruning for skipping mandatory courses
            return group_key in mandatory_codes

        # Calculate new ECTS total
        new_ects = current_ects + sum(course.ects for course in option)

        # Prune if ECTS limit exceeded
        if new_ects > self.max_ects:
            return True

        # Check conflicts based on allow_conflicts setting
        temp_schedule = Schedule(current_courses + option)

        if not self.allow_conflicts:
            # Strict mode: no conflicts allowed
            if temp_schedule.conflict_count > 0:
                return True
        else:
            # Allow conflicts but check if within limits
            if self.scheduler_prefs.max_conflict_hours > 0:
                if temp_schedule.conflict_count > self.scheduler_prefs.max_conflict_hours:
                    return True

        # Advanced pruning based on preferences
        if self.scheduler_prefs:
            # Prune if hard constraints violated
            if self.scheduler_prefs.max_weekly_slots < 60:  # 60 is effectively no limit
                if len(set((day, slot) for course in temp_schedule.courses for day, slot in course.schedule)) > self.scheduler_prefs.max_weekly_slots:
                    return True

            if self.scheduler_prefs.max_daily_slots:
                # Check daily slot limits
                daily_slots = defaultdict(set)
                for course in temp_schedule.courses:
                    for day, slot in course.schedule:
                        daily_slots[day].add(slot)

                if any(len(slots) > self.scheduler_prefs.max_daily_slots for slots in daily_slots.values()):
                    return True

        return False

    def _is_valid_final_schedule(self,
                               schedule: Schedule,
                               ects: int,
                               mandatory_codes: Set[str]) -> bool:
        """
        Check if a complete schedule is valid.

        Args:
            schedule: Schedule to validate
            ects: Total ECTS credits
            mandatory_codes: Set of mandatory course codes

        Returns:
            True if schedule is valid
        """
        # Check ECTS limit
        if ects > self.max_ects:
            return False

        # Check if all mandatory courses are included
        included_main_codes = set(course.main_code for course in schedule.courses)
        if not mandatory_codes.issubset(included_main_codes):
            return False

        # Check conflicts if not allowed
        if not self.allow_conflicts and schedule.conflict_count > 0:
            return False

        # Advanced validation based on preferences
        if self.scheduler_prefs:
            # Check strict free day constraints
            if (self.scheduler_prefs.strict_free_days and
                self.scheduler_prefs.desired_free_days):

                from utils.schedule_metrics import meets_free_day_constraint
                if not meets_free_day_constraint(
                    schedule,
                    self.scheduler_prefs.desired_free_days,
                    strict=True
                ):
                    return False

        return True

    def _add_schedule_if_good(self, schedule: Schedule) -> None:
        """
        Add a schedule to results if it's good enough.

        Args:
            schedule: Schedule to potentially add
        """
        # Calculate score if preferences are set
        if self.scheduler_prefs:
            current_score = score_schedule(schedule, self.scheduler_prefs)

            # Update best score
            if current_score > self.best_score:
                self.best_score = current_score

            # Only add if score is reasonable (above a threshold)
            # This helps filter out poor quality schedules
            if len(self.results) >= self.max_results:
                # Replace worst schedule if this one is better
                worst_schedule = min(self.results, key=lambda s: score_schedule(s, self.scheduler_prefs))
                worst_score = score_schedule(worst_schedule, self.scheduler_prefs)

                if current_score > worst_score:
                    self.results.remove(worst_schedule)
                    self.results.append(schedule)
            else:
                self.results.append(schedule)
        else:
            # Default behavior: add if under limit
            if len(self.results) < self.max_results:
                self.results.append(schedule)
            else:
                # Replace schedule with more conflicts or fewer credits
                worst_schedule = max(self.results, key=lambda s: (s.conflict_count, -s.total_credits))
                if (schedule.conflict_count < worst_schedule.conflict_count or
                    (schedule.conflict_count == worst_schedule.conflict_count and
                     schedule.total_credits > worst_schedule.total_credits)):
                    self.results.remove(worst_schedule)
                    self.results.append(schedule)

    def get_search_statistics(self) -> Dict[str, Any]:
        """
        Get detailed statistics about the search process.

        Returns:
            Dictionary with search statistics
        """
        return self.search_statistics.copy()

    def get_optimization_report(self) -> Dict[str, Any]:
        """
        Generate a detailed optimization report.

        Returns:
            Dictionary with optimization analysis
        """
        if not self.results:
            return {"status": "No schedules generated"}

        # Analyze results
        total_credits = [s.total_credits for s in self.results]
        conflict_counts = [s.conflict_count for s in self.results]

        report = {
            "total_schedules": len(self.results),
            "search_statistics": self.get_search_statistics(),
            "credit_analysis": {
                "min_credits": min(total_credits),
                "max_credits": max(total_credits),
                "avg_credits": sum(total_credits) / len(total_credits),
                "target_credits": self.max_ects
            },
            "conflict_analysis": {
                "conflict_free_schedules": sum(1 for count in conflict_counts if count == 0),
                "min_conflicts": min(conflict_counts),
                "max_conflicts": max(conflict_counts),
                "avg_conflicts": sum(conflict_counts) / len(conflict_counts)
            }
        }

        # Add preference-based analysis if available
        if self.scheduler_prefs:
            scores = [score_schedule(s, self.scheduler_prefs) for s in self.results]
            report["score_analysis"] = {
                "best_score": max(scores),
                "worst_score": min(scores),
                "avg_score": sum(scores) / len(scores),
                "score_range": max(scores) - min(scores)
            }

        return report

    def analyze_schedule_failure(self,
                                course_groups: Dict[str, CourseGroup],
                                mandatory_codes: Set[str]) -> List[str]:
        """
        Analyze why schedule generation might have failed.

        Args:
            course_groups: Dictionary of course groups
            mandatory_codes: Set of mandatory course codes

        Returns:
            List of potential failure reasons
        """
        reasons = []

        # Check for invalid mandatory courses
        for code in mandatory_codes:
            if code not in course_groups:
                reasons.append(f"Mandatory course '{code}' not found in available courses")
                continue

            group = course_groups[code]
            if not group.lecture_courses:
                reasons.append(f"Mandatory course '{code}' has no lecture sections")

        # Check total minimum ECTS
        min_total_ects = sum(
            min(course.ects for course in course_groups[code].lecture_courses)
            for code in mandatory_codes
            if code in course_groups and course_groups[code].lecture_courses
        )

        if min_total_ects > self.max_ects:
            reasons.append(f"Minimum required ECTS ({min_total_ects}) exceeds limit ({self.max_ects})")

        # Check for constraint conflicts
        if self.scheduler_prefs:
            if self.scheduler_prefs.max_weekly_slots < len(mandatory_codes) * 2:
                reasons.append("Weekly hour limit too restrictive for mandatory courses")

        # Check timeout issues
        if self.search_statistics.get("timeout_reached"):
            reasons.append("Search timeout reached - try increasing time limit or reducing course options")

        if not reasons:
            reasons.append("Unknown scheduling failure - check course data and constraints")

        return reasons
