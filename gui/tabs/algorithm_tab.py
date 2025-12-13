"""Algorithm configuration tab with performance hints and auto-tune."""

from __future__ import annotations

from typing import Any, Dict, Optional

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QGroupBox,
    QLabel,
    QPushButton,
    QFrame,
    QCheckBox,
    QProgressBar,
    QMessageBox,
)

from config.settings import ISIK_BLUE_PRIMARY
from gui.widgets import AlgorithmSelector


# Performance hints for each algorithm
ALGORITHM_HINTS: Dict[str, Dict[str, Any]] = {
    "greedy": {
        "speed": "⚡ Very Fast",
        "quality": "⭐⭐",
        "description": "Hızlı ama optimal olmayabilir. Basit programlar için idealdir.",
        "use_case": "Az ders, basit kısıtlamalar",
        "color": "#27ae60"
    },
    "dfs": {
        "speed": "🐢 Slow",
        "quality": "⭐⭐⭐⭐⭐",
        "description": "Tüm olasılıkları tarar. Küçük problem setleri için optimal.",
        "use_case": "Optimal çözüm garantisi",
        "color": "#e74c3c"
    },
    "bfs": {
        "speed": "🐢 Slow",
        "quality": "⭐⭐⭐⭐⭐",
        "description": "En kısa çözüm yolunu bulur. Bellek yoğun olabilir.",
        "use_case": "Minimum adımda çözüm",
        "color": "#e74c3c"
    },
    "a_star": {
        "speed": "⚡ Fast",
        "quality": "⭐⭐⭐⭐",
        "description": "Akıllı arama ile hızlı ve kaliteli sonuç.",
        "use_case": "Dengeli performans",
        "color": "#3498db"
    },
    "genetic": {
        "speed": "🔄 Variable",
        "quality": "⭐⭐⭐⭐",
        "description": "Evrimsel yaklaşım. Büyük problem setleri için uygun.",
        "use_case": "Karmaşık kısıtlamalar",
        "color": "#9b59b6"
    },
    "simulated_annealing": {
        "speed": "🔄 Variable",
        "quality": "⭐⭐⭐⭐",
        "description": "Yerel minimumlardan kaçınabilir. Kaliteli sonuçlar.",
        "use_case": "Optimization problemleri",
        "color": "#f39c12"
    },
    "tabu_search": {
        "speed": "⚡ Fast",
        "quality": "⭐⭐⭐⭐",
        "description": "Daha önce denenen çözümleri hatırlar.",
        "use_case": "Tekrarlı arama önleme",
        "color": "#1abc9c"
    },
    "hill_climbing": {
        "speed": "⚡⚡ Very Fast",
        "quality": "⭐⭐⭐",
        "description": "Basit ve hızlı. Yerel optimuma takılabilir.",
        "use_case": "Hızlı sonuç gerektiğinde",
        "color": "#27ae60"
    },
    "constraint_programming": {
        "speed": "🔄 Variable",
        "quality": "⭐⭐⭐⭐⭐",
        "description": "Kısıtlama tabanlı çözüm. Tam optimal sonuç.",
        "use_case": "Karmaşık kısıtlamalar",
        "color": "#8e44ad"
    },
    "hybrid_ga_sa": {
        "speed": "🐢 Slow",
        "quality": "⭐⭐⭐⭐⭐",
        "description": "Genetik + SA kombinasyonu. En iyi sonuçlar.",
        "use_case": "Maksimum kalite",
        "color": "#c0392b"
    }
}


class AlgorithmTab(QWidget):
    """Tab for algorithm selection and configuration with performance hints."""

    algorithm_configured = pyqtSignal(str, dict)  # Algorithm name, parameters
    auto_tune_requested = pyqtSignal()  # Request auto-tune based on course count

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._simulation_mode = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
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
        """)

        # Description
        info_label = QLabel(
            "Select a scheduling algorithm and configure its parameters to generate your optimal schedule."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #555; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # Algorithm Selector Widget
        self.algo_selector = AlgorithmSelector()
        self.algo_selector.algorithm_changed.connect(self._on_algorithm_changed)
        self.algo_selector.parameters_changed.connect(self._on_params_changed)
        layout.addWidget(self.algo_selector)

        # Performance Hints Section
        layout.addWidget(self._create_performance_hints_section())

        # Auto-Tune & Simulation Section
        layout.addWidget(self._create_auto_tune_section())

        layout.addStretch()

    def _create_performance_hints_section(self) -> QGroupBox:
        """Create the performance hints panel."""
        group = QGroupBox("📊 Performance Hints")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        # Hint display area
        self.hint_frame = QFrame()
        self.hint_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        hint_layout = QVBoxLayout(self.hint_frame)

        # Speed indicator
        self.speed_label = QLabel("Speed: -")
        self.speed_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        hint_layout.addWidget(self.speed_label)

        # Quality indicator
        self.quality_label = QLabel("Quality: -")
        self.quality_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        hint_layout.addWidget(self.quality_label)

        # Description
        self.desc_label = QLabel("Select an algorithm to see performance hints.")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color: #555; font-size: 12px; margin-top: 5px;")
        hint_layout.addWidget(self.desc_label)

        # Use case
        self.usecase_label = QLabel("")
        self.usecase_label.setWordWrap(True)
        self.usecase_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        hint_layout.addWidget(self.usecase_label)

        layout.addWidget(self.hint_frame)

        # Update hints for initial selection
        self._update_performance_hints(self.algo_selector.get_selected_algorithm())

        return group

    def _create_auto_tune_section(self) -> QGroupBox:
        """Create the auto-tune and simulation mode section."""
        group = QGroupBox("🎯 Smart Configuration")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        # Auto-Tune Button
        auto_tune_layout = QHBoxLayout()

        self.auto_tune_btn = QPushButton("🔧 Auto-Tune Algorithm")
        self.auto_tune_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ISIK_BLUE_PRIMARY};
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #1a5276;
            }}
            QPushButton:pressed {{
                background-color: #154360;
            }}
        """)
        self.auto_tune_btn.setToolTip(
            "Ders sayısına ve karmaşıklığa göre en uygun algoritmayı seçer"
        )
        self.auto_tune_btn.clicked.connect(self._on_auto_tune_clicked)
        auto_tune_layout.addWidget(self.auto_tune_btn)

        auto_tune_layout.addStretch()

        # Simulation Mode Checkbox
        self.simulation_checkbox = QCheckBox("🧪 Simulation Mode")
        self.simulation_checkbox.setToolTip(
            "Simülasyon modunda algoritma çalışır ama sonuçlar kaydedilmez.\n"
            "Farklı algoritmaları karşılaştırmak için kullanın."
        )
        self.simulation_checkbox.stateChanged.connect(self._on_simulation_mode_changed)
        auto_tune_layout.addWidget(self.simulation_checkbox)

        layout.addLayout(auto_tune_layout)

        # Progress bar for simulation
        self.simulation_progress = QProgressBar()
        self.simulation_progress.setVisible(False)
        self.simulation_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {ISIK_BLUE_PRIMARY};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.simulation_progress)

        # Recommendation label
        self.recommendation_label = QLabel("")
        self.recommendation_label.setWordWrap(True)
        self.recommendation_label.setStyleSheet("""
            color: #27ae60;
            font-size: 12px;
            padding: 5px;
            background-color: #e8f8f0;
            border-radius: 4px;
        """)
        self.recommendation_label.setVisible(False)
        layout.addWidget(self.recommendation_label)

        return group

    def _update_performance_hints(self, algorithm: str) -> None:
        """Update performance hints for the selected algorithm."""
        # Normalize algorithm name
        algo_key = algorithm.lower().replace(" ", "_").replace("-", "_")

        hints = ALGORITHM_HINTS.get(algo_key, {
            "speed": "🔄 Variable",
            "quality": "⭐⭐⭐",
            "description": "Algorithm performance varies based on configuration.",
            "use_case": "General purpose",
            "color": "#7f8c8d"
        })

        self.speed_label.setText(f"Speed: {hints['speed']}")
        self.quality_label.setText(f"Quality: {hints['quality']}")
        self.desc_label.setText(hints['description'])
        self.usecase_label.setText(f"🎯 Best for: {hints['use_case']}")

        # Update hint frame border color
        self.hint_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #f8f9fa;
                border: 2px solid {hints['color']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)

    def _on_algorithm_changed(self, name: str) -> None:
        """Handle algorithm selection change."""
        self._update_performance_hints(name)
        params = self.algo_selector.get_parameters()
        self.algorithm_configured.emit(name, params)

    def _on_params_changed(self, params: Dict[str, Any]) -> None:
        """Handle parameter changes."""
        name = self.algo_selector.get_selected_algorithm()
        self.algorithm_configured.emit(name, params)

    def _on_auto_tune_clicked(self) -> None:
        """Handle auto-tune button click."""
        # Show recommendation based on typical course load
        self._show_auto_tune_recommendation()
        self.auto_tune_requested.emit()

    def _show_auto_tune_recommendation(self, course_count: int = 6) -> None:
        """Show algorithm recommendation based on course count."""
        if course_count <= 4:
            recommended = "DFS"
            reason = "Az ders sayısı için optimal çözüm garantisi"
        elif course_count <= 6:
            recommended = "A* Search"
            reason = "Orta karmaşıklık için dengeli performans"
        elif course_count <= 8:
            recommended = "Genetic Algorithm"
            reason = "Çok sayıda ders için evrimsel yaklaşım"
        else:
            recommended = "Greedy"
            reason = "Çok yoğun program için hızlı sonuç"

        self.recommendation_label.setText(
            f"✅ Önerilen Algoritma: {recommended}\n💡 {reason}"
        )
        self.recommendation_label.setVisible(True)

        # Ask user if they want to apply
        reply = QMessageBox.question(
            self,
            "Auto-Tune",
            f"Önerilen algoritma: {recommended}\n\n{reason}\n\nBu algoritmayı seçmek ister misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.algo_selector.set_algorithm(recommended)

    def _on_simulation_mode_changed(self, state: int) -> None:
        """Handle simulation mode toggle."""
        self._simulation_mode = state == Qt.CheckState.Checked.value
        if self._simulation_mode:
            self.simulation_progress.setVisible(True)
            self.simulation_progress.setValue(0)
        else:
            self.simulation_progress.setVisible(False)

    def is_simulation_mode(self) -> bool:
        """Check if simulation mode is enabled."""
        return self._simulation_mode

    def update_simulation_progress(self, value: int) -> None:
        """Update simulation progress bar."""
        self.simulation_progress.setValue(value)

    def auto_tune_for_courses(self, course_count: int) -> None:
        """Auto-tune algorithm based on course count."""
        self._show_auto_tune_recommendation(course_count)

    def get_algorithm_config(self) -> tuple[str, Dict[str, Any]]:
        """Get current algorithm configuration."""
        return (
            self.algo_selector.get_selected_algorithm(),
            self.algo_selector.get_parameters()
        )
