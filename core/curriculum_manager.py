"""
Curriculum Manager for SchedularV3.

This module manages curriculum data for different degree programs,
providing filtering and recommendation capabilities based on student's
selected program and current semester.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class CurriculumCourse:
    """Represents a course in a curriculum."""
    code: str
    name_tr: str
    name_en: str
    ects: int
    local_credit: int
    course_type: str  # mandatory, area_elective, general_elective
    semester: int = 0

    def is_elective(self) -> bool:
        """Check if this is an elective course."""
        return self.course_type in ("area_elective", "general_elective")

    def is_mandatory(self) -> bool:
        """Check if this is a mandatory course."""
        return self.course_type == "mandatory"


@dataclass
class CurriculumProgram:
    """Represents an academic program curriculum."""
    program_code: str
    program_name_tr: str
    program_name_en: str
    degree: str  # Lisans, Yüksek Lisans, Doktora
    degree_en: str  # Undergraduate, Master's, PhD
    year: int
    faculty_tr: str
    faculty_en: str
    total_ects: int
    total_credits: int
    semesters: Dict[int, List[CurriculumCourse]] = field(default_factory=dict)

    def get_all_courses(self) -> List[CurriculumCourse]:
        """Get all courses from all semesters."""
        all_courses = []
        for courses in self.semesters.values():
            all_courses.extend(courses)
        return all_courses

    def get_mandatory_courses(self) -> List[CurriculumCourse]:
        """Get all mandatory courses."""
        return [c for c in self.get_all_courses() if c.is_mandatory()]

    def get_elective_courses(self) -> List[CurriculumCourse]:
        """Get all elective courses."""
        return [c for c in self.get_all_courses() if c.is_elective()]

    def get_semester_courses(self, semester: int) -> List[CurriculumCourse]:
        """Get courses for a specific semester."""
        return self.semesters.get(semester, [])

    def get_course_codes(self) -> Set[str]:
        """Get all course codes (excluding elective placeholders like SOFT-AE-I)."""
        return {
            c.code for c in self.get_all_courses()
            if not c.code.endswith(("-AE-I", "-AE-II", "-AE-III", "-AE-IV", "-AE-V", "-AE-VI",
                                     "-GE-I", "-GE-II", "-GE-III", "-GE-IV", "-GE-V", "-GE-VI"))
        }


class CurriculumManager:
    """Manages curriculum data for multiple programs."""

    def __init__(self, curriculum_dir: Optional[Path] = None):
        """
        Initialize the curriculum manager.

        Args:
            curriculum_dir: Directory containing curriculum JSON files.
                          If None, uses default data/curriculums directory.
        """
        if curriculum_dir is None:
            # Default to data/curriculums in the project root
            project_root = Path(__file__).resolve().parent.parent
            curriculum_dir = project_root / "data" / "curriculums"

        self.curriculum_dir = curriculum_dir
        self.programs: Dict[str, CurriculumProgram] = {}
        self._load_all_curriculums()

    def _load_all_curriculums(self) -> None:
        """Load all curriculum JSON files from the directory."""
        if not self.curriculum_dir.exists():
            logger.warning(f"Curriculum directory not found: {self.curriculum_dir}")
            return

        json_files = list(self.curriculum_dir.glob("*.json"))
        logger.info(f"Found {len(json_files)} curriculum files in {self.curriculum_dir}")

        for json_file in json_files:
            try:
                self._load_curriculum_file(json_file)
            except Exception as e:
                logger.error(f"Failed to load curriculum {json_file.name}: {e}")

    def _load_curriculum_file(self, json_path: Path) -> None:
        """Load a single curriculum JSON file."""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        info = data["program_info"]
        program = CurriculumProgram(
            program_code=info["program_code"],
            program_name_tr=info["program_name_tr"],
            program_name_en=info["program_name_en"],
            degree=info["degree"],
            degree_en=info["degree_en"],
            year=info["year"],
            faculty_tr=info["faculty_tr"],
            faculty_en=info["faculty_en"],
            total_ects=info["total_ects"],
            total_credits=info["total_credits"],
        )

        # Load semester courses
        for sem_num_str, sem_data in data["semesters"].items():
            sem_num = int(sem_num_str)
            courses = []
            for course_data in sem_data["courses"]:
                course = CurriculumCourse(
                    code=course_data["code"],
                    name_tr=course_data["name_tr"],
                    name_en=course_data["name_en"],
                    ects=course_data["ects"],
                    local_credit=course_data["local_credit"],
                    course_type=course_data["type"],
                    semester=sem_num,
                )
                courses.append(course)
            program.semesters[sem_num] = courses

        # Store by program key
        program_key = f"{info['program_code']}_{info['year']}"
        self.programs[program_key] = program
        logger.info(f"Loaded curriculum: {program.program_name_en} ({program_key})")

    def get_program(self, program_code: str, year: int = 2021) -> Optional[CurriculumProgram]:
        """
        Get a specific program curriculum.

        Args:
            program_code: Program code (e.g., "SOFT", "COMP")
            year: Curriculum year (default: 2021)

        Returns:
            CurriculumProgram or None if not found
        """
        program_key = f"{program_code}_{year}"
        return self.programs.get(program_key)

    def get_all_programs(self) -> List[CurriculumProgram]:
        """Get all loaded programs."""
        return list(self.programs.values())

    def get_program_list(self) -> List[Dict[str, str]]:
        """
        Get a list of all programs for UI display.

        Returns:
            List of dicts with keys: program_key, program_name_tr, program_name_en, degree
        """
        return [
            {
                "program_key": f"{p.program_code}_{p.year}",
                "program_code": p.program_code,
                "program_name_tr": p.program_name_tr,
                "program_name_en": p.program_name_en,
                "degree": p.degree,
                "year": p.year,
            }
            for p in self.programs.values()
        ]

    def filter_courses_by_program(
        self,
        all_course_codes: Set[str],
        program_code: str,
        year: int = 2021
    ) -> Set[str]:
        """
        Filter course codes to only include those in the program curriculum.

        Args:
            all_course_codes: All available course codes
            program_code: Program code (e.g., "SOFT", "COMP")
            year: Curriculum year

        Returns:
            Set of course codes that belong to the curriculum
        """
        program = self.get_program(program_code, year)
        if not program:
            logger.warning(f"Program {program_code}_{year} not found")
            return all_course_codes

        curriculum_codes = program.get_course_codes()

        # Match by main code (e.g., COMP1111 matches COMP1111.1, COMP1111.2, etc.)
        filtered = set()
        for code in all_course_codes:
            # Extract main code (remove section suffix)
            main_code = code.split(".")[0].split("-")[0]
            if main_code in curriculum_codes:
                filtered.add(code)

        logger.info(f"Filtered {len(filtered)} / {len(all_course_codes)} courses for {program_code}_{year}")
        return filtered


# Global instance
_curriculum_manager: Optional[CurriculumManager] = None


def get_curriculum_manager() -> CurriculumManager:
    """Get the global curriculum manager instance."""
    global _curriculum_manager
    if _curriculum_manager is None:
        _curriculum_manager = CurriculumManager()
    return _curriculum_manager


__all__ = [
    "CurriculumCourse",
    "CurriculumProgram",
    "CurriculumManager",
    "get_curriculum_manager",
]
