"""
Academic Tab - Phase 7

Features:
- Prerequisite visualization
- GPA calculator
- Graduation planner
- Transcript import
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QGroupBox,
    QLineEdit, QComboBox, QTextEdit, QProgressBar, QMessageBox,
    QFileDialog, QScrollArea, QFormLayout, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Optional, Dict, Any, Tuple

from core.models import Course, Transcript, GraduationRequirement, Grade
from core.academic import PrerequisiteChecker, GPACalculator, GraduationPlanner
from gui.tabs.graduation_planner_widget import GraduationPlannerWidget
from gui.dialogs.transcript_import_dialog import TranscriptImportWidget

# Işık University official data
try:
    from core.prerequisite_data import (
        get_prerequisites, can_take_course, get_missing_prerequisites,
        get_prerequisite_chain, get_courses_unlocked_by
    )
    from core.curriculum_data import (
        COMPUTER_ENGINEERING_CURRICULUM, GRADUATION_REQUIREMENTS,
        get_semester_courses, get_all_mandatory_courses
    )
    from core.isik_university_data import GRADE_SCALE, ECTS_LIMITS_BY_GPA
    ISIK_DATA_AVAILABLE = True
except ImportError:
    ISIK_DATA_AVAILABLE = False


class PrerequisiteViewer(QWidget):
    """Widget to visualize course prerequisites."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.courses: List[Course] = []
        self.checker: Optional[PrerequisiteChecker] = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("📚 Prerequisite Visualization")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Course selection
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Select Course:"))
        self.course_combo = QComboBox()
        self.course_combo.currentTextChanged.connect(self._on_course_selected)
        selection_layout.addWidget(self.course_combo, 1)
        
        self.check_btn = QPushButton("🔍 Check Prerequisites")
        self.check_btn.clicked.connect(self._check_prerequisites)
        selection_layout.addWidget(self.check_btn)
        
        layout.addLayout(selection_layout)
        
        # Prerequisite chain display
        chain_group = QGroupBox("Prerequisite Chain")
        chain_layout = QVBoxLayout(chain_group)
        
        self.chain_text = QTextEdit()
        self.chain_text.setReadOnly(True)
        self.chain_text.setMaximumHeight(150)
        chain_layout.addWidget(self.chain_text)
        
        layout.addWidget(chain_group)
        
        # Prerequisites table
        table_group = QGroupBox("Direct Prerequisites")
        table_layout = QVBoxLayout(table_group)
        
        self.prereq_table = QTableWidget()
        self.prereq_table.setColumnCount(3)
        self.prereq_table.setHorizontalHeaderLabels(["Course Code", "Course Name", "ECTS"])
        self.prereq_table.horizontalHeader().setStretchLastSection(True)
        table_layout.addWidget(self.prereq_table)
        
        layout.addWidget(table_group)
        
        # Completed courses input
        completed_group = QGroupBox("My Completed Courses")
        completed_layout = QVBoxLayout(completed_group)
        
        completed_info = QLabel("Enter completed course codes (comma-separated):")
        completed_layout.addWidget(completed_info)
        
        self.completed_input = QLineEdit()
        self.completed_input.setPlaceholderText("e.g., CS101, CS102, MATH101")
        completed_layout.addWidget(self.completed_input)
        
        check_layout = QHBoxLayout()
        self.validate_btn = QPushButton("✅ Validate Prerequisites")
        self.validate_btn.clicked.connect(self._validate_prerequisites)
        check_layout.addWidget(self.validate_btn)
        
        self.show_available_btn = QPushButton("📋 Show Available Courses")
        self.show_available_btn.clicked.connect(self._show_available_courses)
        check_layout.addWidget(self.show_available_btn)
        
        completed_layout.addLayout(check_layout)
        
        self.validation_result = QLabel()
        self.validation_result.setWordWrap(True)
        completed_layout.addWidget(self.validation_result)
        
        layout.addWidget(completed_group)
        
        layout.addStretch()
    
    def set_courses(self, courses: List[Course]):
        """Set available courses and update UI."""
        self.courses = courses
        self.checker = PrerequisiteChecker(courses)
        
        # Update combo box
        self.course_combo.clear()
        unique_codes = sorted(set(c.main_code for c in courses))
        self.course_combo.addItems(unique_codes)
        
        # Check for circular dependencies
        cycle = self.checker.detect_circular_dependency()
        if cycle:
            QMessageBox.warning(
                self,
                "Circular Dependency Detected",
                f"⚠️ Circular dependency found:\n{' → '.join(cycle)}\n\n"
                "This may cause issues with prerequisite validation."
            )
    
    def _on_course_selected(self, course_code: str):
        """Handle course selection."""
        if not course_code or not self.checker:
            return
        
        # Find course
        course = next((c for c in self.courses if c.main_code == course_code), None)
        if not course:
            return
        
        # Update prerequisites table
        self.prereq_table.setRowCount(len(course.prerequisites))
        for i, prereq_code in enumerate(course.prerequisites):
            prereq_course = next((c for c in self.courses if c.main_code == prereq_code), None)
            
            self.prereq_table.setItem(i, 0, QTableWidgetItem(prereq_code))
            if prereq_course:
                self.prereq_table.setItem(i, 1, QTableWidgetItem(prereq_course.name))
                self.prereq_table.setItem(i, 2, QTableWidgetItem(str(prereq_course.ects)))
            else:
                self.prereq_table.setItem(i, 1, QTableWidgetItem("Unknown"))
                self.prereq_table.setItem(i, 2, QTableWidgetItem("-"))
    
    def _check_prerequisites(self):
        """Display full prerequisite chain."""
        course_code = self.course_combo.currentText()
        if not course_code or not self.checker:
            return
        
        chain = self.checker.get_prerequisite_chain(course_code)
        
        if not chain:
            self.chain_text.setText("✅ No prerequisites required!")
            return
        
        # Format chain display
        text = f"📊 Prerequisite Chain for {course_code}:\n\n"
        for level_num, level in enumerate(chain, 1):
            text += f"Level {level_num}: {', '.join(level)}\n"
        
        text += f"\nℹ️ You must complete all Level 1 courses before Level 2, and so on."
        self.chain_text.setText(text)
    
    def _validate_prerequisites(self):
        """Validate if prerequisites are met."""
        course_code = self.course_combo.currentText()
        if not course_code or not self.checker:
            return
        
        # Parse completed courses
        completed_text = self.completed_input.text().strip()
        if not completed_text:
            self.validation_result.setText("⚠️ Please enter your completed courses.")
            self.validation_result.setStyleSheet("color: orange;")
            return
        
        completed = [c.strip() for c in completed_text.split(",")]
        
        # Check prerequisites
        can_take, missing = self.checker.check_prerequisites(course_code, completed)
        
        if can_take:
            self.validation_result.setText(
                f"✅ You can take {course_code}! All prerequisites are satisfied."
            )
            self.validation_result.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.validation_result.setText(
                f"❌ Cannot take {course_code}.\n"
                f"Missing prerequisites: {', '.join(missing)}"
            )
            self.validation_result.setStyleSheet("color: red; font-weight: bold;")
    
    def _show_available_courses(self):
        """Show all courses available with current completed courses."""
        completed_text = self.completed_input.text().strip()
        if not completed_text or not self.checker:
            QMessageBox.warning(
                self,
                "No Completed Courses",
                "Please enter your completed courses first."
            )
            return
        
        completed = [c.strip() for c in completed_text.split(",")]
        available = self.checker.get_available_courses(completed, self.courses)
        
        # Show in dialog
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Available Courses")
        dialog.setIcon(QMessageBox.Icon.Information)
        
        if available:
            course_list = "\n".join([f"• {c.main_code} - {c.name}" for c in available[:20]])
            if len(available) > 20:
                course_list += f"\n\n... and {len(available) - 20} more courses"
            
            dialog.setText(
                f"📚 You can take {len(available)} courses with your current progress:\n\n{course_list}"
            )
        else:
            dialog.setText("No additional courses available with current prerequisites.")
        
        dialog.exec()


class GPACalculatorWidget(QWidget):
    """Widget for GPA calculation and simulation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.transcript: Optional[Transcript] = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("📊 GPA Calculator & Simulator")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Current GPA display
        gpa_group = QGroupBox("Current GPA")
        gpa_layout = QFormLayout(gpa_group)
        
        self.current_gpa_label = QLabel("0.00")
        self.current_gpa_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.current_gpa_label.setStyleSheet("color: #2196F3;")
        gpa_layout.addRow("CGPA:", self.current_gpa_label)
        
        self.ects_earned_label = QLabel("0 / 0")
        gpa_layout.addRow("ECTS Earned:", self.ects_earned_label)
        
        self.ects_limit_label = QLabel("37 ECTS")
        gpa_layout.addRow("Semester Limit:", self.ects_limit_label)
        
        layout.addWidget(gpa_group)
        
        # GPA Simulator
        sim_group = QGroupBox("What-If GPA Simulator")
        sim_layout = QVBoxLayout(sim_group)
        
        sim_info = QLabel(
            "Simulate your GPA by adding planned courses and expected grades:"
        )
        sim_info.setWordWrap(True)
        sim_layout.addWidget(sim_info)
        
        # Simulation inputs
        input_layout = QHBoxLayout()
        
        input_layout.addWidget(QLabel("Course ECTS:"))
        self.sim_ects_input = QSpinBox()
        self.sim_ects_input.setRange(1, 15)
        self.sim_ects_input.setValue(6)
        input_layout.addWidget(self.sim_ects_input)
        
        input_layout.addWidget(QLabel("Expected Grade:"))
        self.sim_grade_input = QComboBox()
        self.sim_grade_input.addItems([
            "AA (4.0)", "BA (3.5)", "BB (3.0)", "CB (2.5)",
            "CC (2.0)", "DC (1.5)", "DD (1.0)", "FF (0.0)"
        ])
        input_layout.addWidget(self.sim_grade_input)
        
        self.add_sim_btn = QPushButton("➕ Add Course")
        self.add_sim_btn.clicked.connect(self._add_simulated_course)
        input_layout.addWidget(self.add_sim_btn)
        
        sim_layout.addLayout(input_layout)
        
        # Simulated courses list
        self.sim_courses_text = QTextEdit()
        self.sim_courses_text.setReadOnly(True)
        self.sim_courses_text.setMaximumHeight(100)
        self.sim_courses_text.setPlaceholderText("No simulated courses added yet...")
        sim_layout.addWidget(self.sim_courses_text)
        
        # Simulation buttons
        sim_btn_layout = QHBoxLayout()
        
        self.calculate_sim_btn = QPushButton("🧮 Calculate Simulated GPA")
        self.calculate_sim_btn.clicked.connect(self._calculate_simulation)
        sim_btn_layout.addWidget(self.calculate_sim_btn)
        
        self.clear_sim_btn = QPushButton("🗑️ Clear All")
        self.clear_sim_btn.clicked.connect(self._clear_simulation)
        sim_btn_layout.addWidget(self.clear_sim_btn)
        
        sim_layout.addLayout(sim_btn_layout)
        
        # Simulation result
        self.sim_result_label = QLabel()
        self.sim_result_label.setWordWrap(True)
        self.sim_result_label.setStyleSheet("padding: 10px; background: #E3F2FD; border-radius: 5px;")
        sim_layout.addWidget(self.sim_result_label)
        
        layout.addWidget(sim_group)
        
        # Required GPA calculator
        req_group = QGroupBox("Target GPA Calculator")
        req_layout = QFormLayout(req_group)
        
        self.target_gpa_input = QDoubleSpinBox()
        self.target_gpa_input.setRange(0.0, 4.0)
        self.target_gpa_input.setSingleStep(0.1)
        self.target_gpa_input.setValue(3.0)
        req_layout.addRow("Target GPA:", self.target_gpa_input)
        
        self.remaining_ects_input = QSpinBox()
        self.remaining_ects_input.setRange(1, 200)
        self.remaining_ects_input.setValue(30)
        req_layout.addRow("Remaining ECTS:", self.remaining_ects_input)
        
        self.calc_required_btn = QPushButton("🎯 Calculate Required GPA")
        self.calc_required_btn.clicked.connect(self._calculate_required_gpa)
        req_layout.addRow(self.calc_required_btn)
        
        self.required_result_label = QLabel()
        self.required_result_label.setWordWrap(True)
        req_layout.addRow(self.required_result_label)
        
        layout.addWidget(req_group)
        
        layout.addStretch()
        
        # Simulated courses storage
        self.simulated_courses: List[Tuple[str, int, str]] = []
    
    def set_transcript(self, transcript: Transcript):
        """Set current transcript and update display."""
        self.transcript = transcript
        self._update_gpa_display()
    
    def _update_gpa_display(self):
        """Update current GPA display."""
        if not self.transcript:
            return
        
        gpa = self.transcript.get_gpa()
        total_ects = self.transcript.get_total_ects()
        total_taken = sum(g.ects for g in self.transcript.grades)
        ects_limit = self.transcript.get_ects_limit()
        
        self.current_gpa_label.setText(f"{gpa:.2f}")
        self.ects_earned_label.setText(f"{total_ects} / {total_taken}")
        self.ects_limit_label.setText(f"{ects_limit} ECTS")
    
    def _add_simulated_course(self):
        """Add a simulated course."""
        ects = self.sim_ects_input.value()
        grade_text = self.sim_grade_input.currentText()
        letter = grade_text.split()[0]  # Extract "AA" from "AA (4.0)"
        
        self.simulated_courses.append((f"SIM{len(self.simulated_courses)+1}", ects, letter))
        self._update_simulated_display()
    
    def _update_simulated_display(self):
        """Update simulated courses display."""
        if not self.simulated_courses:
            self.sim_courses_text.clear()
            return
        
        text = "Simulated Courses:\n"
        for code, ects, grade in self.simulated_courses:
            text += f"• {code}: {ects} ECTS - Grade {grade}\n"
        
        self.sim_courses_text.setText(text)
    
    def _calculate_simulation(self):
        """Calculate simulated GPA."""
        if not self.transcript:
            QMessageBox.warning(self, "No Transcript", "Please load a transcript first.")
            return
        
        if not self.simulated_courses:
            QMessageBox.warning(self, "No Courses", "Please add some simulated courses first.")
            return
        
        result = GPACalculator.simulate_gpa(self.transcript, self.simulated_courses)
        
        # Format result
        gpa_change = result["gpa_change"]
        change_symbol = "📈" if gpa_change > 0 else "📉" if gpa_change < 0 else "➡️"
        change_color = "green" if gpa_change > 0 else "red" if gpa_change < 0 else "gray"
        
        result_text = (
            f"<b>Simulation Results:</b><br>"
            f"Current GPA: {result['current_gpa']:.2f}<br>"
            f"Simulated GPA: <b>{result['simulated_gpa']:.2f}</b><br>"
            f"{change_symbol} Change: <span style='color: {change_color};'><b>{gpa_change:+.2f}</b></span><br><br>"
            f"Current ECTS: {result['current_ects']}<br>"
            f"Simulated ECTS: {result['simulated_ects']} (+{result['ects_change']})"
        )
        
        self.sim_result_label.setText(result_text)
    
    def _clear_simulation(self):
        """Clear all simulated courses."""
        self.simulated_courses.clear()
        self.sim_courses_text.clear()
        self.sim_result_label.clear()
    
    def _calculate_required_gpa(self):
        """Calculate required GPA for remaining courses."""
        if not self.transcript:
            QMessageBox.warning(self, "No Transcript", "Please load a transcript first.")
            return
        
        target = self.target_gpa_input.value()
        remaining = self.remaining_ects_input.value()
        
        required = GPACalculator.calculate_required_gpa(
            self.transcript,
            target,
            remaining
        )
        
        if required is None:
            self.required_result_label.setText(
                f"❌ Target GPA of {target:.2f} is <b>impossible</b> to achieve "
                f"with {remaining} ECTS remaining."
            )
            self.required_result_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            difficulty = (
                "Very Easy! 🎉" if required < 2.0 else
                "Easy 😊" if required < 2.5 else
                "Moderate 💪" if required < 3.0 else
                "Challenging 🔥" if required < 3.5 else
                "Very Challenging! 💯"
            )
            
            self.required_result_label.setText(
                f"✅ To reach GPA {target:.2f}, you need an average of "
                f"<b>{required:.2f}</b> in your remaining {remaining} ECTS.<br>"
                f"Difficulty: <b>{difficulty}</b>"
            )
            self.required_result_label.setStyleSheet("color: green;")


class AcademicTab(QWidget):
    """Main academic features tab."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Sub-tabs
        self.tab_widget = QTabWidget()
        
        # Prerequisites tab
        self.prereq_viewer = PrerequisiteViewer()
        self.tab_widget.addTab(self.prereq_viewer, "📚 Prerequisites")
        
        # GPA Calculator tab
        self.gpa_calculator = GPACalculatorWidget()
        self.tab_widget.addTab(self.gpa_calculator, "📊 GPA Calculator")
        
        # Graduation Planner tab
        self.grad_planner = GraduationPlannerWidget()
        self.tab_widget.addTab(self.grad_planner, "🎓 Graduation")
        
        # Transcript Import tab
        self.transcript_import = TranscriptImportWidget()
        self.transcript_import.transcript_imported.connect(self._on_transcript_imported)
        self.tab_widget.addTab(self.transcript_import, "📥 Import")
        
        layout.addWidget(self.tab_widget)
    
    def _on_transcript_imported(self, transcript: Transcript):
        """Handle transcript import."""
        # Update GPA calculator and graduation planner
        self.gpa_calculator.set_transcript(transcript)
        self.grad_planner.set_transcript(transcript)
        
        # Show success message
        QMessageBox.information(
            self,
            "Transcript Loaded",
            f"✅ Transcript loaded for {transcript.student_name}!\n\n"
            f"GPA: {transcript.get_gpa():.2f}\n"
            f"ECTS: {transcript.get_total_ects()}\n"
            f"Courses: {len(transcript.grades)}"
        )
    
    def set_courses(self, courses: List[Course]):
        """Set courses for prerequisite viewer."""
        self.prereq_viewer.set_courses(courses)
        self.grad_planner.set_available_courses(courses)
    
    def set_transcript(self, transcript: Transcript):
        """Set transcript for GPA calculator and graduation planner."""
        self.gpa_calculator.set_transcript(transcript)
        self.grad_planner.set_transcript(transcript)
