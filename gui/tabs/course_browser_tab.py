"""Course browser tab with advanced search and filter capabilities."""

from __future__ import annotations

from typing import List, Optional, Set, Tuple, cast

import pandas as pd

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
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


ALL_FACULTIES = "All Faculties"
ALL_PREFIXES = "All Prefixes"
ALL_TEACHERS = "All Teachers"
ALL_MAIN_CODES = "All Main Codes"
INFO_LABEL_STYLE = "color: #757575; font-style: italic;"


class CourseBrowserTab(QWidget):
    """Tab for browsing and searching courses with advanced filters."""

    course_selected = pyqtSignal(Course)
    courses_updated = pyqtSignal(list)  # Emitted when courses are deleted
    main_code_filter_changed = pyqtSignal(list, str, str)  # prefixes, custom_text, mode

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
        """Create collapsible advanced filter panel with modern card layout."""
        from PyQt6.QtWidgets import QSpinBox, QScrollArea

        group = QGroupBox("🎯 Advanced Filters")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                background-color: white;
            }
        """)
        main_layout: QVBoxLayout = QVBoxLayout(group)
        main_layout.setSpacing(12)

        # === QUICK PRESETS BAR ===
        presets_frame = QFrame()
        presets_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 8px;
                padding: 5px;
            }
        """)
        presets_layout = QHBoxLayout(presets_frame)
        presets_layout.setSpacing(8)
        presets_layout.setContentsMargins(10, 8, 10, 8)

        preset_label = QLabel("⚡ Quick:")
        preset_label.setStyleSheet("color: white; font-weight: bold;")
        presets_layout.addWidget(preset_label)

        preset_btn_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.9);
                border: none;
                border-radius: 12px;
                padding: 6px 12px;
                font-weight: bold;
                color: #333;
                font-size: 11px;
            }
            QPushButton:hover { background-color: white; }
            QPushButton:pressed { background-color: #e0e0e0; }
        """

        self.preset_morning = QPushButton("🌅 Morning")
        self.preset_morning.setStyleSheet(preset_btn_style)
        self.preset_morning.clicked.connect(lambda: self._apply_preset("morning"))

        self.preset_no_weekend = QPushButton("🎉 No Weekend")
        self.preset_no_weekend.setStyleSheet(preset_btn_style)
        self.preset_no_weekend.clicked.connect(lambda: self._apply_preset("no_weekend"))

        self.preset_high_ects = QPushButton("📚 5+ ECTS")
        self.preset_high_ects.setStyleSheet(preset_btn_style)
        self.preset_high_ects.clicked.connect(lambda: self._apply_preset("high_ects"))

        self.preset_lectures = QPushButton("🎓 Lectures")
        self.preset_lectures.setStyleSheet(preset_btn_style)
        self.preset_lectures.clicked.connect(lambda: self._apply_preset("lectures"))

        presets_layout.addWidget(self.preset_morning)
        presets_layout.addWidget(self.preset_no_weekend)
        presets_layout.addWidget(self.preset_high_ects)
        presets_layout.addWidget(self.preset_lectures)
        presets_layout.addStretch()

        main_layout.addWidget(presets_frame)

        # === FILTER CARDS IN HORIZONTAL LAYOUT ===
        cards_widget = QWidget()
        cards_layout: QHBoxLayout = QHBoxLayout(cards_widget)
        cards_layout.setSpacing(12)
        cards_layout.setContentsMargins(0, 0, 0, 0)

        # --- Card 1: Course Info ---
        card1 = self._create_filter_card("📋 Course", "#2196F3")
        card1_layout = cast(QVBoxLayout, card1.layout())
        if card1_layout is None:
            raise RuntimeError("Course filter card layout could not be initialized")

        # Faculty
        self.faculty_combo = QComboBox()
        self.faculty_combo.addItem(ALL_FACULTIES)
        self.faculty_combo.setMinimumWidth(120)
        card1_layout.addWidget(QLabel("Faculty:"))
        card1_layout.addWidget(self.faculty_combo)

        # Prefix
        self.prefix_combo = QComboBox()
        self.prefix_combo.addItem(ALL_PREFIXES)
        self.prefix_combo.setEditable(True)
        card1_layout.addWidget(QLabel("Prefix:"))
        card1_layout.addWidget(self.prefix_combo)

        # Teacher
        self.teacher_combo = QComboBox()
        self.teacher_combo.addItem(ALL_TEACHERS)
        self.teacher_combo.setEditable(True)
        card1_layout.addWidget(QLabel("Teacher:"))
        card1_layout.addWidget(self.teacher_combo)

        # ECTS - using SpinBox instead of Slider
        ects_widget = QWidget()
        ects_layout = QHBoxLayout(ects_widget)
        ects_layout.setContentsMargins(0, 0, 0, 0)
        self.ects_min_slider = QSpinBox()
        self.ects_min_slider.setRange(0, 12)
        self.ects_min_slider.setValue(0)
        self.ects_min_slider.setPrefix("Min: ")
        self.ects_max_slider = QSpinBox()
        self.ects_max_slider.setRange(0, 12)
        self.ects_max_slider.setValue(12)
        self.ects_max_slider.setPrefix("Max: ")
        self.ects_min_label = QLabel("0")  # For compatibility
        self.ects_max_label = QLabel("12")
        ects_layout.addWidget(self.ects_min_slider)
        ects_layout.addWidget(self.ects_max_slider)
        card1_layout.addWidget(QLabel("ECTS:"))
        card1_layout.addWidget(ects_widget)

        # Main Code filter (compact design)
        main_code_header = QLabel("Main Code:")
        main_code_header.setStyleSheet("margin-top: 5px;")
        card1_layout.addWidget(main_code_header)

        # Mode + Custom input in one row
        mode_custom_widget = QWidget()
        mode_custom_layout = QHBoxLayout(mode_custom_widget)
        mode_custom_layout.setContentsMargins(0, 0, 0, 0)
        mode_custom_layout.setSpacing(4)

        self.main_code_mode = QComboBox()
        self.main_code_mode.addItems(["⊃", "⊂"])  # Starts/Contains symbols
        self.main_code_mode.setToolTip("⊃ = Starts with\n⊂ = Contains")
        self.main_code_mode.setCurrentIndex(0)
        self.main_code_mode.setMaximumWidth(40)
        self.main_code_mode.currentTextChanged.connect(self._emit_main_code_filter_changed)
        mode_custom_layout.addWidget(self.main_code_mode)

        self.main_code_custom = QLineEdit()
        self.main_code_custom.setPlaceholderText("e.g., ARCH, SOFT, MATH")
        self.main_code_custom.textChanged.connect(self._emit_main_code_filter_changed)
        mode_custom_layout.addWidget(self.main_code_custom)

        card1_layout.addWidget(mode_custom_widget)

        # Compact multi-select list
        self.main_code_list = QListWidget()
        self.main_code_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.main_code_list.setMaximumHeight(60)
        self.main_code_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 9px;
                background-color: #fafafa;
            }
            QListWidget::item {
                padding: 2px 4px;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        self.main_code_list.itemSelectionChanged.connect(self._emit_main_code_filter_changed)
        card1_layout.addWidget(self.main_code_list)

        card1_layout.addStretch()
        cards_layout.addWidget(card1)

        # --- Card 2: Schedule ---
        card2 = self._create_filter_card("📅 Schedule", "#4CAF50")
        card2_layout = cast(QVBoxLayout, card2.layout())
        if card2_layout is None:
            raise RuntimeError("Schedule filter card layout could not be initialized")

        # Days
        card2_layout.addWidget(QLabel("Days:"))
        days_widget = QWidget()
        days_layout = QGridLayout(days_widget)
        days_layout.setSpacing(3)
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
        for i, cb in enumerate(self.day_checkboxes):
            cb.setChecked(True)
            days_layout.addWidget(cb, i // 4, i % 4)
        card2_layout.addWidget(days_widget)

        # Time
        card2_layout.addWidget(QLabel("Time:"))
        self.time_morning = QCheckBox("🌅 Morning")
        self.time_afternoon = QCheckBox("☀️ Afternoon")
        self.time_evening = QCheckBox("🌙 Evening")
        for cb in [self.time_morning, self.time_afternoon, self.time_evening]:
            cb.setChecked(True)
            card2_layout.addWidget(cb)

        card2_layout.addStretch()
        cards_layout.addWidget(card2)

        # --- Card 3: Type ---
        card3 = self._create_filter_card("🎯 Type", "#FF9800")
        card3_layout = cast(QVBoxLayout, card3.layout())
        if card3_layout is None:
            raise RuntimeError("Type filter card layout could not be initialized")

        # Course type
        self.type_lecture = QCheckBox("📖 Lecture")
        self.type_lab = QCheckBox("🔬 Lab")
        self.type_ps = QCheckBox("✏️ PS")
        for cb in [self.type_lecture, self.type_lab, self.type_ps]:
            cb.setChecked(True)
            card3_layout.addWidget(cb)

        # Level
        card3_layout.addWidget(QLabel("Level:"))
        level_widget = QWidget()
        level_layout = QHBoxLayout(level_widget)
        level_layout.setContentsMargins(0, 0, 0, 0)
        level_layout.setSpacing(2)
        self.level_1xxx = QCheckBox("1")
        self.level_2xxx = QCheckBox("2")
        self.level_3xxx = QCheckBox("3")
        self.level_4xxx = QCheckBox("4")
        for cb in [self.level_1xxx, self.level_2xxx, self.level_3xxx, self.level_4xxx]:
            cb.setChecked(True)
            level_layout.addWidget(cb)
        card3_layout.addWidget(level_widget)

        # Delivery mode
        card3_layout.addWidget(QLabel("Mode:"))
        self.live_yes = QCheckBox("🌐 Online")
        self.live_no = QCheckBox("🏫 Physical")
        self.live_both = QCheckBox("Both")
        self.live_both.setChecked(True)
        card3_layout.addWidget(self.live_both)
        card3_layout.addWidget(self.live_yes)
        card3_layout.addWidget(self.live_no)

        card3_layout.addStretch()
        cards_layout.addWidget(card3)

        # --- Card 4: Special ---
        card4 = self._create_filter_card("⚡ Special", "#9C27B0")
        card4_layout = cast(QVBoxLayout, card4.layout())
        if card4_layout is None:
            raise RuntimeError("Special filter card layout could not be initialized")

        # Campus
        self.campus_all = QCheckBox("All Campus")
        self.campus_sile = QCheckBox("🏝️ Şile")
        self.campus_online = QCheckBox("💻 Online")
        self.campus_all.setChecked(True)
        card4_layout.addWidget(self.campus_all)
        card4_layout.addWidget(self.campus_sile)
        card4_layout.addWidget(self.campus_online)

        # Special options
        self.hide_conflicts = QCheckBox("⚠️ Hide Conflicts")
        self.show_favorites_only = QCheckBox("⭐ Favorites Only")
        card4_layout.addWidget(self.hide_conflicts)
        card4_layout.addWidget(self.show_favorites_only)

        card4_layout.addStretch()
        cards_layout.addWidget(card4)

        main_layout.addWidget(cards_widget)

        # === ACTION BUTTONS ===
        button_layout: QHBoxLayout = QHBoxLayout()
        button_layout.addStretch()

        self.clear_filters_btn = QPushButton("🔄 Clear All Filters")
        self.clear_filters_btn.clicked.connect(self._clear_all_filters)
        self.clear_filters_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #d32f2f; }
        """)

        self.apply_filters_btn = QPushButton("✅ Apply Filters")
        self.apply_filters_btn.clicked.connect(self._apply_filters)
        self.apply_filters_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #388E3C; }
        """)

        button_layout.addWidget(self.clear_filters_btn)
        button_layout.addWidget(self.apply_filters_btn)
        main_layout.addLayout(button_layout)

        return group

    def _create_filter_card(self, title: str, color: str) -> QFrame:
        """Create a styled filter card."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 8px;
            }}
            QLabel {{
                color: #555;
                font-size: 11px;
                font-weight: bold;
            }}
            QCheckBox {{
                font-size: 11px;
            }}
            QComboBox, QSpinBox {{
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 3px;
                font-size: 11px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(6)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header
        header = QLabel(title)
        header.setStyleSheet(f"""
            font-weight: bold;
            font-size: 12px;
            color: {color};
            padding: 4px;
            background-color: {color}20;
            border-radius: 4px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        return card

    def _apply_preset(self, preset_name: str) -> None:
        """Apply a quick filter preset."""
        # Reset filters first
        self._clear_all_filters()

        if preset_name == "morning":
            self.time_morning.setChecked(True)
            self.time_afternoon.setChecked(False)
            self.time_evening.setChecked(False)
        elif preset_name == "no_weekend":
            self.day_saturday.setChecked(False)
            self.day_sunday.setChecked(False)
        elif preset_name == "high_ects":
            self.ects_min_slider.setValue(5)
        elif preset_name == "lectures":
            self.type_lecture.setChecked(True)
            self.type_lab.setChecked(False)
            self.type_ps.setChecked(False)

        self._apply_filters()

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
        self.info_label.setStyleSheet(INFO_LABEL_STYLE)

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
        faculties = sorted({c.faculty for c in courses if c.faculty})
        self.faculty_combo.clear()
        self.faculty_combo.addItem(ALL_FACULTIES)
        self.faculty_combo.addItems(faculties)

        # Populate prefix dropdown
        import re
        prefixes = {parts[0] for c in courses if c.code for parts in [re.split(r'[.-]', c.code)] if parts and parts[0]}
        prefixes = sorted(prefixes)
        self.prefix_combo.clear()
        self.prefix_combo.addItem(ALL_PREFIXES)
        self.prefix_combo.addItems(prefixes)

        # Populate teacher dropdown
        teachers = sorted({c.teacher for c in courses if c.teacher})
        self.teacher_combo.clear()
        self.teacher_combo.addItem(ALL_TEACHERS)
        self.teacher_combo.addItems(teachers)

        # Populate main code list
        import re
        main_codes = set()
        for c in courses:
            prefix = self._extract_prefix(c.main_code or c.code)
            if prefix:
                main_codes.add(prefix.upper())

        self.main_code_list.clear()
        for code in sorted(main_codes):
            self.main_code_list.addItem(code)

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

    def _extract_prefix(self, code: str) -> str:
        """Extract alphabetic prefix from course code.

        Args:
            code: Course code (e.g., 'ARCH1112', 'soft-101')

        Returns:
            Uppercase prefix string (e.g., 'ARCH', 'SOFT') or empty string
        """
        if not code:
            return ""
        import re
        match = re.match(r'^[A-Za-z]+', code)
        return match.group(0).upper() if match else ""

    def _match_prefix(self, course: Course, tokens: Set[str], mode: str) -> bool:
        """Check if course matches main code filter tokens.

        Args:
            course: Course to check
            tokens: Set of lowercase filter tokens
            mode: "⊃" (starts with) or "⊂" (contains)

        Returns:
            True if course matches any token
        """
        course_prefix = self._extract_prefix(course.main_code or course.code).lower()
        course_code_lower = (course.code or "").lower()

        if not course_prefix and not course_code_lower:
            return False

        if mode == "⊃":  # Starts with
            # Match if token equals prefix or prefix starts with token
            return any(token == course_prefix or course_prefix.startswith(token) for token in tokens)
        else:  # ⊂ Contains
            # Match if token is in prefix or in full code
            return any(token in course_prefix or token in course_code_lower for token in tokens)

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
            if faculty_selected != ALL_FACULTIES:
                if course.faculty != faculty_selected:
                    continue

            # Prefix filter
            prefix_selected = self.prefix_combo.currentText()
            if prefix_selected != ALL_PREFIXES:
                import re
                course_prefix = re.split(r'[.-]', course.code)[0] if course.code else ""
                if course_prefix != prefix_selected:
                    continue

            # Teacher filter
            teacher_selected = self.teacher_combo.currentText()
            if teacher_selected != ALL_TEACHERS:
                if course.teacher != teacher_selected:
                    continue

            # Main Code filter
            selected_items = self.main_code_list.selectedItems()
            custom_text = self.main_code_custom.text().strip()

            if selected_items or custom_text:
                # Build token set from selections and custom input
                filter_tokens = set()

                # Add selected prefixes
                for item in selected_items:
                    token = item.text().strip().lower()
                    if token:
                        filter_tokens.add(token)

                # Add custom entries (comma-separated)
                if custom_text:
                    for token in custom_text.split(','):
                        token = token.strip().lower()
                        if token:
                            filter_tokens.add(token)

                # Apply filter if we have tokens
                if filter_tokens:
                    match_mode = self.main_code_mode.currentText()
                    if not self._match_prefix(course, filter_tokens, match_mode):
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
                course_days = {day for day, _ in course.schedule}
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

        # Clear main code filter
        self.main_code_list.clearSelection()
        self.main_code_custom.clear()
        self.main_code_mode.setCurrentIndex(0)

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
            self.info_label.setStyleSheet(INFO_LABEL_STYLE)
        else:
            self.info_label.setText("No courses loaded")
            self.info_label.setStyleSheet(INFO_LABEL_STYLE)

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

    def _clear_main_code_filter(self) -> None:
        """Clear main code filter selections."""
        self.main_code_list.clearSelection()
        self.main_code_custom.clear()
        self._apply_filters()
        self._emit_main_code_filter_changed()

    def set_main_code_filter(self, prefixes: List[str], custom_text: str, mode: str) -> None:
        """Set main code filter from external source (e.g., Kanban).

        Args:
            prefixes: List of main code prefixes to select
            custom_text: Custom comma-separated text
            mode: "Starts with" or "Contains"
        """
        # Clear current selection
        self.main_code_list.clearSelection()

        # Select matching items
        for i in range(self.main_code_list.count()):
            item = self.main_code_list.item(i)
            if item and item.text().upper() in [p.upper() for p in prefixes]:
                item.setSelected(True)

        # Set custom text
        self.main_code_custom.setText(custom_text)

        # Set mode
        if "start" in mode.lower():
            mode_index = 0  # ⊃
        else:
            mode_index = 1  # ⊂
        self.main_code_mode.setCurrentIndex(mode_index)

        # Apply filters
        self._apply_filters()

    def _emit_main_code_filter_changed(self) -> None:
        """Emit signal when main code filter changes."""
        selected_prefixes = [item.text() for item in self.main_code_list.selectedItems()]
        custom_text = self.main_code_custom.text().strip()
        mode = self.main_code_mode.currentText()
        self.main_code_filter_changed.emit(selected_prefixes, custom_text, mode)

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
        selected_rows = sorted({item.row() for item in self.course_table.selectedItems()}, reverse=True)

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

    def keyPressEvent(self, a0: Optional[QKeyEvent]) -> None:
        """Handle keyboard shortcuts."""
        from PyQt6.QtCore import Qt

        if a0 is None:
            super().keyPressEvent(a0)
            return

        if a0.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if a0.key() == Qt.Key.Key_F:
                # Ctrl+F: Focus search box
                self.search_edit.setFocus()
                self.search_edit.selectAll()
                a0.accept()
                return
            elif a0.key() == Qt.Key.Key_A:
                # Ctrl+A: Select all
                self.course_table.selectAll()
                a0.accept()
                return
            elif a0.key() == Qt.Key.Key_E:
                # Ctrl+E: Export CSV
                self._export_to_csv()
                a0.accept()
                return
        elif a0.key() == Qt.Key.Key_Delete:
            # Delete: Delete selected
            self._delete_selected_courses()
            a0.accept()
            return
        elif a0.key() == Qt.Key.Key_F5:
            # F5: Refresh
            self._apply_filters()
            a0.accept()
            return
        elif a0.key() == Qt.Key.Key_Escape:
            # Escape: Deselect all
            self.course_table.clearSelection()
            a0.accept()
            return

        # Call parent implementation for other keys
        super().keyPressEvent(a0)


__all__ = ["CourseBrowserTab"]
