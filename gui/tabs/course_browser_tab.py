"""Course browser tab with search and filter capabilities."""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.models import Course


class CourseBrowserTab(QWidget):
    """Tab for browsing and searching courses."""

    course_selected = pyqtSignal(Course)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._courses: List[Course] = []
        self._filtered_courses: List[Course] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Search and filter section
        filter_group = self._create_filter_section()
        layout.addWidget(filter_group)

        # Course table
        table_group = self._create_table_section()
        layout.addWidget(table_group, stretch=1)

    def _create_filter_section(self) -> QGroupBox:
        """Create search and filter controls."""
        group = QGroupBox("🔍 Search & Filter")
        layout = QVBoxLayout(group)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by code, name, or teacher...")
        self.search_edit.textChanged.connect(self._apply_filters)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_edit, stretch=1)

        # Filter controls
        filter_layout = QHBoxLayout()

        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "lecture", "lab", "ps"])
        self.type_filter.currentTextChanged.connect(self._apply_filters)

        self.ects_filter = QComboBox()
        self.ects_filter.addItems(["All ECTS", "0", "3", "4", "5", "6", "7", "8"])
        self.ects_filter.currentTextChanged.connect(self._apply_filters)

        self.clear_button = QPushButton("Clear Filters")
        self.clear_button.clicked.connect(self._clear_filters)

        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.type_filter)
        filter_layout.addWidget(QLabel("ECTS:"))
        filter_layout.addWidget(self.ects_filter)
        filter_layout.addWidget(self.clear_button)
        filter_layout.addStretch()

        layout.addLayout(search_layout)
        layout.addLayout(filter_layout)

        return group

    def _create_table_section(self) -> QGroupBox:
        """Create course table."""
        group = QGroupBox("📚 Course List")
        layout = QVBoxLayout(group)

        # Table widget
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(6)
        self.course_table.setHorizontalHeaderLabels([
            "Code", "Name", "Type", "ECTS", "Teacher", "Schedule"
        ])

        # Configure table
        self.course_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.course_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.course_table.setAlternatingRowColors(True)
        self.course_table.itemSelectionChanged.connect(self._on_selection_changed)

        # Resize columns
        header = self.course_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

        # Info label
        self.info_label = QLabel("No courses loaded")
        self.info_label.setStyleSheet("color: #757575;")

        layout.addWidget(self.course_table)
        layout.addWidget(self.info_label)

        return group

    def set_courses(self, courses: List[Course]) -> None:
        """Update course list."""
        self._courses = courses
        self._filtered_courses = courses.copy()
        self._update_table()

    def _apply_filters(self) -> None:
        """Apply current filters to course list."""
        search_text = self.search_edit.text().lower()
        type_filter = self.type_filter.currentText()
        ects_filter = self.ects_filter.currentText()

        self._filtered_courses = []

        for course in self._courses:
            # Search filter
            if search_text:
                if not (
                    search_text in course.code.lower()
                    or search_text in course.name.lower()
                    or search_text in course.teacher.lower()
                ):
                    continue

            # Type filter
            if type_filter != "All Types":
                if course.course_type != type_filter:
                    continue

            # ECTS filter
            if ects_filter != "All ECTS":
                if course.ects != int(ects_filter):
                    continue

            self._filtered_courses.append(course)

        self._update_table()

    def _clear_filters(self) -> None:
        """Clear all filters."""
        self.search_edit.clear()
        self.type_filter.setCurrentIndex(0)
        self.ects_filter.setCurrentIndex(0)

    def _update_table(self) -> None:
        """Update table with filtered courses."""
        self.course_table.setRowCount(0)

        for row, course in enumerate(self._filtered_courses):
            self.course_table.insertRow(row)

            # Code
            self.course_table.setItem(row, 0, QTableWidgetItem(course.code))

            # Name
            self.course_table.setItem(row, 1, QTableWidgetItem(course.name))

            # Type
            type_item = QTableWidgetItem(course.course_type)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.course_table.setItem(row, 2, type_item)

            # ECTS
            ects_item = QTableWidgetItem(str(course.ects))
            ects_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.course_table.setItem(row, 3, ects_item)

            # Teacher
            self.course_table.setItem(row, 4, QTableWidgetItem(course.teacher))

            # Schedule
            schedule_text = ", ".join(
                f"{day} {slot}" for day, slot in course.schedule
            )
            self.course_table.setItem(row, 5, QTableWidgetItem(schedule_text))

        # Update info
        total = len(self._courses)
        showing = len(self._filtered_courses)
        self.info_label.setText(f"Showing {showing} of {total} courses")

    def _on_selection_changed(self) -> None:
        """Handle table selection change."""
        selected_rows = self.course_table.selectedIndexes()
        if selected_rows:
            row = selected_rows[0].row()
            if 0 <= row < len(self._filtered_courses):
                course = self._filtered_courses[row]
                self.course_selected.emit(course)


__all__ = ["CourseBrowserTab"]
