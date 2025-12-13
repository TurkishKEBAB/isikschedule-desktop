import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("Testing SchedularV3 Module Imports")
print("=" * 60)
print(f"Project root: {project_root}")
print(f"Python version: {sys.version}")
print()

# Test imports
tests_passed = 0
tests_failed = 0

try:
    from core.models import Schedule, Course
    print("✓ PASS: from core.models import Schedule, Course")
    tests_passed += 1
except Exception as e:
    print(f"✗ FAIL: from core.models import Schedule, Course")
    print(f"  Error: {e}")
    tests_failed += 1

try:
    from utils.schedule_metrics import SchedulerPrefs
    print("✓ PASS: from utils.schedule_metrics import SchedulerPrefs")
    tests_passed += 1
except Exception as e:
    print(f"✗ FAIL: from utils.schedule_metrics import SchedulerPrefs")
    print(f"  Error: {e}")
    tests_failed += 1

try:
    from algorithms.evaluator import evaluate_schedule
    print("✓ PASS: from algorithms.evaluator import evaluate_schedule")
    tests_passed += 1
except Exception as e:
    print(f"✗ FAIL: from algorithms.evaluator import evaluate_schedule")
    print(f"  Error: {e}")
    tests_failed += 1

print()
print("=" * 60)
print(f"Results: {tests_passed} passed, {tests_failed} failed")
print("=" * 60)

if tests_failed == 0:
    print("✓ All imports successful!")
    sys.exit(0)
else:
    print("✗ Some imports failed. See errors above.")
    sys.exit(1)

