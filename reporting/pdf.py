"""PDF export functionality for schedules."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
)

from core.models import Schedule


def save_schedules_as_pdf(
    schedules: List[Schedule],
    output_path: str | Path,
    title: str = "Course Schedules",
) -> None:
    """
    Save schedules as a PDF report.

    Args:
        schedules: List of Schedule objects to export
        output_path: Path to save the PDF file
        title: Title of the PDF document
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create PDF document
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=landscape(A4),
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
    )

    # Build content
    story = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30,
        alignment=1,  # Center
    )
    story.append(Paragraph(title, title_style))

    # Generation timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"Generated: {timestamp}", styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))

    # Add each schedule
    for idx, schedule in enumerate(schedules, 1):
        _add_schedule_to_story(story, schedule, idx, styles)
        if idx < len(schedules):
            story.append(PageBreak())

    # Build PDF
    doc.build(story)


def _add_schedule_to_story(
    story: List,
    schedule: Schedule,
    schedule_num: int,
    styles,
) -> None:
    """Add a single schedule to the PDF story."""
    # Schedule header
    header_text = f"Schedule #{schedule_num}"
    story.append(Paragraph(header_text, styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))

    # Statistics
    stats_text = (
        f"<b>Total Courses:</b> {len(schedule.courses)} | "
        f"<b>Total ECTS:</b> {schedule.total_credits} | "
        f"<b>Conflicts:</b> {schedule.conflict_count}"
    )
    story.append(Paragraph(stats_text, styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    # Weekly timetable
    _add_weekly_table(story, schedule)
    story.append(Spacer(1, 0.3 * inch))

    # Course list
    _add_course_list(story, schedule, styles)


def _add_weekly_table(story: List, schedule: Schedule) -> None:
    """Add weekly timetable grid to story."""
    # Define time slots and days
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    slots = list(range(1, 11))  # Slots 1-10

    # Create table data
    data = [['Time'] + days]

    # Build grid
    from collections import defaultdict
    grid = defaultdict(lambda: defaultdict(str))

    for course in schedule.courses:
        if not course.schedule:
            continue
        for day, slot in course.schedule:
            cell_text = f"{course.main_code}\n{course.teacher or 'TBA'}"
            grid[slot][day] = cell_text

    # Fill table
    for slot in slots:
        row = [f"Slot {slot}"]
        for day in days:
            row.append(grid[slot].get(day, ''))
        data.append(row)

    # Create table
    table = Table(data, colWidths=[0.8 * inch] + [1.6 * inch] * 5)

    # Style table
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        # Time column
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#ECF0F1')),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),

        # Data cells
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (1, 1), (-1, -1), 8),

        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
    ]))

    story.append(table)


def _add_course_list(story: List, schedule: Schedule, styles) -> None:
    """Add detailed course list to story."""
    story.append(Paragraph("<b>Course Details:</b>", styles['Heading3']))
    story.append(Spacer(1, 0.1 * inch))

    # Create course table
    data = [['Code', 'Name', 'Type', 'ECTS', 'Instructor', 'Schedule']]

    for course in sorted(schedule.courses, key=lambda c: c.code):
        # Format schedule
        schedule_str = ""
        if course.schedule:
            from collections import defaultdict
            day_slots = defaultdict(list)
            for day, slot in course.schedule:
                day_slots[day].append(str(slot))

            schedule_parts = []
            for day, slots in sorted(day_slots.items()):
                schedule_parts.append(f"{day[:3]}: {','.join(slots)}")
            schedule_str = "\n".join(schedule_parts)

        data.append([
            course.code,
            course.name[:30] + "..." if len(course.name) > 30 else course.name,
            course.course_type.upper(),
            str(course.ects),
            course.teacher[:20] + "..." if course.teacher and len(course.teacher) > 20 else (course.teacher or 'TBA'),
            schedule_str,
        ])

    table = Table(data, colWidths=[1.2 * inch, 2.5 * inch, 0.7 * inch, 0.6 * inch, 1.5 * inch, 1.5 * inch])

    table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),

        # Data
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (2, 1), (3, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.black),

        # Alternating rows
        *[('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F8F9FA'))
          for i in range(2, len(data), 2)],
    ]))

    story.append(table)


__all__ = ["save_schedules_as_pdf"]
