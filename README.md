# SchedularV3

Advanced Course Scheduling System with PyQt6

## Features

- **15+ Scheduling Algorithms**: DFS, A*, Genetic Algorithm, Simulated Annealing, and more
- **Modern GUI**: Built with PyQt6 for cross-platform compatibility
- **Smart Conflict Detection**: Automatic detection and resolution of schedule conflicts
- **Multiple Export Formats**: PDF, Excel, JPEG reports
- **Database Integration**: SQLite for persistent storage
- **Comprehensive Testing**: Full test coverage with pytest

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

Run the application:
```bash
python main.py
```

### Command-line Options

- `--version`: Show version information
- `-v, --verbose`: Enable verbose (DEBUG) logging
- `--no-splash`: Skip the splash screen on startup

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

3.0.0 - Foundation Release

## Authors

Course Scheduler Team
