"""Setup configuration for SchedularV3 project."""

from setuptools import setup, find_packages

setup(
    name="SchedularV3",
    version="3.0.0",
    description="Advanced course scheduling system for universities",
    author="Your Name",
    packages=find_packages(exclude=["tests", "docs"]),
    python_requires=">=3.11",
    install_requires=[
        # Core GUI Framework
        "PyQt6>=6.6.1",
        "PyQt6-Charts>=6.6.0",
        # Data Processing
        "pandas>=2.1.0",
        "numpy>=1.24.0",
        "openpyxl>=3.1.0",
        # Reporting & Visualization
        "reportlab>=4.0.0",
        "matplotlib>=3.7.0",
        "Pillow>=10.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-qt>=4.2.0",
            "pytest-cov>=4.1.0",
            "mypy>=1.5.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

