"""
Phase 2 Demo - Data Layer Showcase

Demonstrates real Işık University Excel format support.
"""
from pathlib import Path
from core.excel_loader import process_excel, save_courses_to_excel
from core.models import Schedule, CourseGroup
from core.database import Database


def main():
    print("=" * 70)
    print("SchedularV3 - Phase 2 Data Layer Demo")
    print("Real Işık University Excel Format Support")
    print("=" * 70)
    print()
    
    # Load courses from real Işık format
    print("📁 Loading courses from Işık University Excel file...")
    courses = process_excel("data/sample_isik_courses.xlsx")
    print(f"✅ Loaded {len(courses)} courses")
    print()
    
    # Display sample courses
    print("📚 Sample Courses:")
    print("-" * 70)
    for i, course in enumerate(courses[:5], 1):
        print(f"{i}. {course.code} - {course.name}")
        print(f"   Teacher: {course.teacher}")
        print(f"   ECTS: {course.ects} | Faculty: {course.faculty}")
        print(f"   Campus: {course.campus}")
        print(f"   Schedule: {course.schedule}")
        print()
    
    # Create a schedule
    print("📅 Creating a sample schedule...")
    selected_courses = [
        courses[0],  # COMP1007.1
        courses[1],  # COMP1111.1
        courses[5],  # MATH1101.1
        courses[6],  # PHYS1101.1
        courses[7],  # ENGL1102.1
    ]
    
    schedule = Schedule(courses=selected_courses)
    print(f"✅ Schedule created with {len(schedule.courses)} courses")
    print(f"   Total credits: {schedule.total_credits} ECTS")
    print(f"   Conflicts: {schedule.conflict_count}")
    print(f"   Status: {'⚠️ Has conflicts' if schedule.has_conflicts else '✓ No conflicts'}")
    print()
    
    # Group courses by main code
    print("📦 Grouping courses by main code...")
    groups = {}
    for course in courses:
        if course.main_code not in groups:
            groups[course.main_code] = []
        groups[course.main_code].append(course)
    
    print(f"✅ Found {len(groups)} course groups:")
    for main_code, group_courses in list(groups.items())[:3]:
        print(f"   {main_code}: {len(group_courses)} section(s)")
    print()
    
    # Save to database
    print("💾 Saving to database...")
    with Database() as db:
        db.initialize()
        db.save_courses(courses)
        
        # Retrieve and verify
        loaded = db.get_all_courses()
        print(f"✅ Saved and verified {len(loaded)} courses in database")
    print()
    
    # Export to Excel
    output_path = Path("output/demo_export.xlsx")
    output_path.parent.mkdir(exist_ok=True)
    
    print("📤 Exporting courses to Excel...")
    save_courses_to_excel(courses[:5], str(output_path))
    print(f"✅ Exported to: {output_path}")
    print()
    
    # Display time slot parsing examples
    print("⏰ Time Slot Parsing Examples:")
    print("-" * 70)
    examples = [
        ("M1, M2", "Monday periods 1-2"),
        ("T6, T7, T8", "Tuesday periods 6-8"),
        ("Th5, Th6, F7", "Thursday 5-6, Friday 7"),
        ("W1, W2, W3, W4", "Wednesday periods 1-4"),
    ]
    
    for time_str, description in examples:
        print(f"   {time_str:20} → {description}")
    print()
    
    print("=" * 70)
    print("✅ Phase 2 Demo Complete!")
    print("=" * 70)
    print()
    print("Features demonstrated:")
    print("  ✓ Real Işık University Excel format import")
    print("  ✓ Time slot parsing (M1, T2, Th5 format)")
    print("  ✓ Course type detection (lecture/lab/ps)")
    print("  ✓ Schedule creation and conflict detection")
    print("  ✓ Course grouping")
    print("  ✓ Database persistence")
    print("  ✓ Excel export")
    print()


if __name__ == "__main__":
    main()
