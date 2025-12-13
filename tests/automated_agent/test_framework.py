"""
Core Testing Framework - Base classes and utilities
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pathlib import Path
import json
import logging


class TestPhase(Enum):
    """Test execution phases"""
    GUI = "gui"
    TRANSCRIPT = "transcript"
    ALGORITHM = "algorithm"
    INTEGRATION = "integration"
    STRESS = "stress"


class ActionType(Enum):
    """Types of test actions"""
    CLICK = "click"
    INPUT = "input"
    SELECT = "select"
    LOAD_FILE = "load_file"
    VALIDATE = "validate"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    STATE_CAPTURE = "state_capture"


class TestStatus(Enum):
    """Test result status"""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"


@dataclass
class TestAction:
    """Record of a single test action"""
    timestamp: str
    phase: str
    action_type: str
    element: str
    value: Any
    expected: Any
    actual: Any
    status: str
    details: str
    screenshot_before: Optional[str] = None
    screenshot_after: Optional[str] = None
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp,
            "phase": self.phase,
            "action_type": self.action_type,
            "element": self.element,
            "value": str(self.value) if self.value is not None else None,
            "expected": str(self.expected) if self.expected is not None else None,
            "actual": str(self.actual) if self.actual is not None else None,
            "status": self.status,
            "details": self.details,
            "screenshot_before": self.screenshot_before,
            "screenshot_after": self.screenshot_after,
            "duration_ms": self.duration_ms
        }


@dataclass
class StateSnapshot:
    """Application state at a point in time"""
    timestamp: str
    gpa: float
    selected_credits: int
    max_credits_internal: int
    max_credits_ui: int
    selected_courses: List[str]
    total_ects: int
    conflicts: int
    free_days: int
    preferences: Dict[str, Any]
    inconsistencies: List[str] = field(default_factory=list)

    def validate_consistency(self) -> List[str]:
        """Detect state inconsistencies"""
        issues = []

        # Check max ECTS consistency
        if self.max_credits_internal != self.max_credits_ui:
            issues.append(
                f"CRITICAL: Max ECTS mismatch - Internal={self.max_credits_internal}, "
                f"UI Display={self.max_credits_ui}"
            )

        # Check selected credits vs max
        if self.selected_credits > self.max_credits_internal:
            issues.append(
                f"CRITICAL: Selected credits ({self.selected_credits}) exceeds "
                f"max allowed ({self.max_credits_internal})"
            )

        # Check total ECTS calculation
        calculated_ects = sum(
            int(course.split('(')[1].split(')')[0])
            for course in self.selected_courses
            if '(' in course and ')' in course
        )
        if calculated_ects != self.total_ects:
            issues.append(
                f"WARNING: ECTS calculation mismatch - Calculated={calculated_ects}, "
                f"Stored={self.total_ects}"
            )

        # Validate GPA-based ECTS limits
        expected_max_ects = self._calculate_expected_max_ects(self.gpa)
        if self.max_credits_internal != expected_max_ects:
            issues.append(
                f"WARNING: GPA-based ECTS limit incorrect - GPA={self.gpa}, "
                f"Expected={expected_max_ects}, Actual={self.max_credits_internal}"
            )

        self.inconsistencies = issues
        return issues

    @staticmethod
    def _calculate_expected_max_ects(gpa: float) -> int:
        """Calculate expected max ECTS based on GPA"""
        if gpa >= 3.5:
            return 45
        elif gpa >= 3.0:
            return 40
        elif gpa >= 2.5:
            return 35
        else:
            return 30

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp,
            "gpa": self.gpa,
            "selected_credits": self.selected_credits,
            "max_credits_internal": self.max_credits_internal,
            "max_credits_ui": self.max_credits_ui,
            "selected_courses": self.selected_courses,
            "total_ects": self.total_ects,
            "conflicts": self.conflicts,
            "free_days": self.free_days,
            "preferences": self.preferences,
            "inconsistencies": self.inconsistencies
        }


class TestLogger:
    """Comprehensive test logging system"""

    def __init__(self, test_name: str, output_dir: Path):
        self.test_name = test_name
        self.output_dir = Path(output_dir)
        self.start_time = datetime.now()

        # Storage
        self.actions: List[TestAction] = []
        self.snapshots: List[StateSnapshot] = []
        self.issues: List[str] = []

        # Create directory structure
        self.log_dir = self.output_dir / "agent_logs"
        self.screenshot_dir = self.output_dir / "screenshots"
        self.report_dir = self.output_dir / "reports"

        for directory in [self.log_dir, self.screenshot_dir, self.report_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Setup file logger
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"{test_name}_{timestamp}.log"
        self.json_log_file = self.log_dir / f"{test_name}_{timestamp}.json"

        # Configure logging
        self.logger = logging.getLogger(f"TestAgent.{test_name}")
        self.logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Also log to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        self.logger.info(f"="*80)
        self.logger.info(f"Test Session Started: {test_name}")
        self.logger.info(f"Timestamp: {self.start_time}")
        self.logger.info(f"="*80)

    def log_action(self, action: TestAction):
        """Log a test action"""
        self.actions.append(action)

        status_symbol = {
            "SUCCESS": "✅",
            "FAILED": "❌",
            "WARNING": "⚠️",
            "SKIPPED": "⏭️"
        }.get(action.status, "❓")

        log_msg = (
            f"{status_symbol} [{action.phase.upper()}] "
            f"{action.action_type}: {action.element} | "
            f"Expected: {action.expected} | Actual: {action.actual}"
        )

        if action.status == "FAILED":
            self.logger.error(f"{log_msg} | {action.details}")
            self.issues.append(f"[{action.timestamp}] {action.details}")
        elif action.status == "WARNING":
            self.logger.warning(f"{log_msg} | {action.details}")
        else:
            self.logger.info(log_msg)

    def log_snapshot(self, snapshot: StateSnapshot):
        """Log a state snapshot"""
        self.snapshots.append(snapshot)

        # Validate consistency
        issues = snapshot.validate_consistency()

        if issues:
            self.logger.error(f"🔍 STATE INCONSISTENCIES DETECTED ({len(issues)}):")
            for issue in issues:
                self.logger.error(f"   • {issue}")
                self.issues.append(f"[{snapshot.timestamp}] {issue}")

        self.logger.info(
            f"📸 STATE SNAPSHOT: GPA={snapshot.gpa:.2f}, "
            f"Credits={snapshot.selected_credits}/{snapshot.max_credits_internal}, "
            f"Courses={len(snapshot.selected_courses)}, Conflicts={snapshot.conflicts}"
        )

    def save_json_log(self):
        """Save detailed JSON log"""
        data = {
            "test_name": self.test_name,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "actions": [action.to_dict() for action in self.actions],
            "snapshots": [snapshot.to_dict() for snapshot in self.snapshots],
            "issues": self.issues,
            "summary": self.get_summary()
        }

        with open(self.json_log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"JSON log saved: {self.json_log_file}")

    def get_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        total_actions = len(self.actions)
        failed = len([a for a in self.actions if a.status == "FAILED"])
        warnings = len([a for a in self.actions if a.status == "WARNING"])
        success = len([a for a in self.actions if a.status == "SUCCESS"])

        success_rate = (success / total_actions * 100) if total_actions > 0 else 0

        return {
            "total_actions": total_actions,
            "success": success,
            "failed": failed,
            "warnings": warnings,
            "success_rate": f"{success_rate:.2f}%",
            "total_snapshots": len(self.snapshots),
            "total_issues": len(self.issues),
            "duration": str(datetime.now() - self.start_time)
        }

    def finalize(self):
        """Finalize logging and generate reports"""
        summary = self.get_summary()

        self.logger.info(f"="*80)
        self.logger.info(f"Test Session Complete: {self.test_name}")
        self.logger.info(f"Duration: {summary['duration']}")
        self.logger.info(f"Total Actions: {summary['total_actions']}")
        self.logger.info(f"Success: {summary['success']} | Failed: {summary['failed']} | Warnings: {summary['warnings']}")
        self.logger.info(f"Success Rate: {summary['success_rate']}")
        self.logger.info(f"Total Issues: {summary['total_issues']}")
        self.logger.info(f"="*80)

        # Save JSON log
        self.save_json_log()

        return summary

