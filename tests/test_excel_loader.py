"""
Unit tests for Excel import/export functionality.

Tests process_excel, parse_schedule, normalize_columns, and save_courses_to_excel.
"""
import pytest
import pandas as pd
from pathlib import Path
from core.excel_loader import (
    process_excel,
    parse_schedule,
    normalize_columns,
    save_courses_to_excel
)
from core.models import Course


class TestParseSchedule:
    """Test cases for schedule parsing."""

    def test_parse_basic_schedule(self):
        """Test parsing a basic schedule string."""
        schedule_str = "Pazartesi 09:00-10:50, Çarşamba 09:00-10:50"
        result = parse_schedule(schedule_str)

        assert "Pazartesi" in result
        assert "Çarşamba" in result
        assert "09:00-10:50" in result["Pazartesi"]
        assert "09:00-10:50" in result["Çarşamba"]

    def test_parse_single_day(self):
        """Test parsing schedule with single day."""
        schedule_str = "Salı 11:00-12:50"
        result = parse_schedule(schedule_str)

        assert "Salı" in result
        assert result["Salı"] == ["11:00-12:50"]

    def test_parse_multiple_slots_same_day(self):
        """Test parsing multiple time slots on the same day."""
        schedule_str = "Pazartesi 09:00-10:50, Pazartesi 13:00-14:50"
        result = parse_schedule(schedule_str)

        assert "Pazartesi" in result
        assert len(result["Pazartesi"]) == 2
        assert "09:00-10:50" in result["Pazartesi"]
        assert "13:00-14:50" in result["Pazartesi"]

    def test_parse_empty_schedule(self):
        """Test parsing empty or invalid schedule."""
        assert parse_schedule("") == {}
        assert parse_schedule(None) == {}
        assert parse_schedule("   ") == {}

    def test_parse_with_extra_whitespace(self):
        """Test parsing schedule with extra whitespace."""
        schedule_str = "  Pazartesi   09:00-10:50  ,   Çarşamba   11:00-12:50  "
        result = parse_schedule(schedule_str)

        assert "Pazartesi" in result
        assert "Çarşamba" in result

    def test_parse_turkish_days(self):
        """Test parsing all Turkish day names."""
        schedule_str = (
            "Pazartesi 09:00-10:50, Salı 09:00-10:50, Çarşamba 09:00-10:50, "
            "Perşembe 09:00-10:50, Cuma 09:00-10:50"
        )
        result = parse_schedule(schedule_str)

        assert "Pazartesi" in result
        assert "Salı" in result
        assert "Çarşamba" in result
        assert "Perşembe" in result
        assert "Cuma" in result


class TestNormalizeColumns:
    """Test cases for column normalization."""

    def test_normalize_turkish_columns(self):
        """Test normalizing Turkish column names."""
        df = pd.DataFrame({
            "Ders Kodu": ["CS101-01"],
            "Ana Ders Kodu": ["CS101"],
            "Ders Adı": ["Programming"],
            "AKTS": [6],
            "Ders Türü": ["Zorunlu"],
            "Gün/Saat": ["Pazartesi 09:00-10:50"],
            "Öğretim Üyesi": ["Dr. Ali"]
        })

        result = normalize_columns(df)

        assert "code" in result.columns
        assert "main_code" in result.columns
        assert "name" in result.columns
        assert "ects" in result.columns
        assert "course_type" in result.columns
        assert "schedule" in result.columns
        assert "teacher" in result.columns

    def test_normalize_english_columns(self):
        """Test normalizing English column names."""
        df = pd.DataFrame({
            "Course Code": ["CS101-01"],
            "Main Course Code": ["CS101"],
            "Course Name": ["Programming"],
            "ECTS": [6],
            "Course Type": ["Mandatory"],
            "Day/Time": ["Monday 09:00-10:50"],
            "Instructor": ["Dr. Ali"]
        })

        result = normalize_columns(df)

        assert "code" in result.columns
        assert "main_code" in result.columns
        assert "name" in result.columns

    def test_normalize_mixed_columns(self):
        """Test normalizing mixed column names."""
        df = pd.DataFrame({
            "Ders Kodu": ["CS101-01"],
            "Main Course Code": ["CS101"],
            "name": ["Programming"],
            "AKTS": [6]
        })

        result = normalize_columns(df)

        assert "code" in result.columns
        assert "main_code" in result.columns
        assert "name" in result.columns
        assert "ects" in result.columns


class TestProcessExcel:
    """Test cases for Excel file processing."""

    @pytest.fixture
    def temp_excel_file(self, tmp_path):
        """Create a temporary Excel file for testing."""
        df = pd.DataFrame({
            "Ders Kodu": ["CS101-01", "MATH101-01", "PHYS101-01"],
            "Ana Ders Kodu": ["CS101", "MATH101", "PHYS101"],
            "Ders Adı": ["Programming I", "Calculus I", "Physics I"],
            "AKTS": [6, 5, 6],
            "Ders Türü": ["Zorunlu", "Zorunlu", "Zorunlu"],
            "Gün/Saat": [
                "Pazartesi 09:00-10:50, Çarşamba 09:00-10:50",
                "Salı 11:00-12:50, Perşembe 11:00-12:50",
                "Cuma 13:00-14:50"
            ],
            "Öğretim Üyesi": ["Dr. Ali Yılmaz", "Prof. Dr. Mehmet Demir", "Dr. Ayşe Kaya"]
        })

        excel_path = tmp_path / "test_courses.xlsx"
        df.to_excel(excel_path, index=False)
        return excel_path

    def test_process_excel_basic(self, temp_excel_file):
        """Test processing a basic Excel file."""
        courses = process_excel(str(temp_excel_file))

        assert len(courses) == 3
        assert all(isinstance(c, Course) for c in courses)

    def test_process_excel_course_attributes(self, temp_excel_file):
        """Test that courses have correct attributes."""
        courses = process_excel(str(temp_excel_file))

        cs_course = next(c for c in courses if c.code == "CS101-01")
        assert cs_course.main_code == "CS101"
        assert cs_course.name == "Programming I"
        assert cs_course.ects == 6
        assert cs_course.course_type == "Zorunlu"
        assert cs_course.teacher == "Dr. Ali Yılmaz"

    def test_process_excel_schedule_parsing(self, temp_excel_file):
        """Test that schedules are parsed correctly."""
        courses = process_excel(str(temp_excel_file))

        cs_course = next(c for c in courses if c.code == "CS101-01")
        assert "Pazartesi" in cs_course.schedule
        assert "Çarşamba" in cs_course.schedule
        assert "09:00-10:50" in cs_course.schedule["Pazartesi"]

    def test_process_excel_with_faculty_columns(self, tmp_path):
        """Test processing Excel with faculty/department/campus columns."""
        df = pd.DataFrame({
            "Ders Kodu": ["CS101-01"],
            "Ana Ders Kodu": ["CS101"],
            "Ders Adı": ["Programming I"],
            "AKTS": [6],
            "Ders Türü": ["Zorunlu"],
            "Gün/Saat": ["Pazartesi 09:00-10:50"],
            "Öğretim Üyesi": ["Dr. Ali"],
            "Fakülte": ["Faculty of Engineering"],
            "Bölüm": ["Computer Science"],
            "Kampüs": ["Main Campus"]
        })

        excel_path = tmp_path / "test_with_faculty.xlsx"
        df.to_excel(excel_path, index=False)

        courses = process_excel(str(excel_path))

        assert len(courses) == 1
        assert courses[0].faculty == "Faculty of Engineering"
        assert courses[0].department == "Computer Science"
        assert courses[0].campus == "Main Campus"

    def test_process_excel_missing_optional_columns(self, tmp_path):
        """Test processing Excel with only required columns."""
        df = pd.DataFrame({
            "Ders Kodu": ["CS101-01"],
            "Ana Ders Kodu": ["CS101"],
            "Ders Adı": ["Programming I"],
            "AKTS": [6],
            "Ders Türü": ["Zorunlu"],
            "Gün/Saat": ["Pazartesi 09:00-10:50"]
        })

        excel_path = tmp_path / "test_minimal.xlsx"
        df.to_excel(excel_path, index=False)

        courses = process_excel(str(excel_path))

        assert len(courses) == 1
        assert courses[0].teacher is None
        assert courses[0].faculty == "Unknown Faculty"
        assert courses[0].has_lecture is False

    def test_process_excel_invalid_file(self):
        """Test processing non-existent file."""
        with pytest.raises(FileNotFoundError):
            process_excel("non_existent_file.xlsx")

    def test_process_excel_empty_file(self, tmp_path):
        """Test processing empty Excel file."""
        df = pd.DataFrame()
        excel_path = tmp_path / "empty.xlsx"
        df.to_excel(excel_path, index=False)

        courses = process_excel(str(excel_path))
        assert len(courses) == 0


class TestSaveCoursesToExcel:
    """Test cases for exporting courses to Excel."""

    @pytest.fixture
    def sample_courses(self):
        """Create sample courses for export testing."""
        return [
            Course(
                code="CS101-01",
                main_code="CS101",
                name="Programming I",
                ects=6,
                course_type="Zorunlu",
                schedule={"Pazartesi": ["09:00-10:50"], "Çarşamba": ["09:00-10:50"]},
                teacher="Dr. Ali Yılmaz",
                has_lecture=True,
                faculty="Faculty of Engineering",
                department="Computer Science",
                campus="Main Campus"
            ),
            Course(
                code="MATH101-01",
                main_code="MATH101",
                name="Calculus I",
                ects=5,
                course_type="Zorunlu",
                schedule={"Salı": ["11:00-12:50"], "Perşembe": ["11:00-12:50"]},
                teacher="Prof. Dr. Mehmet Demir"
            )
        ]

    def test_save_courses_basic(self, sample_courses, tmp_path):
        """Test saving courses to Excel."""
        output_path = tmp_path / "output.xlsx"
        save_courses_to_excel(sample_courses, str(output_path))

        assert output_path.exists()

    def test_save_and_load_courses(self, sample_courses, tmp_path):
        """Test round-trip: save courses and load them back."""
        output_path = tmp_path / "roundtrip.xlsx"
        save_courses_to_excel(sample_courses, str(output_path))

        # Load the saved file
        loaded_courses = process_excel(str(output_path))

        assert len(loaded_courses) == len(sample_courses)

        # Check first course
        cs_course = next(c for c in loaded_courses if c.code == "CS101-01")
        assert cs_course.main_code == "CS101"
        assert cs_course.name == "Programming I"
        assert cs_course.ects == 6
        assert cs_course.teacher == "Dr. Ali Yılmaz"
        assert cs_course.faculty == "Faculty of Engineering"

    def test_save_empty_course_list(self, tmp_path):
        """Test saving empty course list."""
        output_path = tmp_path / "empty_output.xlsx"
        save_courses_to_excel([], str(output_path))

        assert output_path.exists()

        # Load and verify
        loaded_courses = process_excel(str(output_path))
        assert len(loaded_courses) == 0

    def test_save_with_turkish_characters(self, tmp_path):
        """Test saving courses with Turkish characters."""
        courses = [
            Course(
                code="TÜRK101-01",
                main_code="TÜRK101",
                name="Türk Dili I",
                ects=3,
                course_type="Zorunlu",
                schedule={"Çarşamba": ["15:00-16:50"]},
                teacher="Doç. Dr. Şebnem Öztürk",
                faculty="Edebiyat Fakültesi",
                department="Türk Dili ve Edebiyatı",
                campus="Merkez Kampüs"
            )
        ]

        output_path = tmp_path / "turkish_output.xlsx"
        save_courses_to_excel(courses, str(output_path))

        # Load and verify Turkish characters preserved
        loaded_courses = process_excel(str(output_path))
        assert len(loaded_courses) == 1
        assert loaded_courses[0].name == "Türk Dili I"
        assert loaded_courses[0].teacher == "Doç. Dr. Şebnem Öztürk"
        assert loaded_courses[0].faculty == "Edebiyat Fakültesi"

    def test_save_schedule_format(self, tmp_path):
        """Test that schedule is saved in correct format."""
        courses = [
            Course(
                code="TEST101-01",
                main_code="TEST101",
                name="Test Course",
                ects=4,
                course_type="Seçmeli",
                schedule={
                    "Pazartesi": ["09:00-10:50", "13:00-14:50"],
                    "Çarşamba": ["11:00-12:50"]
                }
            )
        ]

        output_path = tmp_path / "schedule_format.xlsx"
        save_courses_to_excel(courses, str(output_path))

        # Read the Excel file directly
        df = pd.read_excel(output_path)

        # Check schedule column formatting
        schedule_str = df.iloc[0]["Gün/Saat"]
        assert "Pazartesi" in schedule_str
        assert "09:00-10:50" in schedule_str
        assert "13:00-14:50" in schedule_str
        assert "Çarşamba" in schedule_str
