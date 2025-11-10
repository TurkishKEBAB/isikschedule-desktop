"""Parallel execution helpers for schedulers."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Iterable, Optional, Sequence, Tuple, Type, Union

from core.models import CourseGroup, Schedule
from utils.schedule_metrics import SchedulerPrefs
from . import get_registered_scheduler
from .base_scheduler import BaseScheduler


AlgorithmSpec = Union[str, Type[BaseScheduler]]


def run_algorithms_parallel(
    algorithms: Iterable[AlgorithmSpec],
    course_groups: Dict[str, CourseGroup],
    mandatory_codes: Sequence[str],
    optional_codes: Optional[Sequence[str]] = None,
    prefs: Optional[SchedulerPrefs] = None,
    max_workers: int = 4,
    **shared_kwargs,
) -> Dict[str, Tuple[BaseScheduler, Optional[Schedule]]]:
    """Execute algorithms concurrently and return their best schedules."""

    optional_set = set(optional_codes or [])
    futures = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for spec in algorithms:
            scheduler_cls = _resolve(spec)
            name = scheduler_cls.metadata.name if hasattr(scheduler_cls, "metadata") else scheduler_cls.__name__
            scheduler = scheduler_cls(scheduler_prefs=prefs, **shared_kwargs)
            future = executor.submit(
                scheduler.generate_schedules,
                course_groups,
                set(mandatory_codes),
                optional_set,
            )
            futures[future] = (name, scheduler)

        results: Dict[str, Tuple[BaseScheduler, Optional[Schedule]]] = {}
        for future in as_completed(futures):
            name, scheduler = futures[future]
            try:
                schedules = future.result()
                best_schedule = schedules[0] if schedules else None
            except Exception:  # pragma: no cover - defensive guard
                best_schedule = None
            results[name] = (scheduler, best_schedule)

    return results


def _resolve(spec: AlgorithmSpec) -> Type[BaseScheduler]:
    if isinstance(spec, str):
        cls = get_registered_scheduler(spec)
        if cls is None:
            raise ValueError(f"Unknown algorithm '{spec}'")
        return cls
    return spec


__all__ = ["run_algorithms_parallel"]
