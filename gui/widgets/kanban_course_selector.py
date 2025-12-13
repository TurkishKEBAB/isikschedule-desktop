"""Kanban-style drag-and-drop course selector widget."""

from __future__ import annotations

from typing import Dict, List, Optional, Set

from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QDrag, QColor, QPalette
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QSizePolicy,
)

from core.models import Course, CourseGroup
from core.curriculum_manager import get_curriculum_manager


class DraggableCourseItem(QListWidgetItem):
    """A course item that can be dragged between columns."""

    def __init__(
        self,
        main_code: str,
        course_name: str,
        ects: int,
        section_count: int,
        is_curriculum: bool = False
    ):
        display_text = f"{main_code}\n{course_name[:30]}{'...' if len(course_name) > 30 else ''}\n{ects} ECTS • {section_count} sections"
        super().__init__(display_text)
        self.main_code = main_code
        self.course_name = course_name
        self.ects = ects
        self.section_count = section_count
        self.is_curriculum = is_curriculum

        # Highlight curriculum courses
        if is_curriculum:
            self.setBackground(QColor("#E3F2FD"))  # Light blue
            self.setToolTip("✅ Bu ders müfredatınızda / This course is in your curriculum")

        # Set size hint for better visibility
        self.setSizeHint(self.sizeHint().expandedTo(self.sizeHint()))


class KanbanColumn(QWidget):
    """A single Kanban column that accepts dropped items."""

    item_dropped = pyqtSignal(str, str)  # course_code, column_id
    item_removed = pyqtSignal(str, str)  # course_code, column_id

    def __init__(
        self,
        column_id: str,
        title: str,
        color: str,
        icon: str = "",
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.column_id = column_id
        self._color = color
        self._setup_ui(title, icon)

    def _setup_ui(self, title: str, icon: str) -> None:
        """Setup column UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Header
        header = QLabel(f"{icon} {title}")
        header.setStyleSheet(f"""
            font-weight: bold;
            font-size: 14px;
            color: {self._color};
            padding: 8px;
            background-color: {self._color}20;
            border-radius: 5px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Count label
        self.count_label = QLabel("0 courses • 0 ECTS")
        self.count_label.setStyleSheet("color: #757575; font-size: 11px;")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.count_label)

        # List widget for courses
        self.course_list = QListWidget()
        self.course_list.setDragEnabled(True)
        self.course_list.setAcceptDrops(True)
        self.course_list.setDropIndicatorShown(True)
        self.course_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.course_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.course_list.setStyleSheet(f"""
            QListWidget {{
                border: 2px dashed {self._color}60;
                border-radius: 8px;
                background-color: {self._color}10;
                padding: 5px;
            }}
            QListWidget::item {{
                background-color: white;
                border: 1px solid {self._color}40;
                border-radius: 5px;
                padding: 8px;
                margin: 3px;
            }}
            QListWidget::item:selected {{
                background-color: {self._color}30;
                border: 2px solid {self._color};
            }}
            QListWidget::item:hover {{
                background-color: {self._color}20;
            }}
        """)

        # Enable drag and drop between lists
        self.course_list.setDragDropMode(QListWidget.DragDropMode.DragDrop)

        layout.addWidget(self.course_list, stretch=1)

        # Set minimum width
        self.setMinimumWidth(220)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def add_course(
        self,
        main_code: str,
        course_name: str,
        ects: int,
        section_count: int,
        is_curriculum: bool = False
    ) -> None:
        """Add a course to this column."""
        item = DraggableCourseItem(main_code, course_name, ects, section_count, is_curriculum)
        self.course_list.addItem(item)
        self._update_count()

    def remove_course(self, main_code: str) -> bool:
        """Remove a course from this column."""
        for i in range(self.course_list.count()):
            item = self.course_list.item(i)
            if isinstance(item, DraggableCourseItem) and item.main_code == main_code:
                self.course_list.takeItem(i)
                self._update_count()
                return True
        return False

    def get_course_codes(self) -> Set[str]:
        """Get all course codes in this column."""
        codes = set()
        for i in range(self.course_list.count()):
            item = self.course_list.item(i)
            if isinstance(item, DraggableCourseItem):
                codes.add(item.main_code)
        return codes

    def get_total_ects(self) -> int:
        """Get total ECTS in this column."""
        total = 0
        for i in range(self.course_list.count()):
            item = self.course_list.item(i)
            if isinstance(item, DraggableCourseItem):
                total += item.ects
        return total

    def _update_count(self) -> None:
        """Update the count label."""
        count = self.course_list.count()
        ects = self.get_total_ects()
        self.count_label.setText(f"{count} courses • {ects} ECTS")

    def clear(self) -> None:
        """Clear all courses from this column."""
        self.course_list.clear()
        self._update_count()

    def contains(self, main_code: str) -> bool:
        """Check if column contains a course."""
        for i in range(self.course_list.count()):
            item = self.course_list.item(i)
            if isinstance(item, DraggableCourseItem) and item.main_code == main_code:
                return True
        return False


class KanbanCourseSelector(QWidget):
    """
    Kanban-style course selector with three columns:
    - Pool: All available courses
    - Optional: Courses to try to include
    - Mandatory: Courses that must be included
    """

    selection_changed = pyqtSignal(set, set)  # mandatory_codes, optional_codes

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._course_groups: Dict[str, CourseGroup] = {}
        self._active_program: Optional[str] = None
        self._active_year: Optional[int] = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Setup the Kanban board UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Instructions
        instructions = QLabel(
            "📋 <b>Drag courses between columns to select them.</b> "
            "Courses in <b style='color:#4CAF50'>Mandatory</b> will always be included. "
            "Courses in <b style='color:#FF9800'>Optional</b> will be included if possible."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("background-color: #E3F2FD; padding: 10px; border-radius: 5px; margin-bottom: 10px;")
        main_layout.addWidget(instructions)

        # ECTS summary bar
        self.ects_summary = QLabel("Selected: 0 ECTS (Mandatory: 0 + Optional: 0)")
        self.ects_summary.setStyleSheet("""
            font-weight: bold;
            font-size: 13px;
            padding: 8px;
            background-color: #FFF3E0;
            border-radius: 5px;
            border: 1px solid #FFB74D;
        """)
        self.ects_summary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.ects_summary)

        # Kanban columns container
        columns_widget = QWidget()
        columns_layout = QHBoxLayout(columns_widget)
        columns_layout.setSpacing(15)

        # Create three columns
        self.pool_column = KanbanColumn(
            "pool", "Course Pool", "#2196F3", "📚"
        )
        self.optional_column = KanbanColumn(
            "optional", "Optional (Try to Include)", "#FF9800", "❓"
        )
        self.mandatory_column = KanbanColumn(
            "mandatory", "Mandatory (Must Include)", "#4CAF50", "✅"
        )

        columns_layout.addWidget(self.pool_column)
        columns_layout.addWidget(self.optional_column)
        columns_layout.addWidget(self.mandatory_column)

        # Scroll area for columns
        scroll = QScrollArea()
        scroll.setWidget(columns_widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setMinimumHeight(400)

        main_layout.addWidget(scroll, stretch=1)

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        # Connect list model changes to emit selection updates
        for column in [self.pool_column, self.optional_column, self.mandatory_column]:
            model = column.course_list.model()
            if model:
                model.rowsInserted.connect(self._on_selection_changed)
                model.rowsRemoved.connect(self._on_selection_changed)

    def _on_selection_changed(self, parent=None, first=0, last=0) -> None:
        """Handle selection changes and emit signal."""
        mandatory = self.mandatory_column.get_course_codes()
        optional = self.optional_column.get_course_codes()

        # Update ECTS summary
        mandatory_ects = self.mandatory_column.get_total_ects()
        optional_ects = self.optional_column.get_total_ects()
        total = mandatory_ects + optional_ects

        self.ects_summary.setText(
            f"Selected: {total} ECTS (Mandatory: {mandatory_ects} + Optional: {optional_ects})"
        )

        # Update column counts
        self.pool_column._update_count()
        self.optional_column._update_count()
        self.mandatory_column._update_count()

        self.selection_changed.emit(mandatory, optional)

    def set_course_groups(self, course_groups: Dict[str, CourseGroup]) -> None:
        """Set available course groups and populate pool."""
        self._course_groups = course_groups
        self._rebuild_pool()

    def set_active_program(self, program_code: str, year: int) -> None:
        """Set the active curriculum program for filtering."""
        self._active_program = program_code
        self._active_year = year
        self._rebuild_pool()
        print(f"Kanban: Active program set to {program_code} ({year})")

    def _is_in_curriculum(self, main_code: str) -> bool:
        """Check if a course is in the active curriculum."""
        if not self._active_program or not self._active_year:
            return False

        curriculum_mgr = get_curriculum_manager()
        program = curriculum_mgr.get_program(self._active_program, self._active_year)
        if not program:
            return False

        curriculum_codes = program.get_course_codes()
        return main_code in curriculum_codes

    def set_courses(self, courses: List[Dict]) -> None:
        """Set available courses from a list of dictionaries.

        Args:
            courses: List of dicts with keys: code, name, ects, sections
        """
        # Clear all columns
        self.pool_column.clear()
        self.optional_column.clear()
        self.mandatory_column.clear()

        # Store course data internally
        self._course_data = {c['code']: c for c in courses}

        # Add all courses to pool
        for course in courses:
            is_curriculum = self._is_in_curriculum(course['code'])
            self.pool_column.add_course(
                course['code'],
                course['name'],
                course.get('ects', 0),
                course.get('sections', 1),
                is_curriculum
            )

        self._on_selection_changed()

    def _rebuild_pool(self) -> None:
        """Rebuild the pool column with all courses."""
        # Save current selections
        mandatory = self.mandatory_column.get_course_codes()
        optional = self.optional_column.get_course_codes()

        # Clear all columns
        self.pool_column.clear()
        self.optional_column.clear()
        self.mandatory_column.clear()

        # Add courses to appropriate columns
        for main_code, group in sorted(self._course_groups.items()):
            if not group.courses:
                continue

            first_course = group.courses[0]
            course_name = first_course.name
            ects = first_course.ects
            section_count = len(group.courses)
            is_curriculum = self._is_in_curriculum(main_code)

            if main_code in mandatory:
                self.mandatory_column.add_course(main_code, course_name, ects, section_count, is_curriculum)
            elif main_code in optional:
                self.optional_column.add_course(main_code, course_name, ects, section_count, is_curriculum)
            else:
                self.pool_column.add_course(main_code, course_name, ects, section_count, is_curriculum)

        self._on_selection_changed()

    def get_selected_courses(self) -> tuple[Set[str], Set[str]]:
        """Get currently selected courses."""
        return (
            self.mandatory_column.get_course_codes(),
            self.optional_column.get_course_codes()
        )

    def select_all_mandatory(self) -> None:
        """Move all courses to mandatory."""
        for main_code, group in self._course_groups.items():
            if not self.mandatory_column.contains(main_code):
                first_course = group.courses[0] if group.courses else None
                if first_course:
                    self.pool_column.remove_course(main_code)
                    self.optional_column.remove_course(main_code)
                    self.mandatory_column.add_course(
                        main_code, first_course.name, first_course.ects, len(group.courses)
                    )
        self._on_selection_changed()

    def clear_selection(self) -> None:
        """Move all courses back to pool."""
        self._rebuild_pool()


__all__ = ["KanbanCourseSelector", "KanbanColumn", "DraggableCourseItem"]
