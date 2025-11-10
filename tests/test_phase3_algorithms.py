"""
Comprehensive tests for Phase 3: Scheduling Algorithms

Tests cover:
- ConstraintUtils (constraint generation and validation)
- DFSScheduler (depth-first search scheduling)
- AnnealingOptimizer (simulated annealing optimization)
- SchedulerPrefs and schedule scoring metrics
"""
import pytest
from core.models import Course, Schedule, CourseGroup
from algorithms.constraints import ConstraintUtils
from algorithms.dfs_scheduler import DFSScheduler
from algorithms.simulated_annealing import AnnealingOptimizer
from utils.schedule_metrics import (
    SchedulerPrefs, compute_schedule_stats, score_schedule,
    meets_weekly_hours_constraint, meets_daily_hours_constraint,
    meets_free_day_constraint, analyze_schedule_efficiency,
    compare_schedules
)


@pytest.fixture
def sample_courses():
    """Create sample courses for testing."""
    return [
        Course(
            code="COMP1007.1",
            main_code="COMP1007",
            name="Introduction to Computing",
            ects=3,
            course_type="lecture",
            schedule=[("Tuesday", 4)],
            teacher="Dr. Smith"
        ),
        Course(
            code="COMP1007.2",
            main_code="COMP1007",
            name="Introduction to Computing",
            ects=3,
            course_type="lecture",
            schedule=[("Monday", 2), ("Monday", 3)],
            teacher="Dr. Jones"
        ),
        Course(
            code="COMP1111.1",
            main_code="COMP1111",
            name="Programming Fundamentals",
            ects=6,
            course_type="lecture",
            schedule=[("Tuesday", 6), ("Tuesday", 7), ("Tuesday", 8)],
            teacher="Dr. Brown"
        ),
        Course(
            code="COMP1111-L.1",
            main_code="COMP1111",
            name="Programming Lab",
            ects=0,
            course_type="lab",
            schedule=[("Wednesday", 3), ("Wednesday", 4)],
            teacher="TA Alice"
        ),
        Course(
            code="COMP1111-L.2",
            main_code="COMP1111",
            name="Programming Lab",
            ects=0,
            course_type="lab",
            schedule=[("Thursday", 3), ("Thursday", 4)],
            teacher="TA Bob"
        ),
        Course(
            code="MATH1101.1",
            main_code="MATH1101",
            name="Calculus I",
            ects=5,
            course_type="lecture",
            schedule=[("Monday", 5), ("Wednesday", 5)],
            teacher="Prof. Wilson"
        ),
        Course(
            code="PHYS1101.1",
            main_code="PHYS1101",
            name="Physics I",
            ects=6,
            course_type="lecture",
            schedule=[("Tuesday", 2), ("Thursday", 2)],
            teacher="Prof. Garcia"
        ),
        Course(
            code="PHYS1101-L.1",
            main_code="PHYS1101",
            name="Physics Lab",
            ects=0,
            course_type="lab",
            schedule=[("Friday", 1), ("Friday", 2)],
            teacher="TA Charlie"
        ),
    ]


@pytest.fixture
def course_groups(sample_courses):
    """Create CourseGroup objects from sample courses."""
    groups = {}
    for course in sample_courses:
        if course.main_code not in groups:
            groups[course.main_code] = []
        groups[course.main_code].append(course)
    
    return {
        main_code: CourseGroup(main_code=main_code, courses=courses)
        for main_code, courses in groups.items()
    }


class TestConstraintUtils:
    """Test ConstraintUtils functionality."""
    
    def test_auto_generate_constraints(self, sample_courses):
        """Test automatic constraint generation."""
        constraints = ConstraintUtils.auto_generate_constraints(sample_courses)
        
        assert "COMP1007" in constraints
        assert "COMP1111" in constraints
        assert "MATH1101" in constraints
        assert "PHYS1101" in constraints
        
        # COMP1007 has no PS/lab
        assert constraints["COMP1007"]["must_ps"] is False
        assert constraints["COMP1007"]["must_lab"] is False
        
        # COMP1111 has lab but no PS
        assert constraints["COMP1111"]["must_ps"] is False
        assert constraints["COMP1111"]["must_lab"] is True
        
        # PHYS1101 has lab but no PS
        assert constraints["PHYS1101"]["must_ps"] is False
        assert constraints["PHYS1101"]["must_lab"] is True
    
    def test_generate_valid_group_selections(self, sample_courses):
        """Test valid course selection generation."""
        comp1111_courses = [c for c in sample_courses if c.main_code == "COMP1111"]
        constraints = ConstraintUtils.auto_generate_constraints(sample_courses)
        
        selections = ConstraintUtils.generate_valid_group_selections(
            comp1111_courses, constraints
        )
        
        # Should have selections for each lecture + each lab combination
        assert len(selections) == 2  # 1 lecture * 2 labs
        
        # Each selection should have lecture + lab
        for selection in selections:
            assert len(selection) == 2
            assert any(c.course_type == "lecture" for c in selection)
            assert any(c.course_type == "lab" for c in selection)
    
    def test_build_group_options(self, course_groups):
        """Test building group options with constraints."""
        mandatory_codes = {"COMP1007", "COMP1111"}
        
        valid_selections, options = ConstraintUtils.build_group_options(
            course_groups, mandatory_codes
        )
        
        # Mandatory courses should not have None option
        assert all(opt is not None for opt in options["COMP1007"])
        assert all(opt is not None for opt in options["COMP1111"])
        
        # Optional courses should have None option
        assert options["MATH1101"][0] is None
        assert options["PHYS1101"][0] is None
    
    def test_validate_course_group(self, course_groups):
        """Test course group validation."""
        validation = ConstraintUtils.validate_course_group(course_groups["COMP1111"])
        
        assert validation["valid"] is True
        assert validation["has_lab"] is True
        assert validation["lecture_count"] == 1
        assert validation["lab_count"] == 2
    
    def test_get_conflict_matrix(self, sample_courses):
        """Test conflict matrix generation."""
        conflict_matrix = ConstraintUtils.get_conflict_matrix(sample_courses)
        
        # Check that courses with overlapping times are marked as conflicting
        assert len(conflict_matrix) == len(sample_courses)
        
        # COMP1007.2 (Monday 2-3) should not conflict with COMP1007.1 (Tuesday 4)
        comp1007_1_conflicts = conflict_matrix["COMP1007.1"]
        assert "COMP1007.2" not in comp1007_1_conflicts


class TestScheduleMetrics:
    """Test schedule scoring and metrics."""
    
    def test_scheduler_prefs_defaults(self):
        """Test SchedulerPrefs default values."""
        prefs = SchedulerPrefs()
        
        assert prefs.compress_classes is False
        assert prefs.desired_free_days == []
        assert prefs.strict_free_days is True
        assert prefs.max_weekly_slots == 60
    
    def test_compute_schedule_stats(self, sample_courses):
        """Test schedule statistics computation."""
        # Create schedule with specific courses
        schedule = Schedule([
            sample_courses[0],  # COMP1007.1 - Tuesday 4
            sample_courses[5],  # MATH1101.1 - Monday 5, Wednesday 5
        ])
        
        stats = compute_schedule_stats(schedule)
        
        assert stats.days_used == 3  # Monday, Tuesday, Wednesday
        assert stats.total_slots == 3
        assert "Monday" in stats.daily_slot_counts
        assert "Tuesday" in stats.daily_slot_counts
        assert "Wednesday" in stats.daily_slot_counts
        
        # Check free days
        assert "Thursday" in stats.free_days
        assert "Friday" in stats.free_days
    
    def test_score_schedule_free_days(self, sample_courses):
        """Test schedule scoring with free day preferences."""
        schedule = Schedule([sample_courses[0], sample_courses[5]])
        
        prefs = SchedulerPrefs(
            desired_free_days=["Thursday", "Friday"],
            strict_free_days=True,
            weight_free_days=1.0
        )
        
        score = score_schedule(schedule, prefs)
        
        # Should get points for achieving both free days
        assert score > 0
    
    def test_meets_weekly_hours_constraint(self, sample_courses):
        """Test weekly hours constraint checking."""
        schedule = Schedule([
            sample_courses[0],  # 1 slot
            sample_courses[5],  # 2 slots
        ])
        
        assert meets_weekly_hours_constraint(schedule, 5) is True
        assert meets_weekly_hours_constraint(schedule, 2) is False
    
    def test_meets_daily_hours_constraint(self, sample_courses):
        """Test daily hours constraint checking."""
        schedule = Schedule([sample_courses[2]])  # COMP1111.1 - 3 slots on Tuesday
        
        assert meets_daily_hours_constraint(schedule, 3) is True
        assert meets_daily_hours_constraint(schedule, 2) is False
    
    def test_meets_free_day_constraint_strict(self, sample_courses):
        """Test strict free day constraint."""
        schedule = Schedule([
            sample_courses[0],  # Tuesday
            sample_courses[5],  # Monday, Wednesday
        ])
        
        # Thursday and Friday should be free
        assert meets_free_day_constraint(schedule, ["Thursday", "Friday"], strict=True) is True
        
        # Monday should not be free
        assert meets_free_day_constraint(schedule, ["Monday"], strict=True) is False
    
    def test_analyze_schedule_efficiency(self, sample_courses):
        """Test schedule efficiency analysis."""
        schedule = Schedule([
            sample_courses[0],
            sample_courses[5],
        ])
        
        efficiency = analyze_schedule_efficiency(schedule)
        
        assert "total_slots" in efficiency
        assert "days_used" in efficiency
        assert "free_days" in efficiency
        assert "overall_efficiency" in efficiency
        assert efficiency["total_slots"] == 3
    
    def test_compare_schedules(self, sample_courses):
        """Test schedule comparison."""
        schedule1 = Schedule([sample_courses[0], sample_courses[5]])
        schedule2 = Schedule([sample_courses[1], sample_courses[6]])
        
        prefs = SchedulerPrefs()
        comparison = compare_schedules(schedule1, schedule2, prefs)
        
        assert "better_schedule" in comparison
        assert "schedule1" in comparison
        assert "schedule2" in comparison
        assert comparison["better_schedule"] in [1, 2]


class TestDFSScheduler:
    """Test DFS scheduler functionality."""
    
    def test_dfs_scheduler_initialization(self):
        """Test DFS scheduler initialization."""
        scheduler = DFSScheduler(max_results=5, max_ects=30)
        
        assert scheduler.max_results == 5
        assert scheduler.max_ects == 30
        assert scheduler.allow_conflicts is False
        assert scheduler.results == []
    
    def test_generate_schedules_basic(self, course_groups):
        """Test basic schedule generation."""
        scheduler = DFSScheduler(max_results=3, max_ects=30)
        
        mandatory_codes = {"COMP1007", "COMP1111"}
        schedules = scheduler.generate_schedules(course_groups, mandatory_codes)
        
        # Should generate schedules
        assert len(schedules) > 0
        assert len(schedules) <= 3
        
        # Each schedule should have mandatory courses
        for schedule in schedules:
            main_codes = set(c.main_code for c in schedule.courses)
            assert "COMP1007" in main_codes
            assert "COMP1111" in main_codes
    
    def test_generate_schedules_with_preferences(self, course_groups):
        """Test schedule generation with preferences."""
        prefs = SchedulerPrefs(
            desired_free_days=["Friday"],
            compress_classes=True
        )
        scheduler = DFSScheduler(max_results=5, scheduler_prefs=prefs)
        
        mandatory_codes = {"COMP1007"}
        schedules = scheduler.generate_schedules(course_groups, mandatory_codes)
        
        assert len(schedules) > 0
    
    def test_get_search_statistics(self, course_groups):
        """Test search statistics retrieval."""
        scheduler = DFSScheduler(max_results=3)
        
        mandatory_codes = {"COMP1007"}
        scheduler.generate_schedules(course_groups, mandatory_codes)
        
        stats = scheduler.get_search_statistics()
        
        assert "total_time" in stats
        assert "nodes_explored" in stats
        assert "schedules_found" in stats
        assert stats["nodes_explored"] > 0
    
    def test_get_optimization_report(self, course_groups):
        """Test optimization report generation."""
        scheduler = DFSScheduler(max_results=3)
        
        mandatory_codes = {"COMP1007"}
        scheduler.generate_schedules(course_groups, mandatory_codes)
        
        report = scheduler.get_optimization_report()
        
        assert "total_schedules" in report
        assert "credit_analysis" in report
        assert "conflict_analysis" in report
    
    def test_ects_limit_enforcement(self, course_groups):
        """Test ECTS limit enforcement."""
        scheduler = DFSScheduler(max_results=5, max_ects=10)  # Very low limit
        
        mandatory_codes = {"COMP1007", "COMP1111"}
        schedules = scheduler.generate_schedules(course_groups, mandatory_codes)
        
        # Should generate schedules within ECTS limit
        for schedule in schedules:
            assert schedule.total_credits <= 10


class TestAnnealingOptimizer:
    """Test simulated annealing optimizer."""
    
    def test_annealing_initialization(self):
        """Test annealing optimizer initialization."""
        optimizer = AnnealingOptimizer(temp0=100, alpha=0.95, iterations=500)
        
        assert optimizer.temp0 == 100
        assert optimizer.alpha == 0.95
        assert optimizer.iterations == 500
    
    def test_optimize_schedule(self, sample_courses, course_groups):
        """Test schedule optimization."""
        # Create initial schedule
        initial_schedule = Schedule([
            sample_courses[0],  # COMP1007.1
            sample_courses[2],  # COMP1111.1
            sample_courses[3],  # COMP1111-L.1
        ])
        
        # Prepare group options
        group_keys = list(course_groups.keys())
        _, group_options = ConstraintUtils.build_group_options(
            course_groups, {"COMP1007", "COMP1111"}
        )
        
        optimizer = AnnealingOptimizer(iterations=100)
        optimized = optimizer.optimize(initial_schedule, group_keys, group_options)
        
        # Should return a valid schedule
        assert isinstance(optimized, Schedule)
        assert len(optimized.courses) > 0
    
    def test_repair_schedule_with_priority(self, sample_courses, course_groups):
        """Test schedule repair with priority."""
        schedule = Schedule([
            sample_courses[2],  # COMP1111.1 lecture
            sample_courses[3],  # COMP1111-L.1 lab
        ])
        
        valid_selections, _ = ConstraintUtils.build_group_options(
            course_groups, {"COMP1111"}
        )
        
        optimizer = AnnealingOptimizer()
        repaired = optimizer.repair_schedule_with_priority(
            schedule, valid_selections, ["lecture", "lab"]
        )
        
        assert isinstance(repaired, Schedule)
    
    def test_global_repair_schedule(self, sample_courses):
        """Test global schedule repair."""
        # Create schedule with conflicts
        schedule = Schedule([
            sample_courses[0],  # Tuesday 4
            sample_courses[2],  # Tuesday 6,7,8
        ])
        
        optimizer = AnnealingOptimizer()
        repaired = optimizer.global_repair_schedule(schedule, sample_courses)
        
        assert isinstance(repaired, Schedule)
    
    def test_multi_objective_optimize(self, sample_courses, course_groups):
        """Test multi-objective optimization."""
        initial_schedule = Schedule([sample_courses[0], sample_courses[5]])
        
        group_keys = list(course_groups.keys())
        _, group_options = ConstraintUtils.build_group_options(
            course_groups, {"COMP1007", "MATH1101"}
        )
        
        optimizer = AnnealingOptimizer(iterations=50)
        objectives = {"conflicts": 2.0, "ects": 1.0, "gaps": 0.5}
        
        optimized = optimizer.multi_objective_optimize(
            initial_schedule, group_keys, group_options, objectives
        )
        
        assert isinstance(optimized, Schedule)


class TestIntegration:
    """Integration tests combining multiple components."""
    
    def test_full_scheduling_workflow(self, course_groups):
        """Test complete scheduling workflow."""
        # Step 1: Generate schedules with DFS
        scheduler = DFSScheduler(max_results=5, max_ects=30)
        mandatory_codes = {"COMP1007", "COMP1111"}
        
        schedules = scheduler.generate_schedules(course_groups, mandatory_codes)
        assert len(schedules) > 0
        
        # Step 2: Optimize best schedule with annealing
        if schedules:
            best_schedule = schedules[0]
            
            group_keys = list(course_groups.keys())
            _, group_options = ConstraintUtils.build_group_options(
                course_groups, mandatory_codes
            )
            
            optimizer = AnnealingOptimizer(iterations=50)
            optimized = optimizer.optimize(best_schedule, group_keys, group_options)
            
            assert isinstance(optimized, Schedule)
    
    def test_constraint_aware_scheduling(self, course_groups):
        """Test that scheduler respects constraints."""
        scheduler = DFSScheduler(max_results=5)
        
        # COMP1111 requires lab
        mandatory_codes = {"COMP1111"}
        schedules = scheduler.generate_schedules(course_groups, mandatory_codes)
        
        # All schedules should include both lecture and lab for COMP1111
        for schedule in schedules:
            comp1111_courses = [c for c in schedule.courses if c.main_code == "COMP1111"]
            types = set(c.course_type for c in comp1111_courses)
            assert "lecture" in types
            assert "lab" in types
    
    def test_preference_optimization(self, course_groups):
        """Test schedule generation with preferences."""
        prefs = SchedulerPrefs(
            desired_free_days=["Friday"],
            strict_free_days=True,
            compress_classes=True,
            weight_free_days=2.0
        )
        
        scheduler = DFSScheduler(max_results=5, scheduler_prefs=prefs)
        mandatory_codes = {"COMP1007"}
        
        schedules = scheduler.generate_schedules(course_groups, mandatory_codes)
        
        # Check that best schedules respect preferences
        if schedules:
            best_schedule = schedules[0]
            stats = compute_schedule_stats(best_schedule)
            
            # Friday should ideally be free
            assert "Friday" in stats.free_days or stats.daily_slot_counts.get("Friday", 0) <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
