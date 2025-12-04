"""
Unit tests for ECTS limit calculation.

Tests the get_ects_limit() method in Transcript class to ensure:
1. Minimum ECTS limit is 31 for all GPA levels
2. ECTS limits correctly adjust based on GPA thresholds
3. Consistency with official Işık University regulations
"""
import pytest
from core.models import Transcript, Grade


class TestECTSLimits:
    """Test cases for ECTS limit calculation based on GPA."""

    def create_transcript_with_gpa(self, target_gpa: float, total_ects: int = 30) -> Transcript:
        """
        Helper method to create a transcript with a specific GPA.
        
        Args:
            target_gpa: Desired GPA (0.0 - 4.0)
            total_ects: Total ECTS credits for the transcript
            
        Returns:
            Transcript object with the specified GPA
        """
        transcript = Transcript(
            student_id="12345",
            student_name="Test Student",
            program="Computer Engineering"
        )
        
        # Add a single grade with the target GPA
        grade = Grade(
            course_code="TEST101",
            course_name="Test Course",
            ects=total_ects,
            letter_grade=self._gpa_to_letter(target_gpa),
            numeric_grade=target_gpa,
            semester="2024 Fall",
            is_retake=False
        )
        transcript.add_grade(grade)
        
        return transcript
    
    def _gpa_to_letter(self, gpa: float) -> str:
        """Convert numeric GPA to letter grade."""
        if gpa >= 4.0:
            return "AA"
        elif gpa >= 3.5:
            return "BA"
        elif gpa >= 3.0:
            return "BB"
        elif gpa >= 2.5:
            return "CB"
        elif gpa >= 2.0:
            return "CC"
        elif gpa >= 1.5:
            return "DC"
        elif gpa >= 1.0:
            return "DD"
        else:
            return "FF"

    def test_minimum_ects_limit_is_31(self):
        """Test that minimum ECTS limit is 31, not 30."""
        # Test with GPA = 0.0 (worst case)
        transcript = self.create_transcript_with_gpa(0.0)
        assert transcript.get_ects_limit() == 31, \
            "Minimum ECTS limit should be 31 even for GPA 0.0"
        
        # Test with GPA = 1.0
        transcript = self.create_transcript_with_gpa(1.0)
        assert transcript.get_ects_limit() == 31, \
            "ECTS limit should be 31 for GPA 1.0"

    def test_low_gpa_ects_limit(self):
        """Test ECTS limit for GPA < 2.5."""
        # GPA = 2.0 (just below threshold)
        transcript = self.create_transcript_with_gpa(2.0)
        assert transcript.get_ects_limit() == 31, \
            "ECTS limit should be 31 for GPA 2.0"
        
        # GPA = 2.49 (just below threshold)
        transcript = self.create_transcript_with_gpa(2.49)
        assert transcript.get_ects_limit() == 31, \
            "ECTS limit should be 31 for GPA 2.49"

    def test_medium_gpa_ects_limit(self):
        """Test ECTS limit for 2.5 ≤ GPA < 3.5."""
        # GPA = 2.5 (at threshold)
        transcript = self.create_transcript_with_gpa(2.5)
        assert transcript.get_ects_limit() == 37, \
            "ECTS limit should be 37 for GPA 2.5"
        
        # GPA = 3.0 (middle of range)
        transcript = self.create_transcript_with_gpa(3.0)
        assert transcript.get_ects_limit() == 37, \
            "ECTS limit should be 37 for GPA 3.0"
        
        # GPA = 3.49 (just below next threshold)
        transcript = self.create_transcript_with_gpa(3.49)
        assert transcript.get_ects_limit() == 37, \
            "ECTS limit should be 37 for GPA 3.49"

    def test_high_gpa_ects_limit(self):
        """Test ECTS limit for GPA ≥ 3.5."""
        # GPA = 3.5 (at threshold)
        transcript = self.create_transcript_with_gpa(3.5)
        assert transcript.get_ects_limit() == 42, \
            "ECTS limit should be 42 for GPA 3.5"
        
        # GPA = 3.75 (middle of range)
        transcript = self.create_transcript_with_gpa(3.75)
        assert transcript.get_ects_limit() == 42, \
            "ECTS limit should be 42 for GPA 3.75"
        
        # GPA = 4.0 (maximum)
        transcript = self.create_transcript_with_gpa(4.0)
        assert transcript.get_ects_limit() == 42, \
            "ECTS limit should be 42 for GPA 4.0"

    def test_empty_transcript_default_limit(self):
        """Test that empty transcript returns minimum limit (31 ECTS)."""
        transcript = Transcript(
            student_id="12345",
            student_name="Test Student",
            program="Computer Engineering"
        )
        
        # Empty transcript should have GPA 0.0 and return minimum limit
        assert transcript.get_gpa() == 0.0, "Empty transcript should have GPA 0.0"
        assert transcript.get_ects_limit() == 31, \
            "Empty transcript should have minimum ECTS limit of 31"

    def test_ects_limit_consistency_with_isik_data(self):
        """Test consistency with ECTS_LIMITS_BY_GPA in isik_university_data.py."""
        from core.isik_university_data import ECTS_LIMITS_BY_GPA
        
        # Verify that the data matches expected values
        assert ECTS_LIMITS_BY_GPA["freshmen"] == 31, \
            "Freshmen ECTS limit should be 31"
        assert ECTS_LIMITS_BY_GPA["low"] == 31, \
            "Low GPA ECTS limit should be 31"
        assert ECTS_LIMITS_BY_GPA["medium"] == 37, \
            "Medium GPA ECTS limit should be 37"
        assert ECTS_LIMITS_BY_GPA["high"] == 42, \
            "High GPA ECTS limit should be 42"

    def test_multiple_grades_average_gpa(self):
        """Test ECTS limit with multiple grades averaging to specific GPA."""
        transcript = Transcript(
            student_id="12345",
            student_name="Test Student",
            program="Computer Engineering"
        )
        
        # Add grades that average to GPA 3.0
        # AA (4.0) + BB (3.0) + BB (3.0) = 10.0 / 3 = 3.33
        transcript.add_grade(Grade("CS101", "Course 1", 6, "AA", 4.0, "2024 Fall"))
        transcript.add_grade(Grade("CS102", "Course 2", 6, "BB", 3.0, "2024 Fall"))
        transcript.add_grade(Grade("CS103", "Course 3", 6, "BB", 3.0, "2024 Fall"))
        
        # GPA should be around 3.33, which means limit should be 37
        gpa = transcript.get_gpa()
        assert 3.3 <= gpa <= 3.4, f"Expected GPA around 3.33, got {gpa:.2f}"
        assert transcript.get_ects_limit() == 37, \
            f"ECTS limit should be 37 for GPA {gpa:.2f}"

    def test_boundary_conditions(self):
        """Test boundary conditions for GPA thresholds."""
        # Test exact boundary at 2.5
        transcript = self.create_transcript_with_gpa(2.5)
        assert transcript.get_ects_limit() == 37, \
            "ECTS limit should be 37 exactly at GPA 2.5"
        
        # Test just below 2.5
        transcript = self.create_transcript_with_gpa(2.499)
        assert transcript.get_ects_limit() == 31, \
            "ECTS limit should be 31 just below GPA 2.5"
        
        # Test exact boundary at 3.5
        transcript = self.create_transcript_with_gpa(3.5)
        assert transcript.get_ects_limit() == 42, \
            "ECTS limit should be 42 exactly at GPA 3.5"
        
        # Test just below 3.5
        transcript = self.create_transcript_with_gpa(3.499)
        assert transcript.get_ects_limit() == 37, \
            "ECTS limit should be 37 just below GPA 3.5"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
