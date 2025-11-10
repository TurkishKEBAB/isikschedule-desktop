"""
Unit tests for core data models.

Tests Course, Schedule, CourseGroup, and Program dataclasses.
"""
import pytest
from core.models import Course, Schedule, CourseGroup, Program


class TestCourse:
    """Test cases for Course dataclass."""

    def test_course_creation(self):
        """Test creating a basic course."""
        course = Course(
            code="CS101-01",
            main_code="CS101",
            name="Introduction to Programming",
            ects=6,
            course_type="Zorunlu",
            schedule={"Pazartesi": ["09:00-10:50"], "Çarşamba": ["09:00-10:50"]},
            teacher="Dr. Ali Yılmaz",
            has_lecture=True
        )

        assert course.code == "CS101-01"
        assert course.main_code == "CS101"
        assert course.name == "Introduction to Programming"
        assert course.ects == 6
        assert course.course_type == "Zorunlu"
        assert course.teacher == "Dr. Ali Yılmaz"
        assert course.has_lecture is True

    def test_course_with_defaults(self):
        """Test course with default values."""
        course = Course(
            code="MATH201-01",
            main_code="MATH201",
            name="Calculus II",
            ects=5,
            course_type="Zorunlu",
            schedule={"Salı": ["13:00-14:50"]}
        )

        assert course.teacher is None
        assert course.has_lecture is False
        assert course.faculty == "Unknown Faculty"
        assert course.department == "Unknown Department"
        assert course.campus == "Main"

    def test_course_custom_location(self):
        """Test course with custom faculty/department/campus."""
        course = Course(
            code="ENG301-01",
            main_code="ENG301",
            name="Advanced English",
            ects=4,
            course_type="Seçmeli",
            schedule={"Perşembe": ["15:00-16:50"]},
            faculty="Faculty of Arts and Sciences",
            department="English Language and Literature",
            campus="North Campus"
        )

        assert course.faculty == "Faculty of Arts and Sciences"
        assert course.department == "English Language and Literature"
        assert course.campus == "North Campus"

    def test_course_dict_conversion(self):
        """Test converting course to and from dictionary."""
        original = Course(
            code="PHYS201-02",
            main_code="PHYS201",
            name="Physics II",
            ects=6,
            course_type="Zorunlu",
            schedule={"Pazartesi": ["11:00-12:50"], "Cuma": ["11:00-12:50"]},
            teacher="Prof. Dr. Mehmet Demir",
            has_lecture=True,
            faculty="Faculty of Engineering",
            department="Physics",
            campus="South Campus"
        )

        # Convert to dict
        course_dict = {
            "code": original.code,
            "main_code": original.main_code,
            "name": original.name,
            "ects": original.ects,
            "course_type": original.course_type,
            "schedule": original.schedule,
            "teacher": original.teacher,
            "has_lecture": original.has_lecture,
            "faculty": original.faculty,
            "department": original.department,
            "campus": original.campus
        }

        # Convert back from dict
        restored = Course.from_dict(course_dict)

        assert restored.code == original.code
        assert restored.main_code == original.main_code
        assert restored.name == original.name
        assert restored.ects == original.ects
        assert restored.teacher == original.teacher
        assert restored.faculty == original.faculty

    def test_course_empty_schedule(self):
        """Test course with empty schedule."""
        course = Course(
            code="PROJ499-01",
            main_code="PROJ499",
            name="Project",
            ects=8,
            course_type="Zorunlu",
            schedule={}
        )

        assert course.schedule == {}


class TestSchedule:
    """Test cases for Schedule dataclass."""

    @pytest.fixture
    def sample_courses(self):
        """Create sample courses for testing."""
        return [
            Course(
                code="CS101-01",
                main_code="CS101",
                name="Programming I",
                ects=6,
                course_type="Zorunlu",
                schedule={"Pazartesi": ["09:00-10:50"], "Çarşamba": ["09:00-10:50"]}
            ),
            Course(
                code="MATH101-01",
                main_code="MATH101",
                name="Calculus I",
                ects=5,
                course_type="Zorunlu",
                schedule={"Salı": ["11:00-12:50"], "Perşembe": ["11:00-12:50"]}
            ),
            Course(
                code="PHYS101-01",
                main_code="PHYS101",
                name="Physics I",
                ects=6,
                course_type="Zorunlu",
                schedule={"Cuma": ["13:00-14:50"]}
            )
        ]

    def test_schedule_creation(self, sample_courses):
        """Test creating a schedule."""
        schedule = Schedule(courses=sample_courses)

        assert len(schedule.courses) == 3
        assert schedule.total_credits == 17
        assert schedule.conflict_count == 0

    def test_schedule_total_credits(self, sample_courses):
        """Test total credits calculation."""
        schedule = Schedule(courses=sample_courses[:2])
        assert schedule.total_credits == 11

        schedule = Schedule(courses=sample_courses)
        assert schedule.total_credits == 17

    def test_schedule_conflict_detection(self):
        """Test conflict detection between courses."""
        conflicting_courses = [
            Course(
                code="CS201-01",
                main_code="CS201",
                name="Data Structures",
                ects=6,
                course_type="Zorunlu",
                schedule={"Pazartesi": ["09:00-10:50"]}
            ),
            Course(
                code="MATH201-01",
                main_code="MATH201",
                name="Linear Algebra",
                ects=5,
                course_type="Zorunlu",
                schedule={"Pazartesi": ["09:00-10:50"]}  # Same time slot!
            )
        ]

        schedule = Schedule(courses=conflicting_courses)
        assert schedule.conflict_count == 1

    def test_schedule_has_conflicts(self):
        """Test has_conflicts property."""
        no_conflict = Schedule(courses=[
            Course(
                code="CS101-01",
                main_code="CS101",
                name="Programming",
                ects=6,
                course_type="Zorunlu",
                schedule={"Pazartesi": ["09:00-10:50"]}
            ),
            Course(
                code="MATH101-01",
                main_code="MATH101",
                name="Calculus",
                ects=5,
                course_type="Zorunlu",
                schedule={"Salı": ["11:00-12:50"]}
            )
        ])
        assert no_conflict.has_conflicts is False

        with_conflict = Schedule(courses=[
            Course(
                code="CS101-01",
                main_code="CS101",
                name="Programming",
                ects=6,
                course_type="Zorunlu",
                schedule={"Pazartesi": ["09:00-10:50"]}
            ),
            Course(
                code="MATH101-01",
                main_code="MATH101",
                name="Calculus",
                ects=5,
                course_type="Zorunlu",
                schedule={"Pazartesi": ["09:00-10:50"]}
            )
        ])
        assert with_conflict.has_conflicts is True

    def test_schedule_get_conflict_slots(self):
        """Test getting conflicting time slots."""
        courses = [
            Course(
                code="CS201-01",
                main_code="CS201",
                name="Data Structures",
                ects=6,
                course_type="Zorunlu",
                schedule={"Pazartesi": ["09:00-10:50", "13:00-14:50"]}
            ),
            Course(
                code="MATH201-01",
                main_code="MATH201",
                name="Linear Algebra",
                ects=5,
                course_type="Zorunlu",
                schedule={"Pazartesi": ["09:00-10:50"]}
            )
        ]

        schedule = Schedule(courses=courses)
        conflicts = schedule.get_conflict_slots()

        assert ("Pazartesi", "09:00-10:50") in conflicts
        assert ("Pazartesi", "13:00-14:50") not in conflicts

    def test_schedule_statistics(self, sample_courses):
        """Test statistics calculation."""
        schedule = Schedule(courses=sample_courses)
        stats = schedule.get_statistics()

        assert stats["total_courses"] == 3
        assert stats["total_credits"] == 17
        assert stats["conflict_count"] == 0
        assert stats["has_conflicts"] is False


class TestCourseGroup:
    """Test cases for CourseGroup dataclass."""

    def test_course_group_creation(self):
        """Test creating a course group."""
        courses = [
            Course(
                code="CS101-01",
                main_code="CS101",
                name="Programming I",
                ects=6,
                course_type="Zorunlu",
                schedule={"Pazartesi": ["09:00-10:50"]}
            ),
            Course(
                code="CS101-02",
                main_code="CS101",
                name="Programming I",
                ects=6,
                course_type="Zorunlu",
                schedule={"Salı": ["11:00-12:50"]}
            )
        ]

        group = CourseGroup(main_code="CS101", courses=courses)

        assert group.main_code == "CS101"
        assert len(group.courses) == 2
        assert group.name == "Programming I"

    def test_course_group_name(self):
        """Test that group name comes from first course."""
        courses = [
            Course(
                code="MATH201-01",
                main_code="MATH201",
                name="Linear Algebra",
                ects=5,
                course_type="Zorunlu",
                schedule={"Çarşamba": ["09:00-10:50"]}
            )
        ]

        group = CourseGroup(main_code="MATH201", courses=courses)
        assert group.name == "Linear Algebra"

    def test_course_group_empty(self):
        """Test empty course group."""
        group = CourseGroup(main_code="EMPTY001", courses=[])
        assert group.name == "Unknown Course"


class TestProgram:
    """Test cases for Program dataclass."""

    @pytest.fixture
    def sample_schedule(self):
        """Create a sample schedule."""
        courses = [
            Course(
                code="CS101-01",
                main_code="CS101",
                name="Programming I",
                ects=6,
                course_type="Zorunlu",
                schedule={"Pazartesi": ["09:00-10:50"]}
            ),
            Course(
                code="MATH101-01",
                main_code="MATH101",
                name="Calculus I",
                ects=5,
                course_type="Zorunlu",
                schedule={"Salı": ["11:00-12:50"]}
            )
        ]
        return Schedule(courses=courses)

    def test_program_creation(self):
        """Test creating a program."""
        program = Program(name="Computer Science Fall 2024")

        assert program.name == "Computer Science Fall 2024"
        assert len(program.schedules) == 0
        assert program.metadata == {}

    def test_program_with_metadata(self):
        """Test program with custom metadata."""
        metadata = {
            "semester": "Fall 2024",
            "department": "Computer Science",
            "year": 1
        }
        program = Program(name="CS Year 1", metadata=metadata)

        assert program.metadata["semester"] == "Fall 2024"
        assert program.metadata["department"] == "Computer Science"
        assert program.metadata["year"] == 1

    def test_program_add_schedule(self, sample_schedule):
        """Test adding a schedule to a program."""
        program = Program(name="Test Program")
        program.add_schedule(sample_schedule)

        assert len(program.schedules) == 1
        assert program.schedules[0] == sample_schedule

    def test_program_multiple_schedules(self, sample_schedule):
        """Test program with multiple schedules."""
        program = Program(name="Test Program")

        # Add first schedule
        program.add_schedule(sample_schedule)

        # Create and add second schedule
        schedule2_courses = [
            Course(
                code="CS101-02",
                main_code="CS101",
                name="Programming I",
                ects=6,
                course_type="Zorunlu",
                schedule={"Çarşamba": ["13:00-14:50"]}
            )
        ]
        schedule2 = Schedule(courses=schedule2_courses)
        program.add_schedule(schedule2)

        assert len(program.schedules) == 2

    def test_program_get_best_schedule(self, sample_schedule):
        """Test getting best schedule (no conflicts, most credits)."""
        program = Program(name="Test Program")

        # Add schedules with different qualities
        conflict_schedule = Schedule(courses=[
            Course(
                code="CS201-01",
                main_code="CS201",
                name="Data Structures",
                ects=6,
                course_type="Zorunlu",
                schedule={"Pazartesi": ["09:00-10:50"]}
            ),
            Course(
                code="MATH201-01",
                main_code="MATH201",
                name="Linear Algebra",
                ects=5,
                course_type="Zorunlu",
                schedule={"Pazartesi": ["09:00-10:50"]}  # Conflict!
            )
        ])

        program.add_schedule(sample_schedule)  # No conflicts, 11 credits
        program.add_schedule(conflict_schedule)  # Has conflicts, 11 credits

        best = program.get_best_schedule()
        assert best == sample_schedule  # No conflicts wins

    def test_program_statistics(self, sample_schedule):
        """Test program statistics."""
        program = Program(name="Test Program")
        program.add_schedule(sample_schedule)

        stats = program.get_statistics()

        assert stats["total_schedules"] == 1
        assert stats["name"] == "Test Program"
        assert "metadata" in stats
