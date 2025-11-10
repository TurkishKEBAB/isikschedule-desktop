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

from .models import Course, Schedule, Program, Transcript, Grade
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
            
            # Create transcripts table (Phase 7.5)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS transcripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                student_name TEXT NOT NULL,
                program TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create grades table (Phase 7.5)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transcript_id INTEGER NOT NULL,
                course_code TEXT NOT NULL,
                course_name TEXT NOT NULL,
                ects INTEGER NOT NULL,
                letter_grade TEXT NOT NULL,
                numeric_grade REAL NOT NULL,
                semester TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (transcript_id) REFERENCES transcripts (id) ON DELETE CASCADE
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
    
    # ========================================================================
    # Phase 7.5: Transcript Management Methods
    # ========================================================================
    
    def save_transcript(self, transcript: Transcript) -> int:
        """
        Save or update a transcript in the database.
        
        Args:
            transcript: Transcript object to save
            
        Returns:
            Transcript ID
        """
        if not self.conn:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            
            # Check if transcript already exists
            cursor.execute('''
            SELECT id FROM transcripts WHERE student_id = ?
            ''', (transcript.student_id,))
            
            row = cursor.fetchone()
            
            if row:
                # Update existing transcript
                transcript_id = row[0]
                cursor.execute('''
                UPDATE transcripts
                SET student_name = ?, program = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''', (transcript.student_name, transcript.program, transcript_id))
                
                # Delete existing grades
                cursor.execute('DELETE FROM grades WHERE transcript_id = ?', (transcript_id,))
            else:
                # Insert new transcript
                cursor.execute('''
                INSERT INTO transcripts (student_id, student_name, program)
                VALUES (?, ?, ?)
                ''', (transcript.student_id, transcript.student_name, transcript.program))
                
                transcript_id = cursor.lastrowid
            
            # Insert grades
            for grade in transcript.grades:
                cursor.execute('''
                INSERT INTO grades (
                    transcript_id, course_code, course_name, ects,
                    letter_grade, numeric_grade, semester
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    transcript_id, grade.course_code, grade.course_name,
                    grade.ects, grade.letter_grade, grade.numeric_grade,
                    grade.semester
                ))
            
            self.conn.commit()
            logger.info(f"Saved transcript for student {transcript.student_id}")
            
            return transcript_id
        
        except sqlite3.Error as e:
            logger.error(f"Error saving transcript: {e}")
            raise
    
    def load_transcript(self, student_id: str) -> Optional[Transcript]:
        """
        Load a transcript from the database.
        
        Args:
            student_id: Student ID to load
            
        Returns:
            Transcript object if found, None otherwise
        """
        if not self.conn:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            
            # Get transcript
            cursor.execute('''
            SELECT id, student_id, student_name, program
            FROM transcripts
            WHERE student_id = ?
            ''', (student_id,))
            
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Transcript not found for student {student_id}")
                return None
            
            transcript_id = row[0]
            student_name = row[2]
            program = row[3]
            
            # Get grades
            cursor.execute('''
            SELECT course_code, course_name, ects, letter_grade, numeric_grade, semester
            FROM grades
            WHERE transcript_id = ?
            ORDER BY created_at
            ''', (transcript_id,))
            
            grades = []
            for grade_row in cursor.fetchall():
                grade = Grade(
                    course_code=grade_row[0],
                    course_name=grade_row[1],
                    ects=grade_row[2],
                    letter_grade=grade_row[3],
                    numeric_grade=grade_row[4],
                    semester=grade_row[5]
                )
                grades.append(grade)
            
            return Transcript(
                student_id=student_id,
                student_name=student_name,
                program=program,
                grades=grades
            )
        
        except sqlite3.Error as e:
            logger.error(f"Error loading transcript: {e}")
            raise
    
    def get_all_transcripts(self) -> List[Transcript]:
        """
        Get all transcripts from database.
        
        Returns:
            List of Transcript objects
        """
        if not self.conn:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT student_id FROM transcripts ORDER BY created_at DESC')
            
            transcripts = []
            for row in cursor.fetchall():
                student_id = row[0]
                transcript = self.load_transcript(student_id)
                if transcript:
                    transcripts.append(transcript)
            
            return transcripts
        
        except sqlite3.Error as e:
            logger.error(f"Error retrieving all transcripts: {e}")
            raise
    
    def delete_transcript(self, student_id: str) -> bool:
        """
        Delete a transcript from database.
        
        Args:
            student_id: Student ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        if not self.conn:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('DELETE FROM transcripts WHERE student_id = ?', (student_id,))
            self.conn.commit()
            
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted transcript for student {student_id}")
            else:
                logger.warning(f"Transcript not found for student {student_id}")
            
            return deleted
        
        except sqlite3.Error as e:
            logger.error(f"Error deleting transcript: {e}")
            raise
