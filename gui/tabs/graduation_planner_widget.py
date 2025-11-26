"""
Graduation Planner Widget - Phase 7.3

Features:
- Graduation progress tracking
- Remaining requirements visualization
- Semester-by-semester planning
- Timeline estimation
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QProgressBar, QTableWidget, QTableWidgetItem,
    QMessageBox, QFormLayout, QListWidget, QTextEdit, QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from typing import List, Optional, Dict, Any

from core.models import Course, Transcript, GraduationRequirement
from core.academic import GraduationPlanner

# Işık University curriculum data
try:
    from core.curriculum_data import (
        COMPUTER_ENGINEERING_CURRICULUM, GRADUATION_REQUIREMENTS as ISIK_GRAD_REQ,
        get_semester_courses, get_all_mandatory_courses, get_total_ects_by_semester
    )
    from core.curriculum_data_REAL import CURRICULUM_SUMMARY
    from config.settings import ECTS_LIMITS_BY_GPA
    ISIK_DATA_AVAILABLE = True
except ImportError:
    ISIK_DATA_AVAILABLE = False
    CURRICULUM_SUMMARY = {"total_ects": 240}  # Fallback


class GraduationPlannerWidget(QWidget):
    """Widget for graduation planning and progress tracking."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.planner: Optional[GraduationPlanner] = None
        self.transcript: Optional[Transcript] = None
        self.requirement: Optional[GraduationRequirement] = None
        self.available_courses: List[Course] = []
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🎓 Graduation Planner")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Setup section
        setup_group = QGroupBox("Setup Graduation Requirements")
        setup_layout = QFormLayout(setup_group)
        
        self.program_input = QComboBox()
        total_ects = CURRICULUM_SUMMARY["total_ects"]
        if ISIK_DATA_AVAILABLE:
            self.program_input.addItems([
                f"Işık University - Computer Engineering ({total_ects} ECTS)",
                f"Işık University - Software Engineering ({total_ects} ECTS)",
                f"Işık University - Electrical Engineering ({total_ects} ECTS)",
                "Custom..."
            ])
        else:
            self.program_input.addItems([
                f"Computer Engineering ({total_ects} ECTS)",
                f"Software Engineering ({total_ects} ECTS)",
                f"Electrical Engineering ({total_ects} ECTS)",
                "Custom..."
            ])
        self.program_input.currentIndexChanged.connect(self._on_program_changed)
        setup_layout.addRow("Program:", self.program_input)
        
        self.total_ects_input = QSpinBox()
        self.total_ects_input.setRange(180, 300)
        self.total_ects_input.setValue(total_ects)
        setup_layout.addRow("Total ECTS Required:", self.total_ects_input)
        
        self.min_gpa_input = QSpinBox()
        self.min_gpa_input.setRange(0, 400)
        self.min_gpa_input.setValue(200)
        self.min_gpa_input.setSuffix(" (2.00)")
        setup_layout.addRow("Minimum GPA:", self.min_gpa_input)
        
        self.load_requirement_btn = QPushButton("📋 Load Requirements")
        self.load_requirement_btn.clicked.connect(self._load_requirements)
        setup_layout.addRow(self.load_requirement_btn)
        
        layout.addWidget(setup_group)
        
        # Progress Overview
        progress_group = QGroupBox("Graduation Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        # Overall progress bar
        overall_layout = QHBoxLayout()
        overall_layout.addWidget(QLabel("Overall Progress:"))
        self.overall_progress = QProgressBar()
        self.overall_progress.setMinimum(0)
        self.overall_progress.setMaximum(100)
        self.overall_progress.setFormat("%p% Complete")
        overall_layout.addWidget(self.overall_progress, 1)
        self.overall_percentage_label = QLabel("0%")
        self.overall_percentage_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        overall_layout.addWidget(self.overall_percentage_label)
        progress_layout.addLayout(overall_layout)
        
        # Stats grid
        stats_layout = QHBoxLayout()
        
        # ECTS stats
        ects_stats = QGroupBox("ECTS Credits")
        ects_layout = QFormLayout(ects_stats)
        self.ects_earned_label = QLabel("0")
        self.ects_required_label = QLabel(str(CURRICULUM_SUMMARY["total_ects"]))
        self.ects_remaining_label = QLabel(str(CURRICULUM_SUMMARY["total_ects"]))
        ects_layout.addRow("Earned:", self.ects_earned_label)
        ects_layout.addRow("Required:", self.ects_required_label)
        ects_layout.addRow("Remaining:", self.ects_remaining_label)
        stats_layout.addWidget(ects_stats)
        
        # GPA stats
        gpa_stats = QGroupBox("GPA Status")
        gpa_layout = QFormLayout(gpa_stats)
        self.current_gpa_label = QLabel("0.00")
        self.min_gpa_label = QLabel("2.00")
        self.gpa_status_label = QLabel("❌ Below minimum")
        gpa_layout.addRow("Current GPA:", self.current_gpa_label)
        gpa_layout.addRow("Required GPA:", self.min_gpa_label)
        gpa_layout.addRow("Status:", self.gpa_status_label)
        stats_layout.addWidget(gpa_stats)
        
        # Timeline stats
        timeline_stats = QGroupBox("Timeline")
        timeline_layout = QFormLayout(timeline_stats)
        self.semesters_remaining_label = QLabel("?")
        self.ects_limit_label = QLabel("37")
        self.estimated_grad_label = QLabel("Not set")
        timeline_layout.addRow("Semesters Left:", self.semesters_remaining_label)
        timeline_layout.addRow("ECTS/Semester:", self.ects_limit_label)
        timeline_layout.addRow("Est. Graduation:", self.estimated_grad_label)
        stats_layout.addWidget(timeline_stats)
        
        progress_layout.addLayout(stats_layout)
        
        # Can graduate status
        self.grad_status_label = QLabel()
        self.grad_status_label.setWordWrap(True)
        self.grad_status_label.setStyleSheet(
            "padding: 15px; background: #E3F2FD; border-radius: 5px; font-size: 12pt;"
        )
        progress_layout.addWidget(self.grad_status_label)
        
        layout.addWidget(progress_group)
        
        # Işık University Curriculum Integration
        if ISIK_DATA_AVAILABLE:
            curriculum_group = self._create_curriculum_section()
            layout.addWidget(curriculum_group)
        
        # Missing courses section
        missing_group = QGroupBox("Missing Core Courses")
        missing_layout = QVBoxLayout(missing_group)
        
        self.missing_courses_list = QListWidget()
        self.missing_courses_list.setMaximumHeight(100)
        missing_layout.addWidget(self.missing_courses_list)
        
        layout.addWidget(missing_group)
        
        # Next semester suggestion
        semester_group = QGroupBox("Next Semester Suggestion")
        semester_layout = QVBoxLayout(semester_group)
        
        suggestion_controls = QHBoxLayout()
        suggestion_controls.addWidget(QLabel("Current Semester:"))
        self.current_semester_input = QComboBox()
        self.current_semester_input.addItems([
            "2024 Fall", "2025 Spring", "2025 Fall",
            "2026 Spring", "2026 Fall"
        ])
        suggestion_controls.addWidget(self.current_semester_input)
        
        self.suggest_btn = QPushButton("💡 Suggest Courses")
        self.suggest_btn.clicked.connect(self._suggest_next_semester)
        suggestion_controls.addWidget(self.suggest_btn)
        suggestion_controls.addStretch()
        
        semester_layout.addLayout(suggestion_controls)
        
        self.suggestion_table = QTableWidget()
        self.suggestion_table.setColumnCount(4)
        self.suggestion_table.setHorizontalHeaderLabels([
            "Course Code", "Course Name", "ECTS", "Type"
        ])
        self.suggestion_table.horizontalHeader().setStretchLastSection(True)
        self.suggestion_table.setMaximumHeight(200)
        semester_layout.addWidget(self.suggestion_table)
        
        self.suggestion_summary = QLabel()
        self.suggestion_summary.setWordWrap(True)
        semester_layout.addWidget(self.suggestion_summary)
        
        layout.addWidget(semester_group)
        
        layout.addStretch()
    
    def set_transcript(self, transcript: Transcript):
        """Set transcript and update display."""
        self.transcript = transcript
        self._update_display()
    
    def set_available_courses(self, courses: List[Course]):
        """Set available courses for suggestions."""
        self.available_courses = courses
    
    def _load_requirements(self):
        """Load graduation requirements."""
        program = self.program_input.currentText()
        total_ects = self.total_ects_input.value()
        min_gpa = self.min_gpa_input.value() / 100.0
        
        # Create sample requirement (in real app, load from database)
        self.requirement = GraduationRequirement(
            program_name=program,
            total_ects_required=total_ects,
            core_courses=[],  # Would be populated from curriculum
            elective_ects_required=60,
            min_gpa=min_gpa
        )
        
        if self.transcript:
            self.planner = GraduationPlanner(self.requirement, self.transcript)
            self._update_display()
            QMessageBox.information(
                self,
                "Requirements Loaded",
                f"✅ Loaded graduation requirements for {program}"
            )
        else:
            QMessageBox.warning(
                self,
                "No Transcript",
                "Please load a transcript first from the GPA Calculator tab."
            )
    
    def _update_display(self):
        """Update all progress displays."""
        if not self.planner or not self.transcript:
            return
        
        report = self.planner.get_progress_report()
        
        # Update overall progress
        percentage = report["completion_percentage"]
        self.overall_progress.setValue(int(percentage))
        self.overall_percentage_label.setText(f"{percentage:.1f}%")
        
        # Update ECTS stats
        self.ects_earned_label.setText(str(report["ects"]["earned"]))
        self.ects_required_label.setText(str(report["ects"]["required"]))
        self.ects_remaining_label.setText(str(report["ects"]["remaining"]))
        
        # Update GPA stats
        self.current_gpa_label.setText(f"{report['gpa']['current']:.2f}")
        self.min_gpa_label.setText(f"{report['gpa']['required']:.2f}")
        if report["gpa"]["meets_requirement"]:
            self.gpa_status_label.setText("✅ Meets requirement")
            self.gpa_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.gpa_status_label.setText("❌ Below minimum")
            self.gpa_status_label.setStyleSheet("color: red; font-weight: bold;")
        
        # Update timeline
        self.semesters_remaining_label.setText(
            str(report["timeline"]["semesters_remaining"])
        )
        self.ects_limit_label.setText(
            str(report["timeline"]["ects_per_semester_limit"])
        )
        
        # Estimate graduation
        current_sem = self.current_semester_input.currentText()
        est_grad = self.planner.estimate_graduation_date(current_sem)
        self.estimated_grad_label.setText(est_grad)
        
        # Update graduation status
        if report["can_graduate"]:
            self.grad_status_label.setText(
                "🎉 Congratulations! You meet all graduation requirements!"
            )
            self.grad_status_label.setStyleSheet(
                "padding: 15px; background: #C8E6C9; border-radius: 5px; "
                "font-size: 12pt; color: #2E7D32; font-weight: bold;"
            )
        else:
            issues = []
            if not report["core_courses"]["completed"] == report["core_courses"]["total"]:
                issues.append(
                    f"{report['core_courses']['total'] - report['core_courses']['completed']} core courses"
                )
            if report["ects"]["remaining"] > 0:
                issues.append(f"{report['ects']['remaining']} ECTS credits")
            if not report["gpa"]["meets_requirement"]:
                issues.append("GPA requirement")
            
            self.grad_status_label.setText(
                f"📚 Still need to complete: {', '.join(issues)}"
            )
            self.grad_status_label.setStyleSheet(
                "padding: 15px; background: #FFF9C4; border-radius: 5px; "
                "font-size: 12pt; color: #F57F17;"
            )
        
        # Update missing courses
        self.missing_courses_list.clear()
        for course_code in report["core_courses"]["missing"]:
            self.missing_courses_list.addItem(f"❌ {course_code}")
    
    def _suggest_next_semester(self):
        """Suggest courses for next semester."""
        if not self.planner or not self.available_courses:
            QMessageBox.warning(
                self,
                "Cannot Suggest",
                "Please load graduation requirements and course data first."
            )
            return
        
        suggestions = self.planner.suggest_next_semester(self.available_courses)
        
        if not suggestions:
            QMessageBox.information(
                self,
                "No Suggestions",
                "No course suggestions available. You may have completed "
                "all requirements or reached your ECTS limit."
            )
            return
        
        # Populate table
        self.suggestion_table.setRowCount(len(suggestions))
        total_ects = 0
        
        for i, course in enumerate(suggestions):
            self.suggestion_table.setItem(i, 0, QTableWidgetItem(course.main_code))
            self.suggestion_table.setItem(i, 1, QTableWidgetItem(course.name))
            self.suggestion_table.setItem(i, 2, QTableWidgetItem(str(course.ects)))
            self.suggestion_table.setItem(i, 3, QTableWidgetItem(course.course_type))
            total_ects += course.ects
        
        # Update summary
        ects_limit = self.transcript.get_ects_limit() if self.transcript else 37
        utilization = (total_ects / ects_limit * 100) if ects_limit > 0 else 0
        
        self.suggestion_summary.setText(
            f"💡 Suggested {len(suggestions)} courses totaling {total_ects} ECTS "
            f"({utilization:.1f}% of your {ects_limit} ECTS limit)"
        )
    
    def _create_curriculum_section(self) -> QGroupBox:
        """Create Işık University curriculum display section."""
        group = QGroupBox("📚 Işık University - Computer Engineering Curriculum")
        layout = QVBoxLayout(group)
        
        info_label = QLabel(
            "Official curriculum with 240 ECTS requirement.\n"
            "Track your progress through each semester's mandatory courses."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #757575; font-style: italic;")
        layout.addWidget(info_label)
        
        # Curriculum progress by semester
        self.curriculum_table = QTableWidget()
        self.curriculum_table.setColumnCount(4)
        self.curriculum_table.setHorizontalHeaderLabels([
            "Semester", "Total ECTS", "Completed", "Progress"
        ])
        self.curriculum_table.setMaximumHeight(200)
        layout.addWidget(self.curriculum_table)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Curriculum Progress")
        refresh_btn.clicked.connect(self._update_curriculum_progress)
        layout.addWidget(refresh_btn)
        
        return group
    
    def _update_curriculum_progress(self):
        """Update curriculum progress display with Işık data."""
        if not ISIK_DATA_AVAILABLE or not self.transcript:
            return
        
        # Get completed courses
        completed_codes = {g.course_code for g in self.transcript.grades}
        
        # Calculate progress for each semester
        semesters = ["Fall-1", "Spring-1", "Fall-2", "Spring-2", 
                     "Fall-3", "Spring-3", "Fall-4", "Spring-4"]
        
        self.curriculum_table.setRowCount(len(semesters))
        
        for i, semester in enumerate(semesters):
            courses = get_semester_courses(semester)
            if isinstance(courses, dict):  # Semesters 7-8 have different structure
                total_ects = courses.get("total_ects", 0)
                mandatory_courses = courses.get("mandatory", [])
                completed_count = sum(
                    1 for c in mandatory_courses 
                    if c.get("code") in completed_codes
                )
                total_count = len(mandatory_courses)
            else:
                total_ects = sum(c["ects"] for c in courses)
                completed_count = sum(
                    1 for c in courses if c["code"] in completed_codes
                )
                total_count = len(courses)
            
            # Set table items
            self.curriculum_table.setItem(i, 0, QTableWidgetItem(semester))
            self.curriculum_table.setItem(i, 1, QTableWidgetItem(f"{total_ects} ECTS"))
            self.curriculum_table.setItem(i, 2, 
                QTableWidgetItem(f"{completed_count}/{total_count}"))
            
            # Progress percentage
            progress = (completed_count / total_count * 100) if total_count > 0 else 0
            progress_item = QTableWidgetItem(f"{progress:.0f}%")
            
            # Color code based on completion
            if progress == 100:
                progress_item.setBackground(QColor("#C8E6C9"))  # Green
            elif progress >= 50:
                progress_item.setBackground(QColor("#FFF9C4"))  # Yellow
            else:
                progress_item.setBackground(QColor("#FFCDD2"))  # Red
            
            self.curriculum_table.setItem(i, 3, progress_item)
    
    def _on_program_changed(self, index: int):
        """Handle program selection change."""
        if not ISIK_DATA_AVAILABLE:
            return
        
        if index == 0:  # Computer Engineering
            # Load Işık CS curriculum
            self.total_ects_input.setValue(ISIK_GRAD_REQ["total_ects"])
            self.min_gpa_input.setValue(int(ISIK_GRAD_REQ["minimum_gpa"] * 100))
            
            # Update curriculum display
            if hasattr(self, "curriculum_table"):
                self._update_curriculum_progress()
