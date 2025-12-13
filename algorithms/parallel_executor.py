"""Parallel execution helpers for schedulers."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import TYPE_CHECKING, Dict, Iterable, Optional, Sequence, Tuple, Type, Union

if TYPE_CHECKING:
    from core.models import CourseGroup, Schedule
    from utils.schedule_metrics import SchedulerPrefs

# Runtime imports
try:
    from core.models import CourseGroup, Schedule
except ImportError as e:
    raise ImportError(f"Required module core.models not found: {e}")

try:
    from utils.schedule_metrics import SchedulerPrefs
except ImportError as e:
    raise ImportError(f"Required module utils.schedule_metrics not found: {e}")

from . import get_registered_scheduler
from .base_scheduler import BaseScheduler


AlgorithmSpec = Union[str, Type[BaseScheduler]]


def _execute_algorithm(
    scheduler_cls: Type[BaseScheduler],
    course_groups: Dict[str, CourseGroup],
    mandatory_codes: set,
    optional_set: set,
    prefs: Optional[SchedulerPrefs],
    shared_kwargs: dict,
) -> Tuple[str, BaseScheduler, Optional[Schedule]]:
    """
    Execute a single algorithm in a separate process.

    This function is designed to be pickled and executed by ProcessPoolExecutor.

    Args:
        scheduler_cls: Scheduler class to instantiate
        course_groups: Course groups dictionary
        mandatory_codes: Set of mandatory course codes
        optional_set: Set of optional course codes
        prefs: Scheduler preferences
        shared_kwargs: Additional keyword arguments

    Returns:
        Tuple of (algorithm_name, scheduler_instance, best_schedule)
    """
    name = scheduler_cls.metadata.name if hasattr(scheduler_cls, "metadata") else scheduler_cls.__name__
    scheduler = scheduler_cls(scheduler_prefs=prefs, **shared_kwargs)

    try:
        schedules = scheduler.generate_schedules(
            course_groups,
            mandatory_codes,
            optional_set,
        )
        best_schedule = schedules[0] if schedules else None
    except Exception:  # pragma: no cover - defensive guard
        best_schedule = None

    return name, scheduler, best_schedule


def run_algorithms_parallel(
    algorithms: Iterable[AlgorithmSpec],
    course_groups: Dict[str, CourseGroup],
    mandatory_codes: Sequence[str],
    optional_codes: Optional[Sequence[str]] = None,
    prefs: Optional[SchedulerPrefs] = None,
    max_workers: int = 4,
    use_multiprocessing: bool = True,
    **shared_kwargs,
) -> Dict[str, Tuple[BaseScheduler, Optional[Schedule]]]:
    """
    Execute algorithms concurrently and return their best schedules.

    Args:
        algorithms: Algorithm specifications (names or classes)
        course_groups: Course groups to schedule
        mandatory_codes: Mandatory course codes
        optional_codes: Optional course codes
        prefs: Scheduler preferences
        max_workers: Maximum number of parallel workers
        use_multiprocessing: If True, uses ProcessPoolExecutor for true parallelism.
                           If False, uses ThreadPoolExecutor (for debugging).
        **shared_kwargs: Additional arguments passed to schedulers

    Returns:
        Dictionary mapping algorithm names to (scheduler, best_schedule) tuples
    """
    optional_set = set(optional_codes or [])
    mandatory_set = set(mandatory_codes)
    futures = {}

    # Choose executor based on use_multiprocessing flag
    executor_class = ProcessPoolExecutor if use_multiprocessing else __import__('concurrent.futures').futures.ThreadPoolExecutor

    with executor_class(max_workers=max_workers) as executor:
        for spec in algorithms:
            scheduler_cls = _resolve(spec)

            if use_multiprocessing:
                # For multiprocessing, use the helper function
                future = executor.submit(
                    _execute_algorithm,
                    scheduler_cls,
                    course_groups,
                    mandatory_set,
                    optional_set,
                    prefs,
                    shared_kwargs,
                )
                futures[future] = None  # Name will come from result
            else:
                # For threading, use the old approach
                name = scheduler_cls.metadata.name if hasattr(scheduler_cls, "metadata") else scheduler_cls.__name__
                scheduler = scheduler_cls(scheduler_prefs=prefs, **shared_kwargs)
                future = executor.submit(
                    scheduler.generate_schedules,
                    course_groups,
                    mandatory_set,
                    optional_set,
                )
                futures[future] = (name, scheduler)

        results: Dict[str, Tuple[BaseScheduler, Optional[Schedule]]] = {}
        for future in as_completed(futures):
            try:
                if use_multiprocessing:
                    name, scheduler, best_schedule = future.result()
                else:
                    name, scheduler = futures[future]
                    schedules = future.result()
                    best_schedule = schedules[0] if schedules else None
            except Exception:  # pragma: no cover - defensive guard
                if not use_multiprocessing:
                    name, scheduler = futures[future]
                    best_schedule = None
                else:
                    continue  # Skip failed multiprocessing tasks

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
