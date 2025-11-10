"""JPEG export functionality for schedule grids."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtWidgets import QWidget

from core.models import Schedule
from gui.widgets import ScheduleGrid


def save_schedules_as_jpegs(
    schedules: List[Schedule],
    output_dir: str | Path,
    prefix: str = "schedule",
    size: Optional[QSize] = None,
) -> List[Path]:
    """
    Save schedules as JPEG images.

    Args:
        schedules: List of Schedule objects to export
        output_dir: Directory to save JPEG files
        prefix: Filename prefix for images
        size: Optional size for rendered images (default: 1200x800)

    Returns:
        List of paths to created JPEG files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if size is None:
        size = QSize(1200, 800)

    created_files = []

    for idx, schedule in enumerate(schedules, 1):
        # Create grid widget
        grid = ScheduleGrid()
        grid.set_schedule(schedule)
        grid.resize(size)

        # Render to image
        image = QImage(size, QImage.Format.Format_RGB32)
        image.fill(0xFFFFFF)  # White background

        painter = QPainter(image)
        try:
            grid.render(painter)
        finally:
            painter.end()

        # Save image
        filename = f"{prefix}_{idx}.jpg"
        filepath = output_dir / filename
        image.save(str(filepath), "JPEG", quality=95)

        created_files.append(filepath)

    return created_files


def save_widget_as_jpeg(
    widget: QWidget,
    output_path: str | Path,
    size: Optional[QSize] = None,
) -> Path:
    """
    Save any Qt widget as a JPEG image.

    Args:
        widget: Qt widget to capture
        output_path: Path to save the JPEG file
        size: Optional size for rendered image

    Returns:
        Path to created JPEG file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if size is not None:
        widget.resize(size)

    # Render to image
    image = QImage(widget.size(), QImage.Format.Format_RGB32)
    image.fill(0xFFFFFF)  # White background

    painter = QPainter(image)
    try:
        widget.render(painter)
    finally:
        painter.end()

    # Save image
    image.save(str(output_path), "JPEG", quality=95)

    return output_path


__all__ = ["save_schedules_as_jpegs", "save_widget_as_jpeg"]
