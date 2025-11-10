"""Course browser tab with advanced search and filter capabilities."""

from __future__ import annotations

from typing import List, Optional, Set, Tuple

import pandas as pd

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QFrame,
    QProgressBar,
    QMessageBox,
    QFileDialog,
)

from core.models import Course


class CourseBrowserTab(QWidget):
    """Tab for browsing and searching courses with advanced filters."""

    course_selected = pyqtSignal(Course)
    courses_updated = pyqtSignal(list)  # Emitted when courses are deleted

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._courses: List[Course] = []
        self._filtered_courses: List[Course] = []
        self._selected_courses: Set[str] = set()  # For conflict detection
        self._favorites: Set[str] = set()  # Favorite course codes
        self._filters_visible = False

        # Debouncing timer for search/sort (quick filters)
        self._filter_timer = QTimer()
        self._filter_timer.setSingleShot(True)
        self._filter_timer.timeout.connect(self._apply_filters_delayed)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Search and quick filters (always visible)
        quick_filter = self._create_quick_filter_section()
        layout.addWidget(quick_filter)

        # Advanced filters (collapsible)
        self.advanced_filters = self._create_advanced_filters()
        self.advanced_filters.setVisible(False)
        layout.addWidget(self.advanced_filters)

        # Course table
        table_group = self._create_table_section()
        layout.addWidget(table_group, stretch=1)

    def _create_quick_filter_section(self) -> QWidget:
        """Create always-visible quick search and sort controls."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Search bar
        search_icon = QLabel("🔍")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by course code, name, or teacher...")
        self.search_edit.textChanged.connect(self._on_quick_filter_changed)

        # Toggle filters button
        self.toggle_filters_btn = QPushButton("🔽 Show Filters")
        self.toggle_filters_btn.setCheckable(True)
        self.toggle_filters_btn.toggled.connect(self._toggle_filters)
        self.toggle_filters_btn.setMaximumWidth(150)

        # Sort dropdown
        sort_label = QLabel("Sort:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Code (A-Z)",
            "Code (Z-A)",
            "Name (A-Z)",
            "Name (Z-A)",
            "ECTS (Low-High)",
            "ECTS (High-Low)",
            "Capacity (Most Available)",
        ])
        self.sort_combo.currentTextChanged.connect(self._on_quick_filter_changed)
        self.sort_combo.setMaximumWidth(200)

        # Export CSV button
        self.export_csv_btn = QPushButton("📤 Export CSV")
        self.export_csv_btn.clicked.connect(self._export_to_csv)
        self.export_csv_btn.setToolTip("Export filtered courses to CSV")
        self.export_csv_btn.setMaximumWidth(130)

        layout.addWidget(search_icon)
        layout.addWidget(self.search_edit, stretch=1)
        layout.addWidget(self.export_csv_btn)
        layout.addWidget(self.toggle_filters_btn)
        layout.addWidget(sort_label)
        layout.addWidget(self.sort_combo)

        return widget

    def _create_advanced_filters(self) -> QGroupBox:
        """Create collapsible advanced filter panel."""
        group = QGroupBox("🎯 Advanced Filters")
        main_layout = QVBoxLayout(group)

        # Create filter grid
        grid = QGridLayout()
        grid.setSpacing(15)

        row = 0

        # === BASIC FILTERS ===
        # Campus filter
        grid.addWidget(QLabel("🏢 <b>Campus:</b>"), row, 0, Qt.AlignmentFlag.AlignTop)
        campus_widget = QWidget()
        campus_layout = QVBoxLayout(campus_widget)
        campus_layout.setContentsMargins(0, 0, 0, 0)
        self.campus_sile = QCheckBox("Şile")
        self.campus_online = QCheckBox("Online")
        self.campus_all = QCheckBox("All")
        self.campus_all.setChecked(True)
        self.campus_all.toggled.connect(lambda checked: self._toggle_all_checkboxes(
            [self.campus_sile, self.campus_online], checked
        ))
        campus_layout.addWidget(self.campus_all)
        campus_layout.addWidget(self.campus_sile)
        campus_layout.addWidget(self.campus_online)
        campus_layout.addStretch()
        grid.addWidget(campus_widget, row, 1)

        # Faculty filter
        grid.addWidget(QLabel("🎓 <b>Faculty:</b>"), row, 2, Qt.AlignmentFlag.AlignTop)
        self.faculty_combo = QComboBox()
        self.faculty_combo.addItem("All Faculties")
        # Removed auto-trigger for performance
        grid.addWidget(self.faculty_combo, row, 3)

        row += 1

        # Course prefix filter
        grid.addWidget(QLabel("🔤 <b>Prefix:</b>"), row, 0)
        self.prefix_combo = QComboBox()
        self.prefix_combo.addItem("All Prefixes")
        self.prefix_combo.setEditable(True)
        # Removed auto-trigger for performance
        grid.addWidget(self.prefix_combo, row, 1)

        # Teacher filter
        grid.addWidget(QLabel("👤 <b>Teacher:</b>"), row, 2)
        self.teacher_combo = QComboBox()
        self.teacher_combo.addItem("All Teachers")
        self.teacher_combo.setEditable(True)
        # Removed auto-trigger for performance
        grid.addWidget(self.teacher_combo, row, 3)

        row += 1

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        grid.addWidget(line, row, 0, 1, 4)
        row += 1

        # === ACADEMIC FILTERS ===
        # ECTS filter
        grid.addWidget(QLabel("💳 <b>ECTS Credits:</b>"), row, 0)
        ects_widget = QWidget()
        ects_layout = QHBoxLayout(ects_widget)
        ects_layout.setContentsMargins(0, 0, 0, 0)
        self.ects_min_slider = QSlider(Qt.Orientation.Horizontal)
        self.ects_min_slider.setRange(0, 12)
        self.ects_min_slider.setValue(0)
        self.ects_max_slider = QSlider(Qt.Orientation.Horizontal)
        self.ects_max_slider.setRange(0, 12)
        self.ects_max_slider.setValue(12)
        self.ects_min_label = QLabel("0")
        self.ects_max_label = QLabel("12")
        self.ects_min_slider.valueChanged.connect(lambda v: self.ects_min_label.setText(str(v)))
        self.ects_max_slider.valueChanged.connect(lambda v: self.ects_max_label.setText(str(v)))
        ects_layout.addWidget(QLabel("Min:"))
        ects_layout.addWidget(self.ects_min_slider)
        ects_layout.addWidget(self.ects_min_label)
        ects_layout.addWidget(QLabel("Max:"))
        ects_layout.addWidget(self.ects_max_slider)
        ects_layout.addWidget(self.ects_max_label)
        grid.addWidget(ects_widget, row, 1, 1, 3)

        row += 1

        # Class level filter
        grid.addWidget(QLabel("📊 <b>Level:</b>"), row, 0)
        level_widget = QWidget()
        level_layout = QHBoxLayout(level_widget)
        level_layout.setContentsMargins(0, 0, 0, 0)
        self.level_1xxx = QCheckBox("1xxx (Freshman)")
        self.level_2xxx = QCheckBox("2xxx (Sophomore)")
        self.level_3xxx = QCheckBox("3xxx (Junior)")
        self.level_4xxx = QCheckBox("4xxx (Senior)")
        for cb in [self.level_1xxx, self.level_2xxx, self.level_3xxx, self.level_4xxx]:
            cb.setChecked(True)
            # Removed auto-trigger for performance
            level_layout.addWidget(cb)
        grid.addWidget(level_widget, row, 1, 1, 3)

        row += 1

        # Separator
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        grid.addWidget(line2, row, 0, 1, 4)
        row += 1

        # === TIME FILTERS ===
        # Day selector
        grid.addWidget(QLabel("📅 <b>Days:</b>"), row, 0, Qt.AlignmentFlag.AlignTop)
        days_widget = QWidget()
        days_layout = QHBoxLayout(days_widget)
        days_layout.setContentsMargins(0, 0, 0, 0)
        self.day_monday = QCheckBox("Mon")
        self.day_tuesday = QCheckBox("Tue")
        self.day_wednesday = QCheckBox("Wed")
        self.day_thursday = QCheckBox("Thu")
        self.day_friday = QCheckBox("Fri")
        self.day_saturday = QCheckBox("Sat")
        self.day_sunday = QCheckBox("Sun")
        self.day_checkboxes = [
            self.day_monday, self.day_tuesday, self.day_wednesday,
            self.day_thursday, self.day_friday, self.day_saturday, self.day_sunday
        ]
        for cb in self.day_checkboxes:
            cb.setChecked(True)
            # Removed auto-trigger for performance
            days_layout.addWidget(cb)
        days_layout.addStretch()
        grid.addWidget(days_widget, row, 1, 1, 3)

        row += 1

        # Time range filter
        grid.addWidget(QLabel("⏰ <b>Time:</b>"), row, 0)
        time_widget = QWidget()
        time_layout = QHBoxLayout(time_widget)
        time_layout.setContentsMargins(0, 0, 0, 0)
        self.time_morning = QCheckBox("Morning (1-4)")
        self.time_afternoon = QCheckBox("Afternoon (5-8)")
        self.time_evening = QCheckBox("Evening (9+)")
        for cb in [self.time_morning, self.time_afternoon, self.time_evening]:
            cb.setChecked(True)
            # Removed auto-trigger for performance
            time_layout.addWidget(cb)
        time_layout.addStretch()
        grid.addWidget(time_widget, row, 1, 1, 3)

        row += 1

        # Course type filter
        grid.addWidget(QLabel("📚 <b>Type:</b>"), row, 0)
        type_widget = QWidget()
        type_layout = QHBoxLayout(type_widget)
        type_layout.setContentsMargins(0, 0, 0, 0)
        self.type_lecture = QCheckBox("Lecture")
        self.type_lab = QCheckBox("Lab")
        self.type_ps = QCheckBox("Problem Session")
        for cb in [self.type_lecture, self.type_lab, self.type_ps]:
            cb.setChecked(True)
            # Removed auto-trigger for performance
            type_layout.addWidget(cb)
        type_layout.addStretch()
        grid.addWidget(type_widget, row, 1, 1, 3)

        row += 1

        # Separator
        line3 = QFrame()
        line3.setFrameShape(QFrame.Shape.HLine)
        line3.setFrameShadow(QFrame.Shadow.Sunken)
        grid.addWidget(line3, row, 0, 1, 4)
        row += 1

        # === SPECIAL FILTERS ===
        # Live section filter
        grid.addWidget(QLabel("🌐 <b>Live Section:</b>"), row, 0)
        live_widget = QWidget()
        live_layout = QHBoxLayout(live_widget)
        live_layout.setContentsMargins(0, 0, 0, 0)
        self.live_yes = QCheckBox("Online Only")
        self.live_no = QCheckBox("Physical Only")
        self.live_both = QCheckBox("Both")
        self.live_both.setChecked(True)
        for cb in [self.live_yes, self.live_no, self.live_both]:
            # Removed auto-trigger for performance
            live_layout.addWidget(cb)
        live_layout.addStretch()
        grid.addWidget(live_widget, row, 1, 1, 3)

        row += 1

        # Conflict filter
        grid.addWidget(QLabel("⚠️ <b>Conflicts:</b>"), row, 0)
        self.hide_conflicts = QCheckBox("Hide courses conflicting with selected")
        # Removed auto-trigger for performance
        grid.addWidget(self.hide_conflicts, row, 1, 1, 3)

        row += 1

        # Favorites filter
        grid.addWidget(QLabel("⭐ <b>Favorites:</b>"), row, 0)
        self.show_favorites_only = QCheckBox("Show only favorites")
        # Removed auto-trigger for performance
        grid.addWidget(self.show_favorites_only, row, 1, 1, 3)

        main_layout.addLayout(grid)

        # Action buttons
        button_layout = QHBoxLayout()
        self.clear_filters_btn = QPushButton("🔄 Clear All Filters")
        self.clear_filters_btn.clicked.connect(self._clear_all_filters)
        self.apply_filters_btn = QPushButton("✅ Apply Filters")
        self.apply_filters_btn.clicked.connect(self._apply_filters)
        self.apply_filters_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        button_layout.addStretch()
        button_layout.addWidget(self.clear_filters_btn)
        button_layout.addWidget(self.apply_filters_btn)
        main_layout.addLayout(button_layout)

        return group

    def _toggle_all_checkboxes(self, checkboxes: List[QCheckBox], checked: bool) -> None:
        """Toggle all checkboxes in a group."""
        for cb in checkboxes:
            cb.setChecked(checked)

    def _toggle_filters(self, checked: bool) -> None:
        """Toggle advanced filters visibility."""
        self._filters_visible = checked
        self.advanced_filters.setVisible(checked)
        self.toggle_filters_btn.setText("🔼 Hide Filters" if checked else "🔽 Show Filters")

    def _create_table_section(self) -> QGroupBox:
        """Create course table."""
        group = QGroupBox("📚 Course List")
        layout = QVBoxLayout(group)

        # Table widget
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(8)
        self.course_table.setHorizontalHeaderLabels([
            "⭐", "Code", "Name", "Type", "ECTS", "Teacher", "Schedule", "❌"
        ])

        # Configure table
        self.course_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.course_table.setSelectionMode(
            QTableWidget.SelectionMode.ExtendedSelection  # Multi-select with Ctrl/Shift
        )
        self.course_table.setAlternatingRowColors(True)
        self.course_table.itemSelectionChanged.connect(self._on_selection_changed)

        # Resize columns
        header = self.course_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Favorite
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Code
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Name
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Type
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # ECTS
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Teacher
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # Schedule
            header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Delete

        # Info label
        self.info_label = QLabel("No courses loaded")
        self.info_label.setStyleSheet("color: #757575; font-style: italic;")

        # Selection controls
        selection_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("✅ Select All")
        self.select_all_btn.clicked.connect(self.course_table.selectAll)
        self.select_all_btn.setMaximumWidth(120)
        
        self.deselect_all_btn = QPushButton("❌ Deselect All")
        self.deselect_all_btn.clicked.connect(self.course_table.clearSelection)
        self.deselect_all_btn.setMaximumWidth(120)
        
        self.delete_selected_btn = QPushButton("🗑️ Delete Selected")
        self.delete_selected_btn.clicked.connect(self._delete_selected_courses)
        self.delete_selected_btn.setMaximumWidth(150)
        self.delete_selected_btn.setStyleSheet("QPushButton { color: #d32f2f; font-weight: bold; }")
        
        selection_layout.addWidget(self.select_all_btn)
        selection_layout.addWidget(self.deselect_all_btn)
        selection_layout.addStretch()
        selection_layout.addWidget(self.delete_selected_btn)

        layout.addWidget(self.course_table)
        layout.addWidget(self.info_label)
        layout.addLayout(selection_layout)

        return group

    def set_courses(self, courses: List[Course]) -> None:
        """Update course list and populate filter dropdowns."""
        self._courses = courses
        self._filtered_courses = courses.copy()
        
        # Populate faculty dropdown
        faculties = sorted(set(c.faculty for c in courses if c.faculty))
        self.faculty_combo.clear()
        self.faculty_combo.addItem("All Faculties")
        self.faculty_combo.addItems(faculties)
        
        # Populate prefix dropdown
        import re
        prefixes = set()
        for c in courses:
            if c.code:
                parts = re.split(r'[.-]', c.code)
                if parts:
                    prefixes.add(parts[0])
        prefixes = sorted([p for p in prefixes if p])  # Remove empty strings
        self.prefix_combo.clear()
        self.prefix_combo.addItem("All Prefixes")
        self.prefix_combo.addItems(prefixes)
        
        # Populate teacher dropdown
        teachers = sorted(set(c.teacher for c in courses if c.teacher))
        self.teacher_combo.clear()
        self.teacher_combo.addItem("All Teachers")
        self.teacher_combo.addItems(teachers)
        
        self._update_table()

    def set_selected_courses(self, selected_codes: Set[str]) -> None:
        """Update selected courses for conflict detection."""
        self._selected_courses = selected_codes
        if self.hide_conflicts.isChecked():
            self._apply_filters()

    def add_favorite(self, course_code: str) -> None:
        """Add a course to favorites."""
        self._favorites.add(course_code)
        if self.show_favorites_only.isChecked():
            self._apply_filters()

    def remove_favorite(self, course_code: str) -> None:
        """Remove a course from favorites."""
        self._favorites.discard(course_code)
        if self.show_favorites_only.isChecked():
            self._apply_filters()

    def _get_course_level(self, code: str) -> Optional[int]:
        """Extract course level from code (1xxx, 2xxx, etc.)."""
        import re
        match = re.search(r'(\d)', code)
        if match:
            return int(match.group(1))
        return None

    def _has_time_conflict(self, course1: Course, course2: Course) -> bool:
        """Check if two courses have overlapping schedules."""
        if not course1.schedule or not course2.schedule:
            return False
        schedule1 = set(course1.schedule)
        schedule2 = set(course2.schedule)
        return bool(schedule1 & schedule2)

    def _get_time_period(self, schedule: List[Tuple[str, int]]) -> Set[str]:
        """Determine time periods (morning/afternoon/evening) for a course."""
        periods = set()
        for _, slot in schedule:
            if 1 <= slot <= 4:
                periods.add("morning")
            elif 5 <= slot <= 8:
                periods.add("afternoon")
            else:
                periods.add("evening")
        return periods

    def _on_quick_filter_changed(self) -> None:
        """Debounced trigger for quick filters (search/sort).
        Starts a 300ms timer. If user continues typing/changing within 300ms,
        timer resets. After 300ms of idle, filtering executes once.
        This prevents GUI freeze when filtering large course lists.
        """
        self._filter_timer.stop()
        self._filter_timer.start(300)  # 300ms delay

    def _apply_filters_delayed(self) -> None:
        """Apply filters after debounce delay.
        Called by QTimer after 300ms idle period.
        Triggers the actual filtering operation.
        """
        self._apply_filters()

    def _apply_filters(self) -> None:
        """Apply all active filters to course list."""
        # Show loading indicator
        total = len(self._courses)
        self.info_label.setText(f"🔄 Filtering {total} courses...")
        self.info_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        # Process events to update UI immediately
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
        search_text = self.search_edit.text().lower().strip()
        self._filtered_courses = []

        for course in self._courses:
            # === SEARCH FILTER ===
            if search_text:
                teacher_text = course.teacher.lower() if course.teacher else ""
                if not (
                    search_text in course.code.lower()
                    or search_text in course.name.lower()
                    or search_text in teacher_text
                ):
                    continue

            # === BASIC FILTERS ===
            # Campus filter
            if not self.campus_all.isChecked():
                campus_match = False
                if self.campus_sile.isChecked() and course.campus == "Şile":
                    campus_match = True
                if self.campus_online.isChecked() and course.campus == "Online":
                    campus_match = True
                if not campus_match:
                    continue

            # Faculty filter
            faculty_selected = self.faculty_combo.currentText()
            if faculty_selected != "All Faculties":
                if course.faculty != faculty_selected:
                    continue

            # Prefix filter
            prefix_selected = self.prefix_combo.currentText()
            if prefix_selected != "All Prefixes":
                import re
                course_prefix = re.split(r'[.-]', course.code)[0] if course.code else ""
                if course_prefix != prefix_selected:
                    continue

            # Teacher filter
            teacher_selected = self.teacher_combo.currentText()
            if teacher_selected != "All Teachers":
                if course.teacher != teacher_selected:
                    continue

            # === ACADEMIC FILTERS ===
            # ECTS filter
            ects_min = self.ects_min_slider.value()
            ects_max = self.ects_max_slider.value()
            if not (ects_min <= course.ects <= ects_max):
                continue

            # Level filter
            level = self._get_course_level(course.code)
            if level is not None:
                level_match = False
                if level == 1 and self.level_1xxx.isChecked():
                    level_match = True
                if level == 2 and self.level_2xxx.isChecked():
                    level_match = True
                if level == 3 and self.level_3xxx.isChecked():
                    level_match = True
                if level == 4 and self.level_4xxx.isChecked():
                    level_match = True
                if not level_match:
                    continue

            # === TIME FILTERS ===
            # Day filter
            if course.schedule:
                day_map = {
                    "Monday": self.day_monday,
                    "Tuesday": self.day_tuesday,
                    "Wednesday": self.day_wednesday,
                    "Thursday": self.day_thursday,
                    "Friday": self.day_friday,
                    "Saturday": self.day_saturday,
                    "Sunday": self.day_sunday,
                }
                course_days = set(day for day, _ in course.schedule)
                day_match = any(
                    day in course_days and cb.isChecked()
                    for day, cb in day_map.items()
                )
                if not day_match and course_days:  # Only filter if course has schedule
                    continue

            # Time range filter
            if course.schedule:
                time_periods = self._get_time_period(course.schedule)
                time_match = False
                if self.time_morning.isChecked() and "morning" in time_periods:
                    time_match = True
                if self.time_afternoon.isChecked() and "afternoon" in time_periods:
                    time_match = True
                if self.time_evening.isChecked() and "evening" in time_periods:
                    time_match = True
                if not time_match and time_periods:
                    continue

            # Course type filter
            type_match = False
            if self.type_lecture.isChecked() and course.course_type == "lecture":
                type_match = True
            if self.type_lab.isChecked() and course.course_type == "lab":
                type_match = True
            if self.type_ps.isChecked() and course.course_type == "ps":
                type_match = True
            if not type_match:
                continue

            # === SPECIAL FILTERS ===
            # Live section filter
            if not self.live_both.isChecked():
                # Assume online courses are in "Online" campus
                is_online = course.campus == "Online"
                live_match = False
                if self.live_yes.isChecked() and is_online:
                    live_match = True
                if self.live_no.isChecked() and not is_online:
                    live_match = True
                if not live_match:
                    continue

            # Conflict filter
            if self.hide_conflicts.isChecked() and self._selected_courses:
                has_conflict = False
                for selected_code in self._selected_courses:
                    # Find selected course
                    selected_course = next(
                        (c for c in self._courses if c.code == selected_code),
                        None
                    )
                    if selected_course and self._has_time_conflict(course, selected_course):
                        has_conflict = True
                        break
                if has_conflict:
                    continue

            # Favorites filter
            if self.show_favorites_only.isChecked():
                if course.code not in self._favorites:
                    continue

            # === PASSED ALL FILTERS ===
            self._filtered_courses.append(course)

        # Apply sorting
        self._sort_courses()
        self._update_table()

    def _sort_courses(self) -> None:
        """Sort filtered courses based on selected sort option."""
        sort_option = self.sort_combo.currentText()
        
        if sort_option == "Code (A-Z)":
            self._filtered_courses.sort(key=lambda c: c.code)
        elif sort_option == "Code (Z-A)":
            self._filtered_courses.sort(key=lambda c: c.code, reverse=True)
        elif sort_option == "Name (A-Z)":
            self._filtered_courses.sort(key=lambda c: c.name)
        elif sort_option == "Name (Z-A)":
            self._filtered_courses.sort(key=lambda c: c.name, reverse=True)
        elif sort_option == "ECTS (Low-High)":
            self._filtered_courses.sort(key=lambda c: c.ects)
        elif sort_option == "ECTS (High-Low)":
            self._filtered_courses.sort(key=lambda c: c.ects, reverse=True)
        # Capacity sorting would need quota data from Course model

    def _clear_all_filters(self) -> None:
        """Reset all filters to default state."""
        # Search
        self.search_edit.clear()
        
        # Sort
        self.sort_combo.setCurrentIndex(0)
        
        # Basic filters
        self.campus_all.setChecked(True)
        self.faculty_combo.setCurrentIndex(0)
        self.prefix_combo.setCurrentIndex(0)
        self.teacher_combo.setCurrentIndex(0)
        
        # Academic filters
        self.ects_min_slider.setValue(0)
        self.ects_max_slider.setValue(12)
        for cb in [self.level_1xxx, self.level_2xxx, self.level_3xxx, self.level_4xxx]:
            cb.setChecked(True)
        
        # Time filters
        for cb in self.day_checkboxes:
            cb.setChecked(True)
        for cb in [self.time_morning, self.time_afternoon, self.time_evening]:
            cb.setChecked(True)
        for cb in [self.type_lecture, self.type_lab, self.type_ps]:
            cb.setChecked(True)
        
        # Special filters
        self.live_both.setChecked(True)
        self.hide_conflicts.setChecked(False)
        self.show_favorites_only.setChecked(False)
        
        self._apply_filters()

    def _update_table(self) -> None:
        """Update table with filtered courses (optimized for large datasets)."""
        # Disable updates during bulk operations to prevent redraws
        self.course_table.setUpdatesEnabled(False)
        
        # Clear table efficiently
        self.course_table.clearContents()
        self.course_table.setRowCount(len(self._filtered_courses))

        # Batch insert rows
        for row, course in enumerate(self._filtered_courses):
            # Favorite button
            fav_btn = QPushButton("⭐" if course.code in self._favorites else "☆")
            fav_btn.setMaximumWidth(40)
            fav_btn.setStyleSheet("border: none; font-size: 16px;")
            fav_btn.clicked.connect(lambda checked, c=course: self._toggle_favorite(c))
            self.course_table.setCellWidget(row, 0, fav_btn)

            # Code
            code_item = QTableWidgetItem(course.code)
            code_item.setForeground(Qt.GlobalColor.blue)
            self.course_table.setItem(row, 1, code_item)

            # Name
            self.course_table.setItem(row, 2, QTableWidgetItem(course.name))

            # Type
            type_item = QTableWidgetItem(course.course_type)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # Color code by type
            if course.course_type == "lecture":
                type_item.setForeground(Qt.GlobalColor.darkGreen)
            elif course.course_type == "lab":
                type_item.setForeground(Qt.GlobalColor.darkBlue)
            else:
                type_item.setForeground(Qt.GlobalColor.darkRed)
            self.course_table.setItem(row, 3, type_item)

            # ECTS
            ects_item = QTableWidgetItem(str(course.ects))
            ects_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.course_table.setItem(row, 4, ects_item)

            # Teacher
            teacher_text = str(course.teacher) if course.teacher else "—"
            self.course_table.setItem(row, 5, QTableWidgetItem(teacher_text))

            # Schedule
            schedule_text = ", ".join(
                f"{day[:3]}{slot}" for day, slot in course.schedule
            ) if course.schedule else "—"
            schedule_item = QTableWidgetItem(schedule_text)
            schedule_item.setToolTip(", ".join(
                f"{day} {slot}" for day, slot in course.schedule
            ) if course.schedule else "No schedule")
            self.course_table.setItem(row, 6, schedule_item)

            # Delete button
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumWidth(40)
            delete_btn.setStyleSheet("border: none; font-size: 16px;")
            delete_btn.setToolTip("Remove from list")
            delete_btn.clicked.connect(lambda checked, c=course: self._delete_course(c))
            self.course_table.setCellWidget(row, 7, delete_btn)

        # Re-enable updates and refresh display
        self.course_table.setUpdatesEnabled(True)
        
        # Update info
        total = len(self._courses)
        showing = len(self._filtered_courses)
        if total > 0:
            percentage = (showing / total) * 100
            self.info_label.setText(
                f"📊 Showing <b>{showing}</b> of <b>{total}</b> courses "
                f"({percentage:.1f}%)"
            )
            self.info_label.setStyleSheet("color: #757575; font-style: italic;")
        else:
            self.info_label.setText("No courses loaded")
            self.info_label.setStyleSheet("color: #757575; font-style: italic;")

    def _toggle_favorite(self, course: Course) -> None:
        """Toggle favorite status of a course."""
        if course.code in self._favorites:
            self.remove_favorite(course.code)
        else:
            self.add_favorite(course.code)
        self._update_table()

    def _delete_course(self, course: Course) -> None:
        """Remove course from the list permanently.
        
        Smart deletion:
        - If deleting a lecture with only one section, prompt to delete related Lab/PS
        - If deleting Lab/PS, just delete it (user manages manually)
        - Uses QMessageBox for confirmation
        """
        from PyQt6.QtWidgets import QMessageBox
        
        # Find related courses (same main_code)
        related_courses = [
            c for c in self._courses
            if c.main_code == course.main_code
        ]
        
        # Count lecture sections
        lecture_sections = [
            c for c in related_courses
            if c.course_type == "lecture"
        ]
        
        # Find Lab/PS for this course
        lab_ps_courses = [
            c for c in related_courses
            if c.course_type in ["lab", "ps"]
        ]
        
        courses_to_delete = [course]  # Always delete the selected course
        
        # If deleting a lecture AND it's the only section AND there are Lab/PS
        if (course.course_type == "lecture" and 
            len(lecture_sections) == 1 and 
            len(lab_ps_courses) > 0):
            
            # Build warning message
            lab_ps_names = ", ".join([
                f"{c.code} ({c.course_type.upper()})"
                for c in lab_ps_courses
            ])
            
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Delete Related Courses?")
            msg_box.setText(
                f"You are deleting the only lecture section of <b>{course.main_code}</b>."
            )
            msg_box.setInformativeText(
                f"This course has related Lab/PS sections:\n\n"
                f"{lab_ps_names}\n\n"
                f"Do you want to delete these as well?"
            )
            msg_box.setStandardButtons(
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
            
            # Add detailed text
            msg_box.setDetailedText(
                f"Course: {course.code}\n"
                f"Name: {course.name}\n"
                f"Related sections: {len(lab_ps_courses)}\n"
                f"\n"
                f"Yes: Delete lecture + all Lab/PS\n"
                f"No: Delete only the lecture\n"
                f"Cancel: Keep everything"
            )
            
            result = msg_box.exec()
            
            if result == QMessageBox.StandardButton.Cancel:
                return  # User canceled, do nothing
            elif result == QMessageBox.StandardButton.Yes:
                courses_to_delete.extend(lab_ps_courses)
            # If No, only delete the lecture (already in courses_to_delete)
        
        # Perform deletion (optimized - no immediate table update)
        for c in courses_to_delete:
            if c in self._courses:
                self._courses.remove(c)
            if c in self._filtered_courses:
                self._filtered_courses.remove(c)
        
        # Single table update at the end (prevents multiple redraws)
        self._update_table()
        
        # Emit signal to notify other tabs about the deletion
        self.courses_updated.emit(self._courses.copy())

    def _on_selection_changed(self) -> None:
        """Handle table selection change."""
        selected_rows = self.course_table.selectedIndexes()
        if selected_rows:
            row = selected_rows[0].row()
            if 0 <= row < len(self._filtered_courses):
                course = self._filtered_courses[row]
                self.course_selected.emit(course)

    def get_favorites(self) -> List[str]:
        """Get list of favorite course codes."""
        return list(self._favorites)

    def get_courses(self) -> List[Course]:
        """Get current course list (after deletions)."""
        return self._courses.copy()

    def _export_to_csv(self) -> None:
        """Export filtered courses to CSV file."""
        if not self._filtered_courses:
            QMessageBox.warning(
                self,
                "No Data",
                "No courses to export! Please load courses first."
            )
            return
        
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to CSV",
            "courses_export.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return  # User canceled
        
        try:
            # Create DataFrame from filtered courses
            data = []
            for course in self._filtered_courses:
                # Format schedule for CSV
                schedule_str = ""
                if course.schedule:
                    schedule_parts = [f"{day[:3]}{period}" for day, period in course.schedule]
                    schedule_str = ", ".join(schedule_parts)
                
                data.append({
                    'Course Code': course.code,
                    'Main Code': course.main_code,
                    'Course Name': course.name,
                    'Type': course.course_type,
                    'ECTS': course.ects,
                    'Teacher': course.teacher,
                    'Faculty': course.faculty,
                    'Department': course.department,
                    'Campus': course.campus,
                    'Schedule': schedule_str
                })
            
            df = pd.DataFrame(data)
            
            # Save to CSV
            df.to_csv(file_path, index=False, encoding='utf-8-sig')  # utf-8-sig for Excel compatibility
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Exported {len(self._filtered_courses)} courses to:\n{file_path}"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export courses:\n{str(e)}"
            )

    def _delete_selected_courses(self) -> None:
        """Delete all selected courses from the table."""
        selected_rows = sorted(set(item.row() for item in self.course_table.selectedItems()), reverse=True)
        
        if not selected_rows:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select courses to delete using Ctrl+Click or Shift+Click."
            )
            return
        
        count = len(selected_rows)
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Bulk Deletion",
            f"Delete {count} selected course(s)?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Collect courses to delete
        courses_to_delete = []
        for row in selected_rows:
            if 0 <= row < len(self._filtered_courses):
                courses_to_delete.append(self._filtered_courses[row])
        
        # Delete courses (optimized - no immediate table updates)
        for course in courses_to_delete:
            if course in self._courses:
                self._courses.remove(course)
            if course in self._filtered_courses:
                self._filtered_courses.remove(course)
        
        # Single table update at the end
        self._update_table()
        
        # Emit signal to notify other tabs
        self.courses_updated.emit(self._courses.copy())
        
        QMessageBox.information(
            self,
            "Deletion Complete",
            f"Successfully deleted {count} course(s)."
        )

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QKeyEvent
        
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_F:
                # Ctrl+F: Focus search box
                self.search_edit.setFocus()
                self.search_edit.selectAll()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_A:
                # Ctrl+A: Select all
                self.course_table.selectAll()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_E:
                # Ctrl+E: Export CSV
                self._export_to_csv()
                event.accept()
                return
        elif event.key() == Qt.Key.Key_Delete:
            # Delete: Delete selected
            self._delete_selected_courses()
            event.accept()
            return
        elif event.key() == Qt.Key.Key_F5:
            # F5: Refresh
            self._apply_filters()
            event.accept()
            return
        elif event.key() == Qt.Key.Key_Escape:
            # Escape: Deselect all
            self.course_table.clearSelection()
            event.accept()
            return
        
        # Call parent implementation for other keys
        super().keyPressEvent(event)


__all__ = ["CourseBrowserTab"]
