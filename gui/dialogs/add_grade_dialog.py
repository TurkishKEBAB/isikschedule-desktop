"""
Add/Edit Grade Dialog - Phase 7.5

Manual grade entry dialog for transcript management.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton,
    QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QLabel, QMessageBox,
    QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.models import Grade


class AddGradeDialog(QDialog):
    """Dialog for adding or editing a grade."""
    
    # Grade to numeric mapping
    GRADE_NUMERIC_MAP = {
        'AA': 4.0,
        'BA': 3.5,
        'BB': 3.0,
        'CB': 2.5,
        'CC': 2.0,
        'DC': 1.5,
        'DD': 1.0,
        'FD': 0.5,
        'FF': 0.0,
        'P': 0.0,  # Pass (not included in GPA)
        'F': 0.0,  # Fail
        'W': 0.0,  # Withdrawn
        'I': 0.0,  # Incomplete
        'NA': 0.0  # Not Applicable
    }
    
    def __init__(self, grade: Optional[Grade] = None, parent: Optional[QDialog | QWidget] = None):
        super().__init__(parent)
        self.grade = grade
        self._setup_ui()
        
        if grade:
            self._populate_fields(grade)
    
    def _setup_ui(self) -> None:
        """Initialize UI components."""
        self.setWindowTitle("Add Grade" if not self.grade else "Edit Grade")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("✏️ Grade Information")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Form
        form = self._create_form()
        layout.addLayout(form)
        
        # Buttons
        button_layout = self._create_buttons()
        layout.addLayout(button_layout)
    
    def _create_form(self) -> QFormLayout:
        """Create form fields."""
        form = QFormLayout()
        
        # Course Code
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("e.g., CS101")
        form.addRow("Course Code*:", self.code_input)
        
        # Course Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Introduction to Programming")
        form.addRow("Course Name*:", self.name_input)
        
        # ECTS Credits
        self.ects_input = QSpinBox()
        self.ects_input.setRange(1, 30)
        self.ects_input.setValue(6)
        form.addRow("ECTS Credits*:", self.ects_input)
        
        # Letter Grade
        self.grade_combo = QComboBox()
        self.grade_combo.addItems([
            'AA', 'BA', 'BB', 'CB', 'CC', 'DC', 'DD', 'FD', 'FF',
            'P', 'F', 'W', 'I', 'NA'
        ])
        self.grade_combo.currentTextChanged.connect(self._update_numeric_grade)
        form.addRow("Letter Grade*:", self.grade_combo)
        
        # Numeric Grade (auto-calculated, read-only)
        self.numeric_input = QDoubleSpinBox()
        self.numeric_input.setRange(0.0, 4.0)
        self.numeric_input.setDecimals(1)
        self.numeric_input.setReadOnly(True)
        self.numeric_input.setValue(4.0)
        self.numeric_input.setStyleSheet("background-color: #f0f0f0;")
        form.addRow("Numeric Grade:", self.numeric_input)
        
        # Semester
        self.semester_input = QLineEdit()
        self.semester_input.setPlaceholderText("e.g., 2023-2024 Fall")
        form.addRow("Semester*:", self.semester_input)
        
        # Note
        note_label = QLabel("* Required fields")
        note_label.setStyleSheet("color: #666; font-style: italic; font-size: 10px;")
        form.addRow("", note_label)
        
        return form
    
    def _create_buttons(self) -> QHBoxLayout:
        """Create action buttons."""
        layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self._save)
        self.save_btn.setMinimumHeight(35)
        self.save_btn.setStyleSheet("QPushButton { background-color: #2E7D32; color: white; font-weight: bold; }")
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setMinimumHeight(35)
        
        layout.addWidget(self.save_btn)
        layout.addWidget(self.cancel_btn)
        
        return layout
    
    def _update_numeric_grade(self, letter_grade: str) -> None:
        """Auto-calculate numeric grade from letter grade."""
        numeric = self.GRADE_NUMERIC_MAP.get(letter_grade, 0.0)
        self.numeric_input.setValue(numeric)
    
    def _populate_fields(self, grade: Grade) -> None:
        """Populate form fields with existing grade data."""
        self.code_input.setText(grade.course_code)
        self.name_input.setText(grade.course_name)
        self.ects_input.setValue(grade.ects)
        
        # Set letter grade
        index = self.grade_combo.findText(grade.letter_grade)
        if index >= 0:
            self.grade_combo.setCurrentIndex(index)
        
        self.numeric_input.setValue(grade.numeric_grade)
        self.semester_input.setText(grade.semester)
    
    def _validate_input(self) -> bool:
        """Validate form input."""
        # Check required fields
        if not self.code_input.text().strip():
            QMessageBox.warning(self, "Missing Data", "Course Code is required!")
            self.code_input.setFocus()
            return False
        
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Missing Data", "Course Name is required!")
            self.name_input.setFocus()
            return False
        
        if not self.semester_input.text().strip():
            QMessageBox.warning(self, "Missing Data", "Semester is required!")
            self.semester_input.setFocus()
            return False
        
        return True
    
    def _save(self) -> None:
        """Validate and save grade."""
        if not self._validate_input():
            return
        
        self.accept()
    
    def get_grade(self) -> Grade:
        """Get Grade object from form data."""
        return Grade(
            course_code=self.code_input.text().strip(),
            course_name=self.name_input.text().strip(),
            ects=self.ects_input.value(),
            letter_grade=self.grade_combo.currentText(),
            numeric_grade=self.numeric_input.value(),
            semester=self.semester_input.text().strip()
        )


__all__ = ["AddGradeDialog"]
