"""
SchedularV3 - Application Entry Point

This module serves as the entry point for the course scheduler application,
initializing the GUI with PyQt6 and setting up logging.
"""
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# Add the current directory to Python path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from config.settings import (
    APP_NAME,
    APP_VERSION,
    LOGS_DIR,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    LOG_LEVEL,
    LOG_FILE_MAX_BYTES,
    LOG_FILE_BACKUP_COUNT,
)


def setup_logging(verbose: bool = False) -> Path:
    """
    Configure the logging system.
    
    Args:
        verbose: If True, set logging level to DEBUG
        
    Returns:
        Path to the log file
    """
    # Create logs directory if it doesn't exist
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"schedular_{timestamp}.log"
    
    # Determine log level
    level = logging.DEBUG if verbose else getattr(logging, LOG_LEVEL)
    
    # Configure logging with rotation
    from logging.handlers import RotatingFileHandler
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=LOG_FILE_MAX_BYTES,
        backupCount=LOG_FILE_BACKUP_COUNT
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.info(f"{APP_NAME} v{APP_VERSION} - Logging initialized")
    logging.info(f"Log file: {log_file}")
    
    return log_file


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - Advanced Course Scheduling System"
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'{APP_NAME} v{APP_VERSION}'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose (DEBUG) logging'
    )
    parser.add_argument(
        '--no-splash',
        action='store_true',
        help='Skip the splash screen on startup'
    )
    
    return parser.parse_args()


def exception_hook(exctype, value, traceback):
    """
    Global exception handler for uncaught exceptions.
    
    Args:
        exctype: Exception type
        value: Exception value
        traceback: Exception traceback
    """
    logging.critical("Uncaught exception", exc_info=(exctype, value, traceback))
    
    # Show error dialog to user
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle("Critical Error")
    msg.setText("An unexpected error occurred.")
    msg.setInformativeText(str(value))
    msg.setDetailedText(''.join(traceback.format_exception(exctype, value, traceback)))
    msg.exec()
    
    # Call the default exception handler
    sys.__excepthook__(exctype, value, traceback)


def main():
    """
    Application entry point.
    
    Initializes the PyQt6 application, shows splash screen (optional),
    and creates the main window.
    """
    # Parse command-line arguments
    args = parse_arguments()
    
    # Setup logging
    try:
        log_file = setup_logging(verbose=args.verbose)
    except Exception as e:
        print(f"Failed to setup logging: {e}", file=sys.stderr)
        return 1
    
    logging.info(f"Starting {APP_NAME} v{APP_VERSION}")
    logging.info(f"Python version: {sys.version}")
    logging.info(f"Platform: {sys.platform}")
    
    # Install global exception handler
    sys.excepthook = exception_hook
    
    # Create QApplication
    try:
        # Enable High DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)
        app.setOrganizationName("Course Scheduler Team")
        
        logging.info("QApplication initialized successfully")
        
        # TODO: Show splash screen if not disabled
        # if not args.no_splash:
        #     from gui.splash import SplashScreen
        #     splash = SplashScreen()
        #     splash.show()
        
        # TODO: Create and show main window
        # from gui.main_window import MainWindow
        # main_window = MainWindow()
        # main_window.show()
        
        # For now, show a simple message box to confirm everything works
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(APP_NAME)
        msg.setText(f"Welcome to {APP_NAME} v{APP_VERSION}!")
        msg.setInformativeText("Foundation setup complete.\nGUI components will be added in Phase 4.")
        msg.exec()
        
        logging.info("Application initialized successfully")
        
        # Start event loop
        # return_code = app.exec()
        # logging.info(f"Application exiting with code {return_code}")
        # return return_code
        
        logging.info("Phase 1 complete - exiting")
        return 0
        
    except Exception as e:
        logging.critical(f"Failed to start application: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
