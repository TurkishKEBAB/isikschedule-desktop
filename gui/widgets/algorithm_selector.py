"""Algorithm selector widget with modern flat design."""

from __future__ import annotations

from typing import Any, Dict, Optional

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QWheelEvent
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

try:
    from algorithms import iter_registered_schedulers
except ImportError:
    def iter_registered_schedulers():
        return []


class NoScrollSpinBox(QSpinBox):
    """SpinBox that ignores wheel events unless focused to prevent accidental changes."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class NoScrollDoubleSpinBox(QDoubleSpinBox):
    """DoubleSpinBox that ignores wheel events unless focused to prevent accidental changes."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()



class AlgorithmSelector(QWidget):
    """Widget for selecting and configuring scheduling algorithms."""

    algorithm_changed = pyqtSignal(str)
    parameters_changed = pyqtSignal(dict)

    # Default parameter configurations for each algorithm
    ALGORITHM_PARAMS = {
        "DFS": {
            "max_results": (1, 100, 10, "Maximum schedules to generate"),
            "timeout_seconds": (30, 600, 300, "Timeout in seconds"),
        },
        "BFS": {
            "max_results": (1, 50, 10, "Maximum schedules to generate"),
            "timeout_seconds": (30, 300, 180, "Timeout in seconds"),
        },
        "IDDFS": {
            "max_results": (1, 50, 10, "Maximum schedules to generate"),
            "depth_increment": (1, 10, 1, "Depth increment per iteration"),
            "timeout_seconds": (30, 400, 240, "Timeout in seconds"),
        },
        "A*": {
            "max_results": (1, 50, 10, "Maximum schedules to generate"),
            "timeout_seconds": (30, 300, 180, "Timeout in seconds"),
        },
        "Greedy": {
            "max_results": (1, 20, 5, "Maximum schedules to generate"),
            "timeout_seconds": (10, 120, 60, "Timeout in seconds"),
        },
        "Dijkstra": {
            "max_results": (1, 20, 5, "Maximum schedules to generate"),
            "timeout_seconds": (30, 300, 180, "Timeout in seconds"),
        },
        "SimulatedAnnealing": {
            "max_results": (1, 5, 1, "Maximum schedules to generate"),
            "annealing_iterations": (50, 1000, 400, "Annealing iterations"),
            "timeout_seconds": (30, 300, 180, "Timeout in seconds"),
        },
        "HillClimbing": {
            "max_results": (1, 5, 1, "Maximum schedules to generate"),
            "max_iterations": (10, 100, 30, "Maximum iterations"),
            "timeout_seconds": (30, 200, 120, "Timeout in seconds"),
        },
        "TabuSearch": {
            "max_results": (1, 5, 1, "Maximum schedules to generate"),
            "max_iterations": (10, 100, 40, "Maximum iterations"),
            "tabu_tenure": (3, 20, 7, "Tabu list tenure"),
            "timeout_seconds": (30, 300, 180, "Timeout in seconds"),
        },
        "Genetic": {
            "max_results": (1, 10, 3, "Maximum schedules to generate"),
            "population_size": (6, 100, 20, "Population size"),
            "generations": (5, 100, 30, "Number of generations"),
            "crossover_rate": (0.0, 1.0, 0.7, "Crossover rate", True),
            "mutation_rate": (0.0, 1.0, 0.2, "Mutation rate", True),
            "timeout_seconds": (30, 300, 180, "Timeout in seconds"),
        },
        "PSO": {
            "max_results": (1, 5, 1, "Maximum schedules to generate"),
            "swarm_size": (5, 50, 15, "Swarm size"),
            "iterations": (10, 100, 25, "Number of iterations"),
            "inertia": (0.0, 1.0, 0.4, "Inertia weight", True),
            "social": (0.0, 1.0, 0.4, "Social component", True),
            "cognitive": (0.0, 1.0, 0.4, "Cognitive component", True),
            "timeout_seconds": (30, 200, 120, "Timeout in seconds"),
        },
        "HybridGA+SA": {
            "max_results": (1, 10, 3, "Maximum schedules to generate"),
            "population_size": (6, 100, 20, "GA population size"),
            "generations": (5, 50, 20, "GA generations"),
            "annealing_iterations": (50, 500, 300, "SA iterations"),
            "timeout_seconds": (60, 400, 240, "Timeout in seconds"),
        },
        "ConstraintProgramming": {
            "max_results": (1, 50, 10, "Maximum schedules to generate"),
            "timeout_seconds": (60, 600, 300, "Timeout in seconds"),
        },
    }

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._current_params: Dict[str, Any] = {}
        self._param_widgets: Dict[str, QWidget] = {}
        self._setup_ui()

    def _create_section_card(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        """Create a styled card section with title."""
        card = QFrame()
        card.setObjectName("sectionCard")
        
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title label
        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        title_label.setStyleSheet("""
            QLabel#sectionTitle {
                font-size: 14px;
                font-weight: bold;
                color: #0018A8;
                padding-bottom: 8px;
                border-bottom: 2px solid #0018A8;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(title_label)
        
        return card, layout

    def _create_labeled_row(self, label_text: str, widget: QWidget) -> QWidget:
        """Create a horizontal row with label and widget."""
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 4, 0, 4)
        row_layout.setSpacing(12)
        
        label = QLabel(label_text)
        label.setMinimumWidth(120)
        label.setStyleSheet("font-weight: 500;")
        
        row_layout.addWidget(label)
        row_layout.addWidget(widget, 1)
        
        return row

    def _setup_ui(self) -> None:
        """Initialize UI components with modern flat design."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ========== 1. Algorithm Selection Card ==========
        algo_card, algo_layout = self._create_section_card("🔧 Algorithm Selection")
        
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.setMinimumHeight(36)
        self._populate_algorithms()
        self.algorithm_combo.currentTextChanged.connect(self._on_algorithm_changed)
        
        algo_layout.addWidget(self._create_labeled_row("Algorithm:", self.algorithm_combo))
        
        # Info label
        self.info_label = QLabel("Select an algorithm to see details")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #666; font-style: italic; padding: 8px 0;")
        algo_layout.addWidget(self.info_label)
        
        main_layout.addWidget(algo_card)

        # ========== 2. Lifestyle Mode Card ==========
        lifestyle_card, lifestyle_layout = self._create_section_card("🎯 Lifestyle Mode")
        
        self.lifestyle_combo = QComboBox()
        self.lifestyle_combo.setMinimumHeight(36)
        self.lifestyle_combo.addItem("⚖️ Balanced (Dengeli)", "balanced")
        self.lifestyle_combo.addItem("🌙 Minimal (Hafif Yük)", "minimal")
        self.lifestyle_combo.addItem("🔥 Intensive (Yoğun)", "intensive")
        self.lifestyle_combo.addItem("⚙️ Custom (Manuel)", "custom")
        self.lifestyle_combo.currentIndexChanged.connect(self._on_lifestyle_changed)
        
        lifestyle_layout.addWidget(self._create_labeled_row("Mode:", self.lifestyle_combo))
        
        self.morning_checkbox = QCheckBox("🌅 Morning Person (Sabah İnsanıyım)")
        self.morning_checkbox.setMinimumHeight(32)
        self.morning_checkbox.stateChanged.connect(self._emit_parameters)
        lifestyle_layout.addWidget(self.morning_checkbox)
        
        self.free_day_combo = QComboBox()
        self.free_day_combo.setMinimumHeight(36)
        self.free_day_combo.addItem("No Free Day", "")
        self.free_day_combo.addItem("Monday Free", "Monday")
        self.free_day_combo.addItem("Friday Free", "Friday")
        self.free_day_combo.addItem("Saturday Free", "Saturday")
        self.free_day_combo.currentIndexChanged.connect(self._emit_parameters)
        
        lifestyle_layout.addWidget(self._create_labeled_row("Free Day:", self.free_day_combo))
        
        main_layout.addWidget(lifestyle_card)

        # ========== 3. Parameters Card ==========
        params_card, params_inner_layout = self._create_section_card("⚙️ Algorithm Parameters")
        
        self.params_container = QWidget()
        self.params_layout = QVBoxLayout(self.params_container)
        self.params_layout.setContentsMargins(0, 0, 0, 0)
        self.params_layout.setSpacing(8)
        
        params_inner_layout.addWidget(self.params_container)
        self.params_card = params_card
        
        main_layout.addWidget(params_card)

        # ========== 4. Common Settings Card ==========
        common_card, common_layout = self._create_section_card("📊 Common Settings")
        
        self.max_ects_spin = NoScrollSpinBox()
        self.max_ects_spin.setRange(10, 50)
        self.max_ects_spin.setValue(31)
        self.max_ects_spin.setSuffix(" ECTS")
        self.max_ects_spin.setMinimumHeight(36)
        self.max_ects_spin.valueChanged.connect(self._emit_parameters)
        
        common_layout.addWidget(self._create_labeled_row("Max ECTS:", self.max_ects_spin))
        
        self.max_conflicts_spin = NoScrollSpinBox()
        self.max_conflicts_spin.setRange(0, 10)
        self.max_conflicts_spin.setValue(1)
        self.max_conflicts_spin.setSuffix(" conflict(s)")
        self.max_conflicts_spin.setMinimumHeight(36)
        self.max_conflicts_spin.setToolTip("Maximum allowed time slot conflicts (0 = no conflicts)")
        self.max_conflicts_spin.valueChanged.connect(self._emit_parameters)
        
        common_layout.addWidget(self._create_labeled_row("Max Conflicts:", self.max_conflicts_spin))
        
        main_layout.addWidget(common_card)
        
        # Add stretch at bottom
        main_layout.addStretch()

        # Initialize
        self._on_algorithm_changed(self.algorithm_combo.currentText())

    def _populate_algorithms(self) -> None:
        """Populate algorithm dropdown from registry or fallback."""
        algorithms = []
        
        try:
            for scheduler_cls in iter_registered_schedulers():
                metadata = getattr(scheduler_cls, "metadata", None)
                if metadata:
                    algorithms.append((metadata.name, metadata.description))
        except Exception:
            pass
        
        # Fallback if registry is empty
        if not algorithms:
            algorithms = [
                ("DFS", "Depth-first search with pruning"),
                ("BFS", "Breadth-first search"),
                ("A*", "A-star heuristic search"),
                ("Greedy", "Fast greedy algorithm"),
                ("Genetic", "Genetic algorithm optimization"),
                ("SimulatedAnnealing", "Simulated annealing optimization"),
                ("HillClimbing", "Hill climbing local search"),
                ("TabuSearch", "Tabu search metaheuristic"),
                ("IDDFS", "Iterative deepening DFS"),
                ("Dijkstra", "Dijkstra's algorithm"),
                ("PSO", "Particle swarm optimization"),
                ("HybridGA+SA", "Hybrid genetic + simulated annealing"),
                ("ConstraintProgramming", "Constraint programming solver"),
            ]

        algorithms.sort(key=lambda x: x[0])
        for name, _ in algorithms:
            self.algorithm_combo.addItem(name)

    def _on_algorithm_changed(self, algorithm_name: str) -> None:
        """Handle algorithm selection change."""
        # Update info
        params = self.ALGORITHM_PARAMS.get(algorithm_name, {})
        param_count = len(params)
        self.info_label.setText(f"📈 {algorithm_name} - {param_count} configurable parameters")
        
        # Rebuild parameter widgets
        self._rebuild_parameter_widgets(algorithm_name)
        
        self.algorithm_changed.emit(algorithm_name)
        self._emit_parameters()

    def _on_lifestyle_changed(self, index: int) -> None:
        """Handle lifestyle mode change."""
        mode = self.lifestyle_combo.currentData()
        
        if mode == "minimal":
            self.max_ects_spin.setValue(25)
            self.algorithm_combo.setCurrentText("Greedy")
        elif mode == "intensive":
            self.max_ects_spin.setValue(40)
            self.algorithm_combo.setCurrentText("Genetic")
        elif mode == "balanced":
            self.max_ects_spin.setValue(31)
            self.algorithm_combo.setCurrentText("DFS")
        
        # Always keep params visible
        self._emit_parameters()

    def _get_algorithm_metadata(self, name: str):
        """Get metadata for algorithm by name."""
        try:
            for scheduler_cls in iter_registered_schedulers():
                metadata = getattr(scheduler_cls, "metadata", None)
                if metadata and metadata.name == name:
                    return metadata
        except Exception:
            pass
        return None

    def _rebuild_parameter_widgets(self, algorithm_name: str) -> None:
        """Rebuild parameter input widgets for selected algorithm."""
        # Clear existing
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        self._param_widgets.clear()

        # Get parameters
        params = self.ALGORITHM_PARAMS.get(algorithm_name, {})

        if not params:
            no_params_label = QLabel("No additional parameters for this algorithm")
            no_params_label.setStyleSheet("color: #888; font-style: italic;")
            self.params_layout.addWidget(no_params_label)
            return

        for param_name, config in params.items():
            if len(config) == 4:
                min_val, max_val, default, tooltip = config
                is_float = False
            else:
                min_val, max_val, default, tooltip, is_float = config

            if is_float:
                spin = NoScrollDoubleSpinBox()
                spin.setDecimals(2)
                spin.setSingleStep(0.1)
            else:
                spin = NoScrollSpinBox()

            spin.setRange(int(min_val) if not is_float else min_val, 
                         int(max_val) if not is_float else max_val)
            spin.setValue(default)
            spin.setToolTip(tooltip)
            spin.setMinimumHeight(36)
            spin.valueChanged.connect(self._emit_parameters)

            label = param_name.replace("_", " ").title() + ":"
            self.params_layout.addWidget(self._create_labeled_row(label, spin))
            self._param_widgets[param_name] = spin

    def _emit_parameters(self) -> None:
        """Emit current parameter configuration."""
        params = {
            "max_ects": self.max_ects_spin.value(),
            "allow_conflicts": self.max_conflicts_spin.value() > 0,
            "max_conflicts": self.max_conflicts_spin.value(),
            "lifestyle_mode": self.lifestyle_combo.currentData(),
            "morning_person": self.morning_checkbox.isChecked(),
            "free_day_preference": self.free_day_combo.currentData(),
        }

        for param_name, widget in self._param_widgets.items():
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                params[param_name] = widget.value()

        self._current_params = params
        self.parameters_changed.emit(params)

    def get_selected_algorithm(self) -> str:
        """Get currently selected algorithm name."""
        return self.algorithm_combo.currentText()

    def set_algorithm(self, name: str) -> bool:
        """Set the selected algorithm by name."""
        index = self.algorithm_combo.findText(name)
        if index >= 0:
            self.algorithm_combo.setCurrentIndex(index)
            return True

        for i in range(self.algorithm_combo.count()):
            if self.algorithm_combo.itemText(i).lower() == name.lower():
                self.algorithm_combo.setCurrentIndex(i)
                return True

        for i in range(self.algorithm_combo.count()):
            if name.lower() in self.algorithm_combo.itemText(i).lower():
                self.algorithm_combo.setCurrentIndex(i)
                return True

        return False

    def get_parameters(self) -> Dict[str, Any]:
        """Get current parameter configuration."""
        return self._current_params.copy()

    def get_lifestyle_preferences(self) -> Dict[str, Any]:
        """Get lifestyle-based preferences for scheduler."""
        return {
            "lifestyle_mode": self.lifestyle_combo.currentData(),
            "morning_person": self.morning_checkbox.isChecked(),
            "free_day_preference": self.free_day_combo.currentData(),
        }


__all__ = ["AlgorithmSelector"]
