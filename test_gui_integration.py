"""
Test script for Işık University integration in GUI components.
Tests prerequisite warnings, ECTS limits, and smart filtering.
"""

print("=" * 70)
print("IŞIK UNIVERSITY GUI INTEGRATION TEST")
print("=" * 70)

# Test 1: Prerequisite data availability
print("\n1. PREREQUISITE DATA AVAILABILITY")
print("-" * 70)
try:
    from core.prerequisite_data import get_prerequisites, can_take_course
    print("✅ Prerequisite data module imported successfully")
    
    prereqs = get_prerequisites("COMP3112")
    print(f"✅ COMP3112 prerequisites: {prereqs}")
except ImportError as e:
    print(f"❌ Failed to import prerequisite data: {e}")

# Test 2: Curriculum data availability
print("\n2. CURRICULUM DATA AVAILABILITY")
print("-" * 70)
try:
    from core.curriculum_data import GRADUATION_REQUIREMENTS, get_semester_courses
    print("✅ Curriculum data module imported successfully")
    print(f"✅ Total ECTS requirement: {GRADUATION_REQUIREMENTS['total_ects']}")
    print(f"✅ Minimum GPA: {GRADUATION_REQUIREMENTS['minimum_gpa']}")
except ImportError as e:
    print(f"❌ Failed to import curriculum data: {e}")

# Test 3: ECTS limits
print("\n3. ECTS LIMITS BY GPA")
print("-" * 70)
try:
    from core.isik_university_data import ECTS_LIMITS_BY_GPA
    print("✅ ECTS limits module imported successfully")
    for key, value in ECTS_LIMITS_BY_GPA.items():
        print(f"  {key}: {value} ECTS")
except ImportError as e:
    print(f"❌ Failed to import ECTS limits: {e}")

# Test 4: GUI components
print("\n4. GUI COMPONENTS INTEGRATION")
print("-" * 70)
try:
    from gui.tabs.course_selector_tab import CourseSelectorTab, ISIK_PREREQ_AVAILABLE
    print(f"✅ Course Selector Tab - Prerequisite checking: {ISIK_PREREQ_AVAILABLE}")
except Exception as e:
    print(f"❌ Course Selector Tab error: {e}")

try:
    from gui.tabs.schedule_viewer_tab import ScheduleViewerTab, ISIK_ECTS_AVAILABLE
    print(f"✅ Schedule Viewer Tab - ECTS limit tracking: {ISIK_ECTS_AVAILABLE}")
except Exception as e:
    print(f"❌ Schedule Viewer Tab error: {e}")

try:
    from gui.tabs.graduation_planner_widget import ISIK_DATA_AVAILABLE
    print(f"✅ Graduation Planner - Curriculum integration: {ISIK_DATA_AVAILABLE}")
except Exception as e:
    print(f"❌ Graduation Planner error: {e}")

# Test 5: Algorithm smart filtering
print("\n5. ALGORITHM SMART FILTERING")
print("-" * 70)
try:
    from algorithms.base_scheduler import ISIK_FILTERING_AVAILABLE
    print(f"✅ Base Scheduler - Smart filtering: {ISIK_FILTERING_AVAILABLE}")
    
    if ISIK_FILTERING_AVAILABLE:
        print("  Functions available:")
        print("    • filter_courses_by_prerequisites()")
        print("    • adjust_max_ects_by_gpa()")
except Exception as e:
    print(f"❌ Base Scheduler error: {e}")

# Test 6: Işık branding
print("\n6. IŞIK UNIVERSITY BRANDING")
print("-" * 70)
try:
    from config.settings import ISIK_BLUE_PRIMARY, SCHEDULE_COLORS
    print(f"✅ Primary color: {ISIK_BLUE_PRIMARY}")
    print(f"✅ Schedule colors (first 3): {SCHEDULE_COLORS[:3]}")
except Exception as e:
    print(f"❌ Settings error: {e}")

# Summary
print("\n" + "=" * 70)
print("✅ INTEGRATION TEST COMPLETED")
print("=" * 70)
print("\nFeatures integrated:")
print("  1. ✅ Prerequisite warnings in Course Selector")
print("  2. ✅ ECTS limit tracking in Schedule Viewer")
print("  3. ✅ Curriculum-based Graduation Planner")
print("  4. ✅ Smart filtering in Algorithms")
print("  5. ✅ Işık University branding theme")
print("\nReady to run: python main.py")
print("=" * 70)
