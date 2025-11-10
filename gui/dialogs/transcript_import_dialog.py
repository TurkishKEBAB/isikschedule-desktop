"""
Transcript Import Widget - Phase 7.5

Allows users to:
- Import transcript from Excel
- Add/edit/delete grades manually
- Save to database
- Export to Excel
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any

import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QFormLayout, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from core.models import Transcript, Grade
from core.academic import GPACalculator


class TranscriptImportWidget(QWidget):
    """Widget for importing and managing student transcripts."""
    
    transcript_imported = pyqtSignal(Transcript)  # Emitted when transcript loaded/updated
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.transcript: Optional[Transcript] = None
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("📥 Transcript Import & Management")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Student info section
        info_group = self._create_student_info_section()
        layout.addWidget(info_group)
        
        # Import/Add buttons
        button_layout = self._create_action_buttons()
        layout.addLayout(button_layout)
        
        # Transcript table
        table_group = self._create_transcript_table()
        layout.addWidget(table_group, stretch=1)
        
        # Summary section
        summary_layout = self._create_summary_section()
        layout.addLayout(summary_layout)
        
        # Save/Export buttons
        save_layout = self._create_save_export_buttons()
        layout.addLayout(save_layout)
    
    def _create_student_info_section(self) -> QGroupBox:
        """Create student information input fields."""
        group = QGroupBox("Student Information")
        form = QFormLayout(group)
        
        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("e.g., 23SOFT1040")
        form.addRow("Student ID:", self.student_id_input)
        
        self.student_name_input = QLineEdit()
        self.student_name_input.setPlaceholderText("e.g., Ali Yılmaz")
        form.addRow("Student Name:", self.student_name_input)
        
        self.program_input = QLineEdit()
        self.program_input.setPlaceholderText("e.g., Computer Engineering")
        form.addRow("Program:", self.program_input)
        
        return group
    
    def _create_action_buttons(self) -> QHBoxLayout:
        """Create import and add buttons."""
        layout = QHBoxLayout()
        
        self.import_excel_btn = QPushButton("📁 Import from Excel")
        self.import_excel_btn.clicked.connect(self._import_from_excel)
        self.import_excel_btn.setMinimumHeight(40)
        
        self.add_manual_btn = QPushButton("✏️ Add Grade Manually")
        self.add_manual_btn.clicked.connect(self._add_grade_manually)
        self.add_manual_btn.setMinimumHeight(40)
        
        layout.addWidget(self.import_excel_btn)
        layout.addWidget(self.add_manual_btn)
        
        return layout
    
    def _create_transcript_table(self) -> QGroupBox:
        """Create transcript table."""
        group = QGroupBox("Transcript")
        layout = QVBoxLayout(group)
        
        self.transcript_table = QTableWidget()
        self.transcript_table.setColumnCount(7)
        self.transcript_table.setHorizontalHeaderLabels([
            "Course Code", "Course Name", "ECTS", "Grade", "Numeric", "Semester", "Actions"
        ])
        
        # Configure table
        self.transcript_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.transcript_table.setAlternatingRowColors(True)
        
        # Resize columns
        header = self.transcript_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Code
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # ECTS
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Grade
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Numeric
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Semester
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Actions
        
        layout.addWidget(self.transcript_table)
        
        return group
    
    def _create_summary_section(self) -> QHBoxLayout:
        """Create summary labels (GPA, ECTS, courses)."""
        layout = QHBoxLayout()
        
        self.gpa_label = QLabel("GPA: --")
        self.gpa_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        
        self.ects_label = QLabel("Total ECTS: 0")
        self.ects_label.setFont(QFont("Segoe UI", 12))
        
        self.courses_label = QLabel("Courses: 0")
        self.courses_label.setFont(QFont("Segoe UI", 12))
        
        layout.addWidget(self.gpa_label)
        layout.addStretch()
        layout.addWidget(self.ects_label)
        layout.addStretch()
        layout.addWidget(self.courses_label)
        
        return layout
    
    def _create_save_export_buttons(self) -> QHBoxLayout:
        """Create save and export buttons."""
        layout = QHBoxLayout()
        
        self.save_db_btn = QPushButton("💾 Save to Database")
        self.save_db_btn.clicked.connect(self._save_to_database)
        self.save_db_btn.setMinimumHeight(40)
        self.save_db_btn.setStyleSheet("QPushButton { background-color: #2E7D32; color: white; font-weight: bold; }")
        
        self.export_excel_btn = QPushButton("📤 Export to Excel")
        self.export_excel_btn.clicked.connect(self._export_to_excel)
        self.export_excel_btn.setMinimumHeight(40)
        
        self.clear_btn = QPushButton("🗑️ Clear All")
        self.clear_btn.clicked.connect(self._clear_all)
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.setStyleSheet("QPushButton { color: #d32f2f; }")
        
        layout.addWidget(self.save_db_btn, stretch=2)
        layout.addWidget(self.export_excel_btn, stretch=1)
        layout.addWidget(self.clear_btn, stretch=1)
        
        return layout
    
    def _import_from_excel(self) -> None:
        """Import transcript from Excel file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Transcript",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if not file_path:
            return  # User canceled
        
        try:
            # Parse Excel file
            from core.transcript_parser import TranscriptParser
            student_info, grades = TranscriptParser.parse_excel(file_path)
            
            # Populate student info
            if student_info.get('id'):
                self.student_id_input.setText(student_info['id'])
            if student_info.get('name'):
                self.student_name_input.setText(student_info['name'])
            if student_info.get('program'):
                self.program_input.setText(student_info['program'])
            
            # Populate table
            self._populate_table(grades)
            self._update_summary()
            
            QMessageBox.information(
                self,
                "Import Successful",
                f"Imported {len(grades)} grades from:\n{file_path}"
            )
        
        except FileNotFoundError:
            QMessageBox.critical(
                self,
                "File Not Found",
                "The selected file could not be found."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Failed to import transcript:\n{str(e)}"
            )
    
    def _add_grade_manually(self) -> None:
        """Open dialog to add grade manually."""
        from gui.dialogs.add_grade_dialog import AddGradeDialog
        
        dialog = AddGradeDialog(parent=self)
        if dialog.exec():
            grade = dialog.get_grade()
            self._add_grade_to_table(grade)
            self._update_summary()
    
    def _populate_table(self, grades: List[Grade]) -> None:
        """Populate table with grades."""
        self.transcript_table.setRowCount(0)  # Clear existing rows
        
        for grade in grades:
            self._add_grade_to_table(grade)
    
    def _add_grade_to_table(self, grade: Grade) -> None:
        """Add a single grade to the table."""
        row = self.transcript_table.rowCount()
        self.transcript_table.insertRow(row)
        
        # Add cells
        self.transcript_table.setItem(row, 0, QTableWidgetItem(grade.course_code))
        self.transcript_table.setItem(row, 1, QTableWidgetItem(grade.course_name))
        self.transcript_table.setItem(row, 2, QTableWidgetItem(str(grade.ects)))
        self.transcript_table.setItem(row, 3, QTableWidgetItem(grade.letter_grade))
        self.transcript_table.setItem(row, 4, QTableWidgetItem(f"{grade.numeric_grade:.1f}"))
        self.transcript_table.setItem(row, 5, QTableWidgetItem(grade.semester))
        
        # Add action buttons
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(4, 4, 4, 4)
        
        edit_btn = QPushButton("✏️")
        edit_btn.setMaximumWidth(30)
        edit_btn.clicked.connect(lambda checked, r=row: self._edit_grade(r))
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setMaximumWidth(30)
        delete_btn.clicked.connect(lambda checked, r=row: self._delete_grade(r))
        
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        
        self.transcript_table.setCellWidget(row, 6, actions_widget)
    
    def _edit_grade(self, row: int) -> None:
        """Edit existing grade."""
        from gui.dialogs.add_grade_dialog import AddGradeDialog
        
        grade = self._get_grade_from_row(row)
        if not grade:
            return
        
        dialog = AddGradeDialog(grade=grade, parent=self)
        if dialog.exec():
            updated_grade = dialog.get_grade()
            self._update_table_row(row, updated_grade)
            self._update_summary()
    
    def _delete_grade(self, row: int) -> None:
        """Delete grade from table."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Delete this grade?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.transcript_table.removeRow(row)
            self._update_summary()
    
    def _get_grade_from_row(self, row: int) -> Optional[Grade]:
        """Get Grade object from table row."""
        if row < 0 or row >= self.transcript_table.rowCount():
            return None
        
        try:
            return Grade(
                course_code=self.transcript_table.item(row, 0).text(),
                course_name=self.transcript_table.item(row, 1).text(),
                ects=int(self.transcript_table.item(row, 2).text()),
                letter_grade=self.transcript_table.item(row, 3).text(),
                numeric_grade=float(self.transcript_table.item(row, 4).text()),
                semester=self.transcript_table.item(row, 5).text()
            )
        except (ValueError, AttributeError):
            return None
    
    def _update_table_row(self, row: int, grade: Grade) -> None:
        """Update table row with new grade data."""
        self.transcript_table.item(row, 0).setText(grade.course_code)
        self.transcript_table.item(row, 1).setText(grade.course_name)
        self.transcript_table.item(row, 2).setText(str(grade.ects))
        self.transcript_table.item(row, 3).setText(grade.letter_grade)
        self.transcript_table.item(row, 4).setText(f"{grade.numeric_grade:.1f}")
        self.transcript_table.item(row, 5).setText(grade.semester)
    
    def _get_transcript(self) -> Optional[Transcript]:
        """Build Transcript object from current UI state."""
        student_id = self.student_id_input.text().strip()
        student_name = self.student_name_input.text().strip()
        program = self.program_input.text().strip()
        
        if not student_id or not student_name or not program:
            return None
        
        # Collect grades from table
        grades = []
        for row in range(self.transcript_table.rowCount()):
            grade = self._get_grade_from_row(row)
            if grade:
                grades.append(grade)
        
        return Transcript(
            student_id=student_id,
            student_name=student_name,
            program=program,
            grades=grades
        )
    
    def _update_summary(self) -> None:
        """Update summary labels (GPA, ECTS, courses)."""
        transcript = self._get_transcript()
        
        if not transcript or not transcript.grades:
            self.gpa_label.setText("GPA: --")
            self.ects_label.setText("Total ECTS: 0")
            self.courses_label.setText("Courses: 0")
            return
        
        gpa = transcript.get_gpa()
        total_ects = transcript.get_total_ects()
        num_courses = len(transcript.grades)
        
        self.gpa_label.setText(f"GPA: {gpa:.2f}")
        self.ects_label.setText(f"Total ECTS: {total_ects}")
        self.courses_label.setText(f"Courses: {num_courses}")
        
        # Color code GPA
        if gpa >= 3.0:
            self.gpa_label.setStyleSheet("color: #2E7D32; font-weight: bold;")  # Green
        elif gpa >= 2.0:
            self.gpa_label.setStyleSheet("color: #F57C00; font-weight: bold;")  # Orange
        else:
            self.gpa_label.setStyleSheet("color: #d32f2f; font-weight: bold;")  # Red
    
    def _save_to_database(self) -> None:
        """Save current transcript to database."""
        transcript = self._get_transcript()
        
        if not transcript:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter Student ID, Name, and Program before saving."
            )
            return
        
        if not transcript.grades:
            QMessageBox.warning(
                self,
                "No Grades",
                "Please add at least one grade before saving."
            )
            return
        
        try:
            from core.database import Database
            
            db = Database()
            db.initialize()
            db.save_transcript(transcript)
            
            self.transcript = transcript
            self.transcript_imported.emit(transcript)
            
            QMessageBox.information(
                self,
                "Saved Successfully",
                f"Transcript saved for {transcript.student_name}!\n\n"
                f"GPA: {transcript.get_gpa():.2f}\n"
                f"Total ECTS: {transcript.get_total_ects()}\n"
                f"Courses: {len(transcript.grades)}"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Failed",
                f"Failed to save transcript:\n{str(e)}"
            )
    
    def _export_to_excel(self) -> None:
        """Export current transcript to Excel."""
        transcript = self._get_transcript()
        
        if not transcript or not transcript.grades:
            QMessageBox.warning(
                self,
                "No Data",
                "Transcript is empty! Please add grades first."
            )
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Transcript",
            f"transcript_{transcript.student_id}.xlsx",
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if not file_path:
            return  # User canceled
        
        try:
            # Create DataFrame
            data = [{
                'Course Code': g.course_code,
                'Course Name': g.course_name,
                'ECTS': g.ects,
                'Letter Grade': g.letter_grade,
                'Numeric Grade': g.numeric_grade,
                'Semester': g.semester
            } for g in transcript.grades]
            
            df = pd.DataFrame(data)
            
            # Add summary row
            summary = {
                'Course Code': 'SUMMARY',
                'Course Name': f'Student: {transcript.student_name} ({transcript.student_id})',
                'ECTS': transcript.get_total_ects(),
                'Letter Grade': f'GPA: {transcript.get_gpa():.2f}',
                'Numeric Grade': '',
                'Semester': transcript.program
            }
            df = pd.concat([df, pd.DataFrame([summary])], ignore_index=True)
            
            # Save to Excel
            df.to_excel(file_path, index=False)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Transcript exported to:\n{file_path}"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export transcript:\n{str(e)}"
            )
    
    def _clear_all(self) -> None:
        """Clear all data."""
        reply = QMessageBox.question(
            self,
            "Confirm Clear",
            "Clear all transcript data?\n\nThis will not delete saved data from database.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.student_id_input.clear()
            self.student_name_input.clear()
            self.program_input.clear()
            self.transcript_table.setRowCount(0)
            self._update_summary()
    
    def set_transcript(self, transcript: Transcript) -> None:
        """Load transcript into widget."""
        self.transcript = transcript
        
        # Populate student info
        self.student_id_input.setText(transcript.student_id)
        self.student_name_input.setText(transcript.student_name)
        self.program_input.setText(transcript.program)
        
        # Populate grades
        self._populate_table(transcript.grades)
        self._update_summary()


__all__ = ["TranscriptImportWidget"]
