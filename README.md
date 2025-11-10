# SchedularV3

Advanced Course Scheduling System with PyQt6

## Features

### ✅ Phase 1 & 2 Complete (Data Layer)
- **🎓 Real Işık University Format**: Native support for Işık University Excel files
- **📅 Smart Time Parsing**: Handles "M1, M2, T3, Th5" format automatically
- **🔍 Course Type Detection**: Automatically detects lecture/lab/ps courses
- **💾 Database Integration**: SQLite for persistent storage
- **🎯 Conflict Detection**: Automatic detection of schedule conflicts
- **📊 Excel Import/Export**: Turkish character support, faculty/campus fields
- **✅ Comprehensive Testing**: 19/19 tests passing

### 🚧 Coming in Phase 3 (Scheduling Algorithms)
- **15+ Scheduling Algorithms**: DFS, A*, Genetic Algorithm, Simulated Annealing
- **Smart Optimization**: Multi-objective optimization with constraints
- **Performance Benchmarks**: Algorithm comparison and analytics

### 🚧 Coming in Phase 4+ (GUI & Reporting)
- **Modern GUI**: PyQt6-based desktop interface
- **Multiple Export Formats**: PDF, Excel, JPEG reports
- **Interactive Visualization**: Drag-and-drop schedule builder

## Installation

### Requirements

- Python 3.11 or higher
- Windows, macOS, or Linux

### Setup

1. Clone the repository or extract the archive

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (CMD)
.\venv\Scripts\activate.bat

# Linux/macOS
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Demo

```bash
# Run Phase 2 demo (Data Layer)
python demo_phase2.py
```

### Run the Application

```bash
python main.py
```

### Command-line Options

- `--version`: Show version information
- `-v, --verbose`: Enable verbose (DEBUG) logging
- `--no-splash`: Skip the splash screen on startup

## Real Işık University Excel Format

SchedularV3 supports the official Işık University course export format:

**Expected Columns:**
- `Ders Kodu` / Course Code (e.g., "COMP1111.1")
- `Başlık` / Course Name
- `AKTS Kredisi` / ECTS
- `Kampüs` / Campus (Şile, Online)
- `Eğitmen Adı` / Teacher First Name
- `Eğitmen Soyadı` / Teacher Last Name
- `Fakülte Adı` / Faculty Name
- `Ders Saati(leri)` / Schedule (e.g., "M1, M2, T3")

**Time Format:** 
- `M1, M2` = Monday periods 1-2
- `T6, T7, T8` = Tuesday periods 6-8
- `Th5, Th6` = Thursday periods 5-6
- `W1, W2, W3` = Wednesday periods 1-3
- `F7` = Friday period 7

**Example Usage:**

```python
from core.excel_loader import process_excel, save_courses_to_excel
from core.models import Schedule

# Load courses
courses = process_excel("my_courses.xlsx")

# Create schedule
schedule = Schedule(courses=courses[:10])
print(f"Credits: {schedule.total_credits}")
print(f"Conflicts: {schedule.conflict_count}")

# Export
save_courses_to_excel(schedule.courses, "output.xlsx")
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black .

# Type checking
mypy .

# Linting
flake8 .
```

## Project Structure

```
SchedularV3/
├── config/          # Configuration settings
├── core/            # Core business logic
├── algorithms/      # Scheduling algorithms
├── gui/             # GUI components
│   └── widgets/     # Custom widgets
├── reporting/       # Report generation
├── utils/           # Utility functions
├── tests/           # Unit tests
├── resources/       # Images, icons, styles
│   ├── icons/
│   ├── images/
│   └── styles/
├── logs/            # Application logs
└── docs/            # Documentation

```

## License

See LICENSE file for details.

## Version

**3.0.0-alpha** - Phase 1 & 2 Complete

**Release Status:**
- ✅ Phase 1: Foundation (Complete)
- ✅ Phase 2: Data Layer (Complete)  
- 🚧 Phase 3: Scheduling Algorithms (In Progress)
- 🚧 Phase 4: GUI Layer (Planned)
- 🚧 Phase 5: Reporting (Planned)

**Test Results:**
```
19/19 tests passing (100%)
Coverage: 80% excel_loader, 60% models
```

## Authors

Course Scheduler Team
