"""Helpers for scoring and comparing scheduler outputs."""

from __future__ import annotations

from statistics import mean
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional

if TYPE_CHECKING:
    from core.models import Schedule
    from utils.schedule_metrics import SchedulerPrefs

# Runtime imports
try:
    from core.models import Schedule
except ImportError as e:
    raise ImportError(f"Required module core.models not found: {e}")

try:
    from utils.schedule_metrics import (
        SchedulerPrefs,
        analyze_schedule_efficiency,
        compute_schedule_stats,
        score_schedule,
    )
except ImportError as e:
    raise ImportError(f"Required module utils.schedule_metrics not found: {e}")


def evaluate_schedule(schedule: Schedule, prefs: Optional[SchedulerPrefs] = None) -> Dict[str, float]:
    """Return key metrics for a single schedule."""

    stats = compute_schedule_stats(schedule)
    efficiency = analyze_schedule_efficiency(schedule)
    score = score_schedule(schedule, prefs) if prefs else None

    return {
        "score": score if score is not None else 0.0,
        "credits": schedule.total_credits,
        "conflicts": schedule.conflict_count,
        "days_used": stats.days_used,
        "overall_efficiency": efficiency["overall_efficiency"],
        "total_gaps": efficiency["total_gaps"],
    }


def summarize_schedules(
    schedules: Iterable[Schedule], prefs: Optional[SchedulerPrefs] = None
) -> Dict[str, float]:
    """Aggregate metrics across multiple schedules."""

    schedules = list(schedules)
    if not schedules:
        return {
            "total": 0,
            "best_score": 0.0,
            "avg_score": 0.0,
            "avg_conflicts": 0.0,
            "avg_credits": 0.0,
        }

    evaluations = [evaluate_schedule(schedule, prefs) for schedule in schedules]
    scores = [item["score"] for item in evaluations]
    conflicts = [item["conflicts"] for item in evaluations]
    credit_values = [item["credits"] for item in evaluations]

    return {
        "total": len(schedules),
        "best_score": max(scores),
        "avg_score": mean(scores) if scores else 0.0,
        "avg_conflicts": mean(conflicts) if conflicts else 0.0,
        "avg_credits": mean(credit_values) if credit_values else 0.0,
    }


def compare_algorithm_outputs(
    results: Dict[str, List[Schedule]], prefs: Optional[SchedulerPrefs] = None
) -> Dict[str, Dict[str, float]]:
    """Compare multiple algorithms' outputs using the same metrics."""

    comparison: Dict[str, Dict[str, float]] = {}
    for algo_name, schedules in results.items():
        comparison[algo_name] = summarize_schedules(schedules, prefs)
    return comparison


__all__ = [
    "compare_algorithm_outputs",
    "evaluate_schedule",
    "summarize_schedules",
]
