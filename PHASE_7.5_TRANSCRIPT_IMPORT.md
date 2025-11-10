# 📥 Phase 7.5: Transcript Import - Task List

**Durum:** 🔴 NOT STARTED (0%)  
**Öncelik:** HIGH  
**Tahmini Süre:** 8-10 saat (1-2 gün)  
**Hedef Tarih:** 12 Kasım 2025

---

## 🎯 Hedef

Academic Tab'ın 4. sub-tab'ını tamamlamak: Transcript Import functionality.

**Şu anda:** Placeholder label ("Coming soon in Phase 7.4...")  
**Hedef:** Fully functional transcript import/export system

---

## ✅ Önkoşullar (Tamamlandı)

- ✅ Grade, Transcript, GraduationRequirement models (Phase 7.1)
- ✅ GPACalculator, PrerequisiteChecker (Phase 7.2-7.3)
- ✅ Academic Tab GUI structure (Phase 7.4)
- ✅ Database layer (Phase 2)

---

## 📋 Görev Listesi

### 1. Excel Import Functionality (4 saat) 🔴

#### 1.1 Create TranscriptImportWidget
**Dosya:** `gui/dialogs/transcript_import_dialog.py`  
**Tahmini Süre:** 1.5 saat

**UI Components:**
```python
class TranscriptImportWidget(QWidget):
    transcript_imported = pyqtSignal(Transcript)
    
    def __init__(self):
        # Student info inputs
        self.student_id_input = QLineEdit()
        self.student_name_input = QLineEdit()
        self.program_input = QLineEdit()
        
        # Import buttons
        self.import_excel_btn = QPushButton("📁 Import from Excel")
        self.add_manual_btn = QPushButton("✏️ Add Grade Manually")
        
        # Transcript table
        self.transcript_table = QTableWidget()
        # Columns: Code, Name, ECTS, Grade, Numeric, Semester, Actions
        
        # Action buttons
        self.save_btn = QPushButton("💾 Save to Database")
        self.export_btn = QPushButton("📤 Export to Excel")
        self.clear_btn = QPushButton("🗑️ Clear All")
```

**Signals:**
- `transcript_imported(Transcript)` - Emitted when transcript loaded
- `transcript_saved()` - Emitted when saved to database

**Methods:**
- `_import_from_excel()` - Open file dialog, parse Excel
- `_populate_table(grades)` - Fill table with grades
- `_get_transcript()` - Build Transcript object from table
- `_save_to_database()` - Save to SQLite
- `_export_to_excel()` - Export current transcript

---

#### 1.2 Excel Parser Implementation
**Dosya:** `core/transcript_parser.py`  
**Tahmini Süre:** 1.5 saat

**Expected Excel Format:**
```
| Course Code | Course Name | ECTS | Grade | Semester |
|-------------|-------------|------|-------|----------|
| CS101       | Intro to CS | 6    | AA    | Fall 2023|
| MATH101     | Calculus I  | 6    | BA    | Fall 2023|
| ...         | ...         | ...  | ...   | ...      |
```

**Alternative Columns (flexible mapping):**
- "Ders Kodu" / "Course Code"
- "Ders Adı" / "Başlık" / "Course Name"
- "AKTS" / "ECTS" / "Kredi"
- "Harf Notu" / "Grade" / "Letter Grade"
- "Dönem" / "Semester"

**Implementation:**
```python
class TranscriptParser:
    """Parse Excel files to extract transcript data."""
    
    @staticmethod
    def parse_excel(file_path: str) -> Tuple[Dict[str, str], List[Grade]]:
        """
        Parse Excel file.
        
        Returns:
            (student_info, grades)
            student_info: {'id': '...', 'name': '...', 'program': '...'}
            grades: List of Grade objects
        """
        df = pd.read_excel(file_path)
        
        # Auto-detect columns
        column_map = TranscriptParser._detect_columns(df)
        
        # Extract student info (from first row metadata or user input)
        student_info = {
            'id': '',
            'name': '',
            'program': ''
        }
        
        # Parse grades
        grades = []
        for _, row in df.iterrows():
            try:
                grade = Grade(
                    course_code=row[column_map['code']],
                    course_name=row[column_map['name']],
                    ects=int(row[column_map['ects']]),
                    letter_grade=row[column_map['grade']],
                    numeric_grade=GPACalculator.letter_to_numeric(
                        row[column_map['grade']]
                    ),
                    semester=str(row[column_map['semester']])
                )
                grades.append(grade)
            except Exception as e:
                logger.warning(f"Skipping row: {e}")
                continue
        
        return student_info, grades
    
    @staticmethod
    def _detect_columns(df: pd.DataFrame) -> Dict[str, str]:
        """Auto-detect column names."""
        column_map = {}
        
        for col in df.columns:
            col_lower = col.lower()
            if 'kod' in col_lower or 'code' in col_lower:
                column_map['code'] = col
            elif 'ad' in col_lower or 'name' in col_lower or 'başlık' in col_lower:
                column_map['name'] = col
            elif 'ects' in col_lower or 'akts' in col_lower or 'kredi' in col_lower:
                column_map['ects'] = col
            elif 'not' in col_lower or 'grade' in col_lower:
                column_map['grade'] = col
            elif 'dönem' in col_lower or 'semester' in col_lower:
                column_map['semester'] = col
        
        return column_map
    
    @staticmethod
    def validate_grades(grades: List[Grade]) -> List[str]:
        """
        Validate grades.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        seen_codes = set()
        
        for i, grade in enumerate(grades):
            # Check for duplicates
            if grade.course_code in seen_codes:
                errors.append(
                    f"Row {i+1}: Duplicate course {grade.course_code}"
                )
            seen_codes.add(grade.course_code)
            
            # Validate letter grade
            if grade.letter_grade not in GPACalculator.GRADE_SCALE:
                errors.append(
                    f"Row {i+1}: Invalid grade '{grade.letter_grade}' for {grade.course_code}"
                )
            
            # Validate ECTS
            if not (1 <= grade.ects <= 12):
                errors.append(
                    f"Row {i+1}: Invalid ECTS {grade.ects} for {grade.course_code}"
                )
        
        return errors
```

**Error Handling:**
- Invalid Excel file format
- Missing required columns
- Invalid letter grades
- Invalid ECTS values
- Duplicate courses
- Empty rows

---

#### 1.3 UI Integration
**Dosya:** `gui/tabs/academic_tab.py`  
**Tahmini Süre:** 1 saat

**Replace placeholder tab:**
```python
# Before (in AcademicTab.__init__):
import_widget = QLabel("📥 Transcript Import\n\nComing soon in Phase 7.4...")
self.tab_widget.addTab(import_widget, "📥 Import")

# After:
from gui.dialogs.transcript_import_dialog import TranscriptImportWidget

self.import_widget = TranscriptImportWidget()
self.import_widget.transcript_imported.connect(self._on_transcript_imported)
self.tab_widget.addTab(self.import_widget, "📥 Import")

def _on_transcript_imported(self, transcript: Transcript):
    """Handle transcript import."""
    # Update GPA calculator
    self.gpa_calculator.set_transcript(transcript)
    
    # Update graduation planner
    self.grad_planner.set_transcript(transcript)
    
    # Show success message
    QMessageBox.information(
        self, "Success",
        f"Imported transcript for {transcript.student_name}\n"
        f"Total ECTS: {transcript.get_total_ects()}\n"
        f"GPA: {transcript.get_gpa():.2f}"
    )
```

---

### 2. Manual Grade Entry (2 saat) 🔴

#### 2.1 Create AddGradeDialog
**Dosya:** `gui/dialogs/add_grade_dialog.py`  
**Tahmini Süre:** 1.5 saat

**UI Design:**
```python
class AddGradeDialog(QDialog):
    """Dialog for adding/editing a grade manually."""
    
    def __init__(self, grade: Optional[Grade] = None, parent=None):
        """
        Args:
            grade: Existing grade to edit (None for new grade)
        """
        super().__init__(parent)
        self.setWindowTitle("Add Grade" if grade is None else "Edit Grade")
        self.grade = grade
        self._init_ui()
        
        if grade:
            self._populate_fields(grade)
    
    def _init_ui(self):
        layout = QFormLayout(self)
        
        # Course code
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("e.g., CS101")
        layout.addRow("Course Code:", self.code_input)
        
        # Course name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Introduction to CS")
        layout.addRow("Course Name:", self.name_input)
        
        # ECTS
        self.ects_input = QSpinBox()
        self.ects_input.setRange(1, 12)
        self.ects_input.setValue(6)
        layout.addRow("ECTS:", self.ects_input)
        
        # Letter grade
        self.grade_combo = QComboBox()
        self.grade_combo.addItems(["AA", "BA", "BB", "CB", "CC", "DC", "DD", "FD", "FF"])
        layout.addRow("Letter Grade:", self.grade_combo)
        
        # Numeric grade (auto-calculated, read-only)
        self.numeric_label = QLabel("4.0")
        layout.addRow("Numeric Grade:", self.numeric_label)
        self.grade_combo.currentTextChanged.connect(self._update_numeric_grade)
        
        # Semester
        self.semester_input = QLineEdit()
        self.semester_input.setPlaceholderText("e.g., Fall 2023")
        layout.addRow("Semester:", self.semester_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("✅ Save")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addRow(button_layout)
    
    def _update_numeric_grade(self, letter: str):
        """Update numeric grade when letter grade changes."""
        numeric = GPACalculator.letter_to_numeric(letter)
        self.numeric_label.setText(f"{numeric:.1f}")
    
    def get_grade(self) -> Grade:
        """Get Grade object from form."""
        return Grade(
            course_code=self.code_input.text().strip(),
            course_name=self.name_input.text().strip(),
            ects=self.ects_input.value(),
            letter_grade=self.grade_combo.currentText(),
            numeric_grade=GPACalculator.letter_to_numeric(
                self.grade_combo.currentText()
            ),
            semester=self.semester_input.text().strip()
        )
    
    def _populate_fields(self, grade: Grade):
        """Populate form with existing grade."""
        self.code_input.setText(grade.course_code)
        self.name_input.setText(grade.course_name)
        self.ects_input.setValue(grade.ects)
        self.grade_combo.setCurrentText(grade.letter_grade)
        self.semester_input.setText(grade.semester)
```

**Validation:**
- Required fields: code, name, semester
- ECTS range: 1-12
- Grade must be valid letter grade

---

#### 2.2 Integrate with TranscriptImportWidget
**Tahmini Süre:** 30 dakika

**Add manual entry button:**
```python
# In TranscriptImportWidget
def _add_grade_manually(self):
    """Open dialog to add grade manually."""
    dialog = AddGradeDialog(parent=self)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        grade = dialog.get_grade()
        self._add_grade_to_table(grade)
        QMessageBox.information(self, "Success", "Grade added!")

def _edit_grade(self, row: int):
    """Edit existing grade."""
    grade = self._get_grade_from_row(row)
    dialog = AddGradeDialog(grade=grade, parent=self)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        updated_grade = dialog.get_grade()
        self._update_table_row(row, updated_grade)

def _delete_grade(self, row: int):
    """Delete grade from table."""
    reply = QMessageBox.question(
        self, "Confirm Delete",
        "Delete this grade?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if reply == QMessageBox.StandardButton.Yes:
        self.transcript_table.removeRow(row)
```

**Table row actions:**
- Edit button → Opens AddGradeDialog with existing grade
- Delete button → Removes row from table

---

### 3. Database Persistence (2 saat) 🔴

#### 3.1 Extend Database Class
**Dosya:** `core/database.py`  
**Tahmini Süre:** 1.5 saat

**Add transcript table:**
```sql
CREATE TABLE IF NOT EXISTS transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL UNIQUE,
    student_name TEXT NOT NULL,
    program TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transcript_id INTEGER NOT NULL,
    course_code TEXT NOT NULL,
    course_name TEXT NOT NULL,
    ects INTEGER NOT NULL,
    letter_grade TEXT NOT NULL,
    numeric_grade REAL NOT NULL,
    semester TEXT NOT NULL,
    FOREIGN KEY (transcript_id) REFERENCES transcripts(id) ON DELETE CASCADE,
    UNIQUE (transcript_id, course_code)
);
```

**Database methods:**
```python
class Database:
    # ... existing methods ...
    
    def save_transcript(self, transcript: Transcript) -> int:
        """
        Save transcript to database.
        
        Returns:
            transcript_id
        """
        cursor = self.conn.cursor()
        
        # Insert or update transcript
        cursor.execute("""
            INSERT INTO transcripts (student_id, student_name, program)
            VALUES (?, ?, ?)
            ON CONFLICT(student_id) DO UPDATE SET
                student_name = excluded.student_name,
                program = excluded.program,
                updated_at = CURRENT_TIMESTAMP
        """, (transcript.student_id, transcript.student_name, transcript.program))
        
        transcript_id = cursor.lastrowid
        
        # Delete old grades
        cursor.execute("DELETE FROM grades WHERE transcript_id = ?", (transcript_id,))
        
        # Insert new grades
        for grade in transcript.grades:
            cursor.execute("""
                INSERT INTO grades (
                    transcript_id, course_code, course_name,
                    ects, letter_grade, numeric_grade, semester
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                transcript_id, grade.course_code, grade.course_name,
                grade.ects, grade.letter_grade, grade.numeric_grade, grade.semester
            ))
        
        self.conn.commit()
        return transcript_id
    
    def load_transcript(self, student_id: str) -> Optional[Transcript]:
        """Load transcript from database."""
        cursor = self.conn.cursor()
        
        # Get transcript info
        cursor.execute("""
            SELECT student_id, student_name, program
            FROM transcripts
            WHERE student_id = ?
        """, (student_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Get grades
        cursor.execute("""
            SELECT course_code, course_name, ects, letter_grade, numeric_grade, semester
            FROM grades
            WHERE transcript_id = (
                SELECT id FROM transcripts WHERE student_id = ?
            )
        """, (student_id,))
        
        grades = [
            Grade(
                course_code=row[0],
                course_name=row[1],
                ects=row[2],
                letter_grade=row[3],
                numeric_grade=row[4],
                semester=row[5]
            )
            for row in cursor.fetchall()
        ]
        
        return Transcript(
            student_id=row[0],
            student_name=row[1],
            program=row[2],
            grades=grades
        )
    
    def delete_transcript(self, student_id: str):
        """Delete transcript from database."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM transcripts WHERE student_id = ?", (student_id,))
        self.conn.commit()
    
    def list_transcripts(self) -> List[Dict[str, str]]:
        """List all transcripts (student info only)."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT student_id, student_name, program FROM transcripts")
        return [
            {'id': row[0], 'name': row[1], 'program': row[2]}
            for row in cursor.fetchall()
        ]
```

---

#### 3.2 Auto-save and Load
**Tahmini Süre:** 30 dakika

**Auto-load on app startup:**
```python
# In MainWindow.__init__ or Academic Tab
def _load_saved_transcript(self):
    """Load transcript from database if exists."""
    db = Database()
    transcripts = db.list_transcripts()
    
    if transcripts:
        # If multiple transcripts, show selection dialog
        # For now, load the first one
        transcript = db.load_transcript(transcripts[0]['id'])
        if transcript:
            self.academic_tab.import_widget.set_transcript(transcript)
            self.academic_tab.gpa_calculator.set_transcript(transcript)
            self.academic_tab.grad_planner.set_transcript(transcript)
```

**Auto-save on changes:**
```python
# In TranscriptImportWidget
def _save_to_database(self):
    """Save current transcript to database."""
    transcript = self._get_transcript()
    
    if not transcript.student_id or not transcript.student_name:
        QMessageBox.warning(
            self, "Missing Info",
            "Please enter Student ID and Name before saving."
        )
        return
    
    db = Database()
    db.save_transcript(transcript)
    
    QMessageBox.information(
        self, "Saved",
        f"Transcript saved for {transcript.student_name}!"
    )
```

---

### 4. Data Validation (1 saat) 🔴

#### 4.1 Implement Validation Logic
**Tahmini Süre:** 1 saat

**Validation checks:**
```python
class TranscriptValidator:
    """Validate transcript data."""
    
    @staticmethod
    def validate_transcript(transcript: Transcript) -> List[str]:
        """
        Validate entire transcript.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Check student info
        if not transcript.student_id:
            errors.append("Student ID is required")
        if not transcript.student_name:
            errors.append("Student name is required")
        if not transcript.program:
            errors.append("Program is required")
        
        # Check grades
        if not transcript.grades:
            errors.append("Transcript must have at least one grade")
        
        # Validate individual grades
        seen_codes = set()
        for i, grade in enumerate(transcript.grades):
            # Duplicate check
            if grade.course_code in seen_codes:
                errors.append(
                    f"Grade {i+1}: Duplicate course {grade.course_code}"
                )
            seen_codes.add(grade.course_code)
            
            # Validate fields
            if not grade.course_code:
                errors.append(f"Grade {i+1}: Course code is required")
            if not grade.course_name:
                errors.append(f"Grade {i+1}: Course name is required")
            if not (1 <= grade.ects <= 12):
                errors.append(
                    f"Grade {i+1}: Invalid ECTS {grade.ects} (must be 1-12)"
                )
            if grade.letter_grade not in GPACalculator.GRADE_SCALE:
                errors.append(
                    f"Grade {i+1}: Invalid grade '{grade.letter_grade}'"
                )
            if not grade.semester:
                errors.append(f"Grade {i+1}: Semester is required")
        
        return errors
    
    @staticmethod
    def show_validation_errors(errors: List[str], parent=None):
        """Show validation errors in a dialog."""
        if not errors:
            return
        
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Validation Errors")
        msg.setText(f"Found {len(errors)} validation error(s):")
        msg.setDetailedText("\n".join(f"• {e}" for e in errors))
        msg.exec()
```

**Use in save:**
```python
def _save_to_database(self):
    transcript = self._get_transcript()
    
    # Validate before saving
    errors = TranscriptValidator.validate_transcript(transcript)
    if errors:
        TranscriptValidator.show_validation_errors(errors, self)
        return
    
    # Save
    db = Database()
    db.save_transcript(transcript)
    QMessageBox.information(self, "Success", "Transcript saved!")
```

---

### 5. Export Functionality (1 saat) 🔴

#### 5.1 Export to Excel
**Tahmini Süre:** 45 dakika

**Implementation:**
```python
def _export_to_excel(self):
    """Export current transcript to Excel."""
    transcript = self._get_transcript()
    
    if not transcript.grades:
        QMessageBox.warning(self, "No Data", "Transcript is empty!")
        return
    
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Export Transcript", "", "Excel Files (*.xlsx)"
    )
    
    if not file_path:
        return
    
    # Create DataFrame
    data = [{
        'Course Code': g.course_code,
        'Course Name': g.course_name,
        'ECTS': g.ects,
        'Letter Grade': g.letter_grade,
        'Numeric Grade': g.numeric_grade,
        'Semester': g.semester
    } for g in transcript.grades]
    
    df = pd.DataFrame(data)
    
    # Add summary row
    summary = {
        'Course Code': 'SUMMARY',
        'Course Name': f'Student: {transcript.student_name} ({transcript.student_id})',
        'ECTS': transcript.get_total_ects(),
        'Letter Grade': f'GPA: {transcript.get_gpa():.2f}',
        'Numeric Grade': '',
        'Semester': transcript.program
    }
    df = pd.concat([df, pd.DataFrame([summary])], ignore_index=True)
    
    # Save
    df.to_excel(file_path, index=False)
    
    QMessageBox.information(
        self, "Success",
        f"Transcript exported to {file_path}!"
    )
```

---

#### 5.2 Export to PDF (Optional)
**Tahmini Süre:** 15 dakika

**Simple PDF export:**
```python
def _export_to_pdf(self):
    """Export transcript to PDF."""
    # Use existing PDF export from reporting module
    # Similar to schedule export, but for transcript table
    pass
```

---

### 6. Testing (1 saat) 🔴

#### 6.1 Unit Tests
**Dosya:** `tests/test_transcript_import.py`  
**Tahmini Süre:** 1 saat

**Test cases:**
```python
import pytest
from core.transcript_parser import TranscriptParser
from core.models import Transcript, Grade
from gui.dialogs.add_grade_dialog import AddGradeDialog

def test_parse_valid_excel():
    """Test parsing valid Excel file."""
    student_info, grades = TranscriptParser.parse_excel("test_transcript.xlsx")
    assert len(grades) > 0
    assert student_info['id'] != ''

def test_parse_invalid_excel():
    """Test parsing invalid Excel file."""
    with pytest.raises(Exception):
        TranscriptParser.parse_excel("invalid.xlsx")

def test_column_detection():
    """Test auto-detect column names."""
    # Turkish columns
    # English columns
    # Mixed columns

def test_validation():
    """Test grade validation."""
    # Valid grades
    # Invalid letter grade
    # Invalid ECTS
    # Duplicate courses

def test_database_save_load():
    """Test database persistence."""
    # Save transcript
    # Load transcript
    # Verify grades match

def test_add_grade_dialog():
    """Test manual grade entry dialog."""
    # Create dialog
    # Fill form
    # Get grade object
    # Verify fields
```

---

## 📊 İlerleme Takibi

### Task Checklist
- [ ] 1.1 Create TranscriptImportWidget (1.5h)
- [ ] 1.2 Excel Parser Implementation (1.5h)
- [ ] 1.3 UI Integration (1h)
- [ ] 2.1 Create AddGradeDialog (1.5h)
- [ ] 2.2 Integrate Manual Entry (0.5h)
- [ ] 3.1 Extend Database Class (1.5h)
- [ ] 3.2 Auto-save and Load (0.5h)
- [ ] 4.1 Validation Logic (1h)
- [ ] 5.1 Export to Excel (0.75h)
- [ ] 5.2 Export to PDF (0.25h - optional)
- [ ] 6.1 Unit Tests (1h)

**Total:** 10 saat (1-2 gün)

### Daily Plan

**Day 1 (5 saat):**
1. Create TranscriptImportWidget (1.5h)
2. Excel Parser Implementation (1.5h)
3. UI Integration (1h)
4. Create AddGradeDialog (1h)

**Day 2 (5 saat):**
1. Integrate Manual Entry (0.5h)
2. Extend Database (1.5h)
3. Auto-save/Load (0.5h)
4. Validation (1h)
5. Export (1h)
6. Testing (0.5h)

---

## ✅ Definition of Done

Phase 7.5 is complete when:
- ✅ Users can import transcript from Excel
- ✅ Users can add/edit/delete grades manually
- ✅ Transcript persists in database
- ✅ Auto-load on app startup
- ✅ Data validation works (duplicates, invalid grades)
- ✅ Export to Excel works
- ✅ All unit tests pass
- ✅ No critical bugs
- ✅ Academic Tab fully functional

---

## 🚀 Başlayalım!

**Şimdi ne yapmalı?**

1. **Excel import'a başla** (1.1, 1.2, 1.3) - 4 saat
2. **Manual entry ekle** (2.1, 2.2) - 2 saat
3. **Database kaydet** (3.1, 3.2) - 2 saat
4. **Validation + Export** (4.1, 5.1) - 2 saat

**Toplam:** 10 saat → Phase 7.5 Complete! ✅

