"""
Basic smoke test to ensure the foundation is set up correctly.
"""
import sys
from pathlib import Path


def test_python_version():
    """Test that Python version is 3.11 or higher."""
    assert sys.version_info >= (3, 11), "Python 3.11+ is required"


def test_project_structure():
    """Test that the basic project structure exists."""
    base_dir = Path(__file__).parent.parent
    
    required_dirs = [
        'config',
        'core',
        'algorithms',
        'gui',
        'reporting',
        'utils',
        'tests',
        'resources',
        'logs',
    ]
    
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        assert dir_path.exists(), f"Directory {dir_name} not found"
        assert dir_path.is_dir(), f"{dir_name} is not a directory"


def test_config_import():
    """Test that config module can be imported."""
    from config import settings
    
    assert hasattr(settings, 'APP_NAME')
    assert hasattr(settings, 'APP_VERSION')
    assert hasattr(settings, 'DEFAULT_MAX_ECTS')
    assert hasattr(settings, 'PERIOD_TIMES')
    assert hasattr(settings, 'DAYS')


def test_config_values():
    """Test that config values are correct."""
    from config.settings import APP_NAME, APP_VERSION, DEFAULT_MAX_ECTS
    
    assert APP_NAME == "SchedularV3"
    assert APP_VERSION == "3.0.0"
    assert DEFAULT_MAX_ECTS == 31


def test_requirements_file():
    """Test that requirements.txt exists and has required packages."""
    base_dir = Path(__file__).parent.parent
    req_file = base_dir / 'requirements.txt'
    
    assert req_file.exists(), "requirements.txt not found"
    
    content = req_file.read_text()
    required_packages = [
        'PyQt6',
        'pandas',
        'numpy',
        'pytest',
        'mypy',
        'black',
        'flake8',
    ]
    
    for package in required_packages:
        assert package in content, f"Package {package} not in requirements.txt"
