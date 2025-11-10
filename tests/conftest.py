import pytest
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_course_data():
    """Provide sample course data for testing."""
    return {
        'course_code': 'CS101',
        'course_name': 'Introduction to Programming',
        'ects': 6,
        'sections': [
            {
                'section_id': '01',
                'type': 'lecture',
                'instructor': 'Dr. Smith',
                'schedule': [
                    {'day': 'M', 'period': 1},
                    {'day': 'W', 'period': 1},
                ]
            }
        ]
    }


@pytest.fixture
def sample_schedule():
    """Provide a sample schedule for testing."""
    return [
        {
            'course_code': 'CS101',
            'section_id': '01',
            'type': 'lecture',
            'schedule': [
                {'day': 'M', 'period': 1},
                {'day': 'W', 'period': 1},
            ]
        },
        {
            'course_code': 'MATH101',
            'section_id': '01',
            'type': 'lecture',
            'schedule': [
                {'day': 'T', 'period': 2},
                {'day': 'Th', 'period': 2},
            ]
        }
    ]
