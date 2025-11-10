"""Scheduling algorithms package for SchedularV3."""

# Algorithm registry
_ALGORITHMS = {}

def register_scheduler(name: str):
    """Decorator to register a scheduler algorithm."""
    def decorator(cls):
        _ALGORITHMS[name] = cls
        return cls
    return decorator

def get_algorithm(name: str):
    """Get a registered algorithm by name."""
    return _ALGORITHMS.get(name)

def list_algorithms():
    """List all registered algorithm names."""
    return list(_ALGORITHMS.keys())

# Import all algorithms to trigger registration
from .greedy_scheduler import GreedyScheduler
from .bfs_scheduler import BFSScheduler
from .dfs_scheduler import DFSScheduler
from .iddfs_scheduler import IDDFSScheduler
from .a_star_scheduler import AStarScheduler
from .dijkstra_scheduler import DijkstraScheduler
from .simulated_annealing_scheduler import SimulatedAnnealingScheduler
from .genetic_algorithm import GeneticAlgorithmScheduler
from .hill_climbing import HillClimbingScheduler
from .tabu_search import TabuSearchScheduler
from .particle_swarm import ParticleSwarmScheduler
from .hybrid_ga_sa import HybridGASAScheduler
from .constraint_programming import ConstraintProgrammingScheduler

__all__ = [
    'register_scheduler',
    'get_algorithm',
    'list_algorithms',
    'GreedyScheduler',
    'BFSScheduler',
    'DFSScheduler',
    'IDDFSScheduler',
    'AStarScheduler',
    'DijkstraScheduler',
    'SimulatedAnnealingScheduler',
    'GeneticAlgorithmScheduler',
    'HillClimbingScheduler',
    'TabuSearchScheduler',
    'ParticleSwarmScheduler',
    'HybridGASAScheduler',
    'ConstraintProgrammingScheduler',
]
