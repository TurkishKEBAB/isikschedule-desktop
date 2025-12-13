"""Course selector tab with tri-state selection and Kanban view."""

from __future__ import annotations

from typing import Dict, List, Optional, Set

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QSpinBox,
    QProgressBar,
)

from core.models import Course, CourseGroup, Transcript
from gui.widgets import KanbanCourseSelector

# Işık University prerequisite data
try:
    from core.prerequisite_data import (
        get_prerequisites, can_take_course, get_missing_prerequisites
    )
    ISIK_PREREQ_AVAILABLE = True
except ImportError:
    ISIK_PREREQ_AVAILABLE = False


class CourseSelectorTab(QWidget):
    """Tab for selecting courses with tri-state logic and Kanban view."""

    selection_changed = pyqtSignal(set, set)  # mandatory_codes, optional_codes
    request_main_code_filter = pyqtSignal(list, str, str)  # prefixes, custom_text, mode

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._course_groups: Dict[str, CourseGroup] = {}
        self._mandatory: Set[str] = set()
        self._optional: Set[str] = set()
        self._checkboxes: Dict[str, QCheckBox] = {}
        self._transcript: Optional[Transcript] = None
        self._max_ects = 31
        self._setup_ui()

    def set_transcript(self, transcript: Optional[Transcript]) -> None:
        """Set student transcript for prerequisite checking."""
        self._transcript = transcript

    def on_main_code_filter_changed(self, prefixes: List[str], custom_text: str, mode: str) -> None:
        """Handle main code filter changes from Course Browser.

        Args:
            prefixes: List of selected main code prefixes
            custom_text: Custom comma-separated text
            mode: "Starts with" or "Contains"
        """
        # Update Kanban widget if it has a method to show filter status
        # For now, filters are applied in browser tab; selector respects the filtered list
        # Future enhancement: show active filter badge in Kanban view
        pass

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # ECTS Counter and Progress Bar
        ects_layout = QHBoxLayout()

        ects_label = QLabel("🎯 Target ECTS:")
        self.max_ects_spin = QSpinBox()
        self.max_ects_spin.setRange(10, 45)
        self.max_ects_spin.setValue(31)
        self.max_ects_spin.setSuffix(" ECTS")
        self.max_ects_spin.valueChanged.connect(self._on_max_ects_changed)

        ects_layout.addWidget(ects_label)
        ects_layout.addWidget(self.max_ects_spin)
        ects_layout.addSpacing(20)

        # Current ECTS display
        self.current_ects_label = QLabel("Selected: 0 ECTS")
        self.current_ects_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        ects_layout.addWidget(self.current_ects_label)

        ects_layout.addStretch()
        layout.addLayout(ects_layout)

        # ECTS Progress Bar
        self.ects_progress = QProgressBar()
        self.ects_progress.setMinimum(0)
        self.ects_progress.setMaximum(31)
        self.ects_progress.setValue(0)
        self.ects_progress.setFormat("%v / %m ECTS")
        self.ects_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.ects_progress)

        # View Mode Tabs (Classic vs Kanban)
        self.view_tabs = QTabWidget()

        # Classic View (checkbox-based)
        classic_widget = self._create_classic_view()
        self.view_tabs.addTab(classic_widget, "📋 Classic View")

        # Kanban View (drag-drop)
        self.kanban_widget = KanbanCourseSelector()
        self.kanban_widget.selection_changed.connect(self._on_kanban_selection_changed)
        self.view_tabs.addTab(self.kanban_widget, "📊 Kanban View")

        layout.addWidget(self.view_tabs, stretch=1)

        # Selection summary
        self.summary_label = QLabel("No courses loaded")
        self.summary_label.setStyleSheet("color: #757575; font-weight: bold;")
        layout.addWidget(self.summary_label)

    def _create_classic_view(self) -> QWidget:
        """Create classic checkbox-based view."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 10, 0, 0)

        # Instructions
        info_label = QLabel(
            "✅ <b>Check</b> to include course (mandatory)\n"
            "⬜ <b>Uncheck</b> to exclude course\n"
            "❓ <b>Tri-state</b> for optional (will try to include)"
        )
        info_label.setStyleSheet("background-color: #E3F2FD; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)

        # Quick actions
        actions_layout = QHBoxLayout()

        select_all_btn = QPushButton("✅ Select All")
        select_all_btn.clicked.connect(self._select_all)

        deselect_all_btn = QPushButton("⬜ Deselect All")
        deselect_all_btn.clicked.connect(self._deselect_all)

        actions_layout.addWidget(select_all_btn)
        actions_layout.addWidget(deselect_all_btn)
        actions_layout.addStretch()

        layout.addLayout(actions_layout)

        # Course selection area
        self.selection_scroll = QScrollArea()
        self.selection_widget = QWidget()
        self.selection_layout = QVBoxLayout(self.selection_widget)
        self.selection_layout.setSpacing(10)

        self.selection_scroll.setWidget(self.selection_widget)
        self.selection_scroll.setWidgetResizable(True)

        layout.addWidget(self.selection_scroll, stretch=1)

        return widget

    def _on_max_ects_changed(self, value: int) -> None:
        """Handle max ECTS change."""
        self._max_ects = value
        self.ects_progress.setMaximum(value)
        self._update_ects_display()

    def _on_kanban_selection_changed(self, mandatory: set, wishlist: set) -> None:
        """Handle selection change from Kanban view."""
        self._mandatory = mandatory
        self._optional = wishlist

        # Sync to classic view checkboxes
        self._sync_kanban_to_classic()

        self._update_summary()
        self._update_ects_display()
        self.selection_changed.emit(self._mandatory.copy(), self._optional.copy())

    def _sync_kanban_to_classic(self) -> None:
        """Sync Kanban selections to Classic view checkboxes."""
        # Temporarily disconnect signals to avoid recursion
        for main_code, checkbox in self._checkboxes.items():
            checkbox.blockSignals(True)

            # Get course name for display
            course_name = checkbox.text()
            if " - " in course_name:
                # Remove any existing prefix (✅, ❓, etc)
                parts = course_name.split(" - ", 1)
                if len(parts) > 1:
                    name_part = parts[1]
                else:
                    name_part = course_name
            else:
                name_part = course_name

            # Update checkbox state based on Kanban selection
            if main_code in self._mandatory:
                checkbox.setCheckState(Qt.CheckState.Checked)
                checkbox.setText(f"✅ {main_code} - {name_part}")
                checkbox.setStyleSheet("font-weight: bold; color: #2E7D32;")
            elif main_code in self._optional:
                checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
                checkbox.setText(f"❓ {main_code} - {name_part}")
                checkbox.setStyleSheet("font-weight: normal; color: #F57C00;")
            else:
                checkbox.setCheckState(Qt.CheckState.Unchecked)
                checkbox.setText(f"{main_code} - {name_part}")
                checkbox.setStyleSheet("font-weight: normal; color: #757575;")

            checkbox.blockSignals(False)

    def _sync_classic_to_kanban(self) -> None:
        """Sync Classic view selections to Kanban board."""
        # Rebuild Kanban columns based on current selections
        kanban_courses = []
        for main_code, group in self._course_groups.items():
            if group.courses:
                first = group.courses[0]
                kanban_courses.append({
                    'code': main_code,
                    'name': first.name,
                    'ects': first.ects or 0,
                    'sections': len(group.courses)
                })

        # Temporarily disconnect signal to avoid recursion
        self.kanban_widget.selection_changed.disconnect(self._on_kanban_selection_changed)

        # Clear and rebuild Kanban with current selections
        self.kanban_widget.set_courses(kanban_courses)

        # Move courses to appropriate columns
        for code in self._mandatory:
            if code in self._course_groups:
                group = self._course_groups[code]
                first = group.courses[0]
                self.kanban_widget.pool_column.remove_course(code)
                self.kanban_widget.optional_column.remove_course(code)
                self.kanban_widget.mandatory_column.add_course(
                    code, first.name, first.ects or 0, len(group.courses),
                    self.kanban_widget._is_in_curriculum(code)
                )

        for code in self._optional:
            if code in self._course_groups:
                group = self._course_groups[code]
                first = group.courses[0]
                self.kanban_widget.pool_column.remove_course(code)
                self.kanban_widget.mandatory_column.remove_course(code)
                self.kanban_widget.optional_column.add_course(
                    code, first.name, first.ects or 0, len(group.courses),
                    self.kanban_widget._is_in_curriculum(code)
                )

        # Update Kanban display
        self.kanban_widget._on_selection_changed()

        # Reconnect signal
        self.kanban_widget.selection_changed.connect(self._on_kanban_selection_changed)

    def _update_ects_display(self) -> None:
        """Update ECTS counter and progress bar."""
        total_ects = 0
        for code in self._mandatory | self._optional:
            group = self._course_groups.get(code)
            if group and group.courses:
                total_ects += group.courses[0].ects or 0

        self.ects_progress.setValue(min(total_ects, self._max_ects))
        self.current_ects_label.setText(f"Selected: {total_ects} ECTS")

        # Color based on ECTS status
        if total_ects > self._max_ects:
            self.ects_progress.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #d32f2f;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                }
                QProgressBar::chunk {
                    background-color: #d32f2f;
                    border-radius: 3px;
                }
            """)
            self.current_ects_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #d32f2f;")
        elif total_ects >= self._max_ects * 0.8:
            self.ects_progress.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #f57c00;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                }
                QProgressBar::chunk {
                    background-color: #f57c00;
                    border-radius: 3px;
                }
            """)
            self.current_ects_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #f57c00;")
        else:
            self.ects_progress.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 3px;
                }
            """)
            self.current_ects_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2e7d32;")

    def set_course_groups(self, course_groups: Dict[str, CourseGroup]) -> None:
        """Update course groups and rebuild selection UI."""
        self._course_groups = course_groups
        self._rebuild_selection_ui()

        # Update Kanban widget with courses
        kanban_courses = []
        for main_code, group in course_groups.items():
            if group.courses:
                first = group.courses[0]
                kanban_courses.append({
                    'code': main_code,
                    'name': first.name,
                    'ects': first.ects or 0,
                    'sections': len(group.courses)
                })
        self.kanban_widget.set_courses(kanban_courses)

    def _rebuild_selection_ui(self) -> None:
        """Rebuild course selection checkboxes."""
        # Clear existing
        while self.selection_layout.count():
            item = self.selection_layout.takeAt(0)
            widget = item.widget() if item else None
            if widget:
                widget.deleteLater()

        self._checkboxes.clear()

        # Create checkbox for each course group
        for main_code, group in sorted(self._course_groups.items()):
            group_widget = self._create_course_group_widget(main_code, group)
            self.selection_layout.addWidget(group_widget)

        self.selection_layout.addStretch()
        self._update_summary()

    def _create_course_group_widget(
        self, main_code: str, group: CourseGroup
    ) -> QGroupBox:
        """Create widget for a course group."""
        # Get representative course info
        first_course = group.courses[0] if group.courses else None
        if not first_course:
            return QGroupBox(main_code)

        group_box = QGroupBox()
        layout = QVBoxLayout(group_box)

        # Course header with checkbox
        header_layout = QHBoxLayout()

        checkbox = QCheckBox(f"{main_code} - {first_course.name}")
        checkbox.setTristate(True)
        checkbox.setCheckState(Qt.CheckState.Unchecked)
        checkbox.setStyleSheet("font-weight: normal; color: #757575;")  # Initial style

        # Remove the indeterminate style - we'll use text prefix instead

        checkbox.stateChanged.connect(
            lambda state, code=main_code: self._on_checkbox_changed(code, state)
        )
        self._checkboxes[main_code] = checkbox

        header_layout.addWidget(checkbox)
        header_layout.addStretch()

        # Course details
        details = f"📚 {first_course.ects} ECTS | {len(group.courses)} sections available"
        details_label = QLabel(details)
        details_label.setStyleSheet("color: #757575; font-size: 9pt;")

        layout.addLayout(header_layout)
        layout.addWidget(details_label)

        return group_box

    def _on_checkbox_changed(self, main_code: str, state: int) -> None:
        """Handle checkbox state change and update visual indicator."""
        checkbox = self._checkboxes.get(main_code)
        if not checkbox:
            return

        # Check prerequisites if available
        if ISIK_PREREQ_AVAILABLE and self._transcript and state == Qt.CheckState.Checked.value:
            self._check_prerequisites_warning(main_code)

        # Get course name (without prefix)
        course_name = checkbox.text()
        if " - " in course_name:
            _, name_part = course_name.split(" - ", 1)
        else:
            name_part = course_name

        if state == Qt.CheckState.Checked.value:
            # Mandatory - show checkmark
            self._mandatory.add(main_code)
            self._optional.discard(main_code)
            checkbox.setText(f"✅ {main_code} - {name_part}")
            checkbox.setStyleSheet("font-weight: bold; color: #2E7D32;")
        elif state == Qt.CheckState.PartiallyChecked.value:
            # Optional - show X mark
            self._mandatory.discard(main_code)
            self._optional.add(main_code)
            checkbox.setText(f"❓ {main_code} - {name_part}")
            checkbox.setStyleSheet("font-weight: normal; color: #F57C00;")
        else:
            # Excluded - no mark
            self._mandatory.discard(main_code)
            self._optional.discard(main_code)
            checkbox.setText(f"{main_code} - {name_part}")
            checkbox.setStyleSheet("font-weight: normal; color: #757575;")

        self._update_summary()
        self._update_ects_display()

        # Sync to Kanban view
        self._sync_classic_to_kanban()

        self.selection_changed.emit(self._mandatory.copy(), self._optional.copy())

    def _check_prerequisites_warning(self, course_code: str) -> None:
        """Show warning if prerequisites are missing."""
        if not self._transcript:
            return

        # Get completed courses from transcript
        completed = {grade.course_code for grade in self._transcript.grades}

        # Check prerequisites
        missing = get_missing_prerequisites(course_code, list(completed))

        if missing:
            # Show warning dialog
            prereq_names = []
            for prereq in missing:
                prereq_names.append(prereq)

            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("⚠️ Prerequisite Warning")
            msg.setText(f"<b>{course_code}</b> has missing prerequisites:")
            msg.setInformativeText(
                "You have not completed:\n" +
                "\n".join(f"  • {p}" for p in prereq_names) +
                "\n\nDo you still want to add this course?"
            )
            msg.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            msg.setDefaultButton(QMessageBox.StandardButton.No)

            reply = msg.exec()
            if reply == QMessageBox.StandardButton.No:
                # Revert checkbox state
                checkbox = self._checkboxes.get(course_code)
                if checkbox:
                    checkbox.setCheckState(Qt.CheckState.Unchecked)

    def _select_all(self) -> None:
        """Select all courses as mandatory."""
        for checkbox in self._checkboxes.values():
            checkbox.setCheckState(Qt.CheckState.Checked)

    def _deselect_all(self) -> None:
        """Deselect all courses."""
        for checkbox in self._checkboxes.values():
            checkbox.setCheckState(Qt.CheckState.Unchecked)

    def _update_summary(self) -> None:
        """Update selection summary label."""
        total = len(self._course_groups)
        mandatory = len(self._mandatory)
        optional = len(self._optional)
        excluded = total - mandatory - optional

        self.summary_label.setText(
            f"📊 Total: {total} | "
            f"✅ Mandatory: {mandatory} | "
            f"❓ Optional: {optional} | "
            f"⬜ Excluded: {excluded}"
        )

    def get_selected_courses(self) -> tuple[Set[str], Set[str]]:
        """Get currently selected courses."""
        return self._mandatory.copy(), self._optional.copy()


__all__ = ["CourseSelectorTab"]
