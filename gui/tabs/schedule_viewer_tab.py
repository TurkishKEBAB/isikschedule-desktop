"""Schedule viewer tab with comparison and export features."""

from __future__ import annotations

from typing import Dict, List, Optional

from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.models import Schedule
from gui.widgets import ScheduleGrid


class ScheduleViewerTab(QWidget):
    """Tab for viewing and comparing generated schedules."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._schedules: List[Schedule] = []
        self._algorithm_results: Dict[str, List[Schedule]] = {}
        self._setup_ui()

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
        layout = QVBoxLayout(group)

        # Schedule grid
        scroll = QScrollArea()
        self.schedule_grid = ScheduleGrid()
        scroll.setWidget(self.schedule_grid)
        scroll.setWidgetResizable(True)

        layout.addWidget(scroll)

        return group

    def _create_stats_section(self) -> QGroupBox:
        """Create statistics display."""
        group = QGroupBox("📊 Statistics")
        layout = QVBoxLayout(group)

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(120)
        self.stats_text.setPlainText("No schedule selected")

        layout.addWidget(self.stats_text)

        return group

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
        # Placeholder - will be implemented in Phase 5
        print(f"Export as {format} - To be implemented")

    def _show_comparison(self) -> None:
        """Show algorithm comparison dialog."""
        # Placeholder - will be implemented
        print("Algorithm comparison - To be implemented")


__all__ = ["ScheduleViewerTab"]
