"""
Phase 2 Integration Tests - Data Layer

Tests real Işık University Excel format import/export.
"""
import pytest
from pathlib import Path
from core.excel_loader import process_excel, save_courses_to_excel, parse_time_slot, parse_schedule
from core.models import Course, Schedule


class TestTimeSlotParsing:
    """Test time slot parsing functions."""
    
    def test_parse_single_digit_period(self):
        """Test parsing single-digit periods."""
        assert parse_time_slot("M1") == ("Monday", 1)
        assert parse_time_slot("T5") == ("Tuesday", 5)
        assert parse_time_slot("W3") == ("Wednesday", 3)
        assert parse_time_slot("F8") == ("Friday", 8)
    
    def test_parse_double_digit_period(self):
        """Test parsing double-digit periods."""
        assert parse_time_slot("M10") == ("Monday", 10)
        assert parse_time_slot("T12") == ("Tuesday", 12)
        assert parse_time_slot("W11") == ("Wednesday", 11)
    
    def test_parse_thursday(self):
        """Test parsing Thursday slots."""
        assert parse_time_slot("Th1") == ("Thursday", 1)
        assert parse_time_slot("Th5") == ("Thursday", 5)
        assert parse_time_slot("Th10") == ("Thursday", 10)
    
    def test_parse_schedule_string(self):
        """Test parsing full schedule strings."""
        result = parse_schedule("M1, M2, T3")
        assert len(result) == 3
        assert ("Monday", 1) in result
        assert ("Monday", 2) in result
        assert ("Tuesday", 3) in result
    
    def test_parse_schedule_with_thursday(self):
        """Test parsing schedules with Thursday."""
        result = parse_schedule("Th5, Th6, F7")
        assert len(result) == 3
        assert ("Thursday", 5) in result
        assert ("Thursday", 6) in result
        assert ("Friday", 7) in result
    
    def test_parse_empty_schedule(self):
        """Test parsing empty schedule."""
        assert parse_schedule("") == []
        assert parse_schedule(None) == []


class TestExcelImport:
    """Test Excel import functionality."""
    
    @pytest.fixture
    def sample_file(self):
        """Path to sample Excel file."""
        return "data/sample_isik_courses.xlsx"
    
    def test_load_excel_file(self, sample_file):
        """Test loading Excel file."""
        courses = process_excel(sample_file)
        assert len(courses) > 0
    
    def test_course_attributes(self, sample_file):
        """Test that courses have correct attributes."""
        courses = process_excel(sample_file)
        
        # Find a specific course
        comp_course = next(c for c in courses if "COMP1007" in c.code)
        
        assert comp_course.code == "COMP1007.1"
        assert comp_course.main_code == "COMP1007"
        assert "Bilgisayar" in comp_course.name
        assert comp_course.ects >= 0
        assert comp_course.teacher is not None
        assert comp_course.faculty == "Mühendislik ve Doğa Bilimleri Fakültesi"
    
    def test_schedule_parsing(self, sample_file):
        """Test that schedules are parsed correctly."""
        courses = process_excel(sample_file)
        
        # Find course with multiple slots
        comp_course = next(c for c in courses if "COMP1111.1" in c.code)
        
        assert len(comp_course.schedule) == 3
        assert all(isinstance(slot, tuple) for slot in comp_course.schedule)
        assert all(len(slot) == 2 for slot in comp_course.schedule)
    
    def test_course_type_detection(self, sample_file):
        """Test course type detection from code."""
        courses = process_excel(sample_file)
        
        # Regular course
        regular = next(c for c in courses if "COMP1111.1" in c.code)
        assert regular.course_type == "lecture"
        
        # Lab course
        lab = next(c for c in courses if "COMP1111-L" in c.code)
        assert lab.course_type == "lab"
        
        # PS course
        ps = next(c for c in courses if "-PS" in c.code)
        assert ps.course_type == "ps"


class TestScheduleCreation:
    """Test Schedule creation and conflict detection."""
    
    @pytest.fixture
    def sample_courses(self):
        """Create sample courses for testing."""
        course1 = Course(
            code="TEST1.1",
            main_code="TEST1",
            name="Test Course 1",
            ects=5,
            course_type="lecture",
            schedule=[("Monday", 1), ("Monday", 2)]
        )
        
        course2 = Course(
            code="TEST2.1",
            main_code="TEST2",
            name="Test Course 2",
            ects=6,
            course_type="lecture",
            schedule=[("Tuesday", 3), ("Tuesday", 4)]
        )
        
        return [course1, course2]
    
    def test_schedule_creation(self, sample_courses):
        """Test creating a schedule."""
        schedule = Schedule(courses=sample_courses)
        assert len(schedule.courses) == 2
        assert schedule.total_credits == 11
    
    def test_no_conflicts(self, sample_courses):
        """Test schedule with no conflicts."""
        schedule = Schedule(courses=sample_courses)
        assert schedule.conflict_count == 0
        assert schedule.has_conflicts is False
    
    def test_with_conflicts(self):
        """Test schedule with conflicts."""
        course1 = Course(
            code="TEST1.1",
            main_code="TEST1",
            name="Test Course 1",
            ects=5,
            course_type="lecture",
            schedule=[("Monday", 1), ("Monday", 2)]
        )
        
        course2 = Course(
            code="TEST2.1",
            main_code="TEST2",
            name="Test Course 2",
            ects=6,
            course_type="lecture",
            schedule=[("Monday", 1), ("Tuesday", 3)]  # Conflict on Monday 1
        )
        
        schedule = Schedule(courses=[course1, course2])
        assert schedule.conflict_count > 0
        assert schedule.has_conflicts is True


class TestExcelExport:
    """Test Excel export functionality."""
    
    def test_save_and_reload(self, tmp_path):
        """Test round-trip: save and reload courses."""
        # Create test courses
        courses = [
            Course(
                code="TEST1.1",
                main_code="TEST1",
                name="Test Course",
                ects=5,
                course_type="lecture",
                schedule=[("Monday", 1), ("Tuesday", 2)],
                teacher="John Doe",
                faculty="Test Faculty",
                campus="Test Campus"
            )
        ]
        
        # Save to Excel
        output_file = tmp_path / "test_output.xlsx"
        save_courses_to_excel(courses, str(output_file))
        
        assert output_file.exists()
        
        # Reload
        loaded = process_excel(str(output_file))
        
        assert len(loaded) == 1
        assert loaded[0].code == "TEST1.1"
        assert loaded[0].name == "Test Course"
        assert loaded[0].teacher == "John Doe"
