"""Schedule grid widget for displaying weekly timetable."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from PyQt6.QtCore import Qt, QRect, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget

from core.models import Course, Schedule


class ScheduleGrid(QWidget):
    """Visual grid widget for displaying course schedules."""

    course_clicked = pyqtSignal(Course)

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    TIME_SLOTS = list(range(1, 11))  # Slots 1-10
    CELL_WIDTH = 120
    CELL_HEIGHT = 50
    HEADER_HEIGHT = 40
    SIDEBAR_WIDTH = 60

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.schedule: Optional[Schedule] = None
        self._course_rects: Dict[Course, QRect] = {}
        self._init_colors()
        self._setup_ui()

    def _init_colors(self) -> None:
        """Initialize color palette for courses."""
        self.colors = [
            QColor("#E3F2FD"),  # Light Blue
            QColor("#F3E5F5"),  # Light Purple
            QColor("#E8F5E9"),  # Light Green
            QColor("#FFF3E0"),  # Light Orange
            QColor("#FCE4EC"),  # Light Pink
            QColor("#F1F8E9"),  # Light Lime
            QColor("#E0F2F1"),  # Light Teal
            QColor("#FFF9C4"),  # Light Yellow
        ]
        self.color_map: Dict[str, QColor] = {}

    def _setup_ui(self) -> None:
        """Setup widget dimensions."""
        width = self.SIDEBAR_WIDTH + len(self.DAYS) * self.CELL_WIDTH
        height = self.HEADER_HEIGHT + len(self.TIME_SLOTS) * self.CELL_HEIGHT
        self.setMinimumSize(width, height)
        self.setMaximumSize(width + 100, height + 100)

    def set_schedule(self, schedule: Optional[Schedule]) -> None:
        """Update the displayed schedule."""
        self.schedule = schedule
        self._course_rects.clear()
        if schedule:
            self._assign_colors(schedule.courses)
        self.update()

    def _assign_colors(self, courses: List[Course]) -> None:
        """Assign unique colors to course main codes."""
        main_codes = set(course.main_code for course in courses)
        for idx, code in enumerate(sorted(main_codes)):
            self.color_map[code] = self.colors[idx % len(self.colors)]

    def paintEvent(self, event) -> None:
        """Paint the schedule grid."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background
        painter.fillRect(self.rect(), QColor("#FAFAFA"))

        # Draw grid
        self._draw_grid(painter)

        # Draw courses
        if self.schedule:
            self._draw_courses(painter)

    def _draw_grid(self, painter: QPainter) -> None:
        """Draw the grid structure."""
        # Draw headers
        painter.setPen(QPen(QColor("#424242"), 1))
        font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        painter.setFont(font)

        # Day headers
        for day_idx, day in enumerate(self.DAYS):
            x = self.SIDEBAR_WIDTH + day_idx * self.CELL_WIDTH
            rect = QRect(x, 0, self.CELL_WIDTH, self.HEADER_HEIGHT)
            painter.fillRect(rect, QColor("#E3F2FD"))
            painter.drawRect(rect)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, day[:3])

        # Time slot sidebar
        font.setWeight(QFont.Weight.Normal)
        painter.setFont(font)
        for slot_idx, slot in enumerate(self.TIME_SLOTS):
            y = self.HEADER_HEIGHT + slot_idx * self.CELL_HEIGHT
            rect = QRect(0, y, self.SIDEBAR_WIDTH, self.CELL_HEIGHT)
            painter.fillRect(rect, QColor("#E3F2FD"))
            painter.drawRect(rect)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(slot))

        # Grid cells
        painter.setPen(QPen(QColor("#E0E0E0"), 1))
        for day_idx in range(len(self.DAYS)):
            for slot_idx in range(len(self.TIME_SLOTS)):
                x = self.SIDEBAR_WIDTH + day_idx * self.CELL_WIDTH
                y = self.HEADER_HEIGHT + slot_idx * self.CELL_HEIGHT
                rect = QRect(x, y, self.CELL_WIDTH, self.CELL_HEIGHT)
                painter.drawRect(rect)

    def _draw_courses(self, painter: QPainter) -> None:
        """Draw courses on the grid."""
        font = QFont("Segoe UI", 8)
        painter.setFont(font)

        for course in self.schedule.courses:
            color = self.color_map.get(course.main_code, self.colors[0])
            self._draw_course(painter, course, color)

    def _draw_course(self, painter: QPainter, course: Course, color: QColor) -> None:
        """Draw a single course on the grid."""
        if not course.schedule:
            return

        # Group consecutive slots by day
        day_slots: Dict[str, List[int]] = {}
        for day, slot in course.schedule:
            if day not in day_slots:
                day_slots[day] = []
            day_slots[day].append(slot)

        # Draw each day's slots
        for day, slots in day_slots.items():
            if day not in self.DAYS:
                continue

            slots.sort()
            day_idx = self.DAYS.index(day)

            # Find consecutive slot groups
            groups = self._find_consecutive_groups(slots)

            for group in groups:
                start_slot = min(group)
                end_slot = max(group)
                slot_count = end_slot - start_slot + 1

                x = self.SIDEBAR_WIDTH + day_idx * self.CELL_WIDTH + 2
                y = self.HEADER_HEIGHT + (start_slot - 1) * self.CELL_HEIGHT + 2
                width = self.CELL_WIDTH - 4
                height = slot_count * self.CELL_HEIGHT - 4

                rect = QRect(x, y, width, height)
                self._course_rects[course] = rect

                # Draw course block
                painter.fillRect(rect, color)
                painter.setPen(QPen(color.darker(120), 2))
                painter.drawRect(rect)

                # Draw text
                painter.setPen(QPen(QColor("#212121")))
                text_rect = rect.adjusted(4, 4, -4, -4)

                # Course code (bold)
                font_bold = painter.font()
                font_bold.setBold(True)
                painter.setFont(font_bold)
                painter.drawText(
                    text_rect,
                    Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
                    course.main_code,
                )

                # Course type
                font_normal = painter.font()
                font_normal.setBold(False)
                font_normal.setPointSize(7)
                painter.setFont(font_normal)
                type_rect = text_rect.adjusted(0, 16, 0, 0)
                painter.drawText(
                    type_rect,
                    Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
                    f"({course.course_type})",
                )

    def _find_consecutive_groups(self, slots: List[int]) -> List[List[int]]:
        """Find consecutive slot groups."""
        if not slots:
            return []

        groups = []
        current_group = [slots[0]]

        for i in range(1, len(slots)):
            if slots[i] == slots[i - 1] + 1:
                current_group.append(slots[i])
            else:
                groups.append(current_group)
                current_group = [slots[i]]

        groups.append(current_group)
        return groups

    def mousePressEvent(self, event) -> None:
        """Handle mouse clicks on courses."""
        pos = event.pos()
        for course, rect in self._course_rects.items():
            if rect.contains(pos):
                self.course_clicked.emit(course)
                break
        super().mousePressEvent(event)


__all__ = ["ScheduleGrid"]
