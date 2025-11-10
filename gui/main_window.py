"""Main window for SchedularV3 application."""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QToolBar,
    QWidget,
)


class MainWindow(QMainWindow):
    """Main application window with 4-tab interface."""

    def __init__(self) -> None:
        super().__init__()
        self._current_theme = "light"
        self._setup_ui()
        self._create_menubar()
        self._create_toolbar()
        self._create_statusbar()
        self._apply_theme()

    def _setup_ui(self) -> None:
        """Initialize main UI structure."""
        self.setWindowTitle("SchedularV3 - Course Schedule Generator")
        self.setMinimumSize(1200, 800)

        # Create central tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(False)
        
        # Placeholder tabs (will be replaced with actual implementations)
        self.file_tab = QWidget()
        self.browser_tab = QWidget()
        self.selector_tab = QWidget()
        self.viewer_tab = QWidget()

        self.tab_widget.addTab(self.file_tab, "📁 File & Settings")
        self.tab_widget.addTab(self.browser_tab, "📚 Course Browser")
        self.tab_widget.addTab(self.selector_tab, "✅ Course Selector")
        self.tab_widget.addTab(self.viewer_tab, "📊 Schedule Viewer")

        self.setCentralWidget(self.tab_widget)

    def _create_menubar(self) -> None:
        """Create application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

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

        export_menu = file_menu.addMenu("📤 Export")
        
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
        edit_menu = menubar.addMenu("&Edit")

        preferences_action = QAction("&Preferences...", self)
        preferences_action.setShortcut("Ctrl+,")
        preferences_action.setStatusTip("Open preferences dialog")
        preferences_action.triggered.connect(self._on_preferences)
        edit_menu.addAction(preferences_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        self.theme_action = QAction("🌙 Dark Theme", self)
        self.theme_action.setCheckable(True)
        self.theme_action.setStatusTip("Toggle dark/light theme")
        self.theme_action.triggered.connect(self._on_toggle_theme)
        view_menu.addAction(self.theme_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

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
        help_menu = menubar.addMenu("&Help")

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
        self.statusBar().showMessage("Ready")

    def _apply_theme(self) -> None:
        """Apply current theme stylesheet."""
        if self._current_theme == "dark":
            self._apply_dark_theme()
        else:
            self._apply_light_theme()

    def _apply_light_theme(self) -> None:
        """Apply light theme stylesheet."""
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
        """Apply dark theme stylesheet."""
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
        self.statusBar().showMessage("Open file - To be implemented")

    def _on_save_schedule(self) -> None:
        """Handle save schedule action."""
        self.statusBar().showMessage("Save schedule - To be implemented")

    def _on_export(self, format: str) -> None:
        """Handle export action."""
        self.statusBar().showMessage(f"Export as {format} - To be implemented")

    def _on_preferences(self) -> None:
        """Handle preferences action."""
        self.statusBar().showMessage("Preferences - To be implemented")

    def _on_toggle_theme(self, checked: bool) -> None:
        """Handle theme toggle."""
        if checked:
            self._current_theme = "dark"
            self.theme_action.setText("☀️ Light Theme")
        else:
            self._current_theme = "light"
            self.theme_action.setText("🌙 Dark Theme")
        self._apply_theme()
        self.statusBar().showMessage(f"Switched to {self._current_theme} theme")

    def _on_generate_schedules(self) -> None:
        """Handle generate schedules action."""
        self.statusBar().showMessage("Generate schedules - To be implemented")

    def _on_compare_algorithms(self) -> None:
        """Handle compare algorithms action."""
        self.statusBar().showMessage("Compare algorithms - To be implemented")

    def _on_benchmark(self) -> None:
        """Handle benchmark action."""
        self.statusBar().showMessage("Benchmark - To be implemented")

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
        self.statusBar().showMessage("Documentation - To be implemented")


__all__ = ["MainWindow"]
