"""Scheduling algorithms package for SchedularV3.

Exposes a lightweight registry so algorithms can advertise themselves and be
retrieved dynamically by the benchmarking and auto-selection utilities.
"""

from __future__ import annotations

from typing import Dict, Iterable, Optional, Type

from .base_scheduler import AlgorithmMetadata, BaseScheduler


_ALGORITHM_REGISTRY: Dict[str, Type[BaseScheduler]] = {}


def register_scheduler(cls: Type[BaseScheduler]) -> Type[BaseScheduler]:
	"""Class decorator used by scheduler implementations to self-register."""

	metadata = getattr(cls, "metadata", None)
	if not isinstance(metadata, AlgorithmMetadata):
		raise ValueError(
			f"Scheduler {cls.__name__} must define 'metadata' of type AlgorithmMetadata"
		)

	_ALGORITHM_REGISTRY[metadata.name] = cls
	return cls


def get_registered_scheduler(name: str) -> Optional[Type[BaseScheduler]]:
	"""Return the scheduler class associated with the given name."""

	return _ALGORITHM_REGISTRY.get(name)


def iter_registered_schedulers() -> Iterable[Type[BaseScheduler]]:
	"""Yield all registered scheduler classes."""

	return _ALGORITHM_REGISTRY.values()


__all__ = [
	"AlgorithmMetadata",
	"BaseScheduler",
	"get_registered_scheduler",
	"iter_registered_schedulers",
	"register_scheduler",
]


# Eagerly import core algorithms so they self-register with the registry.
from . import (  # noqa: E402,F401
	a_star_scheduler,
	bfs_scheduler,
	constraint_programming,
	dfs_scheduler,
	dijkstra_scheduler,
	genetic_algorithm,
	greedy_scheduler,
	hill_climbing,
	hybrid_ga_sa,
	iddfs_scheduler,
	particle_swarm,
	simulated_annealing_scheduler,
	tabu_search,
)

