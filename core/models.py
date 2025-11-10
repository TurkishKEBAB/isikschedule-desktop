"""
Data models for SchedularV3.

Enhanced from V2 with additional features:
- Faculty, Department, Campus fields
- Better type hints
- Improved validation
- Enhanced conflict detection
"""
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional, Literal, Any
from collections import defaultdict
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Type definitions
CourseType = Literal["lecture", "ps", "lab"]
TimeSlot = Tuple[str, int]  # (day, period)


@dataclass
class Course:
    """
    Represents a university course with all its properties.

    Attributes:
        code: Unique course code (e.g., "CS101.1" or "CS101-PS1")
        main_code: Base course code without section info (e.g., "CS101")
        name: Course name/title
        ects: European Credit Transfer System credits
        course_type: Type of course (lecture, ps, lab)
        schedule: List of day-period slots this course occupies
        teacher: Name of the instructor
        has_lecture: Whether this course is a lecture
        faculty: Faculty offering the course
        department: Department offering the course
        campus: Campus where the course is held
    """
    code: str
    main_code: str
    name: str
    ects: int
    course_type: CourseType
    schedule: List[TimeSlot]
    teacher: Optional[str] = None
    has_lecture: bool = False
    faculty: str = "Unknown Faculty"
    department: str = "Unknown Department"
    campus: str = "Main"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Course':
        """Create a Course object from a dictionary."""
        return cls(
            code=data["code"],
            main_code=data["main_code"],
            name=data.get("course_name", data.get("name", "Unknown Course")),
            ects=data.get("credit", data.get("ects", data.get("ECTS", 0))),
            course_type=data.get("course_type", data.get("type", "lecture")),
            schedule=data["schedule"],
            teacher=data["teacher"],
            has_lecture=data.get("has_lecture", data.get("hasLecture", False)),
            faculty=data.get("faculty", "Unknown Faculty"),
            department=data.get("department", "Unknown Department"),
            campus=data.get("campus", "Main")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Course object to a dictionary."""
        return {
            "code": self.code,
            "main_code": self.main_code,
            "name": self.name,
            "ECTS": self.ects,
            "type": self.course_type,
            "schedule": self.schedule,
            "hasLecture": self.has_lecture,
            "teacher": self.teacher,
            "faculty": self.faculty,
            "department": self.department,
            "campus": self.campus
        }

    def conflicts_with(self, other: 'Course') -> bool:
        """
        Check if this course conflicts with another course.
        
        Args:
            other: Another Course object to check against
            
        Returns:
            True if there's a time slot conflict, False otherwise
        """
        my_slots = set(self.schedule)
        other_slots = set(other.schedule)
        return bool(my_slots.intersection(other_slots))

    def get_conflict_slots(self, other: 'Course') -> Set[TimeSlot]:
        """
        Get the specific time slots where this course conflicts with another.
        
        Args:
            other: Another Course object to check against
            
        Returns:
            Set of conflicting time slots
        """
        my_slots = set(self.schedule)
        other_slots = set(other.schedule)
        return my_slots.intersection(other_slots)

    def __str__(self) -> str:
        return f"{self.code} - {self.name} ({self.ects} ECTS)"

    def __repr__(self) -> str:
        return f"Course(code='{self.code}', name='{self.name}', ects={self.ects})"
    
    def __hash__(self) -> int:
        """Make Course hashable for use in sets and as dict keys."""
        return hash(self.code)
    
    def __eq__(self, other: object) -> bool:
        """Compare courses by their code."""
        if not isinstance(other, Course):
            return NotImplemented
        return self.code == other.code


@dataclass
class Schedule:
    """
    Represents a complete schedule containing multiple courses.

    Attributes:
        courses: List of Course objects in this schedule
    """
    courses: List[Course] = field(default_factory=list)

    @property
    def total_credits(self) -> int:
        """Calculate the total ECTS credits for this schedule."""
        return sum(course.ects for course in self.courses)

    @property
    def conflict_count(self) -> int:
        """
        Calculate the number of time slot conflicts in this schedule.
        A conflict occurs when two or more courses share the same time slot.
        """
        slot_courses: Dict[TimeSlot, List[Course]] = defaultdict(list)
        conflict_slots = set()

        # Map each time slot to courses occupying it
        for course in self.courses:
            for slot in course.schedule:
                slot_courses[slot].append(course)
                # If multiple courses in same slot, it's a conflict
                if len(slot_courses[slot]) > 1:
                    conflict_slots.add(slot)

        # Log detailed conflict information
        if conflict_slots:
            logger.warning(f"Found {len(conflict_slots)} conflict(s) in schedule:")
            for slot in sorted(conflict_slots):
                conflicting_courses = slot_courses[slot]
                course_codes = ', '.join(c.code for c in conflicting_courses)
                logger.warning(f"  {slot[0]}{slot[1]}: {course_codes}")

        return len(conflict_slots)

    @property
    def has_conflicts(self) -> bool:
        """Check if this schedule has any conflicts."""
        return self.conflict_count > 0

    def add_course(self, course: Course) -> None:
        """Add a course to the schedule."""
        self.courses.append(course)

    def remove_course(self, course_code: str) -> bool:
        """
        Remove a course by code.
        
        Args:
            course_code: Code of the course to remove
            
        Returns:
            True if course was found and removed, False otherwise
        """
        for i, course in enumerate(self.courses):
            if course.code == course_code:
                self.courses.pop(i)
                return True
        return False

    def get_courses_by_main_code(self, main_code: str) -> List[Course]:
        """Get all courses with the specified main code."""
        return [c for c in self.courses if c.main_code == main_code]

    def has_conflict_with(self, new_courses: List[Course]) -> bool:
        """Check if adding the new courses would create conflicts."""
        occupied_slots = set()
        for course in self.courses:
            for slot in course.schedule:
                occupied_slots.add(slot)

        for course in new_courses:
            for slot in course.schedule:
                if slot in occupied_slots:
                    return True
        return False

    def get_course_codes(self) -> Set[str]:
        """Get set of all course codes in the schedule."""
        return {course.code for course in self.courses}

    def get_main_codes(self) -> Set[str]:
        """Get set of all main codes in the schedule."""
        return {course.main_code for course in self.courses}

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert the schedule to a list of dictionaries."""
        return [course.to_dict() for course in self.courses]

    @classmethod
    def from_dict_list(cls, dict_list: List[Dict[str, Any]]) -> 'Schedule':
        """Create a Schedule from a list of course dictionaries."""
        return cls([Course.from_dict(course_dict) for course_dict in dict_list])

    def __len__(self) -> int:
        return len(self.courses)

    def __str__(self) -> str:
        return f"Schedule({len(self.courses)} courses, {self.total_credits} ECTS, {self.conflict_count} conflicts)"


@dataclass
class CourseGroup:
    """
    Represents a group of related course sections (lecture, PS, lab).

    Attributes:
        main_code: The common main code for all courses in this group
        courses: List of all courses in this group
    """
    main_code: str
    courses: List[Course] = field(default_factory=list)

    @property
    def lecture_courses(self) -> List[Course]:
        """Get all lecture courses in this group."""
        return [c for c in self.courses if c.course_type == "lecture"]

    @property
    def ps_courses(self) -> List[Course]:
        """Get all PS (Problem Session) courses in this group."""
        return [c for c in self.courses if c.course_type == "ps"]

    @property
    def lab_courses(self) -> List[Course]:
        """Get all lab courses in this group."""
        return [c for c in self.courses if c.course_type == "lab"]

    @property
    def has_lecture(self) -> bool:
        """Check if this group has any lecture courses."""
        return len(self.lecture_courses) > 0

    @property
    def has_ps(self) -> bool:
        """Check if this group has any PS courses."""
        return len(self.ps_courses) > 0

    @property
    def has_lab(self) -> bool:
        """Check if this group has any lab courses."""
        return len(self.lab_courses) > 0

    def __str__(self) -> str:
        return f"CourseGroup({self.main_code}, {len(self.courses)} sections)"


@dataclass
class Program:
    """
    Represents a complete program with multiple possible schedules.

    Attributes:
        name: Program name
        schedules: List of possible schedules for this program
        metadata: Additional program information
    """
    name: str
    schedules: List[Schedule] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def best_schedule(self) -> Optional[Schedule]:
        """Get the best schedule (least conflicts, highest credits)."""
        if not self.schedules:
            return None

        # Sort by conflicts (ascending), then by credits (descending)
        sorted_schedules = sorted(
            self.schedules,
            key=lambda s: (s.conflict_count, -s.total_credits)
        )
        return sorted_schedules[0]

    @property
    def conflict_free_schedules(self) -> List[Schedule]:
        """Get all schedules without conflicts."""
        return [s for s in self.schedules if s.conflict_count == 0]

    def add_schedule(self, schedule: Schedule) -> None:
        """Add a schedule to this program."""
        self.schedules.append(schedule)

    def get_statistics(self) -> Dict[str, Any]:
        """Get program statistics."""
        if not self.schedules:
            return {"total_schedules": 0}

        total_credits = [s.total_credits for s in self.schedules]
        conflict_counts = [s.conflict_count for s in self.schedules]

        return {
            "total_schedules": len(self.schedules),
            "conflict_free_schedules": len(self.conflict_free_schedules),
            "min_credits": min(total_credits),
            "max_credits": max(total_credits),
            "avg_credits": sum(total_credits) / len(total_credits),
            "min_conflicts": min(conflict_counts),
            "max_conflicts": max(conflict_counts),
            "avg_conflicts": sum(conflict_counts) / len(conflict_counts)
        }

    def __str__(self) -> str:
        return f"Program({self.name}, {len(self.schedules)} schedules)"


# Helper functions

def build_course_groups(courses: List[Course]) -> Dict[str, CourseGroup]:
    """
    Build course groups from a list of courses.

    Args:
        courses: List of Course objects

    Returns:
        Dictionary mapping main codes to CourseGroup objects
    """
    groups: Dict[str, CourseGroup] = {}

    for course in courses:
        main_code = course.main_code

        if main_code not in groups:
            groups[main_code] = CourseGroup(main_code=main_code)

        groups[main_code].courses.append(course)

    return groups


def filter_courses_by_type(courses: List[Course], course_type: CourseType) -> List[Course]:
    """
    Filter courses by type.

    Args:
        courses: List of Course objects
        course_type: Type to filter by

    Returns:
        List of courses of the specified type
    """
    return [c for c in courses if c.course_type == course_type]


def get_unique_main_codes(courses: List[Course]) -> Set[str]:
    """
    Get set of unique main codes from courses.

    Args:
        courses: List of Course objects

    Returns:
        Set of unique main codes
    """
    return {c.main_code for c in courses}


def find_course_by_code(courses: List[Course], code: str) -> Optional[Course]:
    """
    Find a course by its code.

    Args:
        courses: List of Course objects
        code: Course code to search for

    Returns:
        Course object if found, None otherwise
    """
    for course in courses:
        if course.code == code:
            return course
    return None


def get_courses_by_teacher(courses: List[Course], teacher: str) -> List[Course]:
    """
    Get all courses taught by a specific teacher.

    Args:
        courses: List of Course objects
        teacher: Teacher name to search for

    Returns:
        List of courses taught by the teacher
    """
    return [c for c in courses if c.teacher and c.teacher.lower() == teacher.lower()]


def calculate_total_credits(courses: List[Course]) -> int:
    """
    Calculate total ECTS credits for a list of courses.

    Args:
        courses: List of Course objects

    Returns:
        Total ECTS credits
    """
    return sum(c.ects for c in courses)
