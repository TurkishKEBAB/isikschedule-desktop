"""Performance monitoring and logging utilities."""

from __future__ import annotations

import functools
import logging
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor and log performance metrics."""

    @staticmethod
    def measure_time(func: Callable) -> Callable:
        """
        Decorator to measure and log function execution time.

        Usage:
            @PerformanceMonitor.measure_time
            def my_function():
                ...
        """
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                duration = end_time - start_time
                logger.info(
                    f"⏱️ {func.__module__}.{func.__name__} took {duration:.4f}s"
                )
        return wrapper

    @staticmethod
    def measure_time_verbose(operation_name: str) -> Callable:
        """
        Decorator to measure time with custom operation name.

        Usage:
            @PerformanceMonitor.measure_time_verbose("Loading courses")
            def load_courses():
                ...
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.perf_counter()
                logger.info(f"🚀 Starting: {operation_name}")
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.perf_counter()
                    duration = end_time - start_time
                    logger.info(
                        f"✅ Completed: {operation_name} in {duration:.4f}s"
                    )
            return wrapper
        return decorator


class PerformanceTimer:
    """Context manager for timing code blocks."""

    def __init__(self, operation_name: str, log_level: int = logging.INFO):
        """
        Initialize timer.

        Args:
            operation_name: Name of the operation being timed
            log_level: Logging level to use
        """
        self.operation_name = operation_name
        self.log_level = log_level
        self.start_time: float = 0
        self.duration: float = 0

    def __enter__(self) -> PerformanceTimer:
        """Start timer."""
        logger.log(self.log_level, f"🚀 Starting: {self.operation_name}")
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Stop timer and log duration."""
        self.duration = time.perf_counter() - self.start_time
        
        if exc_type is None:
            logger.log(
                self.log_level,
                f"✅ Completed: {self.operation_name} in {self.duration:.4f}s"
            )
        else:
            logger.log(
                self.log_level,
                f"❌ Failed: {self.operation_name} after {self.duration:.4f}s"
            )


class AlgorithmMetrics:
    """Track and log algorithm performance metrics."""

    @staticmethod
    def log_algorithm_start(algorithm_name: str, params: dict) -> None:
        """Log algorithm start with parameters."""
        params_str = ", ".join(f"{k}={v}" for k, v in params.items())
        logger.info(f"🧮 Starting algorithm: {algorithm_name} ({params_str})")

    @staticmethod
    def log_algorithm_result(
        algorithm_name: str,
        duration: float,
        schedules_found: int,
        best_ects: int,
        min_conflicts: int,
    ) -> None:
        """Log algorithm execution results."""
        logger.info(
            f"✅ {algorithm_name} completed in {duration:.2f}s: "
            f"found {schedules_found} schedules, "
            f"best ECTS={best_ects}, "
            f"min conflicts={min_conflicts}"
        )

    @staticmethod
    def log_algorithm_failure(algorithm_name: str, duration: float, error: str) -> None:
        """Log algorithm execution failure."""
        logger.error(
            f"❌ {algorithm_name} failed after {duration:.2f}s: {error}"
        )


__all__ = ["PerformanceMonitor", "PerformanceTimer", "AlgorithmMetrics"]
