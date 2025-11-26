"""File and algorithm settings tab."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from config.settings import ISIK_BLUE_PRIMARY
from gui.widgets import AlgorithmSelector


class FileSettingsTab(QWidget):
    """Tab for file input and algorithm configuration."""

    file_selected = pyqtSignal(str)  # File path
    algorithm_configured = pyqtSignal(str, dict)  # Algorithm name, parameters

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._current_file: Optional[Path] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Apply Işık University theme
        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {ISIK_BLUE_PRIMARY};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                color: {ISIK_BLUE_PRIMARY};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QPushButton {{
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {ISIK_BLUE_PRIMARY};
                color: white;
            }}
        """)

        # File input section
        file_group = self._create_file_section()
        layout.addWidget(file_group)

        # Algorithm selection section
        algo_group = self._create_algorithm_section()
        layout.addWidget(algo_group)

        layout.addStretch()

    def _create_file_section(self) -> QGroupBox:
        """Create file input section."""
        group = QGroupBox("📁 Course Data File")
        layout = QVBoxLayout(group)

        # File path display
        file_layout = QHBoxLayout()
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("No file selected...")
        self.file_path_edit.setReadOnly(True)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._on_browse_file)

        file_layout.addWidget(QLabel("Excel File:"))
        file_layout.addWidget(self.file_path_edit, stretch=1)
        file_layout.addWidget(self.browse_button)

        # File info
        self.file_info_label = QLabel("No file loaded")
        self.file_info_label.setStyleSheet("color: #757575; font-style: italic;")

        # Quick actions
        actions_layout = QHBoxLayout()
        
        self.load_sample_button = QPushButton("📋 Load Sample Data")
        self.load_sample_button.setToolTip("Load sample Turkish courses for testing")
        self.load_sample_button.clicked.connect(self._on_load_sample)

        self.reload_button = QPushButton("🔄 Reload")
        self.reload_button.setEnabled(False)
        self.reload_button.clicked.connect(self._on_reload_file)

        actions_layout.addWidget(self.load_sample_button)
        actions_layout.addWidget(self.reload_button)
        actions_layout.addStretch()

        layout.addLayout(file_layout)
        layout.addWidget(self.file_info_label)
        layout.addLayout(actions_layout)

        return group

    def _create_algorithm_section(self) -> QGroupBox:
        """Create algorithm selection section."""
        group = QGroupBox("⚙️ Algorithm Configuration")
        layout = QVBoxLayout(group)

        # Algorithm selector widget
        self.algorithm_selector = AlgorithmSelector()
        self.algorithm_selector.algorithm_changed.connect(self._on_algorithm_changed)
        self.algorithm_selector.parameters_changed.connect(self._on_parameters_changed)

        # Wrap in scroll area for long parameter lists
        scroll = QScrollArea()
        scroll.setWidget(self.algorithm_selector)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(400)

        layout.addWidget(scroll)

        return group

    def _on_browse_file(self) -> None:
        """Handle browse button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Course Data File",
            str(Path.home()),
            "Excel Files (*.xlsx *.xls);;All Files (*.*)",
        )

        if file_path:
            self._load_file(file_path)

    def _load_file(self, file_path: str) -> None:
        """Load file and update UI."""
        self._current_file = Path(file_path)
        self.file_path_edit.setText(str(self._current_file))
        self.reload_button.setEnabled(True)
        
        # Update file info (placeholder - actual implementation will parse Excel)
        self.file_info_label.setText(
            f"📄 File: {self._current_file.name} | "
            f"Size: {self._current_file.stat().st_size // 1024} KB"
        )

        self.file_selected.emit(str(self._current_file))

    def _on_load_sample(self) -> None:
        """Load sample data file."""
        project_root = Path(__file__).resolve().parents[2]

        candidate_files = [
            project_root / "data" / "sample_isik_courses.xlsx",
            project_root / "data" / "sample_isik_courses.csv",
            project_root / "data" / "sample_courses.xlsx",
            project_root / "resources" / "sample_isik_courses.xlsx",
            project_root.parent / "SchedularV2" / "sample_turkish_courses.csv",
        ]

        for sample_path in candidate_files:
            if sample_path.exists():
                self._load_file(str(sample_path))
                return

        attempted = " | ".join(str(path.relative_to(project_root.parent)) for path in candidate_files)
        self.file_info_label.setText(f"❌ Sample file not found (looked in: {attempted})")

    def _on_reload_file(self) -> None:
        """Reload current file."""
        if self._current_file and self._current_file.exists():
            self._load_file(str(self._current_file))

    def _on_algorithm_changed(self, algorithm_name: str) -> None:
        """Handle algorithm selection change."""
        params = self.algorithm_selector.get_parameters()
        self.algorithm_configured.emit(algorithm_name, params)

    def _on_parameters_changed(self, params: dict) -> None:
        """Handle parameter changes."""
        algorithm_name = self.algorithm_selector.get_selected_algorithm()
        self.algorithm_configured.emit(algorithm_name, params)

    def get_current_file(self) -> Optional[Path]:
        """Get currently selected file."""
        return self._current_file

    def get_algorithm_config(self) -> tuple[str, dict]:
        """Get current algorithm configuration."""
        algorithm = self.algorithm_selector.get_selected_algorithm()
        params = self.algorithm_selector.get_parameters()
        return algorithm, params

    def update_file_status(self, message: str) -> None:
        """Update the informational label under the file picker."""
        self.file_info_label.setText(message)


__all__ = ["FileSettingsTab"]
