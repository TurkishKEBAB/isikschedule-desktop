"""Algorithm recommendation utilities."""

from __future__ import annotations

from typing import Any, Dict, Optional, Type

from . import iter_registered_schedulers
from .base_scheduler import AlgorithmMetadata, BaseScheduler


def score_algorithm(metadata: AlgorithmMetadata, requirements: Dict[str, Any]) -> float:
    """
    Score an algorithm based on how well it matches the given requirements.

    Args:
        metadata: Algorithm metadata to evaluate
        requirements: Dictionary of requirements to match

    Returns:
        Numeric score (higher is better)
    """
    score = 0.0

    if requirements.get("optimal"):
        score += 10 if metadata.optimal else -5

    target_category = requirements.get("category")
    if target_category and metadata.category == target_category:
        score += 4

    if requirements.get("needs_preferences") and metadata.supports_preferences:
        score += 2

    if requirements.get("allow_parallel") and metadata.supports_parallel:
        score += 1

    if requirements.get("optimizer") and metadata.is_optimizer:
        score += 3
    elif requirements.get("optimizer") and not metadata.is_optimizer:
        score -= 3

    return score


def select_scheduler(requirements: Optional[Dict[str, Any]] = None) -> Type[BaseScheduler]:
    """
    Pick the most suitable scheduler based on metadata heuristics.

    Args:
        requirements: Optional dictionary of requirements. Keys may include:
            - optimal: bool - prefer optimal algorithms
            - category: str - prefer specific algorithm category
            - needs_preferences: bool - require preference support
            - allow_parallel: bool - prefer parallel algorithms
            - optimizer: bool - prefer optimizer-type algorithms

    Returns:
        A scheduler class that best matches the requirements
    """
    requirements = requirements or {}
    best_score = float("-inf")
    best_cls: Optional[Type[BaseScheduler]] = None

    for scheduler_cls in iter_registered_schedulers():
        metadata = getattr(scheduler_cls, "metadata", None)
        if not isinstance(metadata, AlgorithmMetadata):
            continue

        score = score_algorithm(metadata, requirements)
        if score > best_score:
            best_score = score
            best_cls = scheduler_cls

    return best_cls or _default_scheduler()


def _default_scheduler() -> Type[BaseScheduler]:
    from .dfs_scheduler import DFSScheduler

    return DFSScheduler


def instantiate_scheduler(
    requirements: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> BaseScheduler:
    scheduler_cls = select_scheduler(requirements)
    return scheduler_cls(**kwargs)


__all__ = ["instantiate_scheduler", "select_scheduler"]
