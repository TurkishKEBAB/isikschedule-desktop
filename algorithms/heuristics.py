"""Reusable heuristic helpers for scheduling algorithms."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List, Optional, Tuple

if TYPE_CHECKING:
    from core.models import Course, Schedule
    from utils.schedule_metrics import SchedulerPrefs

# Runtime imports
try:
    from core.models import Course, Schedule
except ImportError as e:
    raise ImportError(f"Required module core.models not found: {e}")

try:
    from utils.schedule_metrics import SchedulerPrefs, compute_schedule_stats, score_schedule
except ImportError as e:
    raise ImportError(f"Required module utils.schedule_metrics not found: {e}")


def estimate_conflict_penalty(schedule: Schedule) -> float:
    """Return a coarse penalty based on conflicts and day dispersion."""

    stats = compute_schedule_stats(schedule)
    conflict_penalty = schedule.conflict_count * 100
    gap_penalty = sum(stats.gaps_per_day.values()) * 10
    spread_penalty = stats.days_used * 5
    return conflict_penalty + gap_penalty + spread_penalty


def estimate_remaining_group_penalty(remaining_groups: int) -> float:
    """Lightweight heuristic for the remaining depth of the search tree."""

    return remaining_groups * 25.0


def estimate_schedule_density(schedule: Schedule) -> float:
    """Lower values indicate a compact schedule; higher means sparse."""

    stats = compute_schedule_stats(schedule)
    if stats.total_slots == 0:
        return 0.0
    return stats.days_used / stats.total_slots


def option_signature(option: Optional[List[Course]]) -> Tuple[str, ...]:
    """Create a stable signature for a course selection option."""

    if option is None:
        return ("∅",)
    return tuple(sorted(course.code for course in option))


def rank_options_by_score(
    options: Iterable[Optional[List[Course]]],
    current_courses: List[Course],
    prefs: Optional[SchedulerPrefs] = None,
) -> List[Optional[List[Course]]]:
    """Return options sorted by their immediate impact on the schedule."""

    ranked: List[Tuple[float, Optional[List[Course]]]] = []
    for option in options:
        if option is None:
            ranked.append((50.0, None))
            continue

        tentative = Schedule(current_courses + option)
        if prefs:
            score = -score_schedule(tentative, prefs)
        else:
            score = estimate_conflict_penalty(tentative)
        ranked.append((score, option))

    ranked.sort(key=lambda item: item[0])
    return [option for _, option in ranked]


__all__ = [
    "estimate_conflict_penalty",
    "estimate_remaining_group_penalty",
    "estimate_schedule_density",
    "option_signature",
    "rank_options_by_score",
]
