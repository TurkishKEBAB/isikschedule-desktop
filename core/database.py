"""
Database integration for SchedularV3.

SQLite-based persistence layer for courses, schedules, and programs.
Enhanced from V2 with better error handling and type hints.
"""
import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from .models import Course, Schedule, Program
from config.settings import DATABASE_PATH

# Set up logging
logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager for course scheduler application."""

    def __init__(self, db_path: Path = DATABASE_PATH):
        """
        Initialize the database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """Connect to the database, creating it if it doesn't exist."""
        try:
            # Ensure parent directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed")

    def __enter__(self):
        """Support context manager protocol for 'with' statement."""
        if not self.conn:
            self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure the database connection is closed when exiting context."""
        self.close()

    def initialize(self) -> None:
        """Initialize the database schema, creating tables if they don't exist."""
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()

            # Create courses table with additional fields
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                main_code TEXT NOT NULL,
                name TEXT NOT NULL,
                ects INTEGER NOT NULL,
                course_type TEXT NOT NULL,
                schedule TEXT NOT NULL,
                teacher TEXT,
                has_lecture BOOLEAN NOT NULL DEFAULT 0,
                faculty TEXT DEFAULT 'Unknown Faculty',
                department TEXT DEFAULT 'Unknown Department',
                campus TEXT DEFAULT 'Main',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Create schedules table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                total_credits INTEGER NOT NULL,
                conflict_count INTEGER NOT NULL,
                courses TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Create programs table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Create program_schedules join table (many-to-many)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS program_schedules (
                program_id INTEGER NOT NULL,
                schedule_id INTEGER NOT NULL,
                FOREIGN KEY (program_id) REFERENCES programs (id) ON DELETE CASCADE,
                FOREIGN KEY (schedule_id) REFERENCES schedules (id) ON DELETE CASCADE,
                PRIMARY KEY (program_id, schedule_id)
            )
            ''')

            # Create indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_courses_main_code ON courses(main_code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_courses_code ON courses(code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedules_name ON schedules(name)')

            self.conn.commit()
            logger.info("Database schema initialized")
        except sqlite3.Error as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Database initialization error: {e}")
            raise

    def save_course(self, course: Course) -> int:
        """
        Save a course to the database.

        Args:
            course: Course object to save

        Returns:
            ID of the saved course record
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()

            cursor.execute('''
            INSERT OR REPLACE INTO courses 
            (code, main_code, name, ects, course_type, schedule, teacher, has_lecture, 
             faculty, department, campus)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                course.code,
                course.main_code,
                course.name,
                course.ects,
                course.course_type,
                json.dumps(course.schedule),
                course.teacher,
                course.has_lecture,
                course.faculty,
                course.department,
                course.campus
            ))

            self.conn.commit()
            course_id = cursor.lastrowid
            logger.debug(f"Saved course {course.code} (ID: {course_id})")
            return course_id
        except sqlite3.Error as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error saving course {course.code}: {e}")
            raise

    def save_courses(self, courses: List[Course]) -> None:
        """
        Save multiple courses to the database.

        Args:
            courses: List of Course objects to save
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()

            for course in courses:
                cursor.execute('''
                INSERT OR REPLACE INTO courses 
                (code, main_code, name, ects, course_type, schedule, teacher, has_lecture,
                 faculty, department, campus)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    course.code,
                    course.main_code,
                    course.name,
                    course.ects,
                    course.course_type,
                    json.dumps(course.schedule),
                    course.teacher,
                    course.has_lecture,
                    course.faculty,
                    course.department,
                    course.campus
                ))

            self.conn.commit()
            logger.info(f"Saved {len(courses)} courses to database")
        except sqlite3.Error as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error saving courses batch: {e}")
            raise

    def get_all_courses(self) -> List[Course]:
        """
        Retrieve all courses from the database.

        Returns:
            List of Course objects
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM courses ORDER BY code')

            courses = []
            for row in cursor.fetchall():
                course_dict = dict(row)
                course_dict["schedule"] = json.loads(course_dict["schedule"])
                courses.append(Course.from_dict(course_dict))

            logger.debug(f"Retrieved {len(courses)} courses from database")
            return courses
        except sqlite3.Error as e:
            logger.error(f"Error retrieving courses: {e}")
            raise

    def get_courses_by_main_code(self, main_code: str) -> List[Course]:
        """
        Retrieve courses with a specific main code.

        Args:
            main_code: Main course code to search for

        Returns:
            List of matching Course objects
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM courses WHERE main_code = ? ORDER BY code', (main_code,))

            courses = []
            for row in cursor.fetchall():
                course_dict = dict(row)
                course_dict["schedule"] = json.loads(course_dict["schedule"])
                courses.append(Course.from_dict(course_dict))

            return courses
        except sqlite3.Error as e:
            logger.error(f"Error retrieving courses by main code {main_code}: {e}")
            raise

    def get_course_by_code(self, code: str) -> Optional[Course]:
        """
        Retrieve a specific course by code.

        Args:
            code: Course code to search for

        Returns:
            Course object or None if not found
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM courses WHERE code = ?', (code,))

            row = cursor.fetchone()
            if not row:
                return None

            course_dict = dict(row)
            course_dict["schedule"] = json.loads(course_dict["schedule"])
            return Course.from_dict(course_dict)
        except sqlite3.Error as e:
            logger.error(f"Error retrieving course {code}: {e}")
            raise

    def delete_course(self, code: str) -> bool:
        """
        Delete a course by code.

        Args:
            code: Course code to delete

        Returns:
            True if course was deleted, False if not found
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM courses WHERE code = ?', (code,))
            self.conn.commit()

            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted course {code}")
            return deleted
        except sqlite3.Error as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error deleting course {code}: {e}")
            raise

    def clear_all_courses(self) -> None:
        """Delete all courses from the database."""
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM courses')
            self.conn.commit()
            logger.info("Cleared all courses from database")
        except sqlite3.Error as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error clearing courses: {e}")
            raise

    def save_schedule(self, schedule: Schedule, name: str = "") -> int:
        """
        Save a schedule to the database.

        Args:
            schedule: Schedule object to save
            name: Optional name for the schedule

        Returns:
            ID of the saved schedule record
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()

            if not name:
                name = f"Schedule {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            cursor.execute('''
            INSERT INTO schedules 
            (name, total_credits, conflict_count, courses)
            VALUES (?, ?, ?, ?)
            ''', (
                name,
                schedule.total_credits,
                schedule.conflict_count,
                json.dumps([c.code for c in schedule.courses])
            ))

            self.conn.commit()
            schedule_id = cursor.lastrowid
            logger.info(f"Saved schedule '{name}' (ID: {schedule_id})")
            return schedule_id
        except sqlite3.Error as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error saving schedule {name}: {e}")
            raise

    def get_schedule(self, schedule_id: int) -> Optional[Schedule]:
        """
        Retrieve a schedule by ID.

        Args:
            schedule_id: ID of the schedule to retrieve

        Returns:
            Schedule object or None if not found
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM schedules WHERE id = ?', (schedule_id,))

            row = cursor.fetchone()
            if not row:
                return None

            schedule_dict = dict(row)
            course_codes = json.loads(schedule_dict["courses"])

            # Retrieve all referenced courses
            course_list = []
            for code in course_codes:
                course = self.get_course_by_code(code)
                if course:
                    course_list.append(course)

            return Schedule(courses=course_list)
        except sqlite3.Error as e:
            logger.error(f"Error retrieving schedule {schedule_id}: {e}")
            raise

    def get_all_schedules(self) -> List[tuple]:
        """
        Get all schedules (ID and name only).

        Returns:
            List of tuples (id, name, total_credits, conflict_count, created_at)
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, name, total_credits, conflict_count, created_at FROM schedules ORDER BY created_at DESC')
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error retrieving schedules: {e}")
            raise

    def save_program(self, program: Program) -> int:
        """
        Save a program to the database.

        Args:
            program: Program object to save

        Returns:
            ID of the saved program record
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()

            cursor.execute('''
            INSERT INTO programs 
            (name, metadata)
            VALUES (?, ?)
            ''', (
                program.name,
                json.dumps(program.metadata)
            ))

            program_id = cursor.lastrowid

            # Save each schedule and link it to the program
            for schedule in program.schedules:
                schedule_id = self.save_schedule(schedule, f"{program.name} Schedule")

                cursor.execute('''
                INSERT INTO program_schedules (program_id, schedule_id)
                VALUES (?, ?)
                ''', (program_id, schedule_id))

            self.conn.commit()
            logger.info(f"Saved program '{program.name}' (ID: {program_id})")
            return program_id
        except sqlite3.Error as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error saving program {program.name}: {e}")
            raise

    def get_program(self, program_id: int) -> Optional[Program]:
        """
        Retrieve a program by ID.

        Args:
            program_id: ID of the program to retrieve

        Returns:
            Program object or None if not found
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM programs WHERE id = ?', (program_id,))

            row = cursor.fetchone()
            if not row:
                return None

            program_dict = dict(row)
            name = program_dict["name"]
            metadata = json.loads(program_dict["metadata"]) if program_dict["metadata"] else {}

            # Create program
            program = Program(name=name, metadata=metadata)

            # Retrieve linked schedules
            cursor.execute('''
            SELECT schedule_id FROM program_schedules
            WHERE program_id = ?
            ''', (program_id,))

            for row in cursor.fetchall():
                schedule_id = row[0]
                schedule = self.get_schedule(schedule_id)
                if schedule:
                    program.add_schedule(schedule)

            return program
        except sqlite3.Error as e:
            logger.error(f"Error retrieving program {program_id}: {e}")
            raise

    def get_all_programs(self) -> List[Program]:
        """
        Retrieve all programs from the database.

        Returns:
            List of Program objects
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM programs ORDER BY created_at DESC')

            programs = []
            for row in cursor.fetchall():
                program_id = row[0]
                program = self.get_program(program_id)
                if program:
                    programs.append(program)

            return programs
        except sqlite3.Error as e:
            logger.error(f"Error retrieving all programs: {e}")
            raise
