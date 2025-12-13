"""Main window for SchedularV3 application."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, cast

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QToolBar,
    QMenu,
    QMenuBar,
    QStatusBar,
    QWidget,
)

from algorithms import get_registered_scheduler
from core.excel_loader import process_excel
from core.models import Course, CourseGroup, build_course_groups
from utils.schedule_metrics import SchedulerPrefs


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window with 4-tab interface."""

    def __init__(self) -> None:
        super().__init__()
        self._current_theme = "light"
        self._courses: List[Course] = []
        self._course_groups: Dict[str, CourseGroup] = {}
        self._mandatory_codes: Set[str] = set()
        self._optional_codes: Set[str] = set()
        self._selected_algorithm: str = ""
        self._algorithm_params: Dict[str, Any] = {}
        self._scheduler_prefs = SchedulerPrefs()
        self._loaded_file: Optional[Path] = None
        self._setup_ui()
        self._create_menubar()
        self._create_toolbar()
        self._create_statusbar()
        self._apply_theme()
        self._wire_tab_signals()

        initial_algorithm, initial_params = self.algo_tab.get_algorithm_config()
        self._selected_algorithm = initial_algorithm
        self._algorithm_params = initial_params

    def _setup_ui(self) -> None:
        """Initialize main UI structure."""
        self.setWindowTitle("SchedularV3 - Course Schedule Generator")
        self.setMinimumSize(1200, 800)
        self.setObjectName("main_window")

        # Create central tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(False)
        self.tab_widget.setObjectName("tab_widget")

        # Import and create actual tabs
        from gui.tabs.data_profile_tab import DataProfileTab
        from gui.tabs.algorithm_tab import AlgorithmTab
        from gui.tabs.course_browser_tab import CourseBrowserTab
        from gui.tabs.course_selector_tab import CourseSelectorTab
        from gui.tabs.schedule_viewer_tab import ScheduleViewerTab
        from gui.tabs.academic_tab import AcademicTab

        self.data_tab = DataProfileTab()
        self.data_tab.setObjectName("data_tab")
        self.algo_tab = AlgorithmTab()
        self.algo_tab.setObjectName("algo_tab")
        self.browser_tab = CourseBrowserTab()
        self.browser_tab.setObjectName("browser_tab")
        self.selector_tab = CourseSelectorTab()
        self.selector_tab.setObjectName("selector_tab")
        self.viewer_tab = ScheduleViewerTab()
        self.viewer_tab.setObjectName("viewer_tab")
        self.academic_tab = AcademicTab()
        self.academic_tab.setObjectName("academic_tab")

        self.tab_widget.addTab(self.data_tab, "📁 Data & Profile")
        self.tab_widget.addTab(self.algo_tab, "⚙️ Algorithms")
        self.tab_widget.addTab(self.browser_tab, "📚 Course Browser")
        self.tab_widget.addTab(self.selector_tab, "✅ Course Selector")
        self.tab_widget.addTab(self.viewer_tab, "📊 Schedule Viewer")
        self.tab_widget.addTab(self.academic_tab, "🎓 Academic")

        self.setCentralWidget(self.tab_widget)

    def _wire_tab_signals(self) -> None:
        """Connect cross-tab signals for data sharing."""
        self.data_tab.file_selected.connect(self._on_course_file_selected)
        self.data_tab.program_selected.connect(self._on_program_selected)
        self.algo_tab.algorithm_configured.connect(self._on_algorithm_configured)
        self.browser_tab.course_selected.connect(self._on_course_selected)
        self.browser_tab.courses_updated.connect(self._on_courses_updated)
        self.selector_tab.selection_changed.connect(self._on_selection_changed)

        # Wire main code filter sync between browser and selector tabs
        self.browser_tab.main_code_filter_changed.connect(self.selector_tab.on_main_code_filter_changed)
        self.selector_tab.request_main_code_filter.connect(self.browser_tab.set_main_code_filter)

    def _status_bar(self) -> QStatusBar:
        """Return the main window status bar with proper typing."""
        return cast(QStatusBar, self.statusBar())

    def _create_menubar(self) -> None:
        """Create application menu bar."""
        menubar = cast(QMenuBar, self.menuBar())

        # File menu
        file_menu = cast(QMenu, menubar.addMenu("&File"))

        open_action = QAction("&Open Excel...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open course data from Excel file")
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)

        save_action = QAction("&Save Schedule...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Save current schedule")
        save_action.triggered.connect(self._on_save_schedule)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        export_menu = cast(QMenu, file_menu.addMenu("📤 Export"))

        export_pdf = QAction("Export as PDF...", self)
        export_pdf.triggered.connect(lambda: self._on_export("pdf"))
        export_menu.addAction(export_pdf)

        export_jpeg = QAction("Export as JPEG...", self)
        export_jpeg.triggered.connect(lambda: self._on_export("jpeg"))
        export_menu.addAction(export_jpeg)

        export_excel = QAction("Export as Excel...", self)
        export_excel.triggered.connect(lambda: self._on_export("excel"))
        export_menu.addAction(export_excel)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = cast(QMenu, menubar.addMenu("&Edit"))

        preferences_action = QAction("&Preferences...", self)
        preferences_action.setShortcut("Ctrl+,")
        preferences_action.setStatusTip("Open preferences dialog")
        preferences_action.triggered.connect(self._on_preferences)
        edit_menu.addAction(preferences_action)

        # View menu
        view_menu = cast(QMenu, menubar.addMenu("&View"))

        self.theme_action = QAction("🌙 Dark Theme", self)
        self.theme_action.setCheckable(True)
        self.theme_action.setStatusTip("Toggle dark/light theme")
        self.theme_action.triggered.connect(self._on_toggle_theme)
        view_menu.addAction(self.theme_action)

        # Tools menu
        tools_menu = cast(QMenu, menubar.addMenu("&Tools"))

        generate_action = QAction("⚡ Generate Schedules", self)
        generate_action.setShortcut("F5")
        generate_action.setStatusTip("Run algorithm to generate schedules")
        generate_action.triggered.connect(self._on_generate_schedules)
        tools_menu.addAction(generate_action)

        compare_action = QAction("📊 Compare Algorithms", self)
        compare_action.setStatusTip("Run multiple algorithms and compare results")
        compare_action.triggered.connect(self._on_compare_algorithms)
        tools_menu.addAction(compare_action)

        tools_menu.addSeparator()

        benchmark_action = QAction("🔬 Benchmark Algorithms", self)
        benchmark_action.setStatusTip("Run performance benchmarks")
        benchmark_action.triggered.connect(self._on_benchmark)
        tools_menu.addAction(benchmark_action)

        # Help menu
        help_menu = cast(QMenu, menubar.addMenu("&Help"))

        about_action = QAction("&About", self)
        about_action.setStatusTip("About SchedularV3")
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

        docs_action = QAction("📖 Documentation", self)
        docs_action.setStatusTip("Open documentation")
        docs_action.triggered.connect(self._on_documentation)
        help_menu.addAction(docs_action)

    def _create_toolbar(self) -> None:
        """Create main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)

        # Open file
        open_action = QAction("📂 Open", self)
        open_action.setStatusTip("Open Excel file")
        open_action.triggered.connect(self._on_open_file)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        # Quick Schedule (Lucky button)
        lucky_action = QAction("🍀 Şansımı Dene", self)
        lucky_action.setStatusTip("Tek tuşla optimal program oluştur")
        lucky_action.triggered.connect(self._on_quick_schedule)
        toolbar.addAction(lucky_action)

        # Generate
        generate_action = QAction("⚡ Generate", self)
        generate_action.setStatusTip("Generate schedules")
        generate_action.triggered.connect(self._on_generate_schedules)
        toolbar.addAction(generate_action)

        # Compare
        compare_action = QAction("📊 Compare", self)
        compare_action.setStatusTip("Compare algorithms")
        compare_action.triggered.connect(self._on_compare_algorithms)
        toolbar.addAction(compare_action)

        toolbar.addSeparator()

        # Export
        export_action = QAction("💾 Export", self)
        export_action.setStatusTip("Export schedule")
        export_action.triggered.connect(lambda: self._on_export("pdf"))
        toolbar.addAction(export_action)

    def _create_statusbar(self) -> None:
        """Create status bar."""
        self._status_bar().showMessage("Ready")

    def _apply_theme(self) -> None:
        """Apply current theme stylesheet."""
        if self._current_theme == "dark":
            self._apply_dark_theme()
        else:
            self._apply_light_theme()

    def _apply_light_theme(self) -> None:
        """Apply light theme stylesheet from QSS file."""
        qss_path = Path(__file__).parent.parent / "resources" / "styles" / "light_theme.qss"
        if qss_path.exists():
            with open(qss_path, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        else:
            logger.warning(f"Light theme QSS not found: {qss_path}")
            self._apply_light_theme_fallback()

    def _apply_light_theme_fallback(self) -> None:
        """Apply light theme fallback when QSS file not found."""
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #FAFAFA;
            }
            QTabWidget::pane {
                border: 1px solid #E0E0E0;
                background-color: #FFFFFF;
            }
            QTabBar::tab {
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-bottom: none;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                border-bottom: 2px solid #2196F3;
            }
            QTabBar::tab:hover {
                background-color: #EEEEEE;
            }
            QMenuBar {
                background-color: #FAFAFA;
                color: #212121;
            }
            QMenuBar::item:selected {
                background-color: #E3F2FD;
            }
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
            }
            QMenu::item:selected {
                background-color: #E3F2FD;
            }
            QToolBar {
                background-color: #F5F5F5;
                border-bottom: 1px solid #E0E0E0;
                spacing: 10px;
                padding: 5px;
            }
            QStatusBar {
                background-color: #F5F5F5;
                border-top: 1px solid #E0E0E0;
            }
        """
        )

    def _apply_dark_theme(self) -> None:
        """Apply dark theme stylesheet from QSS file."""
        qss_path = Path(__file__).parent.parent / "resources" / "styles" / "dark_theme.qss"
        if qss_path.exists():
            with open(qss_path, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        else:
            logger.warning(f"Dark theme QSS not found: {qss_path}")
            self._apply_dark_theme_fallback()

    def _apply_dark_theme_fallback(self) -> None:
        """Apply dark theme fallback when QSS file not found."""
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #1E1E1E;
                color: #E0E0E0;
            }
            QTabWidget::pane {
                border: 1px solid #3C3C3C;
                background-color: #2D2D2D;
            }
            QTabBar::tab {
                background-color: #252525;
                border: 1px solid #3C3C3C;
                border-bottom: none;
                padding: 8px 16px;
                margin-right: 2px;
                color: #E0E0E0;
            }
            QTabBar::tab:selected {
                background-color: #2D2D2D;
                border-bottom: 2px solid #2196F3;
            }
            QTabBar::tab:hover {
                background-color: #3C3C3C;
            }
            QMenuBar {
                background-color: #1E1E1E;
                color: #E0E0E0;
            }
            QMenuBar::item:selected {
                background-color: #2D2D2D;
            }
            QMenu {
                background-color: #2D2D2D;
                border: 1px solid #3C3C3C;
                color: #E0E0E0;
            }
            QMenu::item:selected {
                background-color: #3C3C3C;
            }
            QToolBar {
                background-color: #252525;
                border-bottom: 1px solid #3C3C3C;
                spacing: 10px;
                padding: 5px;
            }
            QStatusBar {
                background-color: #252525;
                border-top: 1px solid #3C3C3C;
                color: #E0E0E0;
            }
        """
        )

    # Event handlers (to be implemented)
    def _on_open_file(self) -> None:
        """Handle open file action."""
        self.data_tab.browse_button.click()

    def _on_save_schedule(self) -> None:
        """Handle save schedule action."""
        self._status_bar().showMessage("Save schedule - To be implemented")

    def _on_export(self, format: str) -> None:
        """Handle export action."""
        self._status_bar().showMessage(f"Export as {format} - To be implemented")

    def _on_preferences(self) -> None:
        """Handle preferences action."""
        self._status_bar().showMessage("Preferences - To be implemented")

    def _on_toggle_theme(self, checked: bool) -> None:
        """Handle theme toggle."""
        if checked:
            self._current_theme = "dark"
            self.theme_action.setText("☀️ Light Theme")
        else:
            self._current_theme = "light"
            self.theme_action.setText("🌙 Dark Theme")
        self._apply_theme()
        self._status_bar().showMessage(f"Switched to {self._current_theme} theme")

    def _on_generate_schedules(self) -> None:
        """Handle generate schedules action."""
        if not self._course_groups:
            QMessageBox.warning(
                self,
                "No Course Data",
                "Please load an Excel course data file before generating schedules.",
            )
            return

        mandatory_codes, optional_codes = self.selector_tab.get_selected_courses()
        if not mandatory_codes:
            QMessageBox.warning(
                self,
                "No Mandatory Courses",
                "Select at least one course as mandatory in the Course Selector tab.",
            )
            self.tab_widget.setCurrentWidget(self.selector_tab)
            return

        scheduler_cls = get_registered_scheduler(self._selected_algorithm)
        if scheduler_cls is None:
            QMessageBox.critical(
                self,
                "Algorithm Error",
                f"Algorithm '{self._selected_algorithm}' is not registered.",
            )
            return

        params = dict(self._algorithm_params)
        max_ects = int(params.pop("max_ects", 31))
        allow_conflicts = bool(params.pop("allow_conflicts", False))

        # Remove UI-only parameters that schedulers don't expect
        params.pop("lifestyle_mode", None)
        params.pop("morning_person", None)
        params.pop("free_day_preference", None)

        try:
            scheduler = scheduler_cls(
                max_ects=max_ects,
                allow_conflicts=allow_conflicts,
                scheduler_prefs=self._scheduler_prefs,
                **params,
            )
        except Exception as exc:  # pragma: no cover - defensive guard
            logger.exception("Failed to instantiate scheduler %s", self._selected_algorithm)
            self._show_error("Algorithm Error", str(exc))
            return

        try:
            schedules = scheduler.generate_schedules(
                self._course_groups,
                mandatory_codes,
                optional_codes,
            )
        except Exception as exc:  # pragma: no cover - defensive guard
            logger.exception("Scheduler execution failed")
            self._show_error("Generation Failed", str(exc))
            return

        stats = scheduler.get_search_statistics()

        if not schedules:
            # Provide more helpful message based on the failure
            failure_reasons = scheduler.analyze_failure(self._course_groups)
            message = "No valid schedules found.\n\n"

            # Add specific reasons if available
            if failure_reasons:
                message += "Possible reasons:\n" + "\n".join(f"• {reason}" for reason in failure_reasons)
                message += "\n\nConsider:\n"
                message += "• Relaxing ECTS constraints\n"
                message += "• Removing some mandatory courses\n"
                message += "• Allowing time conflicts\n"
                message += "• Checking if selected courses have valid sections"
            else:
                message += "Consider relaxing constraints or selections."

            self._status_bar().showMessage("No valid schedules found")
            QMessageBox.warning(self, "No Schedules Found", message)
            return

        self.viewer_tab.set_schedules(schedules, algorithm=self._selected_algorithm, max_ects=max_ects)
        self.tab_widget.setCurrentWidget(self.viewer_tab)

        total_time = stats.get("total_time") if isinstance(stats, dict) else None
        if isinstance(total_time, (int, float)):
            status = (
                f"{self._selected_algorithm}: generated {len(schedules)} schedules in {total_time:.2f}s"
            )
        else:
            status = f"{self._selected_algorithm}: generated {len(schedules)} schedules"
        self._status_bar().showMessage(status)

    def _on_quick_schedule(self) -> None:
        """Handle quick schedule (Lucky) action - generates optimal schedule with one click."""
        if not self._course_groups:
            QMessageBox.warning(
                self,
                "Ders Verisi Yok",
                "Lütfen önce bir Excel dosyası yükleyiniz.",
            )
            return

        mandatory_codes, optional_codes = self.selector_tab.get_selected_courses()
        if not mandatory_codes:
            QMessageBox.warning(
                self,
                "Ders Seçimi Yok",
                "Lütfen en az bir dersi zorunlu olarak işaretleyiniz.\n\n"
                "İpucu: Ders Seçici sekmesine gidin ve almak istediğiniz dersleri tıklayın.",
            )
            self.tab_widget.setCurrentWidget(self.selector_tab)
            return

        # Use smart configuration based on balanced lifestyle
        from utils.smart_advisor import create_quick_schedule_config

        config = create_quick_schedule_config(
            lifestyle_mode="balanced",
            morning_person=False,
            prefer_gaps=False,
            free_day_preference="Friday",  # Typical preference: Friday off
        )

        algorithm_name = config["algorithm"]
        scheduler_cls = get_registered_scheduler(algorithm_name)

        if scheduler_cls is None:
            # Fallback to DFS
            scheduler_cls = get_registered_scheduler("DFS")
            algorithm_name = "DFS"

        if scheduler_cls is None:
            QMessageBox.critical(self, "Hata", "Planlayıcı algoritması bulunamadı (DFS dahil).")
            self._status_bar().showMessage("❌ Hata: Algoritma bulunamadı.")
            return

        self._status_bar().showMessage("🍀 Şansını deniyorum... Program oluşturuluyor...")

        try:
            scheduler = scheduler_cls(
                max_ects=config["max_ects"],
                max_results=config["max_results"],
                allow_conflicts=False,
                scheduler_prefs=config.get("scheduler_prefs"),
                **config.get("params", {}),
            )

            schedules = scheduler.generate_schedules(
                self._course_groups,
                mandatory_codes,
                optional_codes,
            )
        except Exception as exc:
            logger.exception("Quick schedule generation failed")
            self._show_error("Hızlı Program Hatası", str(exc))
            return

        if not schedules:
            QMessageBox.information(
                self,
                "Program Bulunamadı",
                "Seçtiğin derslerle uygun bir program oluşturulamadı.\n\n"
                "Öneriler:\n"
                "• Zorunlu ders sayısını azalt\n"
                "• Normal 'Generate' butonunu farklı ayarlarla dene",
            )
            return

        self.viewer_tab.set_schedules(schedules, algorithm=f"🍀 Lucky ({algorithm_name})")
        self.tab_widget.setCurrentWidget(self.viewer_tab)
        self._status_bar().showMessage(
            f"🍀 Şanslısın! {len(schedules)} program bulundu. En iyisi seçildi."
        )

    def _on_compare_algorithms(self) -> None:
        """Handle compare algorithms action."""
        self._status_bar().showMessage("Compare algorithms - To be implemented")

    def _on_benchmark(self) -> None:
        """Handle benchmark action."""
        self._status_bar().showMessage("Benchmark - To be implemented")

    def _on_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About SchedularV3",
            "<h2>SchedularV3</h2>"
            "<p>Advanced Course Schedule Generator</p>"
            "<p>Version 3.0.0</p>"
            "<p>Featuring 15+ scheduling algorithms with intelligent optimization</p>"
            "<p><b>Algorithms:</b> DFS, BFS, IDDFS, A*, Greedy, Dijkstra, "
            "Simulated Annealing, Hill Climbing, Tabu Search, Genetic, PSO, "
            "Hybrid GA+SA, Constraint Programming</p>",
        )

    def _on_documentation(self) -> None:
        """Open documentation."""
        self._status_bar().showMessage("Documentation - To be implemented")

    def _on_course_file_selected(self, file_path: str) -> None:
        """React when the user picks a course data file."""
        self._loaded_file = Path(file_path)
        self._status_bar().showMessage(f"Loading courses from {self._loaded_file.name}...")
        self._load_courses_from_file(self._loaded_file)

    def _on_program_selected(self, program_code: str, year: int) -> None:
        """Handle program selection from DataProfileTab."""
        self._status_bar().showMessage(f"Program selected: {program_code} ({year})")

        # Notify selector tab about the program change
        if hasattr(self.selector_tab, 'kanban_widget'):
            self.selector_tab.kanban_widget.set_active_program(program_code, year)

        print(f"MainWindow: Program {program_code} ({year}) activated")

    def _on_algorithm_configured(self, algorithm_name: str, params: dict) -> None:
        """Remember the active algorithm configuration."""
        self._selected_algorithm = algorithm_name
        self._algorithm_params = params
        allow_conflicts = "Yes" if params.get("allow_conflicts") else "No"
        self._status_bar().showMessage(
            f"Configured {algorithm_name} | Allow conflicts: {allow_conflicts}"
        )

    def _on_course_selected(self, course: Course) -> None:
        """Surface quick info about the highlighted course."""
        self._status_bar().showMessage(f"Selected {course.code} - {course.name}")

    def _on_selection_changed(self, mandatory: Set[str], optional: Set[str]) -> None:
        """Track selection summary and update status bar."""
        self._mandatory_codes = set(mandatory)
        self._optional_codes = set(optional)
        self._status_bar().showMessage(
            f"Selection updated | mandatory: {len(mandatory)} | optional: {len(optional)}"
        )

    def _on_courses_updated(self, updated_courses: List[Course]) -> None:
        """Handle course deletions from Browser tab.

        When courses are deleted in the Browser tab, we need to:
        1. Update the main course list
        2. Rebuild course groups
        3. Update the Selector tab with new groups
        """
        self._courses = updated_courses
        self._course_groups = build_course_groups(updated_courses)
        self.selector_tab.set_course_groups(self._course_groups)

        self._status_bar().showMessage(
            f"Courses updated | Total: {len(updated_courses)} | Groups: {len(self._course_groups)}"
        )

    def _load_courses_from_file(self, file_path: Path) -> None:
        """Load courses from Excel and propagate them to tabs."""
        try:
            courses = process_excel(str(file_path))
        except FileNotFoundError:
            self._reset_loaded_data()
            self.data_tab.update_health_status(0, 0, 1)
            self._show_error("File Not Found", f"Could not locate {file_path}.")
            return
        except ValueError as exc:
            self._reset_loaded_data()
            self.data_tab.update_health_status(0, 0, 1)
            self._show_error("Invalid Excel Format", str(exc))
            return
        except Exception as exc:  # pragma: no cover - defensive guard
            logger.exception("Unexpected error while loading courses")
            self._reset_loaded_data()
            self.data_tab.update_health_status(0, 0, 1)
            self._show_error("Load Failed", str(exc))
            return

        if not courses:
            self._reset_loaded_data()
            self.data_tab.update_health_status(0, 0, 0)
            QMessageBox.information(
                self,
                "No Courses",
                "The selected Excel file did not contain any courses.",
            )
            return

        self._courses = courses
        self._course_groups = build_course_groups(courses)
        self.browser_tab.set_courses(courses)
        self.selector_tab.set_course_groups(self._course_groups)
        self.viewer_tab.clear()

        # Update health status (assuming all loaded courses are valid)
        self.data_tab.update_health_status(len(courses), len(courses), 0)

        self._status_bar().showMessage(
            f"Loaded {len(courses)} courses across {len(self._course_groups)} groups"
        )
        self.tab_widget.setCurrentWidget(self.browser_tab)

    def _reset_loaded_data(self) -> None:
        """Clear cached course data and refresh dependent tabs."""
        self._courses.clear()
        self._course_groups.clear()
        self._mandatory_codes.clear()
        self._optional_codes.clear()
        self.browser_tab.set_courses([])
        self.selector_tab.set_course_groups({})
        self.viewer_tab.clear()
        self.data_tab.update_health_status(0, 0, 0)

    def _show_error(self, title: str, message: str) -> None:
        """Show an error dialog and mirror the message in the status bar."""
        QMessageBox.critical(self, title, message)
        self._status_bar().showMessage(message)


__all__ = ["MainWindow"]
