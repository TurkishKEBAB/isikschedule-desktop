"""Progress dialog for long-running operations."""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ProgressDialog(QDialog):
    """Modal dialog showing progress for algorithm execution."""

    def __init__(
        self,
        title: str = "Processing",
        message: str = "Please wait...",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 150)
        self._cancelled = False
        self._setup_ui(message)

    def _setup_ui(self, message: str) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Message label
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)
        font = self.message_label.font()
        font.setPointSize(10)
        self.message_label.setFont(font)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Indeterminate mode
        self.progress_bar.setTextVisible(True)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_font = self.status_label.font()
        status_font.setPointSize(9)
        self.status_label.setFont(status_font)

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel)

        # Add widgets
        layout.addWidget(self.message_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.cancel_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self._apply_style()

    def _apply_style(self) -> None:
        """Apply styling to dialog."""
        self.setStyleSheet(
            """
            QDialog {
                background-color: #FAFAFA;
            }
            QLabel {
                color: #424242;
            }
            QProgressBar {
                border: 2px solid #E0E0E0;
                border-radius: 5px;
                text-align: center;
                background-color: #FFFFFF;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:pressed {
                background-color: #C62828;
            }
        """
        )

    def set_message(self, message: str) -> None:
        """Update the main message."""
        self.message_label.setText(message)

    def set_status(self, status: str) -> None:
        """Update the status text."""
        self.status_label.setText(status)

    def set_progress(self, value: int, maximum: int = 100) -> None:
        """Set determinate progress."""
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"{value}/{maximum}")

    def set_indeterminate(self) -> None:
        """Set indeterminate progress mode."""
        self.progress_bar.setMaximum(0)
        self.progress_bar.setFormat("Processing...")

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self._cancelled = True
        self.cancel_button.setEnabled(False)
        self.cancel_button.setText("Cancelling...")
        self.set_status("Cancellation requested...")

    def is_cancelled(self) -> bool:
        """Check if user cancelled the operation."""
        return self._cancelled

    def auto_close_after(self, milliseconds: int) -> None:
        """Automatically close dialog after specified time."""
        QTimer.singleShot(milliseconds, self.accept)


__all__ = ["ProgressDialog"]
