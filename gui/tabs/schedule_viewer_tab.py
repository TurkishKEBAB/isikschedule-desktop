"""Schedule viewer tab with comparison and export features."""

from __future__ import annotations

from typing import Dict, List, Optional

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from core.models import Schedule, Transcript
from gui.dialogs import AlgorithmComparisonDialog
from gui.widgets import ScheduleGrid
import reporting

# Işık University ECTS limits
try:
    from config.settings import ECTS_LIMITS_BY_GPA
    ISIK_ECTS_AVAILABLE = True
except ImportError:
    ISIK_ECTS_AVAILABLE = False
    ECTS_LIMITS_BY_GPA = {"low": 31, "medium": 37, "high": 42}  # Fallback


class ScheduleViewerTab(QWidget):
    """Tab for viewing and comparing generated schedules."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._schedules: List[Schedule] = []
        self._algorithm_results: Dict[str, List[Schedule]] = {}
        self._transcript: Optional[Transcript] = None
        self._current_gpa: float = 0.0
        self._user_selected_max_ects: int = 31  # Store user's selected max ECTS from algorithm selector
        self._setup_ui()

    def set_transcript(self, transcript: Optional[Transcript]) -> None:
        """Set student transcript for ECTS limit calculation."""
        self._transcript = transcript
        if transcript:
            from core.academic import GPACalculator
            calculator = GPACalculator()
            self._current_gpa = calculator.calculate_gpa(transcript.grades)
            self._update_ects_display()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Schedule selection
        selection_group = self._create_selection_section()
        layout.addWidget(selection_group)

        # Schedule display
        display_group = self._create_display_section()
        layout.addWidget(display_group, stretch=1)

        # Statistics
        stats_group = self._create_stats_section()
        layout.addWidget(stats_group)

        # Export actions
        export_group = self._create_export_section()
        layout.addWidget(export_group)

    def _create_selection_section(self) -> QGroupBox:
        """Create schedule selection controls."""
        group = QGroupBox("📋 Schedule Selection")
        layout = QHBoxLayout(group)

        self.schedule_combo = QComboBox()
        self.schedule_combo.currentIndexChanged.connect(self._on_schedule_changed)

        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItem("All Algorithms")
        self.algorithm_combo.currentTextChanged.connect(self._filter_by_algorithm)

        layout.addWidget(QLabel("Schedule:"))
        layout.addWidget(self.schedule_combo, stretch=1)
        layout.addWidget(QLabel("Filter:"))
        layout.addWidget(self.algorithm_combo)

        return group

    def _create_display_section(self) -> QGroupBox:
        """Create schedule display area with manual edit features."""
        group = QGroupBox("📅 Weekly Schedule")
        layout = QHBoxLayout(group)  # Changed to horizontal layout

        # Schedule grid (left side)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Manual Edit Toolbar
        toolbar_layout = QHBoxLayout()

        self.edit_mode_btn = QPushButton("✏️ Edit Mode")
        self.edit_mode_btn.setCheckable(True)
        self.edit_mode_btn.setToolTip("Enable manual editing of schedule")
        self.edit_mode_btn.toggled.connect(self._on_edit_mode_toggled)
        toolbar_layout.addWidget(self.edit_mode_btn)

        self.pin_course_btn = QPushButton("📌 Pin Selected")
        self.pin_course_btn.setToolTip("Pin the selected course so it won't be changed")
        self.pin_course_btn.clicked.connect(self._pin_selected_course)
        self.pin_course_btn.setEnabled(False)
        toolbar_layout.addWidget(self.pin_course_btn)

        self.unpin_all_btn = QPushButton("🔓 Unpin All")
        self.unpin_all_btn.setToolTip("Remove all pinned courses")
        self.unpin_all_btn.clicked.connect(self._unpin_all_courses)
        toolbar_layout.addWidget(self.unpin_all_btn)

        self.swap_section_btn = QPushButton("🔄 Swap Section")
        self.swap_section_btn.setToolTip("Swap to a different section of the selected course")
        self.swap_section_btn.clicked.connect(self._swap_course_section)
        self.swap_section_btn.setEnabled(False)
        toolbar_layout.addWidget(self.swap_section_btn)

        toolbar_layout.addStretch()

        # Pinned courses indicator
        self.pinned_label = QLabel("📌 Pinned: 0")
        self.pinned_label.setStyleSheet("color: #1976d2; font-weight: bold;")
        toolbar_layout.addWidget(self.pinned_label)

        left_layout.addLayout(toolbar_layout)

        scroll = QScrollArea()
        self.schedule_grid = ScheduleGrid()
        self.schedule_grid.course_clicked.connect(self._on_course_clicked)
        scroll.setWidget(self.schedule_grid)
        scroll.setWidgetResizable(True)

        left_layout.addWidget(scroll, stretch=1)

        # Course details panel (right side)
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)

        details_label = QLabel("<b>📚 Course Details</b>")
        details_layout.addWidget(details_label)

        self.course_details = QTextEdit()
        self.course_details.setReadOnly(True)
        self.course_details.setMaximumWidth(300)
        self.course_details.setPlainText("Click on a course to view details")
        details_layout.addWidget(self.course_details)

        # Pin status area
        pin_status_label = QLabel("<b>📌 Pinned Courses</b>")
        details_layout.addWidget(pin_status_label)

        self.pinned_list = QTextEdit()
        self.pinned_list.setReadOnly(True)
        self.pinned_list.setMaximumHeight(100)
        self.pinned_list.setPlainText("No pinned courses")
        self.pinned_list.setStyleSheet("background-color: #fff3e0; border-radius: 5px;")
        details_layout.addWidget(self.pinned_list)

        layout.addWidget(left_widget, stretch=3)
        layout.addWidget(details_widget, stretch=1)

        return group

    def _create_stats_section(self) -> QGroupBox:
        """Create statistics display."""
        group = QGroupBox("📊 Statistics & ECTS Tracking")
        layout = QVBoxLayout(group)

        # ECTS limit display (Işık University)
        if ISIK_ECTS_AVAILABLE:
            # First row: GPA-based ECTS info
            ects_info_layout = QHBoxLayout()

            self.gpa_ects_label = QLabel("GPA 0.00 → Max 31 ECTS")
            self.gpa_ects_label.setFont(QFont("Segoe UI", 9))
            self.gpa_ects_label.setStyleSheet("color: #757575;")
            ects_info_layout.addWidget(self.gpa_ects_label)

            ects_info_layout.addStretch()

            # Modify Max ECTS checkbox
            self.modify_ects_checkbox = QCheckBox("Modify Max ECTS")
            self.modify_ects_checkbox.setToolTip("Check to manually override GPA-based ECTS limit")
            self.modify_ects_checkbox.stateChanged.connect(self._on_modify_ects_toggled)
            ects_info_layout.addWidget(self.modify_ects_checkbox)

            # Custom ECTS spinbox (disabled by default)
            self.custom_ects_spinbox = QSpinBox()
            self.custom_ects_spinbox.setRange(30, 45)
            self.custom_ects_spinbox.setValue(37)
            self.custom_ects_spinbox.setSuffix(" ECTS")
            self.custom_ects_spinbox.setEnabled(False)
            self.custom_ects_spinbox.setToolTip("Set custom ECTS limit (30-45)")
            self.custom_ects_spinbox.valueChanged.connect(self._on_custom_ects_changed)
            ects_info_layout.addWidget(self.custom_ects_spinbox)

            layout.addLayout(ects_info_layout)

            # Second row: Current ECTS tracking
            ects_limit_layout = QHBoxLayout()

            ects_limit_layout.addWidget(QLabel("<b>Max ECTS:</b>"))

            self.ects_limit_label = QLabel("37 ECTS")
            self.ects_limit_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.ects_limit_label.setStyleSheet("color: #1976D2;")
            ects_limit_layout.addWidget(self.ects_limit_label)

            ects_limit_layout.addWidget(QLabel("Current:"))
            self.current_ects_label = QLabel("0 ECTS")
            self.current_ects_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            ects_limit_layout.addWidget(self.current_ects_label)

            ects_limit_layout.addStretch()

            # Progress bar
            self.ects_progress = QProgressBar()
            self.ects_progress.setMaximum(100)
            self.ects_progress.setFormat("%p%")
            self.ects_progress.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #BDBDBD;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                }
            """)
            ects_limit_layout.addWidget(self.ects_progress, stretch=1)

            layout.addLayout(ects_limit_layout)

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(100)
        self.stats_text.setPlainText("No schedule selected")

        layout.addWidget(self.stats_text)

        return group

    def _on_modify_ects_toggled(self, state):
        """Handle Modify Max ECTS checkbox state change."""
        is_checked = (state == Qt.CheckState.Checked.value)

        # Enable/disable custom spinbox
        if hasattr(self, 'custom_ects_spinbox'):
            self.custom_ects_spinbox.setEnabled(is_checked)

        # Update ECTS display
        self._update_ects_display()

    def _on_custom_ects_changed(self, value):
        """Handle custom ECTS value change."""
        if self.modify_ects_checkbox.isChecked():
            self._update_ects_display()

    def _update_ects_display(self):
        """Update ECTS limit display based on GPA or custom value."""
        if not ISIK_ECTS_AVAILABLE or not hasattr(self, 'ects_limit_label'):
            return

        # Determine max ECTS
        if hasattr(self, 'modify_ects_checkbox') and self.modify_ects_checkbox.isChecked():
            # Use custom value from spinbox
            max_ects = self.custom_ects_spinbox.value()
        else:
            # Use GPA-based limit
            max_ects = self._get_max_ects_for_gpa(self._current_gpa)

            # Update custom spinbox to match GPA-based value (for reference)
            if hasattr(self, 'custom_ects_spinbox'):
                self.custom_ects_spinbox.setValue(max_ects)

        # Update GPA info label
        if hasattr(self, 'gpa_ects_label'):
            gpa_based_ects = self._get_max_ects_for_gpa(self._current_gpa)
            if self._current_gpa >= 3.50:
                gpa_range = "GPA ≥ 3.50"
            elif self._current_gpa >= 2.50:
                gpa_range = "2.50 ≤ GPA < 3.50"
            else:
                gpa_range = "GPA < 2.50"

            self.gpa_ects_label.setText(f"{gpa_range} → Max {gpa_based_ects} ECTS")

        # Update max ECTS label
        self.ects_limit_label.setText(f"{max_ects} ECTS")

        # Update progress bar maximum
        if hasattr(self, 'ects_progress'):
            self.ects_progress.setMaximum(max_ects)

    def _get_max_ects_for_gpa(self, gpa: float) -> int:
        """Get maximum ECTS allowed based on GPA (Işık University rules)."""
        if not ISIK_ECTS_AVAILABLE:
            return 43  # Default

        if gpa >= 3.50:
            return ECTS_LIMITS_BY_GPA["high"]  # 43
        elif gpa >= 2.50:
            return ECTS_LIMITS_BY_GPA["medium"]  # 37
        else:
            return ECTS_LIMITS_BY_GPA["low"]  # 31

    def _create_export_section(self) -> QGroupBox:
        """Create export controls."""
        group = QGroupBox("💾 Export Options")
        layout = QHBoxLayout(group)

        pdf_btn = QPushButton("📄 Export PDF")
        pdf_btn.clicked.connect(lambda: self._export("pdf"))

        jpeg_btn = QPushButton("🖼️ Export JPEG")
        jpeg_btn.clicked.connect(lambda: self._export("jpeg"))

        excel_btn = QPushButton("📊 Export Excel")
        excel_btn.clicked.connect(lambda: self._export("excel"))

        ics_btn = QPushButton("📅 Add to Calendar")
        ics_btn.setToolTip("Export to .ics format for Google Calendar, Outlook, Apple Calendar")
        ics_btn.clicked.connect(lambda: self._export("ics"))

        compare_btn = QPushButton("⚖️ Compare Algorithms")
        compare_btn.clicked.connect(self._show_comparison)

        layout.addWidget(pdf_btn)
        layout.addWidget(jpeg_btn)
        layout.addWidget(excel_btn)
        layout.addWidget(ics_btn)
        layout.addWidget(compare_btn)
        layout.addStretch()

        return group

    def set_schedules(self, schedules: List[Schedule], algorithm: str = "DFS", max_ects: Optional[int] = None) -> None:
        """Update displayed schedules.

        Args:
            schedules: List of schedules to display
            algorithm: Algorithm name used to generate schedules
            max_ects: User-selected max ECTS from algorithm selector (overrides GPA-based limit)
        """
        self._schedules = schedules
        if algorithm not in self._algorithm_results:
            self._algorithm_results[algorithm] = []
        self._algorithm_results[algorithm] = schedules

        # Store user's selected max ECTS if provided
        if max_ects is not None:
            self._user_selected_max_ects = max_ects
            # Update display with user's selection
            if hasattr(self, 'custom_ects_spinbox'):
                self.custom_ects_spinbox.setValue(max_ects)
                self.modify_ects_checkbox.setChecked(True)  # Auto-enable custom ECTS mode
            self._update_ects_display()

        # Update algorithm filter
        if algorithm not in [
            self.algorithm_combo.itemText(i)
            for i in range(self.algorithm_combo.count())
        ]:
            self.algorithm_combo.addItem(algorithm)

        self._update_schedule_list()

    def clear(self) -> None:
        """Reset viewer state."""
        self._schedules = []
        self._algorithm_results.clear()
        self.schedule_combo.clear()
        self.algorithm_combo.clear()
        self.algorithm_combo.addItem("All Algorithms")
        self.schedule_grid.set_schedule(None)
        self.stats_text.setPlainText("No schedule selected")

    def _update_schedule_list(self) -> None:
        """Update schedule combo box."""
        self.schedule_combo.clear()

        for idx, schedule in enumerate(self._schedules, 1):
            label = f"Schedule #{idx} - {schedule.total_credits} ECTS, {schedule.conflict_count} conflicts"
            self.schedule_combo.addItem(label)

        if self._schedules:
            self.schedule_combo.setCurrentIndex(0)

    def _on_schedule_changed(self, index: int) -> None:
        """Handle schedule selection change."""
        if 0 <= index < len(self._schedules):
            schedule = self._schedules[index]
            self.schedule_grid.set_schedule(schedule)
            self._update_stats(schedule)

            # Update ECTS display
            if ISIK_ECTS_AVAILABLE and hasattr(self, 'current_ects_label'):
                current_ects = schedule.total_credits

                # Use custom ECTS if enabled, otherwise use GPA-based limit
                if hasattr(self, 'modify_ects_checkbox') and self.modify_ects_checkbox.isChecked():
                    max_ects = self.custom_ects_spinbox.value()
                else:
                    max_ects = self._get_max_ects_for_gpa(self._current_gpa)

                self.current_ects_label.setText(f"{current_ects} ECTS")

                # Update progress bar
                if hasattr(self, 'ects_progress'):
                    self.ects_progress.setValue(current_ects)
                    self.ects_progress.setMaximum(max_ects)  # FIX: Set maximum based on current max_ects

                    # Change color based on limit
                    if current_ects > max_ects:
                        self.current_ects_label.setStyleSheet("color: #D32F2F; font-weight: bold;")
                        self.ects_progress.setStyleSheet("""
                            QProgressBar::chunk {
                                background-color: #F44336;
                            }
                        """)
                    elif current_ects >= max_ects * 0.9:
                        self.current_ects_label.setStyleSheet("color: #F57C00; font-weight: bold;")
                        self.ects_progress.setStyleSheet("""
                            QProgressBar::chunk {
                                background-color: #FF9800;
                            }
                        """)
                    else:
                        self.current_ects_label.setStyleSheet("color: #388E3C; font-weight: bold;")
                        self.ects_progress.setStyleSheet("""
                            QProgressBar::chunk {
                                background-color: #4CAF50;
                            }
                        """)

    def _on_course_clicked(self, course) -> None:
        """Handle course click event to show details."""
        # Format schedule times
        schedule_text = ""
        if course.schedule:
            from collections import defaultdict
            day_slots = defaultdict(list)
            for day, slot in course.schedule:
                day_slots[day].append(slot)

            for day, slots in sorted(day_slots.items()):
                slots_str = ", ".join(map(str, sorted(slots)))
                schedule_text += f"  {day}: Slot(s) {slots_str}\n"
        else:
            schedule_text = "  No schedule information\n"

        details = f"""<b>📚 {course.main_code}</b>

<b>Course Name:</b>
{course.name}

<b>Course Code:</b> {course.code}

<b>Type:</b> {course.course_type.upper()}

<b>ECTS:</b> {course.ects}

<b>Instructor:</b>
{course.teacher or 'Not assigned'}

<b>Faculty:</b>
{course.faculty}

<b>Department:</b>
{course.department}

<b>Campus:</b>
{course.campus}

<b>Schedule:</b>
{schedule_text}
"""
        self.course_details.setHtml(details)

    def _filter_by_algorithm(self, algorithm: str) -> None:
        """Filter schedules by algorithm."""
        if algorithm == "All Algorithms":
            # Show all schedules from all algorithms
            all_schedules = []
            for schedules in self._algorithm_results.values():
                all_schedules.extend(schedules)
            self._schedules = all_schedules
        else:
            self._schedules = self._algorithm_results.get(algorithm, [])

        self._update_schedule_list()

    def _update_stats(self, schedule: Schedule) -> None:
        """Update statistics display."""
        stats_text = f"""
<b>Schedule Statistics</b>

📚 <b>Total Courses:</b> {len(schedule.courses)}
🎓 <b>Total ECTS:</b> {schedule.total_credits}
⚠️ <b>Conflicts:</b> {schedule.conflict_count}

<b>Courses:</b>
"""
        for course in schedule.courses:
            stats_text += f"\n• {course.code} - {course.name} ({course.ects} ECTS)"

        self.stats_text.setHtml(stats_text)

    def _export(self, format: str) -> None:
        """Export current schedule."""
        current_index = self.schedule_combo.currentIndex()
        if current_index < 0 or current_index >= len(self._schedules):
            QMessageBox.warning(self, "No Schedule", "Please select a schedule to export.")
            return

        schedule = self._schedules[current_index]

        if format == "pdf":
            self._export_pdf([schedule])
        elif format == "jpeg":
            self._export_jpeg([schedule])
        elif format == "excel":
            self._export_excel([schedule])
        elif format == "ics":
            self._export_ics(schedule)

    def _export_pdf(self, schedules: List[Schedule]) -> None:
        """Export schedules as PDF."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF",
            "schedules.pdf",
            "PDF Files (*.pdf)"
        )

        if filepath:
            try:
                reporting.save_schedules_as_pdf(schedules, filepath)
                QMessageBox.information(self, "Success", f"Exported to {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export PDF: {e}")

    def _export_jpeg(self, schedules: List[Schedule]) -> None:
        """Export schedules as JPEG images."""
        dirpath = QFileDialog.getExistingDirectory(
            self,
            "Select Directory for JPEG Export"
        )

        if dirpath:
            try:
                created_files = reporting.save_schedules_as_jpegs(schedules, dirpath)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Exported {len(created_files)} images to {dirpath}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export JPEG: {e}")

    def _export_excel(self, schedules: List[Schedule]) -> None:
        """Export schedules as Excel file."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Excel",
            "schedules.xlsx",
            "Excel Files (*.xlsx)"
        )

        if filepath:
            try:
                reporting.export_to_excel(schedules, filepath)
                QMessageBox.information(self, "Success", f"Exported to {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export Excel: {e}")

    def _export_ics(self, schedule: Schedule) -> None:
        """Export schedule as ICS calendar file."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Calendar File",
            "course_schedule.ics",
            "iCalendar Files (*.ics)"
        )

        if filepath:
            try:
                from pathlib import Path
                from reporting.ics_export import export_schedule_to_ics

                export_schedule_to_ics(
                    schedule,
                    Path(filepath),
                    calendar_name="My Course Schedule"
                )
                QMessageBox.information(
                    self,
                    "Calendar Export Success",
                    f"Schedule exported to {filepath}\n\n"
                    "You can now import this file into:\n"
                    "• Google Calendar\n"
                    "• Microsoft Outlook\n"
                    "• Apple Calendar\n"
                    "• Any other calendar app"
                )
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export calendar: {e}")

    def _show_comparison(self) -> None:
        """Show algorithm comparison dialog."""
        if not self._algorithm_results:
            print("No algorithm results to compare")
            return

        dialog = AlgorithmComparisonDialog(self._algorithm_results, self)
        dialog.exec()

    # ============== Manual Edit Features ==============

    def _on_edit_mode_toggled(self, enabled: bool) -> None:
        """Toggle edit mode for manual schedule adjustments."""
        self.pin_course_btn.setEnabled(enabled)
        self.swap_section_btn.setEnabled(enabled)

        if enabled:
            self.edit_mode_btn.setText("✏️ Exit Edit Mode")
            self.edit_mode_btn.setStyleSheet("background-color: #fff3e0; font-weight: bold;")
            self.schedule_grid.setStyleSheet("border: 2px dashed #ff9800;")
        else:
            self.edit_mode_btn.setText("✏️ Edit Mode")
            self.edit_mode_btn.setStyleSheet("")
            self.schedule_grid.setStyleSheet("")

    def _pin_selected_course(self) -> None:
        """Pin the currently selected course."""
        if not hasattr(self, '_pinned_courses'):
            self._pinned_courses = set()

        # Get currently selected course from grid
        selected_course = getattr(self.schedule_grid, '_last_clicked_course', None)
        if selected_course and hasattr(selected_course, 'code'):
            self._pinned_courses.add(selected_course.code)
            self._update_pinned_display()
            QMessageBox.information(
                self,
                "Course Pinned",
                f"📌 {selected_course.code} - {selected_course.name} has been pinned.\n\n"
                "This course will be preserved when regenerating schedules."
            )
        else:
            QMessageBox.warning(
                self,
                "No Course Selected",
                "Please click on a course in the schedule grid first."
            )

    def _unpin_all_courses(self) -> None:
        """Remove all pinned courses."""
        if hasattr(self, '_pinned_courses'):
            self._pinned_courses.clear()
        self._update_pinned_display()

    def _update_pinned_display(self) -> None:
        """Update the pinned courses display."""
        if not hasattr(self, '_pinned_courses'):
            self._pinned_courses = set()

        count = len(self._pinned_courses)
        self.pinned_label.setText(f"📌 Pinned: {count}")

        if count > 0:
            pinned_text = "\n".join(f"• {code}" for code in sorted(self._pinned_courses))
            self.pinned_list.setPlainText(pinned_text)
        else:
            self.pinned_list.setPlainText("No pinned courses")

    def _swap_course_section(self) -> None:
        """Swap to a different section of the selected course."""
        selected_course = getattr(self.schedule_grid, '_last_clicked_course', None)
        if not selected_course:
            QMessageBox.warning(
                self,
                "No Course Selected",
                "Please click on a course in the schedule grid first."
            )
            return

        # Find alternative sections for this course
        main_code = getattr(selected_course, 'main_code', selected_course.code.split('.')[0])
        current_schedule = self._schedules[self.schedule_combo.currentIndex()] if self._schedules else None

        if not current_schedule:
            return

        # Get all courses with the same main_code from the current schedule's source
        # This would normally come from the course groups
        QMessageBox.information(
            self,
            "Section Swap",
            f"🔄 Looking for alternative sections of {main_code}...\n\n"
            "This feature allows you to swap between different sections of the same course.\n"
            "(Full implementation requires access to course groups)"
        )

    def get_pinned_courses(self) -> set:
        """Get the set of pinned course codes."""
        return getattr(self, '_pinned_courses', set()).copy()

    def set_pinned_courses(self, pinned: set) -> None:
        """Set the pinned courses."""
        self._pinned_courses = pinned.copy()
        self._update_pinned_display()


__all__ = ["ScheduleViewerTab"]
