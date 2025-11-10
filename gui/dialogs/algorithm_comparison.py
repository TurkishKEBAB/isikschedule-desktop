"""Algorithm comparison dialog for side-by-side analysis."""

from __future__ import annotations

from typing import Dict, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.models import Schedule
from gui.widgets import ScheduleGrid


class AlgorithmComparisonDialog(QDialog):
    """Dialog for comparing schedules from different algorithms."""

    def __init__(
        self, algorithm_results: Dict[str, List[Schedule]], parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.algorithm_results = algorithm_results
        self.setWindowTitle("⚖️ Algorithm Comparison")
        self.setMinimumSize(1200, 800)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("<h2>⚖️ Algorithm Performance Comparison</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Summary table
        summary_group = self._create_summary_table()
        layout.addWidget(summary_group)

        # Side-by-side schedules
        schedules_group = self._create_schedules_comparison()
        layout.addWidget(schedules_group, stretch=1)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _create_summary_table(self) -> QGroupBox:
        """Create summary comparison table."""
        group = QGroupBox("📊 Algorithm Performance Summary")
        layout = QVBoxLayout(group)

        table = QTableWidget()
        headers = [
            "Algorithm",
            "Schedules Found",
            "Best ECTS",
            "Min Conflicts",
            "Avg ECTS",
            "Avg Conflicts",
        ]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(self.algorithm_results))

        row = 0
        for algorithm, schedules in self.algorithm_results.items():
            if not schedules:
                continue

            # Calculate statistics
            total_ects = sum(s.total_credits for s in schedules)
            total_conflicts = sum(s.conflict_count for s in schedules)
            best_ects = max(s.total_credits for s in schedules)
            min_conflicts = min(s.conflict_count for s in schedules)
            avg_ects = total_ects / len(schedules)
            avg_conflicts = total_conflicts / len(schedules)

            # Add row
            table.setItem(row, 0, QTableWidgetItem(algorithm))
            table.setItem(row, 1, QTableWidgetItem(str(len(schedules))))
            table.setItem(row, 2, QTableWidgetItem(str(best_ects)))
            table.setItem(row, 3, QTableWidgetItem(str(min_conflicts)))
            table.setItem(row, 4, QTableWidgetItem(f"{avg_ects:.1f}"))
            table.setItem(row, 5, QTableWidgetItem(f"{avg_conflicts:.1f}"))

            # Color code based on performance
            if min_conflicts == 0:
                for col in range(6):
                    table.item(row, col).setBackground(Qt.GlobalColor.green)
            elif min_conflicts <= 2:
                for col in range(6):
                    table.item(row, col).setBackground(Qt.GlobalColor.yellow)

            row += 1

        table.resizeColumnsToContents()
        layout.addWidget(table)

        return group

    def _create_schedules_comparison(self) -> QGroupBox:
        """Create side-by-side schedule comparison."""
        group = QGroupBox("📅 Best Schedules Comparison")
        layout = QHBoxLayout(group)

        # Create a grid for each algorithm's best schedule
        for algorithm, schedules in self.algorithm_results.items():
            if not schedules:
                continue

            # Find best schedule (max ECTS, min conflicts)
            best_schedule = min(
                schedules,
                key=lambda s: (s.conflict_count, -s.total_credits),
            )

            # Create widget for this algorithm
            algo_widget = QWidget()
            algo_layout = QVBoxLayout(algo_widget)
            algo_layout.setContentsMargins(5, 5, 5, 5)

            # Algorithm name and stats
            algo_label = QLabel(f"<b>{algorithm}</b>")
            algo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            algo_layout.addWidget(algo_label)

            stats_label = QLabel(
                f"ECTS: {best_schedule.total_credits} | "
                f"Conflicts: {best_schedule.conflict_count}"
            )
            stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            algo_layout.addWidget(stats_label)

            # Schedule grid
            scroll = QScrollArea()
            grid = ScheduleGrid()
            grid.set_schedule(best_schedule)
            scroll.setWidget(grid)
            scroll.setWidgetResizable(True)
            algo_layout.addWidget(scroll)

            layout.addWidget(algo_widget)

        return group


__all__ = ["AlgorithmComparisonDialog"]
