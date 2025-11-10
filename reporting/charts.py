"""Chart generation for schedule analysis and statistics."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure

from core.models import Schedule


def generate_summary_chart(
    schedules: List[Schedule],
    output_path: Optional[str | Path] = None,
    title: str = "Schedule Analysis",
) -> Figure:
    """
    Generate a summary chart with schedule statistics.

    Args:
        schedules: List of schedules to analyze
        output_path: Optional path to save chart (PNG/SVG)
        title: Chart title

    Returns:
        matplotlib Figure object
    """
    if not schedules:
        raise ValueError("No schedules provided for chart generation")

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(title, fontsize=16, fontweight='bold')

    # 1. ECTS distribution
    _plot_ects_distribution(ax1, schedules)

    # 2. Conflict counts
    _plot_conflict_counts(ax2, schedules)

    # 3. Course type breakdown
    _plot_course_types(ax3, schedules)

    # 4. Top courses
    _plot_top_courses(ax4, schedules)

    plt.tight_layout()

    # Save if output path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches='tight')

    return fig


def _plot_ects_distribution(ax, schedules: List[Schedule]) -> None:
    """Plot ECTS credit distribution across schedules."""
    ects_values = [s.total_credits for s in schedules]

    ax.hist(ects_values, bins=15, color='#3498DB', alpha=0.7, edgecolor='black')
    ax.axvline(sum(ects_values) / len(ects_values), color='red', linestyle='--', 
               linewidth=2, label=f'Mean: {sum(ects_values) / len(ects_values):.1f}')
    
    ax.set_xlabel('Total ECTS Credits', fontweight='bold')
    ax.set_ylabel('Number of Schedules', fontweight='bold')
    ax.set_title('📊 ECTS Distribution', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)


def _plot_conflict_counts(ax, schedules: List[Schedule]) -> None:
    """Plot conflict count distribution."""
    conflict_values = [s.conflict_count for s in schedules]

    # Count schedules by conflict level
    from collections import Counter
    conflict_counts = Counter(conflict_values)

    conflicts = sorted(conflict_counts.keys())
    counts = [conflict_counts[c] for c in conflicts]

    colors = ['#27AE60' if c == 0 else '#F39C12' if c <= 2 else '#E74C3C' 
              for c in conflicts]

    ax.bar(conflicts, counts, color=colors, alpha=0.7, edgecolor='black')
    
    ax.set_xlabel('Number of Conflicts', fontweight='bold')
    ax.set_ylabel('Number of Schedules', fontweight='bold')
    ax.set_title('⚠️ Conflict Distribution', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # Add legend
    green_patch = mpatches.Patch(color='#27AE60', label='No Conflicts')
    orange_patch = mpatches.Patch(color='#F39C12', label='1-2 Conflicts')
    red_patch = mpatches.Patch(color='#E74C3C', label='3+ Conflicts')
    ax.legend(handles=[green_patch, orange_patch, red_patch])


def _plot_course_types(ax, schedules: List[Schedule]) -> None:
    """Plot course type breakdown."""
    # Aggregate course types across all schedules
    type_counts = {}
    for schedule in schedules:
        for course in schedule.courses:
            course_type = course.course_type.upper()
            type_counts[course_type] = type_counts.get(course_type, 0) + 1

    if not type_counts:
        ax.text(0.5, 0.5, 'No course data', ha='center', va='center')
        return

    types = list(type_counts.keys())
    counts = list(type_counts.values())

    colors_map = {
        'COMPULSORY': '#3498DB',
        'ELECTIVE': '#E74C3C',
        'UE': '#F39C12',
        'AE': '#9B59B6',
    }
    colors = [colors_map.get(t, '#95A5A6') for t in types]

    ax.pie(counts, labels=types, autopct='%1.1f%%', colors=colors,
           startangle=90, explode=[0.05] * len(types))
    
    ax.set_title('📚 Course Type Distribution', fontsize=12, fontweight='bold')


def _plot_top_courses(ax, schedules: List[Schedule]) -> None:
    """Plot most frequently selected courses."""
    # Count course occurrences
    course_counts = {}
    for schedule in schedules:
        for course in schedule.courses:
            key = f"{course.main_code}"
            course_counts[key] = course_counts.get(key, 0) + 1

    if not course_counts:
        ax.text(0.5, 0.5, 'No course data', ha='center', va='center')
        return

    # Get top 10
    top_courses = sorted(course_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    courses = [c[0] for c in top_courses]
    counts = [c[1] for c in top_courses]

    ax.barh(courses, counts, color='#2ECC71', alpha=0.7, edgecolor='black')
    
    ax.set_xlabel('Frequency', fontweight='bold')
    ax.set_ylabel('Course Code', fontweight='bold')
    ax.set_title('🏆 Top 10 Most Selected Courses', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')


def generate_algorithm_comparison_chart(
    algorithm_results: Dict[str, List[Schedule]],
    output_path: Optional[str | Path] = None,
) -> Figure:
    """
    Generate comparison chart for multiple algorithms.

    Args:
        algorithm_results: Dict mapping algorithm names to their schedules
        output_path: Optional path to save chart

    Returns:
        matplotlib Figure object
    """
    if not algorithm_results:
        raise ValueError("No algorithm results provided")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('⚖️ Algorithm Performance Comparison', fontsize=16, fontweight='bold')

    algorithms = list(algorithm_results.keys())
    
    # 1. Average ECTS comparison
    avg_ects = []
    for algo in algorithms:
        schedules = algorithm_results[algo]
        if schedules:
            avg = sum(s.total_credits for s in schedules) / len(schedules)
            avg_ects.append(avg)
        else:
            avg_ects.append(0)

    ax1.bar(algorithms, avg_ects, color='#3498DB', alpha=0.7, edgecolor='black')
    ax1.set_ylabel('Average ECTS Credits', fontweight='bold')
    ax1.set_title('📊 Average ECTS per Algorithm', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # 2. Average conflicts comparison
    avg_conflicts = []
    for algo in algorithms:
        schedules = algorithm_results[algo]
        if schedules:
            avg = sum(s.conflict_count for s in schedules) / len(schedules)
            avg_conflicts.append(avg)
        else:
            avg_conflicts.append(0)

    colors = ['#27AE60' if c == 0 else '#F39C12' if c <= 1 else '#E74C3C' 
              for c in avg_conflicts]

    ax2.bar(algorithms, avg_conflicts, color=colors, alpha=0.7, edgecolor='black')
    ax2.set_ylabel('Average Conflicts', fontweight='bold')
    ax2.set_title('⚠️ Average Conflicts per Algorithm', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

    plt.tight_layout()

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches='tight')

    return fig


__all__ = ["generate_summary_chart", "generate_algorithm_comparison_chart"]
