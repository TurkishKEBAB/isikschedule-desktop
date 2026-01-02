"""Algorithm configuration tab with performance hints and auto-tune."""

from __future__ import annotations

from typing import Any, Dict, Optional

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QFrame,
    QCheckBox,
    QProgressBar,
    QMessageBox,
    QScrollArea,
)

try:
    from config.settings import ISIK_BLUE_PRIMARY
except ImportError:
    ISIK_BLUE_PRIMARY = "#0018A8"

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
    "a*": {
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
    "simulatedannealing": {
        "speed": "🔄 Variable",
        "quality": "⭐⭐⭐⭐",
        "description": "Yerel minimumlardan kaçınabilir. Kaliteli sonuçlar.",
        "use_case": "Optimization problemleri",
        "color": "#f39c12"
    },
    "tabusearch": {
        "speed": "⚡ Fast",
        "quality": "⭐⭐⭐⭐",
        "description": "Daha önce denenen çözümleri hatırlar.",
        "use_case": "Tekrarlı arama önleme",
        "color": "#1abc9c"
    },
    "hillclimbing": {
        "speed": "⚡⚡ Very Fast",
        "quality": "⭐⭐⭐",
        "description": "Basit ve hızlı. Yerel optimuma takılabilir.",
        "use_case": "Hızlı sonuç gerektiğinde",
        "color": "#27ae60"
    },
    "constraintprogramming": {
        "speed": "🔄 Variable",
        "quality": "⭐⭐⭐⭐⭐",
        "description": "Kısıtlama tabanlı çözüm. Tam optimal sonuç.",
        "use_case": "Karmaşık kısıtlamalar",
        "color": "#8e44ad"
    },
    "hybridga+sa": {
        "speed": "🐢 Slow",
        "quality": "⭐⭐⭐⭐⭐",
        "description": "Genetik + SA kombinasyonu. En iyi sonuçlar.",
        "use_case": "Maksimum kalite",
        "color": "#c0392b"
    }
}


class AlgorithmTab(QWidget):
    """Tab for algorithm selection and configuration with performance hints."""

    algorithm_configured = pyqtSignal(str, dict)
    auto_tune_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._simulation_mode = False
        self._setup_ui()

    def _create_card(self, title: str = None) -> tuple[QFrame, QVBoxLayout]:
        """Create a styled card frame."""
        card = QFrame()
        card.setObjectName("algorithmCard")
        card.setStyleSheet(f"""
            QFrame#algorithmCard {{
                background-color: palette(base);
                border: 2px solid {ISIK_BLUE_PRIMARY};
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet(f"""
                font-size: 15px;
                font-weight: bold;
                color: {ISIK_BLUE_PRIMARY};
                padding-bottom: 8px;
            """)
            layout.addWidget(title_label)
        
        return card, layout

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        # Main scroll area for responsiveness
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Description
        info_label = QLabel(
            "Select a scheduling algorithm and configure its parameters to generate your optimal schedule."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: palette(text); font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # Algorithm Selector Widget
        self.algo_selector = AlgorithmSelector()
        self.algo_selector.algorithm_changed.connect(self._on_algorithm_changed)
        self.algo_selector.parameters_changed.connect(self._on_params_changed)
        layout.addWidget(self.algo_selector)

        # Performance Hints Card
        hints_card, hints_layout = self._create_card("📊 Performance Hints")
        
        self.speed_label = QLabel("Speed: Select an algorithm")
        self.speed_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 4px;")
        hints_layout.addWidget(self.speed_label)

        self.quality_label = QLabel("Quality: -")
        self.quality_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 4px;")
        hints_layout.addWidget(self.quality_label)

        self.desc_label = QLabel("Select an algorithm to see performance hints.")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color: palette(text); font-size: 13px; padding: 8px 4px;")
        hints_layout.addWidget(self.desc_label)

        self.usecase_label = QLabel("")
        self.usecase_label.setWordWrap(True)
        self.usecase_label.setStyleSheet("color: palette(text); font-size: 12px; font-style: italic; padding: 4px;")
        hints_layout.addWidget(self.usecase_label)
        
        layout.addWidget(hints_card)

        # Smart Configuration Card
        smart_card, smart_layout = self._create_card("🎯 Smart Configuration")
        
        buttons_row = QHBoxLayout()
        
        self.auto_tune_btn = QPushButton("🔧 Auto-Tune Algorithm")
        self.auto_tune_btn.setMinimumHeight(44)
        self.auto_tune_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.auto_tune_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ISIK_BLUE_PRIMARY};
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #0022CC;
            }}
            QPushButton:pressed {{
                background-color: #001080;
            }}
        """)
        self.auto_tune_btn.setToolTip("Ders sayısına göre en uygun algoritmayı seçer")
        self.auto_tune_btn.clicked.connect(self._on_auto_tune_clicked)
        buttons_row.addWidget(self.auto_tune_btn)
        
        buttons_row.addStretch()
        
        self.simulation_checkbox = QCheckBox("🧪 Simulation Mode")
        self.simulation_checkbox.setMinimumHeight(36)
        self.simulation_checkbox.setToolTip("Simülasyon modunda sonuçlar kaydedilmez.")
        self.simulation_checkbox.stateChanged.connect(self._on_simulation_mode_changed)
        buttons_row.addWidget(self.simulation_checkbox)
        
        smart_layout.addLayout(buttons_row)

        self.simulation_progress = QProgressBar()
        self.simulation_progress.setVisible(False)
        self.simulation_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
                min-height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {ISIK_BLUE_PRIMARY};
                border-radius: 4px;
            }}
        """)
        smart_layout.addWidget(self.simulation_progress)

        self.recommendation_label = QLabel("")
        self.recommendation_label.setWordWrap(True)
        self.recommendation_label.setStyleSheet("""
            color: #27ae60;
            font-size: 13px;
            padding: 10px;
            background-color: rgba(39, 174, 96, 0.1);
            border-radius: 6px;
        """)
        self.recommendation_label.setVisible(False)
        smart_layout.addWidget(self.recommendation_label)
        
        layout.addWidget(smart_card)
        
        layout.addStretch()
        
        scroll.setWidget(content_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Initialize hints
        self._update_performance_hints(self.algo_selector.get_selected_algorithm())

    def _update_performance_hints(self, algorithm: str) -> None:
        """Update performance hints for the selected algorithm."""
        algo_key = algorithm.lower().replace(" ", "").replace("-", "").replace("_", "")

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
        self._show_auto_tune_recommendation()
        self.auto_tune_requested.emit()

    def _show_auto_tune_recommendation(self, course_count: int = 6) -> None:
        """Show algorithm recommendation based on course count."""
        if course_count <= 4:
            recommended = "DFS"
            reason = "Az ders sayısı için optimal çözüm garantisi"
        elif course_count <= 6:
            recommended = "A*"
            reason = "Orta karmaşıklık için dengeli performans"
        elif course_count <= 8:
            recommended = "Genetic"
            reason = "Çok sayıda ders için evrimsel yaklaşım"
        else:
            recommended = "Greedy"
            reason = "Çok yoğun program için hızlı sonuç"

        self.recommendation_label.setText(
            f"✅ Önerilen Algoritma: {recommended}\n💡 {reason}"
        )
        self.recommendation_label.setVisible(True)

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
