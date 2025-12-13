#!/usr/bin/env python3
"""Test script to verify all algorithm imports work correctly."""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing algorithm imports...")

try:
    from algorithms.benchmark import AlgorithmBenchmark
    print("[OK] benchmark.py")
except ImportError as e:
    print(f"[FAIL] benchmark.py: {e}")

try:
    from algorithms.simulated_annealing_scheduler import SimulatedAnnealingScheduler
    print("[OK] simulated_annealing_scheduler.py")
except ImportError as e:
    print(f"[FAIL] simulated_annealing_scheduler.py: {e}")

try:
    from algorithms.tabu_search import TabuSearchScheduler
    print("[OK] tabu_search.py")
except ImportError as e:
    print(f"[FAIL] tabu_search.py: {e}")

try:
    from algorithms.constraint_programming import ConstraintProgrammingScheduler
    print("[OK] constraint_programming.py")
except ImportError as e:
    print(f"[FAIL] constraint_programming.py: {e}")

try:
    from algorithms.a_star_scheduler import AStarScheduler
    print("[OK] a_star_scheduler.py")
except ImportError as e:
    print(f"[FAIL] a_star_scheduler.py: {e}")

try:
    from core.models import Course, Schedule
    print("[OK] core.models imports work")
except ImportError as e:
    print(f"[FAIL] core.models: {e}")

try:
    from utils.schedule_metrics import SchedulerPrefs
    print("[OK] utils.schedule_metrics imports work")
except ImportError as e:
    print(f"[FAIL] utils.schedule_metrics: {e}")

print("\n[SUCCESS] All import tests completed!")


