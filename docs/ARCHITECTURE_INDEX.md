# SchedularV3 - Architecture Documentation

**Proje:** SchedularV3 - Advanced Course Scheduling System  
**Versiyon:** 3.0.0  
**Tarih:** 26 Kasım 2025  
**Durum:** Phase 7-8 (85% Complete)

---

## 📋 İçindekiler

1. [Genel Mimari](#1-genel-mimari)
2. [Sınıf Diyagramları](#2-sınıf-diyagramları)
3. [Algoritma Mimarisi](#3-algoritma-mimarisi)
4. [GUI Mimarisi](#4-gui-mimarisi)
5. [Veri Akışı](#5-veri-akışı)
6. [Veritabanı Şeması](#6-veritabanı-şeması)
7. [Sekans Diyagramları](#7-sekans-diyagramları)
8. [Durum Diyagramları](#8-durum-diyagramları)
9. [Deployment](#9-deployment)
10. [Paket Bağımlılıkları](#10-paket-bağımlılıkları)
11. [Use Case](#11-use-case)
12. [Activity Diyagramları](#12-activity-diyagramları)
13. **[📊 Kapsamlı Mimari Rapor](#13-kapsamlı-mimari-rapor)** ⭐ NEW

---

## 1. Genel Mimari

### Dosya: `ARCHITECTURE.puml`

**Açıklama:** Sistemin genel katmanlı mimarisi

**Katmanlar:**
- **Presentation Layer (GUI):** PyQt6 tabanlı 5 ana sekme
- **Application Layer:** Entry point, configuration, logging
- **Business Logic Layer:** 
  - Scheduling Algorithms (15+ algoritma)
  - Academic System (Prerequisites, GPA, Graduation)
  - Constraints & Evaluation
- **Data Layer:**
  - Core Models (Course, Schedule, Program, Transcript, Grade)
  - Data Access (Excel Loader, Database, Transcript Parser)
- **Reporting Layer:** PDF, Excel, JPEG exporters
- **Utilities:** Error handling, performance monitoring

**Dış Kaynaklar:**
- SQLite Database (course_scheduler.db)
- Excel Files (.xlsx, .csv)
- Log Files

**Teknolojiler:**
- PyQt6 6.6.1+
- pandas, numpy, openpyxl
- reportlab, matplotlib, Pillow
- pytest

---

## 2. Sınıf Diyagramları

### Dosya: `CLASS_DIAGRAM.puml`

**Açıklama:** Core models detaylı sınıf yapısı

**Ana Sınıflar:**

#### Course
```python
- code: str
- main_code: str
- name: str
- ects: int
- course_type: CourseType
- schedule: List[TimeSlot]
- teacher: Optional[str]
- prerequisites: List[str]
- corequisites: List[str]
```

**Metodlar:**
- `conflicts_with(other: Course): bool`
- `get_conflict_slots(other: Course): Set[TimeSlot]`
- `from_dict(data: Dict): Course`

#### Schedule
```python
- courses: List[Course]
- total_credits: int (property)
- conflict_count: int (property)
```

**Metodlar:**
- `add_course(course: Course)`
- `has_conflict_with(courses: List[Course]): bool`

#### Transcript
```python
- student_id: str
- student_name: str
- program: str
- grades: List[Grade]
- gpa: float (property)
```

**Metodlar:**
- `get_gpa(): float`
- `get_ects_limit(): int`
- `get_completed_courses(): List[str]`

**ECTS Limits (Işık University):**
- GPA >= 3.5: 42 ECTS
- GPA >= 2.5: 37 ECTS
- GPA < 2.5: 31 ECTS

---

## 3. Algoritma Mimarisi

### Dosya: `ALGORITHM_DIAGRAM.puml`

**Açıklama:** 15+ scheduling algoritmasının mimarisi

**Abstract Base Class:**
```python
BaseScheduler
├── metadata: AlgorithmMetadata
├── max_results: int
├── max_ects: int
├── allow_conflicts: bool
└── scheduler_prefs: SchedulerPrefs
```

**Search Algorithms:**
1. **DFSScheduler** - Depth-First Search (Backtracking)
2. **BFSScheduler** - Breadth-First Search
3. **AStarScheduler** - A* with heuristic
4. **DijkstraScheduler** - Shortest path
5. **IDDFSScheduler** - Iterative Deepening DFS

**Optimization Algorithms:**
6. **GreedyScheduler** - Greedy selection
7. **GeneticAlgorithmScheduler** - Population-based evolution
8. **SimulatedAnnealingScheduler** - Temperature-based optimization
9. **HillClimbingScheduler** - Local search
10. **TabuSearchScheduler** - Tabu list avoidance
11. **ParticleSwarmScheduler** - Swarm intelligence
12. **HybridGASAScheduler** - GA + SA combination
13. **ConstraintProgrammingScheduler** - CP-SAT solver

**Ortak Özellikler:**
- Performance tracking (`@track_performance` decorator)
- Constraint validation
- Preference scoring
- Smart filtering (GPA-based ECTS, prerequisites)

---

## 4. GUI Mimarisi

### Dosya: `GUI_DIAGRAM.puml`

**Açıklama:** PyQt6 tabanlı GUI component yapısı

**Ana Pencere:**
```
MainWindow
├── MenuBar (File, Edit, View, Help)
├── ToolBar (Quick actions)
├── StatusBar (Status messages)
└── QTabWidget (5 tabs)
    ├── 📁 File & Settings Tab
    ├── 📚 Course Browser Tab
    ├── ✅ Course Selector Tab
    ├── 📊 Schedule Viewer Tab
    └── 🎓 Academic Tab
```

**Tab Details:**

1. **File Settings Tab:**
   - File browser
   - Algorithm selector widget
   - Parameters panel
   - Generate button
   - Progress bar

2. **Course Browser Tab:**
   - Advanced filters (Faculty, Department, Campus, Type, Teacher)
   - Quick filters (Search, Sort)
   - Course table view
   - Delete actions
   - Performance: Debouncing (300ms), Batch updates

3. **Course Selector Tab:**
   - Tri-state checkboxes
   - Visual indicators: ✅ (Mandatory), ❌ (Optional), ⬜ (Excluded)
   - Color coding: Green, Orange, Gray
   - Real-time sync with Browser

4. **Schedule Viewer Tab:**
   - Program list
   - Weekly grid (M-F, 14 periods)
   - Conflict highlighting (RED)
   - Course details panel
   - Export buttons

5. **Academic Tab:**
   - Prerequisites Viewer
   - GPA Calculator
   - Graduation Planner
   - Transcript Import

**Custom Widgets:**
- `AlgorithmSelectorWidget`
- `ScheduleGridWidget`
- `CourseCardWidget`
- `ProgressDialogWidget`
- `GraduationPlannerWidget`

**Dialogs:**
- `AlgorithmComparisonDialog`
- `AddGradeDialog`
- `TranscriptImportDialog`

---

## 5. Veri Akışı

### Dosya: `DATA_FLOW_DIAGRAM.puml`

**Açıklama:** Sistemdeki veri akış sırası

**Ana Akışlar:**

1. **Course Data Loading:**
   ```
   User → MainWindow → FileSettingsTab → ExcelLoader
   → Parse → Create Course objects → Database → UI Update
   ```

2. **Course Selection:**
   ```
   User → CourseSelectorTab → Update tri-state
   → Signal → MainWindow → State management
   ```

3. **Schedule Generation:**
   ```
   User → Generate → AlgorithmSelector → BaseScheduler
   → prepare_search_space() → _run_algorithm()
   → validate → sort → ScheduleViewerTab
   ```

4. **Export:**
   ```
   User → Export → ReportExporter → Generate PDF/Excel/JPEG
   → File System → User download
   ```

---

## 6. Veritabanı Şeması

### Dosya: `DATABASE_SCHEMA.puml`

**Açıklama:** SQLite veritabanı tabloları

**Tablolar:**

1. **courses**
   ```sql
   - id: INTEGER PRIMARY KEY
   - code: TEXT UNIQUE
   - main_code: TEXT
   - name: TEXT
   - ects: INTEGER
   - course_type: TEXT
   - schedule: TEXT (JSON)
   - teacher: TEXT
   - faculty: TEXT
   - department: TEXT
   - campus: TEXT
   ```

2. **schedules**
   ```sql
   - id: INTEGER PRIMARY KEY
   - name: TEXT
   - total_credits: INTEGER
   - conflict_count: INTEGER
   - courses: TEXT (JSON array of codes)
   ```

3. **programs**
   ```sql
   - id: INTEGER PRIMARY KEY
   - name: TEXT
   - metadata: TEXT (JSON)
   ```

4. **program_schedules** (many-to-many)
   ```sql
   - program_id: INTEGER FK
   - schedule_id: INTEGER FK
   ```

5. **transcripts**
   ```sql
   - id: INTEGER PRIMARY KEY
   - student_id: TEXT UNIQUE
   - student_name: TEXT
   - program: TEXT
   ```

6. **grades**
   ```sql
   - id: INTEGER PRIMARY KEY
   - transcript_id: INTEGER FK
   - course_code: TEXT
   - letter_grade: TEXT
   - numeric_grade: REAL
   - ects: INTEGER
   - semester: TEXT
   ```

**Indexes:**
- `idx_courses_main_code`
- `idx_courses_code`
- `idx_schedules_name`

---

## 7. Sekans Diyagramları

### Dosya: `SEQUENCE_GENERATE.puml`

**Açıklama:** Schedule generation detaylı sekans

**Participants:**
- User
- FileSettingsTab
- AlgorithmSelector
- DFSScheduler
- ConstraintUtils
- Course
- Schedule
- ScheduleViewerTab

**Ana Akış:**

1. User clicks "Generate Schedules"
2. Validate inputs
3. Select best algorithm
4. Initialize scheduler
5. Prepare search space
   - Build group options
   - Filter by constraints
6. Run DFS recursion
   - Try combinations
   - Validate ECTS limit
   - Check conflicts
   - Prune branches
7. Finalize results
   - Sort by preferences
   - Limit to max_results
8. Display in ScheduleViewerTab

**Performance Tracking:**
- nodes_explored
- branches_pruned
- execution_time

---

## 8. Durum Diyagramları

### Dosya: `STATE_DIAGRAM.puml`

**Açıklama:** Uygulama durumları

**Ana Durumlar:**

```
[*] → NotInitialized
NotInitialized → Initializing → Ready
Ready → {
    NoFileLoaded → FileLoading → FileLoaded
    FileLoaded → CourseSelecting → CourseSelected
    CourseSelected → AlgorithmConfiguring → ReadyToGenerate
    ReadyToGenerate → Generating → SchedulesGenerated
    SchedulesGenerated → ViewingSchedules → Exporting
}
Ready → Exiting → [*]
```

---

## 9. Deployment

### Dosya: `DEPLOYMENT_DIAGRAM.puml`

**Açıklama:** Deployment mimarisi

**Platform:** Windows / macOS / Linux

**Components:**
- SchedularV3 Application (PyQt6 GUI + Business Logic)
- Python 3.11+ Runtime (Virtual Environment)
- SQLite Database (course_scheduler.db)
- File System (Excel, CSV, PDF, JPEG, Logs)

**External Dependencies:**
- PyQt6 6.6.1+
- pandas 2.1.0+
- numpy 1.24.0+
- openpyxl 3.1.0+
- reportlab 4.0.0+
- matplotlib 3.7.0+
- Pillow 10.0.0+
- pytest 7.4.0+

**Özellikler:**
- Standalone desktop application
- No internet required
- Fully offline
- Self-contained

---

## 10. Paket Bağımlılıkları

### Dosya: `PACKAGE_DIAGRAM.puml`

**Açıklama:** Python paketleri arası bağımlılıklar

**Paket Hiyerarşisi:**

```
SchedularV3/
├── main.py
├── config/
│   └── settings.py
├── core/
│   ├── models.py
│   ├── database.py
│   ├── excel_loader.py
│   ├── academic.py
│   └── transcript_parser.py
├── algorithms/
│   ├── base_scheduler.py
│   ├── [15+ algorithm implementations]
│   ├── constraints.py
│   └── evaluator.py
├── gui/
│   ├── main_window.py
│   ├── tabs/
│   ├── widgets/
│   └── dialogs/
├── reporting/
│   ├── pdf.py
│   ├── excel.py
│   ├── jpeg.py
│   └── charts.py
├── utils/
│   ├── error_handler.py
│   ├── performance.py
│   └── schedule_metrics.py
└── tests/
    └── test_*.py
```

**Bağımlılık Yönü:**
```
main.py → config, gui, utils
gui → core, algorithms, reporting, utils
algorithms → core, utils
reporting → core, utils
core → config
tests → core, algorithms, gui
```

---

## 11. Use Case

### Dosya: `USE_CASE_DIAGRAM.puml`

**Açıklama:** Sistem kullanım senaryoları

**Actors:**
1. **Student** (Primary user)
2. **Academic Advisor**
3. **Administrator**

**Main Use Cases:**

**Student:**
- Load Course Data
- Browse & Filter Courses
- Select Mandatory/Optional Courses
- Generate Schedules
- View Schedules & Check Conflicts
- Calculate GPA & Simulate Grades
- Check Prerequisites
- Check Graduation Progress
- Export Schedules

**Academic Advisor:**
- All student features
- Benchmark Algorithms
- Compare Multiple Schedules

**Administrator:**
- System Configuration
- Data Management
- View Logs
- Algorithm Benchmarking

---

## 12. Activity Diyagramları

### Dosya: `ACTIVITY_DIAGRAM.puml`

**Açıklama:** Schedule generation activity flow

**Ana Aktiviteler:**

1. **Load Excel File**
   - Parse data
   - Create Course objects
   - Save to database

2. **Select Courses**
   - Browse courses
   - Tri-state selection (Mandatory/Optional/Excluded)

3. **Configure Algorithm**
   - Select algorithm
   - Set parameters (max_results, max_ects, timeout)
   - Set preferences (free days, time slots, campus)

4. **Generate Schedules**
   - Prepare search space
   - Initialize algorithm
   - Run generation loop
   - Validate & prune branches
   - Sort results

5. **View & Export**
   - Display weekly grid
   - Highlight conflicts
   - Export to PDF/Excel/JPEG

---

## 13. Kapsamlı Mimari Rapor

### Dosya: `ARCHITECTURE_COMPLETE_REPORT.md`

**Açıklama:** Tüm mimari dokümantasyonun birleştirilmiş kapsamlı raporu

**İçerik:**
- ✅ Executive Summary
- ✅ Tüm PlantUML diyagramlarının detaylı açıklamaları
- ✅ Kod örnekleri ve implementation details
- ✅ Performans metrikleri
- ✅ Işık University branding
- ✅ Data security & privacy
- ✅ Future enhancements roadmap
- ✅ Complete documentation index

**Kullanım:**
```bash
# PDF'e dönüştürmek için
pandoc ARCHITECTURE_COMPLETE_REPORT.md -o SchedularV3_Architecture.pdf

# HTML'e dönüştürmek için
pandoc ARCHITECTURE_COMPLETE_REPORT.md -o index.html --standalone --toc
```

**Bölümler:**
1. Executive Summary
2. Architecture Overview (Layered diagram)
3. Core Components (Class diagrams with code)
4. Algorithm Architecture (All 15+ algorithms)
5. GUI Architecture (PyQt6 components)
6. Data Flow (Complete flow examples)
7. Database Schema (SQLite tables)
8. Sequence Diagrams (Generation flow)
9. State Diagram (Application states)
10. Deployment (Platform requirements)
11. Use Cases (All actors & scenarios)
12. Activity Diagram (Step-by-step flow)
13. Metrics & Statistics
14. Işık University Branding
15. Future Enhancements

---

## 🎯 Diagram Usage Guide

### PlantUML Rendering

**Online:**
- PlantUML Web Server: http://www.plantuml.com/plantuml/
- Copy-paste `.puml` file content
- Get PNG/SVG output

**Local (Recommended):**
```bash
# Install PlantUML
brew install plantuml  # macOS
apt-get install plantuml  # Linux
choco install plantuml  # Windows

# Generate all diagrams
cd docs/
plantuml *.puml

# Output: PNG files in same directory
```

**VS Code Extension:**
- Install: "PlantUML" by jebbs
- Preview: Alt+D (Windows/Linux) or Option+D (macOS)
- Export: Right-click → Export diagrams

### Markdown Integration

```markdown
<!-- Embed in README.md -->
![Architecture](docs/ARCHITECTURE.png)
![Class Diagram](docs/CLASS_DIAGRAM.png)
![Algorithm Diagram](docs/ALGORITHM_DIAGRAM.png)
```

---

## 📊 Documentation Coverage

### Completed Documentation
- ✅ **PlantUML Diagrams:** 12/12 diagrams complete
- ✅ **Markdown Guides:** 5/5 complete
- ✅ **Code Documentation:** 80% coverage
- ✅ **Test Documentation:** 65% coverage

### Documentation Files Count
- **PlantUML Files:** 12
- **Markdown Guides:** 5 (USER_GUIDE, PHASE_02, PHASE_07, PHASE_7.5, ISIK_DATA)
- **Architecture Docs:** 2 (ARCHITECTURE_INDEX, ARCHITECTURE_COMPLETE_REPORT)
- **Total:** 19 documentation files

---

## 🔗 Cross-References

### User Guides ↔ Architecture
- **USER_GUIDE.md** → Refers to CLASS_DIAGRAM.puml for data models
- **PHASE_07_ACADEMIC_SYSTEM.md** → Uses SEQUENCE_GENERATE.puml
- **PHASE_7.5_USAGE_GUIDE.md** → References DATABASE_SCHEMA.puml

### Architecture ↔ Code
- **CLASS_DIAGRAM.puml** → Matches `core/models.py`
- **ALGORITHM_DIAGRAM.puml** → Matches `algorithms/` package
- **GUI_DIAGRAM.puml** → Matches `gui/` package

---

## 🔧 Teknik Detaylar

### Design Patterns
- **Abstract Factory:** BaseScheduler + concrete implementations
- **Strategy:** Algorithm selection & execution
- **Observer:** PyQt6 signals & slots
- **Singleton:** Database connection
- **Decorator:** `@track_performance` for monitoring

### Architecture Principles
- **Layered Architecture:** Clear separation of concerns
- **Dependency Injection:** Configurable components
- **Single Responsibility:** Each class has one job
- **Open/Closed:** Extensible without modification
- **Interface Segregation:** Minimal interfaces

### Data Flow Patterns
- **MVC-like:** Model (core), View (gui), Controller (algorithms)
- **Repository:** Database abstraction
- **DTO:** Course, Schedule as data transfer objects

---

## 📝 Notlar

### Işık University Specifics
- **Time Format:** "M1, M2, T3, Th5" → TimeSlot tuples
- **Course Types:** lecture, ps (problem session), lab
- **ECTS Limits:** GPA-based (31/37/42)
- **Grade Scale:** AA(4.0) → FF(0.0)

### Performance Optimizations
- **Debouncing:** 300ms for quick filters
- **Batch Updates:** Table rendering optimization
- **Branch Pruning:** Early termination in DFS
- **Lazy Loading:** On-demand course data

### Planned Features (Phase 9-10)
- Advanced PDF reports
- Custom export templates
- Analytics dashboard
- Heatmap visualizations
- Machine learning predictions

---

## 📚 Referanslar

- **PlantUML Documentation:** https://plantuml.com
- **PyQt6 Documentation:** https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **Project Repository:** GitHub - SchedularV3
- **Işık University Regulations:** Official Academic Calendar

---

**Son Güncelleme:** 26 Kasım 2025  
**Güncelleyen:** GitHub Copilot  
**Durum:** ✅ Architecture Complete (All UML diagrams generated)
