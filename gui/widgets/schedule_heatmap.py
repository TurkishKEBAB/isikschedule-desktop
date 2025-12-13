"""Heatmap visualization widget for course schedule density."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QColor, QPainter, QFont, QPen, QBrush
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolTip,
)

from core.models import Course


# Day mapping
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
TURKISH_DAYS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi"]
DAY_ABBREV = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

# Time slots (1-13)
TIME_SLOTS = list(range(1, 14))
SLOT_TIMES = {
    1: "08:30", 2: "09:30", 3: "10:30", 4: "11:30",
    5: "12:30", 6: "13:30", 7: "14:30", 8: "15:30",
    9: "16:30", 10: "17:30", 11: "18:30", 12: "19:30", 13: "20:30"
}


class ScheduleHeatmap(QWidget):
    """
    Heatmap visualization showing course density across the week.

    Darker colors indicate more courses at that time slot.
    """

    cell_clicked = pyqtSignal(str, int, list)  # day, slot, courses at that slot

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._courses: List[Course] = []
        self._density_map: Dict[Tuple[str, int], int] = {}
        self._course_map: Dict[Tuple[str, int], List[Course]] = defaultdict(list)
        self._max_density = 1
        self._hovered_cell: Optional[Tuple[str, int]] = None

        self.setMinimumSize(600, 300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)

    def set_courses(self, courses: List[Course]) -> None:
        """Update the heatmap with new course data."""
        self._courses = courses
        self._calculate_density()
        self.update()

    def _calculate_density(self) -> None:
        """Calculate course density for each time slot."""
        self._density_map.clear()
        self._course_map.clear()
        self._max_density = 1

        for course in self._courses:
            if not course.schedule:
                continue

            # Handle different schedule formats
            if isinstance(course.schedule, dict):
                for day, slots in course.schedule.items():
                    normalized_day = self._normalize_day(day)
                    if normalized_day:
                        for slot in slots:
                            slot_num = self._parse_slot(slot)
                            if slot_num:
                                key = (normalized_day, slot_num)
                                self._density_map[key] = self._density_map.get(key, 0) + 1
                                self._course_map[key].append(course)
            elif isinstance(course.schedule, list):
                for day, slot in course.schedule:
                    normalized_day = self._normalize_day(day)
                    if normalized_day:
                        key = (normalized_day, slot)
                        self._density_map[key] = self._density_map.get(key, 0) + 1
                        self._course_map[key].append(course)

        if self._density_map:
            self._max_density = max(self._density_map.values())

    def _normalize_day(self, day: str) -> Optional[str]:
        """Normalize day name to English."""
        day_lower = day.lower().strip()

        # Turkish to English mapping
        turkish_map = {
            "pazartesi": "Monday",
            "salı": "Tuesday", "sali": "Tuesday",
            "çarşamba": "Wednesday", "carsamba": "Wednesday",
            "perşembe": "Thursday", "persembe": "Thursday",
            "cuma": "Friday",
            "cumartesi": "Saturday",
            "pazar": "Sunday",
        }

        # English days
        english_days = {d.lower(): d for d in DAYS}

        if day_lower in turkish_map:
            return turkish_map[day_lower]
        elif day_lower in english_days:
            return english_days[day_lower]

        return None

    def _parse_slot(self, slot) -> Optional[int]:
        """Parse slot to integer."""
        if isinstance(slot, int):
            return slot
        elif isinstance(slot, str):
            # Try to extract slot number from time string like "09:00-10:50"
            try:
                return int(slot.split(":")[0]) - 7  # Approximate conversion
            except (ValueError, IndexError):
                pass
        return None

    def _get_density_color(self, density: int) -> QColor:
        """Get color based on density (0 = light, max = dark blue)."""
        if density == 0:
            return QColor(240, 240, 240)  # Light gray for empty

        # Normalize to 0-1 range
        ratio = density / self._max_density

        # Color gradient: light blue -> dark blue
        r = int(230 - (ratio * 180))
        g = int(240 - (ratio * 180))
        b = int(255 - (ratio * 80))

        return QColor(r, g, b)

    def paintEvent(self, a0) -> None:
        """Paint the heatmap."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate cell dimensions
        width = self.width()
        height = self.height()

        header_height = 30
        label_width = 50

        cell_width = (width - label_width) / len(DAYS)
        cell_height = (height - header_height) / len(TIME_SLOTS)

        # Draw day headers
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        for i, day in enumerate(DAY_ABBREV):
            x = label_width + i * cell_width
            rect = QRectF(x, 0, cell_width, header_height)
            painter.setPen(Qt.GlobalColor.black)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, day)

        # Draw time slot labels
        painter.setFont(QFont("Segoe UI", 8))
        for i, slot in enumerate(TIME_SLOTS):
            y = header_height + i * cell_height
            rect = QRectF(0, y, label_width, cell_height)
            time_str = SLOT_TIMES.get(slot, str(slot))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, time_str)

        # Draw cells
        for i, day in enumerate(DAYS):
            for j, slot in enumerate(TIME_SLOTS):
                x = label_width + i * cell_width
                y = header_height + j * cell_height

                density = self._density_map.get((day, slot), 0)
                color = self._get_density_color(density)

                rect = QRectF(x + 1, y + 1, cell_width - 2, cell_height - 2)

                # Highlight hovered cell
                if self._hovered_cell == (day, slot):
                    painter.setPen(QPen(QColor(33, 150, 243), 2))
                else:
                    painter.setPen(QPen(QColor(200, 200, 200), 1))

                painter.setBrush(QBrush(color))
                painter.drawRoundedRect(rect, 3, 3)

                # Draw density number if > 0
                if density > 0:
                    painter.setPen(Qt.GlobalColor.black if density < self._max_density * 0.5 else Qt.GlobalColor.white)
                    painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(density))

        # Draw legend
        self._draw_legend(painter, width, height)

    def _draw_legend(self, painter: QPainter, width: int, height: int) -> None:
        """Draw color legend."""
        legend_width = 150
        legend_height = 20
        legend_x = width - legend_width - 10
        legend_y = 5

        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(Qt.GlobalColor.black)

        # Draw gradient bar
        for i in range(legend_width):
            ratio = i / legend_width
            color = self._get_density_color(int(ratio * self._max_density))
            painter.setPen(QPen(color))
            painter.drawLine(legend_x + i, legend_y, legend_x + i, legend_y + legend_height)

        # Draw labels
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(legend_x - 15, legend_y + 14, "0")
        painter.drawText(legend_x + legend_width + 5, legend_y + 14, str(self._max_density))

    def mouseMoveEvent(self, a0) -> None:
        """Handle mouse hover for tooltips."""
        pos = a0.position()

        # Calculate which cell is hovered
        header_height = 30
        label_width = 50
        cell_width = (self.width() - label_width) / len(DAYS)
        cell_height = (self.height() - header_height) / len(TIME_SLOTS)

        x = pos.x() - label_width
        y = pos.y() - header_height

        if x >= 0 and y >= 0:
            day_idx = int(x / cell_width)
            slot_idx = int(y / cell_height)

            if 0 <= day_idx < len(DAYS) and 0 <= slot_idx < len(TIME_SLOTS):
                day = DAYS[day_idx]
                slot = TIME_SLOTS[slot_idx]
                self._hovered_cell = (day, slot)

                # Show tooltip
                courses = self._course_map.get((day, slot), [])
                if courses:
                    tooltip_text = f"<b>{day} - Slot {slot}</b><br>"
                    tooltip_text += f"<b>{len(courses)} courses:</b><br>"
                    for c in courses[:5]:  # Show max 5
                        tooltip_text += f"• {c.code}: {c.name[:25]}...<br>" if len(c.name) > 25 else f"• {c.code}: {c.name}<br>"
                    if len(courses) > 5:
                        tooltip_text += f"<i>...and {len(courses) - 5} more</i>"
                    QToolTip.showText(a0.globalPosition().toPoint(), tooltip_text, self)
                else:
                    QToolTip.hideText()

                self.update()
            else:
                self._hovered_cell = None
                QToolTip.hideText()
                self.update()

    def mousePressEvent(self, a0) -> None:
        """Handle cell click."""
        if self._hovered_cell:
            day, slot = self._hovered_cell
            courses = self._course_map.get((day, slot), [])
            self.cell_clicked.emit(day, slot, courses)


class HeatmapWidget(QWidget):
    """Container widget with heatmap and controls."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QLabel("🗓️ <b>Schedule Density Heatmap</b> - Darker = More courses at that time")
        header.setStyleSheet("padding: 5px; color: #1976D2;")
        layout.addWidget(header)

        # Heatmap
        self.heatmap = ScheduleHeatmap()
        layout.addWidget(self.heatmap, stretch=1)

        # Stats
        self.stats_label = QLabel("Click on a cell to see courses at that time")
        self.stats_label.setStyleSheet("color: #757575; font-size: 11px; padding: 5px;")
        layout.addWidget(self.stats_label)

    def set_courses(self, courses: List[Course]) -> None:
        """Update heatmap with courses."""
        self.heatmap.set_courses(courses)

        # Update stats
        total = len(courses)
        with_schedule = len([c for c in courses if c.schedule])
        self.stats_label.setText(f"Showing {with_schedule} courses with schedule data (out of {total} total)")


__all__ = ["ScheduleHeatmap", "HeatmapWidget"]
