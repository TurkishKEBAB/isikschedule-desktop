#!/usr/bin/env python3
"""
Quick verification script to ensure all imports work correctly.
Run this to verify that the installation was successful.
"""

import sys
from pathlib import Path

# Add project root to path if needed
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def verify_imports():
    """Verify that all critical imports work."""
    print("=" * 60)
    print("SchedularV3 Import Verification")
    print("=" * 60)

    tests = []

    # Test 1: Core models
    try:
        from core.models import Course, Schedule
        print("✓ core.models imports OK")
        tests.append(True)
    except ImportError as e:
        print(f"✗ core.models import FAILED: {e}")
        tests.append(False)

    # Test 2: Utils
    try:
        from utils.schedule_metrics import SchedulerPrefs
        print("✓ utils.schedule_metrics imports OK")
        tests.append(True)
    except ImportError as e:
        print(f"✗ utils.schedule_metrics import FAILED: {e}")
        tests.append(False)

    # Test 3: Algorithms
    try:
        from algorithms.constraint_programming import ConstraintProgrammingScheduler
        print("✓ algorithms.constraint_programming imports OK")
        tests.append(True)
    except ImportError as e:
        print(f"✗ algorithms.constraint_programming import FAILED: {e}")
        tests.append(False)

    # Test 4: Base scheduler
    try:
        from algorithms.base_scheduler import BaseScheduler
        print("✓ algorithms.base_scheduler imports OK")
        tests.append(True)
    except ImportError as e:
        print(f"✗ algorithms.base_scheduler import FAILED: {e}")
        tests.append(False)

    print("=" * 60)
    passed = sum(tests)
    total = len(tests)

    if passed == total:
        print(f"SUCCESS: All {total} import tests passed! ✓")
        print("\nYou can now use PyCharm normally.")
        print("If you still see red underlines, try:")
        print("  File -> Invalidate Caches -> Just Restart")
        return 0
    else:
        print(f"PARTIAL: {passed}/{total} tests passed")
        print("\nPlease run: pip install -e .")
        return 1

if __name__ == "__main__":
    sys.exit(verify_imports())

