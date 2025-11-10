"""
Phase 3 Demo: Scheduling Algorithms

Demonstrates the complete scheduling workflow:
1. Constraint generation and validation
2. DFS-based schedule generation
3. Simulated annealing optimization
4. Schedule scoring and comparison
"""
import logging
from core.models import CourseGroup
from core.excel_loader import process_excel
from algorithms.constraints import ConstraintUtils
from algorithms.dfs_scheduler import DFSScheduler
from algorithms.simulated_annealing import AnnealingOptimizer
from utils.schedule_metrics import (
    SchedulerPrefs, compute_schedule_stats, score_schedule,
    analyze_schedule_efficiency, compare_schedules
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_separator(title: str):
    """Print a formatted separator."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_constraint_generation(courses):
    """Demonstrate constraint generation."""
    print_separator("1. CONSTRAINT GENERATION")
    
    # Auto-generate constraints
    constraints = ConstraintUtils.auto_generate_constraints(courses)
    
    print("\nAuto-generated constraints:")
    for main_code, constraint in constraints.items():
        must_ps = "✓" if constraint["must_ps"] else "✗"
        must_lab = "✓" if constraint["must_lab"] else "✗"
        print(f"  {main_code:12} | PS: {must_ps} | Lab: {must_lab}")
    
    # Create course groups
    groups = {}
    for course in courses:
        if course.main_code not in groups:
            groups[course.main_code] = []
        groups[course.main_code].append(course)
    
    course_groups = {
        main_code: CourseGroup(main_code=main_code, courses=courses)
        for main_code, courses in groups.items()
    }
    
    # Validate groups
    print("\nCourse group validation:")
    for main_code, group in course_groups.items():
        validation = ConstraintUtils.validate_course_group(group)
        status = "✓ Valid" if validation["valid"] else "✗ Invalid"
        print(f"  {main_code:12} | {status} | "
              f"Lectures: {validation['lecture_count']}, "
              f"PS: {validation['ps_count']}, "
              f"Labs: {validation['lab_count']}")
    
    return course_groups, constraints


def demo_dfs_scheduling(course_groups):
    """Demonstrate DFS scheduling."""
    print_separator("2. DFS SCHEDULING")
    
    # Define mandatory courses
    mandatory_codes = {"COMP1007", "COMP1111", "MATH1101"}
    
    print(f"\nMandatory courses: {', '.join(mandatory_codes)}")
    print(f"Optional courses: {', '.join(set(course_groups.keys()) - mandatory_codes)}")
    
    # Create scheduler with preferences
    prefs = SchedulerPrefs(
        desired_free_days=["Friday"],
        compress_classes=True,
        max_weekly_slots=25,
        weight_free_days=2.0,
        weight_compression=1.5
    )
    
    scheduler = DFSScheduler(
        max_results=5,
        max_ects=30,
        allow_conflicts=False,
        scheduler_prefs=prefs,
        timeout_seconds=60
    )
    
    print("\nGenerating schedules...")
    schedules = scheduler.generate_schedules(course_groups, mandatory_codes)
    
    # Display statistics
    stats = scheduler.get_search_statistics()
    print(f"\n📊 Search Statistics:")
    print(f"  Time elapsed: {stats['total_time']:.2f}s")
    print(f"  Nodes explored: {stats['nodes_explored']}")
    print(f"  Branches pruned: {stats['pruned_branches']}")
    print(f"  Schedules found: {stats['schedules_found']}")
    
    # Display schedules
    print(f"\n📅 Top {len(schedules)} Schedules Generated:")
    for i, schedule in enumerate(schedules[:3], 1):
        schedule_stats = compute_schedule_stats(schedule)
        schedule_score = score_schedule(schedule, prefs)
        
        print(f"\n  Schedule #{i}:")
        print(f"    Total credits: {schedule.total_credits} ECTS")
        print(f"    Conflicts: {schedule.conflict_count}")
        print(f"    Days used: {schedule_stats.days_used}")
        print(f"    Free days: {', '.join(schedule_stats.free_days) if schedule_stats.free_days else 'None'}")
        print(f"    Score: {schedule_score:.2f}")
        print(f"    Courses: {len(schedule.courses)}")
        for course in schedule.courses[:5]:  # Show first 5
            print(f"      - {course.code}: {course.name}")
        if len(schedule.courses) > 5:
            print(f"      ... and {len(schedule.courses) - 5} more")
    
    return schedules, prefs


def demo_simulated_annealing(schedules, course_groups, mandatory_codes, prefs):
    """Demonstrate simulated annealing optimization."""
    print_separator("3. SIMULATED ANNEALING OPTIMIZATION")
    
    if not schedules:
        print("\n⚠️  No schedules to optimize")
        return
    
    # Take the first schedule and optimize it
    initial_schedule = schedules[0]
    
    print(f"\n🔧 Optimizing schedule with {len(initial_schedule.courses)} courses...")
    print(f"   Initial score: {score_schedule(initial_schedule, prefs):.2f}")
    print(f"   Initial conflicts: {initial_schedule.conflict_count}")
    
    # Prepare group options
    group_keys = list(course_groups.keys())
    _, group_options = ConstraintUtils.build_group_options(
        course_groups, mandatory_codes
    )
    
    # Create optimizer
    optimizer = AnnealingOptimizer(
        temp0=100.0,
        alpha=0.95,
        iterations=500,
        max_ects=30,
        scheduler_prefs=prefs
    )
    
    # Optimize
    optimized = optimizer.optimize(initial_schedule, group_keys, group_options)
    
    print(f"\n✨ Optimization complete!")
    print(f"   Optimized score: {score_schedule(optimized, prefs):.2f}")
    print(f"   Optimized conflicts: {optimized.conflict_count}")
    print(f"   Total credits: {optimized.total_credits} ECTS")
    
    # Multi-objective optimization
    print(f"\n🎯 Multi-objective optimization...")
    objectives = {
        "conflicts": 2.0,
        "ects": 1.0,
        "gaps": 0.5,
        "compression": 1.5
    }
    
    multi_optimized = optimizer.multi_objective_optimize(
        initial_schedule, group_keys, group_options, objectives
    )
    
    print(f"   Multi-objective score: {score_schedule(multi_optimized, prefs):.2f}")
    print(f"   Conflicts: {multi_optimized.conflict_count}")
    print(f"   Credits: {multi_optimized.total_credits} ECTS")
    
    return optimized, multi_optimized


def demo_schedule_comparison(schedules, prefs):
    """Demonstrate schedule comparison and analysis."""
    print_separator("4. SCHEDULE ANALYSIS & COMPARISON")
    
    if len(schedules) < 2:
        print("\n⚠️  Not enough schedules to compare")
        return
    
    # Compare first two schedules
    schedule1 = schedules[0]
    schedule2 = schedules[1]
    
    print("\n📊 Comparing Schedule #1 vs Schedule #2:")
    comparison = compare_schedules(schedule1, schedule2, prefs)
    
    print(f"\n  Better schedule: #{comparison['better_schedule']}")
    print(f"  Score difference: {comparison['score_difference']:.2f}")
    
    print(f"\n  Schedule #1:")
    for key, value in comparison['schedule1'].items():
        print(f"    {key:15}: {value}")
    
    print(f"\n  Schedule #2:")
    for key, value in comparison['schedule2'].items():
        print(f"    {key:15}: {value}")
    
    # Detailed efficiency analysis
    print("\n🔍 Detailed Efficiency Analysis (Schedule #1):")
    efficiency = analyze_schedule_efficiency(schedule1)
    
    print(f"  Total slots: {efficiency['total_slots']}")
    print(f"  Days used: {efficiency['days_used']}/7")
    print(f"  Free days: {', '.join(efficiency['free_days'])}")
    print(f"  Total gaps: {efficiency['total_gaps']}")
    print(f"  Average gaps per day: {efficiency['avg_gaps_per_day']:.2f}")
    print(f"  Overall efficiency: {efficiency['overall_efficiency']:.2%}")
    print(f"  Schedule compactness: {efficiency['schedule_compactness']:.2%}")
    print(f"  Credits per day: {efficiency['credits_per_day']:.2f}")
    
    if efficiency['day_utilization']:
        print("\n  Day-by-day utilization:")
        for day, util in efficiency['day_utilization'].items():
            print(f"    {day:10} | Slots: {util['slots']:2} | "
                  f"Consecutive: {util['consecutive']:2} | "
                  f"Gaps: {util['gaps']:2} | "
                  f"Efficiency: {util['efficiency']:.2%}")


def main():
    """Run the complete Phase 3 demo."""
    print("\n" + "=" * 70)
    print("  SchedularV3 - Phase 3: Scheduling Algorithms Demo")
    print("=" * 70)
    
    try:
        # Load courses from Excel
        print("\n📂 Loading courses from Excel...")
        courses = process_excel("data/sample_isik_courses.xlsx")
        print(f"✓ Loaded {len(courses)} courses")
        
        # Demo 1: Constraint Generation
        course_groups, constraints = demo_constraint_generation(courses)
        
        # Demo 2: DFS Scheduling
        mandatory_codes = {"COMP1007", "COMP1111", "MATH1101"}
        schedules, prefs = demo_dfs_scheduling(course_groups)
        
        if not schedules:
            print("\n⚠️  No valid schedules found!")
            return
        
        # Demo 3: Simulated Annealing
        optimized, multi_optimized = demo_simulated_annealing(
            schedules, course_groups, mandatory_codes, prefs
        )
        
        # Demo 4: Schedule Comparison
        demo_schedule_comparison(schedules, prefs)
        
        # Summary
        print_separator("SUMMARY")
        print(f"\n✓ Successfully demonstrated all Phase 3 features!")
        print(f"  • Constraint generation and validation")
        print(f"  • DFS scheduling with {len(schedules)} results")
        print(f"  • Simulated annealing optimization")
        print(f"  • Schedule scoring and comparison")
        print(f"  • Detailed efficiency analysis")
        
    except FileNotFoundError:
        print("\n❌ Error: sample_isik_courses.xlsx not found!")
        print("   Please ensure the data file exists in the data/ directory")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
