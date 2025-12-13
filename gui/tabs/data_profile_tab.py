"""Data input and profile configuration tab."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
    QFrame,
)

from config.settings import ISIK_BLUE_PRIMARY, RESOURCES_DIR
from core.curriculum_manager import get_curriculum_manager


class DataProfileTab(QWidget):
    """Tab for file input, student profile, recent files, and data health check."""

    file_selected = pyqtSignal(str)  # File path
    profile_updated = pyqtSignal(dict)  # Student profile data
    program_selected = pyqtSignal(str, int)  # Program code, year

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._current_file: Optional[Path] = None
        self._recent_files_path = RESOURCES_DIR / "recent_files.json"
        self._profile_path = RESOURCES_DIR / "student_profile.json"
        self._setup_ui()
        self._load_recent_files()
        self._load_profile()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Apply Işık University theme
        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {ISIK_BLUE_PRIMARY};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                color: {ISIK_BLUE_PRIMARY};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QPushButton {{
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {ISIK_BLUE_PRIMARY};
                color: white;
            }}
            QListWidget {{
                border: 1px solid #ccc;
                border-radius: 4px;
            }}
        """)

        # Two-column layout for upper section
        upper_layout = QHBoxLayout()

        # Left column: File + Recent
        left_column = QVBoxLayout()

        # 1. File Input Section
        file_group = self._create_file_section()
        left_column.addWidget(file_group)

        # 2. Recent Files Section
        recent_group = self._create_recent_files_section()
        left_column.addWidget(recent_group)

        upper_layout.addLayout(left_column, stretch=1)

        # Right column: Student Profile
        right_column = QVBoxLayout()

        # 3. Student Profile Section (NEW)
        profile_group = self._create_profile_section()
        right_column.addWidget(profile_group)

        upper_layout.addLayout(right_column, stretch=1)

        layout.addLayout(upper_layout)

        # 4. Data Health Check Section (Bottom, full width)
        health_group = self._create_health_check_section()
        layout.addWidget(health_group)

        # 5. Data Summary Section (NEW)
        summary_group = self._create_summary_section()
        layout.addWidget(summary_group)

        layout.addStretch()
        health_group = self._create_health_check_section()
        layout.addWidget(health_group)

        layout.addStretch()

    def _create_file_section(self) -> QGroupBox:
        """Create file input section."""
        group = QGroupBox("📁 Course Data File")
        layout = QVBoxLayout(group)

        # File path display
        file_layout = QHBoxLayout()

        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("No file selected...")
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setObjectName("file_path_edit")

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._on_browse_file)
        self.browse_button.setObjectName("browse_button")

        file_layout.addWidget(QLabel("Excel File:"))
        file_layout.addWidget(self.file_path_edit, stretch=1)
        file_layout.addWidget(self.browse_button)

        layout.addLayout(file_layout)

        # Help text
        help_label = QLabel("Select the Excel file containing course schedule and curriculum data.")
        help_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(help_label)

        return group

    def _create_recent_files_section(self) -> QGroupBox:
        """Create recent files section."""
        group = QGroupBox("🕒 Recent Files")
        layout = QVBoxLayout(group)

        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(150)
        self.recent_list.itemDoubleClicked.connect(self._on_recent_file_clicked)

        layout.addWidget(self.recent_list)

        clear_btn = QPushButton("Clear Recent History")
        clear_btn.setFixedWidth(150)
        clear_btn.clicked.connect(self._clear_recent_files)
        layout.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignRight)

        return group

    def _create_health_check_section(self) -> QGroupBox:
        """Create data health check section."""
        group = QGroupBox("❤️ Data Health Check")
        layout = QVBoxLayout(group)

        # Status indicators
        self.health_status_label = QLabel("No data loaded")
        self.health_status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #757575;")
        layout.addWidget(self.health_status_label)

        # Details grid
        details_layout = QHBoxLayout()

        self.total_courses_label = QLabel("Total Courses: -")
        self.valid_courses_label = QLabel("Valid: -")
        self.error_courses_label = QLabel("Errors: -")

        details_layout.addWidget(self.total_courses_label)
        details_layout.addWidget(self.valid_courses_label)
        details_layout.addWidget(self.error_courses_label)

        layout.addLayout(details_layout)

        # Progress bar for visual feedback
        self.health_progress = QProgressBar()
        self.health_progress.setTextVisible(False)
        self.health_progress.setValue(0)
        layout.addWidget(self.health_progress)

        return group

    def _create_profile_section(self) -> QGroupBox:
        """Create student profile section."""
        group = QGroupBox("👤 Student Profile")
        layout = QFormLayout(group)
        layout.setSpacing(10)

        # Program selection (NEW)
        self.program_combo = QComboBox()
        self.program_combo.addItem("-- Müfredat Seçiniz / Select Curriculum --", None)

        # Load available programs
        curriculum_mgr = get_curriculum_manager()
        for prog_info in curriculum_mgr.get_program_list():
            display_text = f"{prog_info['program_name_tr']} ({prog_info['year']})"
            self.program_combo.addItem(display_text, prog_info)

        self.program_combo.currentIndexChanged.connect(self._on_program_changed)
        layout.addRow("📖 Program:", self.program_combo)

        # GPA input
        self.gpa_spinbox = QDoubleSpinBox()
        self.gpa_spinbox.setRange(0.0, 4.0)
        self.gpa_spinbox.setSingleStep(0.1)
        self.gpa_spinbox.setDecimals(2)
        self.gpa_spinbox.setValue(2.50)
        self.gpa_spinbox.valueChanged.connect(self._on_profile_changed)
        layout.addRow("📊 GPA:", self.gpa_spinbox)

        # ECTS limit display (auto-calculated)
        self.ects_limit_label = QLabel("31 ECTS")
        self.ects_limit_label.setStyleSheet("font-weight: bold; color: #1976D2;")
        layout.addRow("📚 Max ECTS:", self.ects_limit_label)

        # Department dropdown
        self.department_combo = QComboBox()
        self.department_combo.addItems([
            "Computer Engineering",
            "Software Engineering",
            "Electrical Engineering",
            "Architecture",
            "Interior Architecture",
            "Industrial Design",
            "Business Administration",
            "Economics",
            "Psychology",
            "Other"
        ])
        self.department_combo.setEditable(True)
        self.department_combo.currentTextChanged.connect(self._on_profile_changed)
        layout.addRow("🎓 Department:", self.department_combo)

        # Current semester
        self.semester_spinbox = QSpinBox()
        self.semester_spinbox.setRange(1, 12)
        self.semester_spinbox.setValue(1)
        self.semester_spinbox.valueChanged.connect(self._on_profile_changed)
        layout.addRow("📅 Semester:", self.semester_spinbox)

        # Save profile button
        save_btn = QPushButton("💾 Save Profile")
        save_btn.clicked.connect(self._save_profile)
        layout.addRow("", save_btn)

        return group

    def _create_summary_section(self) -> QGroupBox:
        """Create data summary section with visual statistics."""
        group = QGroupBox("📊 Data Summary")
        layout = QGridLayout(group)

        # Placeholder labels for statistics
        self.summary_mandatory_label = QLabel("Zorunlu: -")
        self.summary_mandatory_label.setStyleSheet("font-size: 12px; padding: 5px;")

        self.summary_elective_label = QLabel("Seçmeli: -")
        self.summary_elective_label.setStyleSheet("font-size: 12px; padding: 5px;")

        self.summary_total_ects_label = QLabel("Toplam ECTS: -")
        self.summary_total_ects_label.setStyleSheet("font-size: 12px; padding: 5px;")

        self.summary_faculties_label = QLabel("Fakülte: -")
        self.summary_faculties_label.setStyleSheet("font-size: 12px; padding: 5px;")

        layout.addWidget(self.summary_mandatory_label, 0, 0)
        layout.addWidget(self.summary_elective_label, 0, 1)
        layout.addWidget(self.summary_total_ects_label, 1, 0)
        layout.addWidget(self.summary_faculties_label, 1, 1)

        return group

    def _on_program_changed(self, index: int) -> None:
        """Handle program selection change."""
        prog_info = self.program_combo.itemData(index)
        if prog_info:
            program_code = prog_info["program_code"]
            year = prog_info["year"]
            self.program_selected.emit(program_code, year)
            print(f"Program selected: {prog_info['program_name_en']} ({year})")

    def _on_profile_changed(self) -> None:
        """Handle profile field changes."""
        gpa = self.gpa_spinbox.value()

        # Calculate ECTS limit based on GPA (Işık University rules)
        if gpa >= 3.50:
            ects_limit = 43
        elif gpa >= 2.50:
            ects_limit = 37
        else:
            ects_limit = 31

        self.ects_limit_label.setText(f"{ects_limit} ECTS")

        # Emit profile update
        profile = self.get_profile()
        self.profile_updated.emit(profile)

    def get_profile(self) -> dict:
        """Get current student profile."""
        gpa = self.gpa_spinbox.value()
        if gpa >= 3.50:
            ects_limit = 43
        elif gpa >= 2.50:
            ects_limit = 37
        else:
            ects_limit = 31

        return {
            "gpa": gpa,
            "ects_limit": ects_limit,
            "department": self.department_combo.currentText(),
            "semester": self.semester_spinbox.value(),
        }

    def _save_profile(self) -> None:
        """Save profile to file."""
        profile = self.get_profile()
        try:
            self._profile_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._profile_path, "w", encoding="utf-8") as f:
                json.dump(profile, f, indent=2)
            QMessageBox.information(self, "Saved", "Profile saved successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save profile: {e}")

    def _load_profile(self) -> None:
        """Load profile from file."""
        if not self._profile_path.exists():
            return

        try:
            with open(self._profile_path, "r", encoding="utf-8") as f:
                profile = json.load(f)
                self.gpa_spinbox.setValue(profile.get("gpa", 2.50))
                dept = profile.get("department", "")
                idx = self.department_combo.findText(dept)
                if idx >= 0:
                    self.department_combo.setCurrentIndex(idx)
                else:
                    self.department_combo.setCurrentText(dept)
                self.semester_spinbox.setValue(profile.get("semester", 1))
        except Exception as e:
            print(f"Error loading profile: {e}")

    def update_data_summary(self, courses: list) -> None:
        """Update data summary with loaded courses."""
        if not courses:
            self.summary_mandatory_label.setText("Zorunlu: -")
            self.summary_elective_label.setText("Seçmeli: -")
            self.summary_total_ects_label.setText("Toplam ECTS: -")
            self.summary_faculties_label.setText("Fakülte: -")
            return

        mandatory = len([c for c in courses if c.course_type and "zorunlu" in c.course_type.lower()])
        elective = len([c for c in courses if c.course_type and "seçmeli" in c.course_type.lower()])
        total_ects = sum(c.ects for c in courses)
        faculties = len(set(c.faculty for c in courses if c.faculty))

        self.summary_mandatory_label.setText(f"📕 Zorunlu: {mandatory}")
        self.summary_elective_label.setText(f"📗 Seçmeli: {elective}")
        self.summary_total_ects_label.setText(f"📚 Toplam ECTS: {total_ects}")
        self.summary_faculties_label.setText(f"🏛️ Fakülte: {faculties}")

    def _on_browse_file(self) -> None:
        """Handle file browse button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Course Data File",
            str(Path.home()),
            "Excel Files (*.xlsx *.xls);;All Files (*.*)",
        )

        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path: str) -> None:
        """Load a file and update UI."""
        path = Path(file_path)
        if not path.exists():
            QMessageBox.warning(self, "Error", "File does not exist!")
            return

        self._current_file = path
        self.file_path_edit.setText(str(path))
        self._add_to_recent_files(str(path))

        # Emit signal for main window to process
        self.file_selected.emit(str(path))

        # Reset health check (will be updated by main window)
        self.health_status_label.setText("Loading and analyzing...")
        self.health_status_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        self.health_progress.setValue(50)

    def update_health_status(self, total: int, valid: int, errors: int) -> None:
        """Update the health check section with real data."""
        self.total_courses_label.setText(f"Total Courses: {total}")
        self.valid_courses_label.setText(f"Valid: {valid}")
        self.error_courses_label.setText(f"Errors: {errors}")

        if errors == 0 and total > 0:
            self.health_status_label.setText("✅ Data Healthy")
            self.health_status_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px;")
            self.health_progress.setValue(100)
            self.health_progress.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
        elif total > 0:
            self.health_status_label.setText(f"⚠️ Issues Found ({errors} errors)")
            self.health_status_label.setStyleSheet("color: #FFC107; font-weight: bold; font-size: 14px;")
            self.health_progress.setValue(100)
            self.health_progress.setStyleSheet("QProgressBar::chunk { background-color: #FFC107; }")
        else:
            self.health_status_label.setText("❌ No Data Found")
            self.health_status_label.setStyleSheet("color: #F44336; font-weight: bold; font-size: 14px;")
            self.health_progress.setValue(0)

    def _load_recent_files(self) -> None:
        """Load recent files from JSON."""
        self.recent_list.clear()
        if not self._recent_files_path.exists():
            return

        try:
            with open(self._recent_files_path, "r", encoding="utf-8") as f:
                files = json.load(f)
                for file_path in files:
                    if os.path.exists(file_path):
                        self.recent_list.addItem(file_path)
        except Exception as e:
            print(f"Error loading recent files: {e}")

    def _add_to_recent_files(self, file_path: str) -> None:
        """Add file to recent list and save."""
        # Update UI
        items = []
        for i in range(self.recent_list.count()):
            item = self.recent_list.item(i)
            if item:
                items.append(item.text())

        if file_path in items:
            items.remove(file_path)

        items.insert(0, file_path)
        items = items[:10]  # Keep last 10

        self.recent_list.clear()
        self.recent_list.addItems(items)

        # Save to file
        self._save_recent_files(items)

    def _save_recent_files(self, files: List[str]) -> None:
        """Save recent files list to JSON."""
        try:
            self._recent_files_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._recent_files_path, "w", encoding="utf-8") as f:
                json.dump(files, f, indent=2)
        except Exception as e:
            print(f"Error saving recent files: {e}")

    def _on_recent_file_clicked(self, item: QListWidgetItem) -> None:
        """Handle click on recent file."""
        self.load_file(item.text())

    def _clear_recent_files(self) -> None:
        """Clear recent files history."""
        self.recent_list.clear()
        self._save_recent_files([])


__all__ = ["DataProfileTab"]
