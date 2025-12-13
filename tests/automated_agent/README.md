# 🧪 Automated Test Agent for SchedularV3

## Overview

Comprehensive automated testing system for SchedularV3 using white-box testing methodology with full action logging, state tracking, and inconsistency detection.

## Features

### 🎯 Test Coverage
- **Phase 1: GUI Tests** - All UI elements, buttons, tabs, inputs
- **Phase 2: Transcript Tests** - Transcript loading, parsing, GPA validation
- **Phase 3: Algorithm Tests** - A*, Greedy, Backtracking, BFS, DFS schedulers
- **Phase 4: Integration Tests** - Complete end-to-end workflows
- **Phase 5: Stress Tests** - Random monkey testing with high volume operations

### 📊 Logging & Reporting
- **Millisecond-precision timestamps** for every action
- **Screenshot capture** before and after critical actions
- **State snapshots** capturing GPA, ECTS, courses, conflicts
- **Inconsistency detection** for UI vs internal state mismatches
- **HTML reports** with visual timeline and embedded screenshots
- **JSON logs** for programmatic analysis

### 🔍 Inconsistency Detection

The agent automatically detects:
- ❌ UI display value ≠ Internal state value (e.g., max ECTS mismatch)
- ❌ Calculated ECTS ≠ Stored ECTS
- ❌ GPA-based ECTS limit violations
- ❌ Constraint violations (max conflicts, free days)
- ❌ Schedule conflicts not detected
- ❌ Prerequisite violations

### 📈 GPA-ECTS Validation

Automatically validates against Işık University rules:
- GPA < 2.0: Max 30 ECTS
- GPA 2.0-2.49: Max 30 ECTS
- GPA 2.5-2.99: Max 35 ECTS
- GPA 3.0-3.49: Max 40 ECTS
- GPA ≥ 3.5: Max 45 ECTS

## Installation

No additional dependencies required beyond SchedularV3 requirements.

## Usage

### Quick Start

```bash
# From the SchedularV3 root directory
python tests/automated_agent/run_tests.py
```

### What Happens

1. **Application launches** with test agent active
2. **Automated testing begins** after 1 second
3. **All 5 phases execute** sequentially
4. **Reports generate** automatically
5. **Application closes** after 2 seconds

### Viewing Results

After test completion:

- **HTML Report**: `tests/logs/reports/test_report.html`
- **JSON Log**: `tests/logs/agent_logs/SchedularV3_FullTest_YYYYMMDD_HHMMSS.json`
- **Text Log**: `tests/logs/agent_logs/SchedularV3_FullTest_YYYYMMDD_HHMMSS.log`
- **Screenshots**: `tests/logs/screenshots/`

## Architecture

```
tests/automated_agent/
├── __init__.py                 # Package initialization
├── test_framework.py           # Core testing framework
│   ├── TestLogger              # Comprehensive logging
│   ├── TestAction              # Action recording
│   ├── StateSnapshot           # State capture & validation
│   └── TestPhase/ActionType    # Enums
├── gui_agent.py                # PyQt6 GUI testing
│   ├── click_button()          # Button interactions
│   ├── enter_text()            # Text input
│   ├── select_combo_item()     # ComboBox selection
│   ├── switch_tab()            # Tab navigation
│   ├── take_screenshot()       # Screenshot capture
│   └── capture_state()         # State snapshot
├── report_generator.py         # HTML report generation
│   └── HTMLReportGenerator     # Visual reports
├── run_tests.py                # Main test runner
│   └── AutomatedTestAgent      # Orchestrator
└── README.md                   # This file
```

## Test Phases

### Phase 1: GUI Tests (~30 seconds)
- Test all 5 tabs
- Test tab switching
- Test "Load Sample Data" button
- Test algorithm selector
- Capture state after each action

### Phase 2: Transcript Tests (~20 seconds)
- Test transcript features
- Test GPA value handling
- Validate ECTS limit calculations

### Phase 3: Algorithm Tests (~60 seconds)
- Test each scheduler algorithm
- Verify algorithm execution
- Check results in Schedule Viewer
- Validate constraints

### Phase 4: Integration Tests (~45 seconds)
- Complete workflow: Load → Browse → Select → Schedule → View
- Test ECTS constraint enforcement
- End-to-end validation

### Phase 5: Stress Tests (~60 seconds)
- Random action execution
- Tab switching chaos
- Button clicking spree
- State capture every 10 actions
- Performance monitoring

## Customization

### Adjust Test Duration

Edit `run_tests.py`:

```python
# Longer stress test
self.run_stress_tests(duration_seconds=300)  # 5 minutes
```

### Add Custom Tests

```python
def run_my_custom_test(self):
    """Add your test logic"""
    self.gui_agent.switch_tab(0)
    self.gui_agent.click_button("MyButton", by_text=True)
    self.gui_agent.capture_state()
```

### Filter Test Phases

Comment out phases in `run_all_tests()`:

```python
def run_all_tests(self):
    self.run_gui_tests()
    self.run_transcript_tests()
    # self.run_algorithm_tests()  # Skip this
    # self.run_integration_tests()  # Skip this
    self.run_stress_tests(duration_seconds=30)
```

## Output Examples

### Console Output
```
================================================================================
SchedularV3 Automated Test Agent
White-box testing with comprehensive logging
================================================================================
2025-12-04 15:30:00.123 - INFO - Test Session Started: SchedularV3_FullTest
================================================================================
PHASE 1: GUI TESTS
================================================================================
2025-12-04 15:30:01.234 - INFO - ✅ [GUI] CLICK: tab_0 | Expected: Switch to tab 0 | Actual: Switched to tab 0: 📁 File & Settings
2025-12-04 15:30:02.345 - INFO - 📸 STATE SNAPSHOT: GPA=3.00, Credits=0/40, Courses=0, Conflicts=0
...
```

### HTML Report Preview
- Visual timeline with color-coded actions (green=success, red=fail, yellow=warning)
- Embedded screenshots showing before/after states
- State snapshots with all metrics
- Inconsistency alerts highlighted in red
- Summary statistics with success rate

## Troubleshooting

### No screenshots captured
- Ensure PyQt6 is properly installed
- Check write permissions in `tests/logs/screenshots/`

### Tests fail immediately
- Verify application launches normally first
- Check that all dependencies are installed
- Review error logs in `tests/logs/agent_logs/`

### Inconsistencies detected
- **This is expected!** The agent is designed to find bugs
- Review HTML report for details
- Check specific state snapshots where issues occur

## Contributing

To add new test scenarios:

1. Create test method in `AutomatedTestAgent`
2. Add to appropriate phase
3. Use `gui_agent` methods for interactions
4. Call `capture_state()` frequently
5. Log with `self.logger.log_action()`

## License

Same as SchedularV3 project.

## Support

For issues or questions, check the main SchedularV3 documentation.

