"""Course card widget for displaying individual course information."""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.models import Course


class CourseCard(QFrame):
    """Card widget displaying course information with visual styling."""

    clicked = pyqtSignal(Course)
    selected = pyqtSignal(Course, bool)

    def __init__(self, course: Course, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.course = course
        self._is_selected = False
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header with course code and type
        header_layout = QHBoxLayout()
        self.code_label = QLabel(self.course.code)
        self.code_label.setObjectName("courseCode")
        font = self.code_label.font()
        font.setBold(True)
        font.setPointSize(11)
        self.code_label.setFont(font)

        self.type_label = QLabel(self.course.course_type.upper())
        self.type_label.setObjectName("courseType")
        type_font = self.type_label.font()
        type_font.setPointSize(9)
        self.type_label.setFont(type_font)

        header_layout.addWidget(self.code_label)
        header_layout.addStretch()
        header_layout.addWidget(self.type_label)

        # Course name
        self.name_label = QLabel(self.course.name)
        self.name_label.setWordWrap(True)
        self.name_label.setObjectName("courseName")

        # Details row
        details_layout = QHBoxLayout()
        self.teacher_label = QLabel(f"👤 {self.course.teacher}")
        self.teacher_label.setObjectName("courseTeacher")

        self.ects_label = QLabel(f"📚 {self.course.ects} ECTS")
        self.ects_label.setObjectName("courseEcts")

        details_layout.addWidget(self.teacher_label)
        details_layout.addStretch()
        details_layout.addWidget(self.ects_label)

        # Schedule info
        schedule_text = self._format_schedule()
        self.schedule_label = QLabel(schedule_text)
        self.schedule_label.setWordWrap(True)
        self.schedule_label.setObjectName("courseSchedule")

        # Add all to main layout
        layout.addLayout(header_layout)
        layout.addWidget(self.name_label)
        layout.addLayout(details_layout)
        layout.addWidget(self.schedule_label)

        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)

    def _format_schedule(self) -> str:
        """Format schedule information for display."""
        if not self.course.schedule:
            return "📅 No schedule"

        schedule_parts = []
        for day, slot in self.course.schedule:
            schedule_parts.append(f"{day} {slot}")

        return "📅 " + ", ".join(schedule_parts)

    def _apply_style(self) -> None:
        """Apply visual styling to the card."""
        self.setStyleSheet(
            """
            CourseCard {
                background-color: #ffffff;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
            }
            CourseCard:hover {
                border-color: #2196F3;
                background-color: #f5f5f5;
            }
            #courseCode {
                color: #1976D2;
            }
            #courseType {
                color: #757575;
                background-color: #E3F2FD;
                padding: 2px 6px;
                border-radius: 3px;
            }
            #courseName {
                color: #424242;
            }
            #courseTeacher, #courseEcts, #courseSchedule {
                color: #616161;
                font-size: 10pt;
            }
        """
        )

    def mousePressEvent(self, event) -> None:
        """Handle mouse click events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.course)
        super().mousePressEvent(event)

    def set_selected(self, selected: bool) -> None:
        """Update visual state for selection."""
        self._is_selected = selected
        if selected:
            self.setStyleSheet(
                self.styleSheet()
                + """
                CourseCard {
                    border-color: #4CAF50;
                    background-color: #E8F5E9;
                }
            """
            )
        else:
            self._apply_style()
        self.selected.emit(self.course, selected)

    @property
    def is_selected(self) -> bool:
        """Return current selection state."""
        return self._is_selected


__all__ = ["CourseCard"]
