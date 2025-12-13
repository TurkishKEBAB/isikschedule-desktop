"""
Schedule metrics and scoring utilities for evaluating schedule quality.

This module provides functions for analyzing schedules and calculating various metrics:
- Day usage analysis (days used, free days)
- Slot analysis (weekly slots, daily slots, gaps)
- Compression metrics (consecutive blocks)
- Schedule scoring based on user preferences

These metrics are used for evaluating and comparing schedules based on
user-defined preferences like day compression and free day requirements.
"""
from typing import Dict, List, Optional, Any, NamedTuple
from dataclasses import dataclass, field
from functools import lru_cache
from core.models import Schedule


@dataclass
class SchedulerPrefs:
    """
    User preferences for schedule optimization.

    Attributes:
        compress_classes: Whether to compress classes into fewer days
        desired_free_days: List of days the user wants to keep free (e.g., ["Monday", "Friday"])
        strict_free_days: Whether desired free days must have zero classes (True) or allow quasi-free days (False)
        max_weekly_slots: Maximum number of weekly class slots allowed
        max_daily_slots: Maximum number of daily class slots allowed (optional)
        allow_conflicts: Whether to allow time conflicts between courses
        max_conflict_hours: Maximum hours of conflicts allowed (when allow_conflicts=True)
        course_type_priorities: Priority order for course types (lecture, ps, lab)
        weight_free_days: Weight for free day satisfaction in scoring (higher = more important)
        weight_compression: Weight for day compression in scoring (higher = more important)
        weight_gaps: Weight for minimizing gaps in scoring (higher = more important)
        weight_consecutive: Weight for maximizing consecutive blocks in scoring (higher = more important)
        weight_conflicts: Weight for penalizing conflicts in scoring (higher = more penalty)
    """
    compress_classes: bool = False
    desired_free_days: List[str] = field(default_factory=list)
    strict_free_days: bool = True
    max_weekly_slots: int = 60  # Default: essentially no limit
    max_daily_slots: Optional[int] = None
    allow_conflicts: bool = False
    max_conflict_hours: int = 0
    course_type_priorities: List[str] = field(default_factory=lambda: ["lecture", "ps", "lab"])
    weight_free_days: float = 1.0
    weight_compression: float = 1.0
    weight_gaps: float = 0.5
    weight_consecutive: float = 0.5
    weight_conflicts: float = 2.0


class ScheduleStats(NamedTuple):
    """
    Statistics about a schedule's usage pattern.

    Attributes:
        days_used: Number of days with classes
        total_slots: Total number of time slots occupied
        gaps_per_day: Dictionary mapping day names to number of gaps
        consecutive_blocks: Dictionary mapping day names to longest consecutive block
        free_days: List of completely free day names
        daily_slot_counts: Dictionary mapping day names to number of slots used
    """
    days_used: int
    total_slots: int
    gaps_per_day: Dict[str, int]
    consecutive_blocks: Dict[str, int]
    free_days: List[str]
    daily_slot_counts: Dict[str, int]


def compute_schedule_stats(schedule: Schedule) -> ScheduleStats:
    """
    Compute comprehensive statistics for a schedule.

    Args:
        schedule: Schedule to analyze

    Returns:
        ScheduleStats object with computed metrics
    """
    # Collect all time slots
    all_slots = []
    for course in schedule.courses:
        all_slots.extend(course.schedule)

    # Group by day
    day_slots = {}
    for day, slot in all_slots:
        if day not in day_slots:
            day_slots[day] = []
        day_slots[day].append(slot)

    # Sort slots for each day
    for day in day_slots:
        day_slots[day] = sorted(set(day_slots[day]))

    # Calculate metrics
    days_used = len(day_slots)
    total_slots = len(set(all_slots))

    # Calculate gaps and consecutive blocks for each day
    gaps_per_day = {}
    consecutive_blocks = {}
    daily_slot_counts = {}

    all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for day in all_days:
        slots = day_slots.get(day, [])
        daily_slot_counts[day] = len(slots)

        if len(slots) <= 1:
            gaps_per_day[day] = 0
            consecutive_blocks[day] = len(slots)
        else:
            # Count gaps
            gaps = 0
            for i in range(len(slots) - 1):
                if slots[i + 1] - slots[i] > 1:
                    gaps += 1
            gaps_per_day[day] = gaps

            # Find longest consecutive block
            max_block = 1
            current_block = 1
            for i in range(1, len(slots)):
                if slots[i] == slots[i - 1] + 1:
                    current_block += 1
                    max_block = max(max_block, current_block)
                else:
                    current_block = 1
            consecutive_blocks[day] = max_block

    # Find free days
    free_days = [day for day in all_days if day not in day_slots]

    return ScheduleStats(
        days_used=days_used,
        total_slots=total_slots,
        gaps_per_day=gaps_per_day,
        consecutive_blocks=consecutive_blocks,
        free_days=free_days,
        daily_slot_counts=daily_slot_counts
    )


def score_schedule(schedule: Schedule, prefs: SchedulerPrefs) -> float:
    """
    Calculate a comprehensive score for a schedule based on user preferences.

    Args:
        schedule: Schedule to score
        prefs: User preferences for scoring

    Returns:
        Score (higher is better)
    """
    stats = compute_schedule_stats(schedule)
    score = 0.0

    # Free days score
    score += _calculate_free_days_score(stats, prefs)

    # Day compression score
    if prefs.compress_classes:
        score += _calculate_compression_score(stats, prefs)

    # Gap minimization score
    score += _calculate_gap_score(stats, prefs)

    # Consecutive blocks score
    score += _calculate_consecutive_score(stats, prefs)

    # Conflict penalty
    score -= prefs.weight_conflicts * schedule.conflict_count * 10

    return score


def _calculate_free_days_score(stats: Any, prefs: SchedulerPrefs) -> float:
    """Calculate score contribution from free days."""
    if not prefs.desired_free_days:
        return 0.0

    achieved_free_days = set(stats.free_days)
    desired_free_days = set(prefs.desired_free_days)

    if prefs.strict_free_days:
        # Strict mode: only count perfectly free days
        free_day_satisfaction = len(achieved_free_days.intersection(desired_free_days)) / len(desired_free_days)
    else:
        # Quasi-free mode: count days with minimal classes as partially free
        quasi_free_days = set()
        for day in prefs.desired_free_days:
            if stats.daily_slot_counts.get(day, 0) <= 1:  # 0 or 1 class
                quasi_free_days.add(day)
        free_day_satisfaction = len(quasi_free_days) / len(desired_free_days)

    return prefs.weight_free_days * free_day_satisfaction * 100


def _calculate_compression_score(stats: Any, prefs: SchedulerPrefs) -> float:
    """Calculate score contribution from day compression."""
    max_days = 7
    compression_score = (max_days - stats.days_used) / max_days
    return prefs.weight_compression * compression_score * 100


def _calculate_gap_score(stats: Any, prefs: SchedulerPrefs) -> float:
    """Calculate score contribution from gap minimization."""
    total_gaps = sum(stats.gaps_per_day.values())
    max_possible_gaps = stats.total_slots  # Worst case: one gap between each class
    if max_possible_gaps > 0:
        gap_score = (max_possible_gaps - total_gaps) / max_possible_gaps
        return prefs.weight_gaps * gap_score * 100
    return 0.0


def _calculate_consecutive_score(stats: Any, prefs: SchedulerPrefs) -> float:
    """Calculate score contribution from consecutive blocks."""
    total_consecutive = sum(stats.consecutive_blocks.values())
    max_possible_consecutive = stats.total_slots  # Best case: all classes consecutive
    if max_possible_consecutive > 0:
        consecutive_score = total_consecutive / max_possible_consecutive
        return prefs.weight_consecutive * consecutive_score * 100
    return 0.0


def meets_weekly_hours_constraint(schedule: Schedule, max_weekly_slots: int) -> bool:
    """
    Check if schedule meets weekly hours constraint.

    Args:
        schedule: Schedule to check
        max_weekly_slots: Maximum allowed weekly slots

    Returns:
        True if constraint is satisfied
    """
    stats = compute_schedule_stats(schedule)
    return stats.total_slots <= max_weekly_slots


def meets_daily_hours_constraint(schedule: Schedule, max_daily_slots: int) -> bool:
    """
    Check if schedule meets daily hours constraint.

    Args:
        schedule: Schedule to check
        max_daily_slots: Maximum allowed daily slots

    Returns:
        True if constraint is satisfied
    """
    stats = compute_schedule_stats(schedule)
    return all(count <= max_daily_slots for count in stats.daily_slot_counts.values())


def meets_free_day_constraint(schedule: Schedule, desired_free_days: List[str], strict: bool = True) -> bool:
    """
    Check if schedule meets free day constraint.

    Args:
        schedule: Schedule to check
        desired_free_days: List of desired free days (e.g., ["Monday", "Friday"])
        strict: Whether to enforce strict free days (no classes) or allow quasi-free days

    Returns:
        True if constraint is satisfied
    """
    stats = compute_schedule_stats(schedule)

    if strict:
        # Strict mode: desired days must be completely free
        achieved_free_days = set(stats.free_days)
        desired_set = set(desired_free_days)
        return desired_set.issubset(achieved_free_days)
    else:
        # Quasi-free mode: desired days can have at most 1 class
        for day in desired_free_days:
            if stats.daily_slot_counts.get(day, 0) > 1:
                return False
        return True


def analyze_schedule_efficiency(schedule: Schedule) -> Dict[str, Any]:
    """
    Analyze schedule efficiency and provide detailed metrics.

    Args:
        schedule: Schedule to analyze

    Returns:
        Dictionary with efficiency metrics
    """
    stats = compute_schedule_stats(schedule)

    # Calculate efficiency metrics
    total_gaps = sum(stats.gaps_per_day.values())
    avg_gaps_per_active_day = total_gaps / max(stats.days_used, 1)

    # Calculate day utilization
    active_days = [day for day, count in stats.daily_slot_counts.items() if count > 0]
    day_utilization = {}
    for day in active_days:
        slots = stats.daily_slot_counts[day]
        max_consecutive = stats.consecutive_blocks[day]
        gaps = stats.gaps_per_day[day]

        # Efficiency = consecutive blocks / total slots (higher is better)
        efficiency = max_consecutive / slots if slots > 0 else 0
        day_utilization[day] = {
            "slots": slots,
            "consecutive": max_consecutive,
            "gaps": gaps,
            "efficiency": efficiency
        }

    # Overall efficiency score
    total_consecutive = sum(stats.consecutive_blocks.values())
    overall_efficiency = total_consecutive / max(stats.total_slots, 1)

    return {
        "total_slots": stats.total_slots,
        "days_used": stats.days_used,
        "free_days": stats.free_days,
        "total_gaps": total_gaps,
        "avg_gaps_per_day": avg_gaps_per_active_day,
        "overall_efficiency": overall_efficiency,
        "day_utilization": day_utilization,
        "schedule_compactness": stats.days_used / 7,  # Lower is more compact
        "credits_per_day": schedule.total_credits / max(stats.days_used, 1)
    }


def compare_schedules(schedule1: Schedule, schedule2: Schedule, prefs: SchedulerPrefs) -> Dict[str, Any]:
    """
    Compare two schedules based on various metrics.

    Args:
        schedule1: First schedule
        schedule2: Second schedule
        prefs: User preferences for scoring

    Returns:
        Dictionary with comparison results
    """
    score1 = score_schedule(schedule1, prefs)
    score2 = score_schedule(schedule2, prefs)

    stats1 = compute_schedule_stats(schedule1)
    stats2 = compute_schedule_stats(schedule2)

    return {
        "better_schedule": 1 if score1 > score2 else 2,
        "score_difference": abs(score1 - score2),
        "schedule1": {
            "score": score1,
            "credits": schedule1.total_credits,
            "conflicts": schedule1.conflict_count,
            "days_used": stats1.days_used,
            "total_gaps": sum(stats1.gaps_per_day.values())
        },
        "schedule2": {
            "score": score2,
            "credits": schedule2.total_credits,
            "conflicts": schedule2.conflict_count,
            "days_used": stats2.days_used,
            "total_gaps": sum(stats2.gaps_per_day.values())
        }
    }
