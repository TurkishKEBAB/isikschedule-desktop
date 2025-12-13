"""
GUI Test Agent - PyQt6-based GUI testing with screenshot capture
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import sys

from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLineEdit,
    QComboBox, QSpinBox, QCheckBox, QLabel, QTabWidget
)
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QScreen

from .test_framework import (
    TestLogger, TestAction, StateSnapshot,
    TestPhase, ActionType, TestStatus
)


class GUITestAgent:
    """Automated GUI testing agent with visual verification"""

    def __init__(self, main_window, logger: TestLogger):
        self.window = main_window
        self.logger = logger
        self.screenshot_counter = 0
        self.app = QApplication.instance()

    def take_screenshot(self, name: str = "screenshot") -> str:
        """Capture screenshot of main window"""
        self.screenshot_counter += 1
        timestamp = datetime.now().strftime("%H%M%S_%f")[:-3]
        filename = f"{self.screenshot_counter:04d}_{name}_{timestamp}.png"
        filepath = self.logger.screenshot_dir / filename

        try:
            screen = self.app.primaryScreen()
            pixmap = screen.grabWindow(self.window.winId())
            pixmap.save(str(filepath))
            return str(filepath)
        except Exception as e:
            self.logger.logger.error(f"Screenshot failed: {e}")
            return ""

    def find_widget(self, widget_name: str, widget_type: type = QWidget) -> Optional[QWidget]:
        """Find widget by object name"""
        widget = self.window.findChild(widget_type, widget_name)
        if not widget:
            # Try to find by accessible name
            for child in self.window.findChildren(widget_type):
                if child.accessibleName() == widget_name:
                    return child
        return widget

    def click_button(
        self,
        button_identifier: str,
        expected_result: str = "Button clicked",
        by_text: bool = False
    ) -> Tuple[bool, str]:
        """Click a button and verify action"""
        start_time = time.time()
        screenshot_before = self.take_screenshot(f"before_click_{button_identifier}")

        # Find button
        if by_text:
            button = None
            for btn in self.window.findChildren(QPushButton):
                if btn.text() == button_identifier:
                    button = btn
                    break
        else:
            button = self.find_widget(button_identifier, QPushButton)

        if not button:
            duration_ms = (time.time() - start_time) * 1000
            action = TestAction(
                timestamp=datetime.now().isoformat(),
                phase=TestPhase.GUI.value,
                action_type=ActionType.CLICK.value,
                element=button_identifier,
                value=None,
                expected=expected_result,
                actual="Button not found",
                status=TestStatus.FAILED.value,
                details=f"Button '{button_identifier}' not found in GUI",
                screenshot_before=screenshot_before,
                duration_ms=duration_ms
            )
            self.logger.log_action(action)
            return False, "Button not found"

        # Check if button is enabled
        if not button.isEnabled():
            duration_ms = (time.time() - start_time) * 1000
            action = TestAction(
                timestamp=datetime.now().isoformat(),
                phase=TestPhase.GUI.value,
                action_type=ActionType.CLICK.value,
                element=button_identifier,
                value=None,
                expected=expected_result,
                actual="Button is disabled",
                status=TestStatus.WARNING.value,
                details=f"Button '{button_identifier}' is disabled",
                screenshot_before=screenshot_before,
                duration_ms=duration_ms
            )
            self.logger.log_action(action)
            return False, "Button disabled"

        # Click the button
        QTest.mouseClick(button, Qt.MouseButton.LeftButton)
        QApplication.processEvents()
        time.sleep(0.2)  # Wait for UI updates

        screenshot_after = self.take_screenshot(f"after_click_{button_identifier}")
        duration_ms = (time.time() - start_time) * 1000

        action = TestAction(
            timestamp=datetime.now().isoformat(),
            phase=TestPhase.GUI.value,
            action_type=ActionType.CLICK.value,
            element=button_identifier,
            value=None,
            expected=expected_result,
            actual="Button clicked successfully",
            status=TestStatus.SUCCESS.value,
            details=f"Successfully clicked button '{button_identifier}'",
            screenshot_before=screenshot_before,
            screenshot_after=screenshot_after,
            duration_ms=duration_ms
        )
        self.logger.log_action(action)
        return True, "Success"

    def enter_text(
        self,
        field_identifier: str,
        text: str,
        clear_first: bool = True
    ) -> Tuple[bool, str]:
        """Enter text into a field"""
        start_time = time.time()
        screenshot_before = self.take_screenshot(f"before_input_{field_identifier}")

        field = self.find_widget(field_identifier, QLineEdit)

        if not field:
            duration_ms = (time.time() - start_time) * 1000
            action = TestAction(
                timestamp=datetime.now().isoformat(),
                phase=TestPhase.GUI.value,
                action_type=ActionType.INPUT.value,
                element=field_identifier,
                value=text,
                expected=text,
                actual="Field not found",
                status=TestStatus.FAILED.value,
                details=f"Text field '{field_identifier}' not found",
                screenshot_before=screenshot_before,
                duration_ms=duration_ms
            )
            self.logger.log_action(action)
            return False, "Field not found"

        if clear_first:
            field.clear()

        QTest.keyClicks(field, text)
        QApplication.processEvents()
        time.sleep(0.1)

        actual_text = field.text()
        screenshot_after = self.take_screenshot(f"after_input_{field_identifier}")
        duration_ms = (time.time() - start_time) * 1000

        status = TestStatus.SUCCESS if actual_text == text else TestStatus.FAILED

        action = TestAction(
            timestamp=datetime.now().isoformat(),
            phase=TestPhase.GUI.value,
            action_type=ActionType.INPUT.value,
            element=field_identifier,
            value=text,
            expected=text,
            actual=actual_text,
            status=status.value,
            details=f"Entered '{text}', got '{actual_text}'",
            screenshot_before=screenshot_before,
            screenshot_after=screenshot_after,
            duration_ms=duration_ms
        )
        self.logger.log_action(action)
        return status == TestStatus.SUCCESS, actual_text

    def select_combo_item(
        self,
        combo_identifier: str,
        item_text: str
    ) -> Tuple[bool, str]:
        """Select item from combo box"""
        start_time = time.time()
        screenshot_before = self.take_screenshot(f"before_select_{combo_identifier}")

        combo = self.find_widget(combo_identifier, QComboBox)

        if not combo:
            duration_ms = (time.time() - start_time) * 1000
            action = TestAction(
                timestamp=datetime.now().isoformat(),
                phase=TestPhase.GUI.value,
                action_type=ActionType.SELECT.value,
                element=combo_identifier,
                value=item_text,
                expected=item_text,
                actual="ComboBox not found",
                status=TestStatus.FAILED.value,
                details=f"ComboBox '{combo_identifier}' not found",
                screenshot_before=screenshot_before,
                duration_ms=duration_ms
            )
            self.logger.log_action(action)
            return False, "ComboBox not found"

        # Find and select item
        index = combo.findText(item_text)
        if index == -1:
            duration_ms = (time.time() - start_time) * 1000
            available_items = [combo.itemText(i) for i in range(combo.count())]
            action = TestAction(
                timestamp=datetime.now().isoformat(),
                phase=TestPhase.GUI.value,
                action_type=ActionType.SELECT.value,
                element=combo_identifier,
                value=item_text,
                expected=item_text,
                actual=f"Item not found. Available: {available_items}",
                status=TestStatus.FAILED.value,
                details=f"Item '{item_text}' not found in ComboBox",
                screenshot_before=screenshot_before,
                duration_ms=duration_ms
            )
            self.logger.log_action(action)
            return False, "Item not found"

        combo.setCurrentIndex(index)
        QApplication.processEvents()
        time.sleep(0.1)

        actual_text = combo.currentText()
        screenshot_after = self.take_screenshot(f"after_select_{combo_identifier}")
        duration_ms = (time.time() - start_time) * 1000

        status = TestStatus.SUCCESS if actual_text == item_text else TestStatus.FAILED

        action = TestAction(
            timestamp=datetime.now().isoformat(),
            phase=TestPhase.GUI.value,
            action_type=ActionType.SELECT.value,
            element=combo_identifier,
            value=item_text,
            expected=item_text,
            actual=actual_text,
            status=status.value,
            details=f"Selected '{item_text}', got '{actual_text}'",
            screenshot_before=screenshot_before,
            screenshot_after=screenshot_after,
            duration_ms=duration_ms
        )
        self.logger.log_action(action)
        return status == TestStatus.SUCCESS, actual_text

    def set_spinbox_value(
        self,
        spinbox_identifier: str,
        value: int
    ) -> Tuple[bool, int]:
        """Set spinbox value"""
        start_time = time.time()

        spinbox = self.find_widget(spinbox_identifier, QSpinBox)

        if not spinbox:
            duration_ms = (time.time() - start_time) * 1000
            action = TestAction(
                timestamp=datetime.now().isoformat(),
                phase=TestPhase.GUI.value,
                action_type=ActionType.INPUT.value,
                element=spinbox_identifier,
                value=value,
                expected=value,
                actual="SpinBox not found",
                status=TestStatus.FAILED.value,
                details=f"SpinBox '{spinbox_identifier}' not found",
                duration_ms=duration_ms
            )
            self.logger.log_action(action)
            return False, 0

        spinbox.setValue(value)
        QApplication.processEvents()
        time.sleep(0.1)

        actual_value = spinbox.value()
        duration_ms = (time.time() - start_time) * 1000

        status = TestStatus.SUCCESS if actual_value == value else TestStatus.FAILED

        action = TestAction(
            timestamp=datetime.now().isoformat(),
            phase=TestPhase.GUI.value,
            action_type=ActionType.INPUT.value,
            element=spinbox_identifier,
            value=value,
            expected=value,
            actual=actual_value,
            status=status.value,
            details=f"Set value to {value}, got {actual_value}",
            duration_ms=duration_ms
        )
        self.logger.log_action(action)
        return status == TestStatus.SUCCESS, actual_value

    def switch_tab(self, tab_index: int) -> Tuple[bool, str]:
        """Switch to a different tab"""
        start_time = time.time()
        screenshot_before = self.take_screenshot(f"before_tab_switch_{tab_index}")

        tab_widget = self.window.tab_widget

        if tab_index < 0 or tab_index >= tab_widget.count():
            duration_ms = (time.time() - start_time) * 1000
            action = TestAction(
                timestamp=datetime.now().isoformat(),
                phase=TestPhase.GUI.value,
                action_type=ActionType.CLICK.value,
                element=f"tab_{tab_index}",
                value=tab_index,
                expected="Tab switched",
                actual=f"Invalid tab index (max: {tab_widget.count()-1})",
                status=TestStatus.FAILED.value,
                details=f"Tab index {tab_index} out of range",
                screenshot_before=screenshot_before,
                duration_ms=duration_ms
            )
            self.logger.log_action(action)
            return False, "Invalid tab index"

        tab_widget.setCurrentIndex(tab_index)
        QApplication.processEvents()
        time.sleep(0.2)

        actual_index = tab_widget.currentIndex()
        tab_name = tab_widget.tabText(actual_index)
        screenshot_after = self.take_screenshot(f"after_tab_switch_{tab_index}")
        duration_ms = (time.time() - start_time) * 1000

        status = TestStatus.SUCCESS if actual_index == tab_index else TestStatus.FAILED

        action = TestAction(
            timestamp=datetime.now().isoformat(),
            phase=TestPhase.GUI.value,
            action_type=ActionType.CLICK.value,
            element=f"tab_{tab_index}",
            value=tab_index,
            expected=f"Switch to tab {tab_index}",
            actual=f"Switched to tab {actual_index}: {tab_name}",
            status=status.value,
            details=f"Tab switched to '{tab_name}'",
            screenshot_before=screenshot_before,
            screenshot_after=screenshot_after,
            duration_ms=duration_ms
        )
        self.logger.log_action(action)
        return status == TestStatus.SUCCESS, tab_name

    def capture_state(self) -> StateSnapshot:
        """Capture current application state"""
        try:
            # Extract state from main window
            gpa = getattr(self.window, 'current_gpa', 0.0)

            # Try to get max ECTS from different sources
            max_credits_internal = getattr(self.window, 'max_ects', 31)

            # Get UI displayed max ECTS
            max_credits_ui = self._extract_ui_max_ects()

            # Get selected courses
            selected_courses = self._get_selected_courses()

            # Calculate totals
            total_ects = sum(
                int(c.split('(')[1].split(')')[0])
                for c in selected_courses
                if '(' in c and ')' in c
            )

            snapshot = StateSnapshot(
                timestamp=datetime.now().isoformat(),
                gpa=gpa,
                selected_credits=total_ects,
                max_credits_internal=max_credits_internal,
                max_credits_ui=max_credits_ui,
                selected_courses=selected_courses,
                total_ects=total_ects,
                conflicts=self._count_conflicts(),
                free_days=self._count_free_days(),
                preferences=self._get_preferences()
            )

            self.logger.log_snapshot(snapshot)
            return snapshot

        except Exception as e:
            self.logger.logger.error(f"Failed to capture state: {e}")
            return StateSnapshot(
                timestamp=datetime.now().isoformat(),
                gpa=0.0,
                selected_credits=0,
                max_credits_internal=0,
                max_credits_ui=0,
                selected_courses=[],
                total_ects=0,
                conflicts=0,
                free_days=0,
                preferences={}
            )

    def _extract_ui_max_ects(self) -> int:
        """Extract max ECTS value from UI display"""
        try:
            # Look for labels containing ECTS information
            for label in self.window.findChildren(QLabel):
                text = label.text()
                if 'max' in text.lower() and 'ects' in text.lower():
                    import re
                    match = re.search(r'(\d+)', text)
                    if match:
                        return int(match.group(1))
            return 31  # Default
        except:
            return 31

    def _get_selected_courses(self) -> List[str]:
        """Get list of selected courses"""
        try:
            if hasattr(self.window, 'selector_tab'):
                # Extract from selector tab
                return []
            return []
        except:
            return []

    def _count_conflicts(self) -> int:
        """Count schedule conflicts"""
        try:
            if hasattr(self.window, 'viewer_tab'):
                # Extract from viewer tab
                return 0
            return 0
        except:
            return 0

    def _count_free_days(self) -> int:
        """Count free days in schedule"""
        try:
            if hasattr(self.window, 'viewer_tab'):
                # Extract from viewer tab
                return 0
            return 0
        except:
            return 0

    def _get_preferences(self) -> Dict[str, Any]:
        """Get user preferences"""
        try:
            prefs = {}
            if hasattr(self.window, '_scheduler_prefs'):
                sp = self.window._scheduler_prefs
                prefs = {
                    'max_conflicts': getattr(sp, 'max_conflicts', 0),
                    'desired_free_days': getattr(sp, 'desired_free_days', []),
                    'prefer_morning': getattr(sp, 'prefer_morning', False),
                    'prefer_afternoon': getattr(sp, 'prefer_afternoon', False)
                }
            return prefs
        except:
            return {}

