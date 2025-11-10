"""Benchmark utilities for comparing scheduling algorithms."""

from __future__ import annotations

import time
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Type, Union

from core.models import CourseGroup, Schedule
from utils.schedule_metrics import SchedulerPrefs
from . import get_registered_scheduler
from .base_scheduler import BaseScheduler
from .evaluator import evaluate_schedule


AlgorithmSpec = Union[str, Type[BaseScheduler]]


class AlgorithmBenchmark:
    """Execute multiple algorithms on identical input data and collect metrics."""

    def __init__(
        self,
        course_groups: Dict[str, CourseGroup],
        mandatory_codes: Sequence[str],
        optional_codes: Optional[Sequence[str]] = None,
        prefs: Optional[SchedulerPrefs] = None,
    ) -> None:
        self.course_groups = course_groups
        self.mandatory_codes = set(mandatory_codes)
        self.optional_codes = set(optional_codes or [])
        self.prefs = prefs

    def run(
        self,
        algorithms: Iterable[AlgorithmSpec],
        per_algorithm_kwargs: Optional[Dict[str, Dict]] = None,
    ) -> Dict[str, Dict[str, float]]:
        per_algorithm_kwargs = per_algorithm_kwargs or {}
        summary: Dict[str, Dict[str, float]] = {}

        for spec in algorithms:
            scheduler_cls = self._resolve_spec(spec)
            name = scheduler_cls.metadata.name if hasattr(scheduler_cls, "metadata") else scheduler_cls.__name__

            kwargs = per_algorithm_kwargs.get(name, {})
            scheduler = scheduler_cls(scheduler_prefs=self.prefs, **kwargs)

            start = time.perf_counter()
            schedules = scheduler.generate_schedules(
                self.course_groups,
                self.mandatory_codes,
                optional_codes=self.optional_codes,
            )
            duration = time.perf_counter() - start

            evaluation = {}
            if schedules:
                evaluation = evaluate_schedule(schedules[0], self.prefs)

            summary[name] = {
                "duration": duration,
                "results": len(schedules),
                "best_conflicts": evaluation.get("conflicts", 0.0),
                "best_score": evaluation.get("score", 0.0),
            }

        return summary

    def _resolve_spec(self, spec: AlgorithmSpec) -> Type[BaseScheduler]:
        if isinstance(spec, str):
            cls = get_registered_scheduler(spec)
            if cls is None:
                raise ValueError(f"Unknown algorithm: {spec}")
            return cls
        return spec


__all__ = ["AlgorithmBenchmark"]
