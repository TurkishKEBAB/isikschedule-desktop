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
        self._setup_ui()
    
    def set_transcript(self, transcript: Optional[Transcript]) -> None:
        """Set student transcript for ECTS limit calculation."""
        self._transcript = transcript
        if transcript:
            from core.academic import GPACalculator
            calculator = GPACalculator()
            self._current_gpa = calculator.calculate_cgpa(transcript)
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
        """Create schedule display area."""
        group = QGroupBox("📅 Weekly Schedule")
        layout = QHBoxLayout(group)  # Changed to horizontal layout

        # Schedule grid (left side)
        scroll = QScrollArea()
        self.schedule_grid = ScheduleGrid()
        self.schedule_grid.course_clicked.connect(self._on_course_clicked)
        scroll.setWidget(self.schedule_grid)
        scroll.setWidgetResizable(True)

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

        layout.addWidget(scroll, stretch=3)
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

        compare_btn = QPushButton("⚖️ Compare Algorithms")
        compare_btn.clicked.connect(self._show_comparison)

        layout.addWidget(pdf_btn)
        layout.addWidget(jpeg_btn)
        layout.addWidget(excel_btn)
        layout.addWidget(compare_btn)
        layout.addStretch()

        return group

    def set_schedules(self, schedules: List[Schedule], algorithm: str = "DFS") -> None:
        """Update displayed schedules."""
        self._schedules = schedules
        if algorithm not in self._algorithm_results:
            self._algorithm_results[algorithm] = []
        self._algorithm_results[algorithm] = schedules

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
                max_ects = self._get_max_ects_for_gpa(self._current_gpa)
                
                self.current_ects_label.setText(f"{current_ects} ECTS")
                
                # Update progress bar
                if hasattr(self, 'ects_progress'):
                    self.ects_progress.setValue(current_ects)
                    
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

    def _show_comparison(self) -> None:
        """Show algorithm comparison dialog."""
        if not self._algorithm_results:
            print("No algorithm results to compare")
            return
        
        dialog = AlgorithmComparisonDialog(self._algorithm_results, self)
        dialog.exec()


__all__ = ["ScheduleViewerTab"]
