"""Global error handling and user-friendly error dialogs."""

from __future__ import annotations

import logging
import sys
import traceback as tb_module
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication, QMessageBox

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Global error handler for the application."""

    @staticmethod
    def setup_exception_hook() -> None:
        """Set up global exception hook to catch all unhandled exceptions."""
        sys.excepthook = ErrorHandler.handle_exception

    @staticmethod
    def handle_exception(exc_type, exc_value, exc_traceback) -> None:
        """
        Handle uncaught exceptions.

        Args:
            exc_type: Exception type
            exc_value: Exception instance
            exc_traceback: Traceback object
        """
        # Don't catch keyboard interrupt
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Log the exception
        logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

        # Format error message
        error_msg = ErrorHandler._format_error_message(exc_type, exc_value, exc_traceback)

        # Show user-friendly dialog
        ErrorHandler.show_error_dialog(
            title="Unexpected Error",
            message="An unexpected error occurred. The application may need to restart.",
            details=error_msg,
            critical=True
        )

    @staticmethod
    def _format_error_message(exc_type, exc_value, exc_traceback) -> str:
        """Format exception as a readable string."""
        tb_lines = tb_module.format_exception(exc_type, exc_value, exc_traceback)
        return "".join(tb_lines)

    @staticmethod
    def show_error_dialog(
        title: str,
        message: str,
        details: Optional[str] = None,
        critical: bool = False,
    ) -> None:
        """
        Show user-friendly error dialog.

        Args:
            title: Dialog title
            message: Main error message
            details: Detailed error information (optional)
            critical: Whether this is a critical error
        """
        app = QApplication.instance()
        if app is None:
            # No GUI available, just print
            print(f"ERROR: {title}\n{message}")
            if details:
                print(f"Details:\n{details}")
            return

        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        if critical:
            msg_box.setIcon(QMessageBox.Icon.Critical)
        else:
            msg_box.setIcon(QMessageBox.Icon.Warning)

        if details:
            msg_box.setDetailedText(details)

        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    @staticmethod
    def show_warning(title: str, message: str) -> None:
        """Show warning dialog."""
        ErrorHandler.show_error_dialog(title, message, critical=False)

    @staticmethod
    def handle_file_error(filepath: Path, operation: str, exc: Exception) -> None:
        """
        Handle file operation errors.

        Args:
            filepath: Path that caused the error
            operation: Operation being performed (e.g., "read", "write")
            exc: Exception that occurred
        """
        logger.error(f"File {operation} error: {filepath}", exc_info=exc)

        message = f"Failed to {operation} file:\n{filepath.name}"
        details = f"Path: {filepath}\n\nError: {exc}"

        ErrorHandler.show_error_dialog(
            title=f"File {operation.capitalize()} Error",
            message=message,
            details=details,
        )

    @staticmethod
    def handle_algorithm_error(algorithm_name: str, exc: Exception) -> None:
        """
        Handle algorithm execution errors.

        Args:
            algorithm_name: Name of the algorithm
            exc: Exception that occurred
        """
        logger.error(f"Algorithm error: {algorithm_name}", exc_info=exc)

        message = (
            f"An error occurred while running {algorithm_name}.\n\n"
            "Try adjusting the parameters or selecting a different algorithm."
        )
        details = f"Algorithm: {algorithm_name}\n\nError: {exc}"

        ErrorHandler.show_error_dialog(
            title="Algorithm Error",
            message=message,
            details=details,
        )

    @staticmethod
    def handle_data_error(message: str, exc: Optional[Exception] = None) -> None:
        """
        Handle data processing errors.

        Args:
            message: User-friendly error message
            exc: Optional exception that occurred
        """
        if exc:
            logger.error(f"Data error: {message}", exc_info=exc)
            details = str(exc)
        else:
            logger.error(f"Data error: {message}")
            details = None

        ErrorHandler.show_error_dialog(
            title="Data Error",
            message=message,
            details=details,
        )


__all__ = ["ErrorHandler"]
