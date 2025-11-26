"""
Transcript Parser - Phase 7.5

Parses transcript data from Excel files.
Supports both Turkish and English column headers.
"""

from __future__ import annotations

from typing import List, Dict, Tuple, Any, Optional

import pandas as pd

from core.models import Grade


class TranscriptParser:
    """Parser for transcript Excel files."""
    
    # Column mapping: Turkish/English -> Standardized
    COLUMN_MAPPINGS = {
        # Course Code
        'course_code': ['Ders Kodu', 'Kodu', 'Course Code', 'Code', 'KODU'],
        # Course Name
        'course_name': ['Ders Adı', 'Ders', 'Course Name', 'Name', 'Ders ADI'],
        # ECTS
        'ects': ['AKTS', 'ECTS', 'Kredi', 'Credits', 'Credit', 'KREDİ'],
        # Letter Grade
        'letter_grade': ['Harf Notu', 'Harf', 'Letter Grade', 'Grade', 'NOT'],
        # Numeric Grade
        'numeric_grade': ['Sayısal Not', 'Sayısal', 'Numeric Grade', 'Numeric', 'SAYISAL'],
        # Semester
        'semester': ['Dönem', 'Yarıyıl', 'Semester', 'Term', 'DÖNEM']
    }
    
    # Grade to numeric mapping
    GRADE_NUMERIC_MAP = {
        'AA': 4.0,
        'BA': 3.5,
        'BB': 3.0,
        'CB': 2.5,
        'CC': 2.0,
        'DC': 1.5,
        'DD': 1.0,
        'FF': 0.0,
        'P': 0.0,  # Pass (not included in GPA)
        'F': 0.0,  # Fail
        'W': 0.0,  # Withdrawn
        'I': 0.0,  # Incomplete
        'NA': 0.0  # Not Applicable
    }
    
    @classmethod
    def parse_excel(cls, file_path: str) -> Tuple[Dict[str, str], List[Grade]]:
        """
        Parse transcript from Excel file.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Tuple of (student_info, grades)
            student_info: {'id': str, 'name': str, 'program': str}
            grades: List of Grade objects
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If required columns are missing
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path, engine='openpyxl')
            
            # Extract student info (usually in first few rows or separate sheet)
            student_info = cls._extract_student_info(df, file_path)
            
            # Find data start row (skip header rows)
            data_start_row = cls._find_data_start_row(df)
            
            # Extract grades data
            grades_df = df.iloc[data_start_row:]
            
            # Map columns
            column_map = cls._detect_columns(grades_df.columns)
            
            # Parse grades
            grades = cls._parse_grades(grades_df, column_map)
            
            return student_info, grades
        
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Failed to parse Excel file: {str(e)}")
    
    @classmethod
    def _extract_student_info(cls, df: pd.DataFrame, file_path: str) -> Dict[str, str]:
        """
        Extract student info from Excel file.
        
        Looks for patterns like:
        - "Student ID: 23SOFT1040"
        - "Name: Ali Yılmaz"
        - "Program: Computer Engineering"
        
        Returns dict with 'id', 'name', 'program' keys.
        """
        student_info = {
            'id': '',
            'name': '',
            'program': ''
        }
        
        # Search first 10 rows for student info
        for i in range(min(10, len(df))):
            row = df.iloc[i]
            
            for col_idx, cell in enumerate(row):
                if pd.isna(cell):
                    continue
                
                cell_str = str(cell).strip()
                
                # Student ID patterns
                if any(keyword in cell_str.lower() for keyword in ['student id', 'öğrenci no', 'numara', 'no:']):
                    # Extract ID from next cell or same cell
                    if ':' in cell_str:
                        student_info['id'] = cell_str.split(':', 1)[1].strip()
                    elif col_idx + 1 < len(row):
                        student_info['id'] = str(row.iloc[col_idx + 1]).strip()
                
                # Student Name patterns
                elif any(keyword in cell_str.lower() for keyword in ['student name', 'ad soyad', 'name:', 'isim']):
                    if ':' in cell_str:
                        student_info['name'] = cell_str.split(':', 1)[1].strip()
                    elif col_idx + 1 < len(row):
                        student_info['name'] = str(row.iloc[col_idx + 1]).strip()
                
                # Program patterns
                elif any(keyword in cell_str.lower() for keyword in ['program', 'bölüm', 'department', 'major']):
                    if ':' in cell_str:
                        student_info['program'] = cell_str.split(':', 1)[1].strip()
                    elif col_idx + 1 < len(row):
                        student_info['program'] = str(row.iloc[col_idx + 1]).strip()
        
        # Fallback: extract from filename
        if not student_info['id']:
            import re
            match = re.search(r'(\d{2}[A-Z]+\d+)', file_path)
            if match:
                student_info['id'] = match.group(1)
        
        return student_info
    
    @classmethod
    def _find_data_start_row(cls, df: pd.DataFrame) -> int:
        """
        Find the row where actual grade data starts.
        
        Looks for rows that contain grade column headers.
        """
        for i in range(min(15, len(df))):
            row = df.iloc[i]
            row_str = ' '.join(str(cell).lower() for cell in row if not pd.isna(cell))
            
            # Check if row contains common header keywords
            if any(keyword in row_str for keyword in [
                'ders kodu', 'course code', 'kodu',
                'harf notu', 'letter grade', 'grade'
            ]):
                return i + 1  # Data starts on next row
        
        # If no header found, assume data starts immediately
        return 0
    
    @classmethod
    def _detect_columns(cls, columns: pd.Index) -> Dict[str, str]:
        """
        Detect and map Excel columns to standard field names.
        
        Args:
            columns: DataFrame column names
            
        Returns:
            Dict mapping standardized field names to actual column names
            
        Raises:
            ValueError: If required columns are not found
        """
        column_map = {}
        
        # Normalize column names
        normalized_cols = {col: str(col).strip() for col in columns}
        
        # Map each field
        for field, possible_names in cls.COLUMN_MAPPINGS.items():
            found = False
            
            for col_name, normalized in normalized_cols.items():
                if any(possible.lower() in normalized.lower() for possible in possible_names):
                    column_map[field] = col_name
                    found = True
                    break
            
            # Required fields
            if not found and field in ['course_code', 'course_name', 'letter_grade']:
                raise ValueError(f"Required column '{field}' not found! Searched for: {possible_names}")
        
        return column_map
    
    @classmethod
    def _parse_grades(cls, df: pd.DataFrame, column_map: Dict[str, str]) -> List[Grade]:
        """
        Parse grades from DataFrame.
        
        Args:
            df: DataFrame with grade data
            column_map: Mapping of field names to column names
            
        Returns:
            List of Grade objects
        """
        grades = []
        
        for _, row in df.iterrows():
            try:
                # Extract required fields
                course_code = str(row[column_map['course_code']]).strip()
                course_name = str(row[column_map['course_name']]).strip()
                letter_grade = str(row[column_map['letter_grade']]).strip().upper()
                
                # Skip empty rows
                if not course_code or course_code == 'nan' or not letter_grade or letter_grade == 'NAN':
                    continue
                
                # Skip summary rows
                if any(keyword in course_code.lower() for keyword in ['toplam', 'total', 'ortalama', 'average']):
                    continue
                
                # Extract optional fields
                ects = cls._parse_ects(row, column_map)
                numeric_grade = cls._parse_numeric_grade(row, column_map, letter_grade)
                semester = cls._parse_semester(row, column_map)
                
                # Create Grade object
                grade = Grade(
                    course_code=course_code,
                    course_name=course_name,
                    ects=ects,
                    letter_grade=letter_grade,
                    numeric_grade=numeric_grade,
                    semester=semester
                )
                
                grades.append(grade)
            
            except Exception as e:
                # Skip problematic rows
                continue
        
        return grades
    
    @classmethod
    def _parse_ects(cls, row: pd.Series, column_map: Dict[str, str]) -> int:
        """Parse ECTS credits from row."""
        if 'ects' not in column_map:
            return 6  # Default ECTS
        
        try:
            ects_val = row[column_map['ects']]
            if pd.isna(ects_val):
                return 6
            return int(float(ects_val))
        except (ValueError, KeyError):
            return 6
    
    @classmethod
    def _parse_numeric_grade(cls, row: pd.Series, column_map: Dict[str, str], letter_grade: str) -> float:
        """Parse numeric grade from row or convert from letter grade."""
        # Try to get from column
        if 'numeric_grade' in column_map:
            try:
                numeric_val = row[column_map['numeric_grade']]
                if not pd.isna(numeric_val):
                    return float(numeric_val)
            except (ValueError, KeyError):
                pass
        
        # Convert from letter grade
        return cls.GRADE_NUMERIC_MAP.get(letter_grade, 0.0)
    
    @classmethod
    def _parse_semester(cls, row: pd.Series, column_map: Dict[str, str]) -> str:
        """Parse semester from row."""
        if 'semester' not in column_map:
            return "Unknown"
        
        try:
            semester_val = row[column_map['semester']]
            if pd.isna(semester_val):
                return "Unknown"
            return str(semester_val).strip()
        except (ValueError, KeyError):
            return "Unknown"


__all__ = ["TranscriptParser"]
