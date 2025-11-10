"""Course selector tab with tri-state selection."""

from __future__ import annotations

from typing import Dict, List, Optional, Set

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.models import Course, CourseGroup


class CourseSelectorTab(QWidget):
    """Tab for selecting courses with tri-state logic."""

    selection_changed = pyqtSignal(set, set)  # mandatory_codes, optional_codes

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._course_groups: Dict[str, CourseGroup] = {}
        self._mandatory: Set[str] = set()
        self._optional: Set[str] = set()
        self._checkboxes: Dict[str, QCheckBox] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

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

        # Selection summary
        self.summary_label = QLabel("No courses loaded")
        self.summary_label.setStyleSheet("color: #757575; font-weight: bold;")
        layout.addWidget(self.summary_label)

    def set_course_groups(self, course_groups: Dict[str, CourseGroup]) -> None:
        """Update course groups and rebuild selection UI."""
        self._course_groups = course_groups
        self._rebuild_selection_ui()

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
        """Handle checkbox state change."""
        if state == Qt.CheckState.Checked.value:
            # Mandatory
            self._mandatory.add(main_code)
            self._optional.discard(main_code)
        elif state == Qt.CheckState.PartiallyChecked.value:
            # Optional
            self._mandatory.discard(main_code)
            self._optional.add(main_code)
        else:
            # Excluded
            self._mandatory.discard(main_code)
            self._optional.discard(main_code)

        self._update_summary()
        self.selection_changed.emit(self._mandatory.copy(), self._optional.copy())

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
