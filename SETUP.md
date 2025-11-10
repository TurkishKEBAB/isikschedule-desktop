# SchedularV3 Setup Guide

This guide will help you set up SchedularV3 development environment.

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git (optional, for version control)

## Installation Steps

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.\venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Verify Installation

Run the foundation tests:
```bash
pytest tests/test_foundation.py -v
```

All tests should pass.

### 6. Run the Application

```bash
python main.py
```

You should see a welcome message box confirming the foundation is set up correctly.

## Command-line Options

- `--version` - Show version information
- `-v, --verbose` - Enable verbose (DEBUG) logging
- `--no-splash` - Skip the splash screen on startup

## Development Tools

### Code Formatting

```bash
black .
```

### Type Checking

```bash
mypy .
```

### Linting

```bash
flake8 .
```

### Running All Tests

```bash
pytest
```

### Test Coverage

```bash
pytest --cov=. --cov-report=html
```

View coverage report: Open `htmlcov/index.html` in your browser.

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
├── logs/            # Application logs
└── docs/            # Documentation
```

## Troubleshooting

### Virtual Environment Activation Issues

If PowerShell shows an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### PyQt6 Import Errors

Make sure you activated the virtual environment and installed dependencies:
```bash
pip list | grep PyQt6
```

### Test Failures

If tests fail, check:
1. Python version (must be 3.11+)
2. All dependencies installed
3. Virtual environment activated

## Next Steps

After successful installation:
1. Read the documentation in `docs/`
2. Explore the codebase structure
3. Run the application and test basic functionality
4. Check the roadmap in `TODO.md` for upcoming features

## Support

For issues or questions, check:
- Project documentation in `docs/`
- Test files in `tests/` for usage examples
- Configuration in `config/settings.py`
