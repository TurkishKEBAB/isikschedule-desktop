"""Algorithm selector widget with dynamic parameter configuration."""

from __future__ import annotations

from typing import Any, Dict, Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from algorithms import iter_registered_schedulers
from algorithms.base_scheduler import BaseScheduler


class AlgorithmSelector(QWidget):
    """Widget for selecting and configuring scheduling algorithms."""

    algorithm_changed = pyqtSignal(str)  # Algorithm name
    parameters_changed = pyqtSignal(dict)  # Parameter dict

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

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Algorithm selection
        selection_group = QGroupBox("Algorithm Selection")
        selection_layout = QFormLayout(selection_group)

        self.algorithm_combo = QComboBox()
        self._populate_algorithms()
        self.algorithm_combo.currentTextChanged.connect(self._on_algorithm_changed)

        selection_layout.addRow("Algorithm:", self.algorithm_combo)

        # Algorithm info label
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #616161; font-style: italic;")
        selection_layout.addRow("Info:", self.info_label)

        # Parameters group
        self.params_group = QGroupBox("Parameters")
        self.params_layout = QFormLayout(self.params_group)

        # Common parameters
        common_group = QGroupBox("Common Settings")
        common_layout = QFormLayout(common_group)

        self.max_ects_spin = QSpinBox()
        self.max_ects_spin.setRange(10, 50)
        self.max_ects_spin.setValue(31)
        self.max_ects_spin.setSuffix(" ECTS")
        self.max_ects_spin.valueChanged.connect(self._emit_parameters)

        self.max_conflicts_spin = QSpinBox()
        self.max_conflicts_spin.setRange(0, 10)
        self.max_conflicts_spin.setValue(1)
        self.max_conflicts_spin.setSuffix(" conflict(s)")
        self.max_conflicts_spin.setToolTip("Maximum allowed time slot conflicts (0 = no conflicts allowed)")
        self.max_conflicts_spin.valueChanged.connect(self._emit_parameters)

        common_layout.addRow("Max ECTS:", self.max_ects_spin)
        common_layout.addRow("Max Conflicts:", self.max_conflicts_spin)

        # Add all groups
        layout.addWidget(selection_group)
        layout.addWidget(self.params_group)
        layout.addWidget(common_group)
        layout.addStretch()

        # Trigger initial setup
        self._on_algorithm_changed(self.algorithm_combo.currentText())

    def _populate_algorithms(self) -> None:
        """Populate algorithm dropdown from registry."""
        algorithms = []
        for scheduler_cls in iter_registered_schedulers():
            metadata = getattr(scheduler_cls, "metadata", None)
            if metadata:
                algorithms.append((metadata.name, metadata.description))

        algorithms.sort(key=lambda x: x[0])
        for name, description in algorithms:
            self.algorithm_combo.addItem(name)

    def _on_algorithm_changed(self, algorithm_name: str) -> None:
        """Handle algorithm selection change."""
        # Update info label
        metadata = self._get_algorithm_metadata(algorithm_name)
        if metadata:
            info_text = (
                f"{metadata.description}\n"
                f"Category: {metadata.category} | "
                f"Complexity: {metadata.complexity} | "
                f"Optimal: {'Yes' if metadata.optimal else 'No'}"
            )
            self.info_label.setText(info_text)

        # Rebuild parameter widgets
        self._rebuild_parameter_widgets(algorithm_name)

        self.algorithm_changed.emit(algorithm_name)
        self._emit_parameters()

    def _get_algorithm_metadata(self, name: str):
        """Get metadata for algorithm by name."""
        for scheduler_cls in iter_registered_schedulers():
            metadata = getattr(scheduler_cls, "metadata", None)
            if metadata and metadata.name == name:
                return metadata
        return None

    def _rebuild_parameter_widgets(self, algorithm_name: str) -> None:
        """Rebuild parameter input widgets for selected algorithm."""
        # Clear existing widgets
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._param_widgets.clear()

        # Get parameters for this algorithm
        params = self.ALGORITHM_PARAMS.get(algorithm_name, {})

        for param_name, config in params.items():
            if len(config) == 4:
                min_val, max_val, default, tooltip = config
                is_float = False
            else:
                min_val, max_val, default, tooltip, is_float = config

            if is_float:
                spin = QDoubleSpinBox()
                spin.setDecimals(2)
                spin.setSingleStep(0.1)
            else:
                spin = QSpinBox()

            spin.setRange(min_val, max_val)
            spin.setValue(default)
            spin.setToolTip(tooltip)
            spin.valueChanged.connect(self._emit_parameters)

            label = param_name.replace("_", " ").title() + ":"
            self.params_layout.addRow(label, spin)
            self._param_widgets[param_name] = spin

    def _emit_parameters(self) -> None:
        """Emit current parameter configuration."""
        params = {
            "max_ects": self.max_ects_spin.value(),
            "allow_conflicts": self.max_conflicts_spin.value() > 0,
            "max_conflicts": self.max_conflicts_spin.value(),
        }

        # Add algorithm-specific parameters
        for param_name, widget in self._param_widgets.items():
            params[param_name] = widget.value()

        self._current_params = params
        self.parameters_changed.emit(params)

    def get_selected_algorithm(self) -> str:
        """Get currently selected algorithm name."""
        return self.algorithm_combo.currentText()

    def get_parameters(self) -> Dict[str, Any]:
        """Get current parameter configuration."""
        return self._current_params.copy()


__all__ = ["AlgorithmSelector"]
