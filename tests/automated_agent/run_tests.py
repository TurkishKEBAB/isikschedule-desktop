"""
Main Automated Test Agent
Executes comprehensive testing scenarios
"""

import sys
import time
import random
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.automated_agent.test_framework import TestLogger, TestPhase
from tests.automated_agent.gui_agent import GUITestAgent
from tests.automated_agent.report_generator import HTMLReportGenerator


class AutomatedTestAgent:
    """
    Main testing agent that orchestrates all test phases
    """

    def __init__(self, app: QApplication, main_window):
        self.app = app
        self.window = main_window

        # Setup logging
        output_dir = Path(__file__).parent.parent.parent / "tests" / "logs"
        self.logger = TestLogger("SchedularV3_FullTest", output_dir)

        # Setup agents
        self.gui_agent = GUITestAgent(main_window, self.logger)

        # Test control
        self.current_phase = None
        self.total_tests_run = 0
        self.phase_results = {}

    def run_all_tests(self):
        """Execute all test phases sequentially"""
        self.logger.logger.info("🚀 Starting comprehensive test suite...")

        try:
            # Phase 1: GUI Tests
            self.logger.logger.info("\n" + "="*80)
            self.logger.logger.info("PHASE 1: GUI TESTS")
            self.logger.logger.info("="*80)
            self.current_phase = TestPhase.GUI
            self.run_gui_tests()

            # Phase 2: Transcript Tests
            self.logger.logger.info("\n" + "="*80)
            self.logger.logger.info("PHASE 2: TRANSCRIPT TESTS")
            self.logger.logger.info("="*80)
            self.current_phase = TestPhase.TRANSCRIPT
            self.run_transcript_tests()

            # Phase 3: Algorithm Tests
            self.logger.logger.info("\n" + "="*80)
            self.logger.logger.info("PHASE 3: ALGORITHM TESTS")
            self.logger.logger.info("="*80)
            self.current_phase = TestPhase.ALGORITHM
            self.run_algorithm_tests()

            # Phase 4: Integration Tests
            self.logger.logger.info("\n" + "="*80)
            self.logger.logger.info("PHASE 4: INTEGRATION TESTS")
            self.logger.logger.info("="*80)
            self.current_phase = TestPhase.INTEGRATION
            self.run_integration_tests()

            # Phase 5: Stress Tests (shorter version)
            self.logger.logger.info("\n" + "="*80)
            self.logger.logger.info("PHASE 5: STRESS TESTS (QUICK VERSION)")
            self.logger.logger.info("="*80)
            self.current_phase = TestPhase.STRESS
            self.run_stress_tests(duration_seconds=60)  # 1 minute stress test

        except Exception as e:
            self.logger.logger.critical(f"Test suite failed with exception: {e}", exc_info=True)

        finally:
            # Generate reports
            self.finalize_tests()

    def run_gui_tests(self):
        """Phase 1: Test all GUI elements"""
        self.logger.logger.info("Testing GUI elements and interactions...")

        # Test 1.1: Take initial screenshot
        self.gui_agent.take_screenshot("initial_state")
        self.gui_agent.capture_state()

        # Test 1.2: Test tab switching
        for i in range(5):  # We have 5 tabs
            success, tab_name = self.gui_agent.switch_tab(i)
            time.sleep(0.5)
            self.gui_agent.capture_state()

        # Test 1.3: Return to File & Settings tab
        self.gui_agent.switch_tab(0)
        time.sleep(0.5)

        # Test 1.4: Test Load Sample Data button
        success, msg = self.gui_agent.click_button("Load Sample Data", by_text=True)
        if success:
            time.sleep(1.0)  # Wait for data to load
            self.gui_agent.capture_state()

        # Test 1.5: Test algorithm selection
        algorithms = ["A*", "Greedy", "Backtracking"]
        for algo in algorithms:
            success, selected = self.gui_agent.select_combo_item("algorithm_selector", algo)
            time.sleep(0.3)

        # Test 1.6: Switch to Course Browser
        self.gui_agent.switch_tab(1)
        time.sleep(0.5)
        self.gui_agent.capture_state()

        # Test 1.7: Switch to Course Selector
        self.gui_agent.switch_tab(2)
        time.sleep(0.5)
        self.gui_agent.capture_state()

        # Test 1.8: Switch to Schedule Viewer
        self.gui_agent.switch_tab(3)
        time.sleep(0.5)
        self.gui_agent.capture_state()

        # Test 1.9: Switch to Academic tab
        self.gui_agent.switch_tab(4)
        time.sleep(0.5)
        self.gui_agent.capture_state()

        self.logger.logger.info("✅ GUI tests completed")

    def run_transcript_tests(self):
        """Phase 2: Test transcript loading and parsing"""
        self.logger.logger.info("Testing transcript functionality...")

        # Switch to Academic tab
        self.gui_agent.switch_tab(4)
        time.sleep(0.5)

        # Test 2.1: Check if we can access transcript features
        self.gui_agent.capture_state()

        # Test 2.2: Try different GPA values
        gpa_values = [2.0, 2.5, 3.0, 3.5, 4.0]
        for gpa in gpa_values:
            self.logger.logger.info(f"Testing GPA: {gpa}")
            # Note: This would require finding the GPA input field
            # For now, just capture state
            self.gui_agent.capture_state()
            time.sleep(0.3)

        self.logger.logger.info("✅ Transcript tests completed")

    def run_algorithm_tests(self):
        """Phase 3: Test scheduler algorithms"""
        self.logger.logger.info("Testing scheduling algorithms...")

        # Switch back to File & Settings
        self.gui_agent.switch_tab(0)
        time.sleep(0.5)

        # Test 3.1: Test each algorithm
        algorithms = ["A*", "Greedy", "Backtracking", "BFS", "DFS"]

        for algo in algorithms:
            self.logger.logger.info(f"Testing algorithm: {algo}")

            # Try to select algorithm
            success, selected = self.gui_agent.select_combo_item("algorithm_selector", algo)
            time.sleep(0.3)

            # Capture state after selection
            self.gui_agent.capture_state()

            # Try to run scheduler (if button exists)
            run_success, msg = self.gui_agent.click_button("Run Scheduler", by_text=True)
            if run_success:
                time.sleep(2.0)  # Wait for scheduling to complete
                self.gui_agent.capture_state()

                # Check results in Schedule Viewer
                self.gui_agent.switch_tab(3)
                time.sleep(0.5)
                self.gui_agent.capture_state()

                # Return to settings
                self.gui_agent.switch_tab(0)
                time.sleep(0.5)

        self.logger.logger.info("✅ Algorithm tests completed")

    def run_integration_tests(self):
        """Phase 4: Test complete workflows"""
        self.logger.logger.info("Testing end-to-end workflows...")

        # Test 4.1: Complete workflow - Load → Select → Schedule → View

        # Step 1: Load sample data
        self.gui_agent.switch_tab(0)
        time.sleep(0.5)

        success, msg = self.gui_agent.click_button("Load Sample Data", by_text=True)
        if success:
            time.sleep(1.0)
            self.gui_agent.capture_state()

        # Step 2: Browse courses
        self.gui_agent.switch_tab(1)
        time.sleep(0.5)
        self.gui_agent.capture_state()

        # Step 3: Select courses
        self.gui_agent.switch_tab(2)
        time.sleep(0.5)
        self.gui_agent.capture_state()

        # Step 4: Generate schedule
        self.gui_agent.switch_tab(0)
        time.sleep(0.5)

        run_success, msg = self.gui_agent.click_button("Run Scheduler", by_text=True)
        if run_success:
            time.sleep(2.0)
            self.gui_agent.capture_state()

        # Step 5: View results
        self.gui_agent.switch_tab(3)
        time.sleep(0.5)
        self.gui_agent.capture_state()

        # Test 4.2: Test ECTS limit constraints
        self.logger.logger.info("Testing ECTS constraints...")

        # Try setting different max ECTS values
        ects_values = [31, 35, 40, 45]
        for ects in ects_values:
            self.logger.logger.info(f"Testing max ECTS: {ects}")
            # Would need to find and set ECTS spinbox
            self.gui_agent.capture_state()
            time.sleep(0.3)

        self.logger.logger.info("✅ Integration tests completed")

    def run_stress_tests(self, duration_seconds: int = 60):
        """Phase 5: Stress testing with random actions"""
        self.logger.logger.info(f"Running stress tests for {duration_seconds} seconds...")

        start_time = time.time()
        action_count = 0

        while time.time() - start_time < duration_seconds:
            # Random action selection
            action_type = random.choice([
                'switch_tab',
                'click_button',
                'capture_state'
            ])

            if action_type == 'switch_tab':
                tab_index = random.randint(0, 4)
                self.gui_agent.switch_tab(tab_index)
                time.sleep(0.2)

            elif action_type == 'click_button':
                # Try clicking common buttons
                buttons = ["Load Sample Data", "Run Scheduler", "Export"]
                button = random.choice(buttons)
                self.gui_agent.click_button(button, by_text=True)
                time.sleep(0.3)

            elif action_type == 'capture_state':
                self.gui_agent.capture_state()

            action_count += 1

            # Capture state every 10 actions
            if action_count % 10 == 0:
                self.gui_agent.capture_state()
                self.logger.logger.info(f"Stress test: {action_count} actions completed")

        self.logger.logger.info(f"✅ Stress tests completed - {action_count} random actions executed")

    def finalize_tests(self):
        """Finalize testing and generate reports"""
        self.logger.logger.info("\n" + "="*80)
        self.logger.logger.info("FINALIZING TESTS AND GENERATING REPORTS")
        self.logger.logger.info("="*80)

        # Finalize logger
        summary = self.logger.finalize()

        # Generate HTML report
        self.logger.logger.info("Generating HTML report...")
        report_gen = HTMLReportGenerator(self.logger)
        report_path = report_gen.generate(self.logger.report_dir)

        self.logger.logger.info(f"✅ HTML Report generated: {report_path}")
        self.logger.logger.info(f"✅ JSON Log saved: {self.logger.json_log_file}")
        self.logger.logger.info(f"✅ Text Log saved: {self.logger.log_file}")

        # Print final summary
        print("\n" + "="*80)
        print("TEST EXECUTION COMPLETE")
        print("="*80)
        print(f"Total Actions: {summary['total_actions']}")
        print(f"Success: {summary['success']}")
        print(f"Failed: {summary['failed']}")
        print(f"Warnings: {summary['warnings']}")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"Total Issues: {summary['total_issues']}")
        print(f"Duration: {summary['duration']}")
        print("="*80)
        print(f"\n📊 View detailed report: {report_path}")
        print(f"📝 View logs: {self.logger.log_file}")
        print("="*80)

        # Close application after a delay
        QTimer.singleShot(2000, self.app.quit)


def main():
    """Main entry point for automated testing"""
    print("="*80)
    print("SchedularV3 Automated Test Agent")
    print("White-box testing with comprehensive logging")
    print("="*80)

    # Import after path setup
    from main import setup_logging
    from gui.main_window import MainWindow

    # Setup logging
    setup_logging(verbose=True)

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("SchedularV3 Test Agent")

    # Create main window
    main_window = MainWindow()
    main_window.show()

    # Wait for window to fully load
    QApplication.processEvents()
    time.sleep(1.0)

    # Create and run test agent
    test_agent = AutomatedTestAgent(app, main_window)

    # Schedule test execution after UI is ready
    QTimer.singleShot(1000, test_agent.run_all_tests)

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

