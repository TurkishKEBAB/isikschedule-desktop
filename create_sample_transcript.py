"""
Create sample transcript Excel for testing.
"""
import pandas as pd
from pathlib import Path

# Student info
student_data = {
    'Field': ['Student ID', 'Student Name', 'Program'],
    'Value': ['23SOFT1040', 'YİĞİT OKUR', 'Computer Science Engineering']
}

# Grades data (sadece geçilen dersler - Retake'lerin son hali)
grades_data = {
    'Course Code': [
        'COMP1007', 'CORE0101', 'CORE0103', 'CORE0201', 'MATH1111',
        'COMP1111', 'CORE0501', 'CORE0105', 'ENGL1101', 'COMP1112',
        'CORE0104', 'CORE0107', 'CORE0102', 'ECON1005', 'COMP2112',
        'ELEC1411', 'SOFT2101', 'ELEC1402', 'CORE0106', 'COMP2222',
        'ENGL1102', 'CORE0402', 'SOFT3511', 'MATH2103'
    ],
    'Course Name': [
        'INTRODUCTION TO COMPUTER AND SOFTWARE ENGINEERING',
        'HISTORY OF TURKISH REPUBLIC I',
        'TURKISH I',
        'NATURE SCIENCE HUMAN I',
        'CALCULUS I',
        'FUNDAMENTALS OF PROGRAMMING',
        'ART SOCIETY HUMAN',
        'ORIENTATION',
        'ACADEMIC ENGLISH 1',
        'OBJECT ORIENTED PROGRAMMING',
        'TURKISH II',
        'CREATIVE THINKING AND PROBLEM SOLVING',
        'HISTORY OF TURKISH REPUBLIC II',
        'INTRODUCTION TO ECONOMICS',
        'DATA STRUCTURES AND ALGORITHMS',
        'LOGIC DESIGN',
        'PRINCIPLES OF SOFTWARE ENGINEERING',
        'LOGIC DESIGN LABORATORY',
        'CAREER PLANNING',
        'DATABASE SYSTEMS',
        'ACADEMIC ENGLISH 2',
        'ETHICS LAW AND SOCIETY',
        'SOFTWARE REQUIREMENTS ENGINEERING',
        'DISCRETE MATHEMATICS'
    ],
    'ECTS': [
        1, 2, 2, 5, 5, 6, 3, 1, 4, 6, 2, 3, 2, 5, 7, 4, 5, 2, 1, 7, 4, 3, 5, 6
    ],
    'Letter Grade': [
        'DD', 'BA', 'BA', 'BB', 'CC', 'CB', 'DC', 'CC', 'BA', 'CC',
        'AA', 'CC', 'BB', 'CC', 'DC', 'DC', 'CC', 'CC', 'AA', 'DD',
        'AA', 'CB', 'DD', 'BA'
    ],
    'Semester': [
        'Fall-2023', 'Fall-2023', 'Fall-2023', 'Fall-2023', 'Spring-2024',
        'Spring-2024', 'Spring-2024', 'Fall-2023', 'Spring-2024', 'Spring-2024',
        'Spring-2024', 'Spring-2024', 'Spring-2024', 'Summer-2024', 'Fall-2024',
        'Fall-2024', 'Fall-2024', 'Fall-2024', 'Fall-2024', 'Spring-2025',
        'Spring-2025', 'Spring-2025', 'Spring-2025', 'Transfer Summer-2025'
    ]
}

# Create DataFrames
student_df = pd.DataFrame(student_data)
grades_df = pd.DataFrame(grades_data)

# Create Excel
excel_path = Path(__file__).parent / "sample_transcript_yigit_okur.xlsx"

with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    # Write student info at top
    student_df.to_excel(writer, sheet_name='Transcript', index=False, startrow=0, header=False)
    
    # Add blank row
    # Write grades starting from row 5
    grades_df.to_excel(writer, sheet_name='Transcript', index=False, startrow=5)

print(f"✅ Excel file created: {excel_path}")
print(f"   Student: YİĞİT OKUR (23SOFT1040)")
print(f"   Courses: {len(grades_df)}")
print(f"   Total ECTS: {grades_df['ECTS'].sum()}")

# Calculate GPA manually to verify
grade_map = {'AA': 4.0, 'BA': 3.5, 'BB': 3.0, 'CB': 2.5, 'CC': 2.0, 'DC': 1.5, 'DD': 1.0, 'F': 0.0}
grades_df['Numeric'] = grades_df['Letter Grade'].map(grade_map)
total_points = (grades_df['ECTS'] * grades_df['Numeric']).sum()
total_ects = grades_df['ECTS'].sum()
gpa = total_points / total_ects
print(f"   Calculated GPA: {gpa:.2f}")

