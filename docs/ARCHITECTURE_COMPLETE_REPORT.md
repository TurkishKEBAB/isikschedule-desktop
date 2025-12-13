# SchedularV3 - Complete Architecture Report

**Proje:** SchedularV3 - Advanced Course Scheduling System  
**Versiyon:** 3.0.0  
**Rapor Tarihi:** 26 Kasım 2025  
**Durum:** Phase 7-8 Complete (85%)  
**Rapor Türü:** Comprehensive System Architecture

---

## 📋 Executive Summary

SchedularV3, Işık Üniversitesi öğrencileri için geliştirilmiş modern bir ders çizelgeleme sistemidir. 15+ farklı algoritma, akademik takip sistemi, ve kapsamlı raporlama özellikleri sunar.

### Temel İstatistikler
- **Toplam Kod:** ~8,000+ satır
- **Python Dosyaları:** 60+ adet
- **Test Kapsamı:** 65%
- **Test Başarısı:** 100% (33/33)
- **Algoritma Sayısı:** 15+
- **GUI Sekmeleri:** 5 ana sekme
- **Veritabanı Tabloları:** 6 tablo
- **Desteklenen Formatlar:** Excel, PDF, JPEG

---

## 📊 Architecture Overview

### Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Presentation Layer (GUI - PyQt6)              │
│  File Settings | Browser | Selector | Viewer | Academic│
├─────────────────────────────────────────────────────────┤
│              Application Layer                          │
│     main.py | config | logging | error handling        │
├─────────────────────────────────────────────────────────┤
│              Business Logic Layer                       │
│  ┌─────────────┬──────────────┬────────────────────┐   │
│  │ Algorithms  │  Academic    │  Constraints &     │   │
│  │ (15+ types) │  System      │  Evaluation        │   │
│  └─────────────┴──────────────┴────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│                Data Layer                               │
│  ┌─────────────────┬─────────────────────────────┐     │
│  │  Core Models    │    Data Access              │     │
│  │  Course,Schedule│  Excel,DB,Parser            │     │
│  └─────────────────┴─────────────────────────────┘     │
├─────────────────────────────────────────────────────────┤
│           Reporting Layer                               │
│        PDF Exporter | Excel Exporter | JPEG            │
├─────────────────────────────────────────────────────────┤
│              Utilities Layer                            │
│    Error Handler | Performance | Schedule Metrics      │
└─────────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────────────────────────┐
        │     External Resources            │
        │  SQLite DB | Excel Files | Logs   │
        └───────────────────────────────────┘
```

**Diagram Reference:** `ARCHITECTURE.puml`

---

## 🎯 Core Components

### 1. Data Models (`CLASS_DIAGRAM.puml`)

#### Course Model
```python
@dataclass
class Course:
    code: str                    # COMP1111.1
    main_code: str               # COMP1111
    name: str                    # Programming Fundamentals
    ects: int                    # 6
    course_type: CourseType      # lecture/ps/lab
    schedule: List[TimeSlot]     # [("Monday", 1), ("Monday", 2)]
    teacher: Optional[str]       # Tuğba Erkoç
    has_lecture: bool            # True
    faculty: str                 # Engineering
    department: str              # Computer Engineering
    campus: str                  # Şile
    prerequisites: List[str]     # ["COMP1007"]
    corequisites: List[str]      # []
    
    # Methods
    def conflicts_with(other: Course) -> bool
    def get_conflict_slots(other: Course) -> Set[TimeSlot]
```

**Key Features:**
- Işık University Excel format support
- Turkish character handling (UTF-8)
- Time slot tuple format: `(day_name: str, period: int)`
- Conflict detection with set operations
- Hashable for efficient lookups

#### Schedule Model
```python
@dataclass
class Schedule:
    courses: List[Course]
    
    @property
    def total_credits(self) -> int
    
    @property
    def conflict_count(self) -> int
    
    @property
    def has_conflicts(self) -> bool
    
    # Methods
    def add_course(course: Course) -> None
    def has_conflict_with(courses: List[Course]) -> bool
    def get_course_codes() -> Set[str]
```

#### Academic Models
```python
@dataclass
class Grade:
    course_code: str
    course_name: str
    ects: int
    letter_grade: str        # AA, BA, BB, ..., FF
    numeric_grade: float     # 0.0-4.0
    semester: str
    
    def is_passing() -> bool  # >= 2.0 (CC)

@dataclass
class Transcript:
    student_id: str
    student_name: str
    program: str
    grades: List[Grade]
    
    @property
    def gpa(self) -> float
    
    @property
    def total_ects_earned(self) -> int
    
    def get_ects_limit() -> int  # GPA-based: 31/37/42
```

**ECTS Limits (Işık University):**
```python
if gpa >= 3.5:
    return 42  # High achievers
elif gpa >= 2.5:
    return 37  # Average
else:
    return 31  # Minimum
```

---

### 2. Algorithm Architecture (`ALGORITHM_DIAGRAM.puml`)

#### Base Scheduler Abstract Class

```python
class BaseScheduler(ABC):
    # Configuration
    metadata: AlgorithmMetadata
    max_results: int             # 1-100
    max_ects: int                # 25-45
    allow_conflicts: bool        # True/False
    max_conflicts: int           # 0-10
    timeout_seconds: int         # 30-300
    scheduler_prefs: SchedulerPrefs
    
    # Smart Features
    transcript: Optional[Transcript]
    enable_smart_filtering: bool
    
    # Abstract method
    @abstractmethod
    def _run_algorithm(search: PreparedSearch) -> List[Schedule]
    
    # Template method
    def generate_schedules(groups, mandatory, optional) -> List[Schedule]:
        1. Prepare search space
        2. Run algorithm (_run_algorithm)
        3. Finalize results (sort, limit, validate)
        4. Return schedules
    
    # Performance tracking
    @track_performance
    def _run_algorithm(...)
    
    # Smart filtering
    def filter_courses_by_prerequisites(courses) -> List[Course]
    def adjust_max_ects_by_gpa() -> int
```

#### Algorithm Categories

**Search Algorithms (Optimal):**
1. **DFSScheduler** - Depth-First Search
   - Complexity: O(b^d) where b=branching, d=depth
   - Optimal: No (finds first solution)
   - Best for: Small-medium problems

2. **BFSScheduler** - Breadth-First Search
   - Complexity: O(b^d)
   - Optimal: Yes (shortest path)
   - Best for: Finding optimal solutions

3. **AStarScheduler** - A* Search
   - Complexity: O(b^d) with good heuristic
   - Optimal: Yes (with admissible heuristic)
   - Best for: General-purpose optimization

4. **DijkstraScheduler** - Dijkstra's Algorithm
   - Complexity: O(V^2) or O(E log V) with heap
   - Optimal: Yes (shortest path)
   - Best for: Weighted graph problems

5. **IDDFSScheduler** - Iterative Deepening DFS
   - Complexity: O(b^d)
   - Optimal: Yes (like BFS)
   - Best for: Memory-limited environments

**Optimization Algorithms:**
6. **GreedyScheduler** - Greedy Selection
   - Complexity: O(n log n)
   - Optimal: No (local optimum)
   - Best for: Fast approximations

7. **GeneticAlgorithmScheduler**
   - Population-based evolution
   - Crossover, mutation, selection
   - Best for: Large search spaces

8. **SimulatedAnnealingScheduler**
   - Temperature-based optimization
   - Accepts worse solutions probabilistically
   - Best for: Avoiding local optima

9. **HillClimbingScheduler**
   - Local search optimization
   - Always moves to better neighbor
   - Best for: Quick local optimization

10. **TabuSearchScheduler**
    - Tabu list prevents cycling
    - Explores neighborhood systematically
    - Best for: Escaping local optima

11. **ParticleSwarmScheduler**
    - Swarm intelligence
    - Particles explore search space
    - Best for: Continuous optimization

12. **HybridGASAScheduler**
    - Combines GA + SA
    - GA for global, SA for local
    - Best for: Complex problems

13. **ConstraintProgrammingScheduler**
    - CP-SAT solver (Google OR-Tools)
    - Constraint satisfaction
    - Best for: Hard constraints

#### Algorithm Selection Logic

```python
class AlgorithmSelector:
    @staticmethod
    def select_scheduler(requirements: Dict) -> Type[BaseScheduler]:
        """
        Score all registered algorithms based on requirements.
        
        Scoring factors:
        - Problem size (course count, group count)
        - Constraint count
        - Time limit
        - Need for optimality
        - Preference support needed
        """
        scores = {}
        
        for name, scheduler_class in REGISTERED_SCHEDULERS.items():
            score = 0
            meta = scheduler_class.metadata
            
            # Size scoring
            if requirements['course_count'] < 50:
                if meta.name in ['DFS', 'BFS', 'A*']:
                    score += 30
            else:
                if meta.name in ['Genetic', 'Simulated Annealing']:
                    score += 30
            
            # Optimality
            if requirements['need_optimal'] and meta.optimal:
                score += 20
            
            # Preferences
            if requirements['has_preferences'] and meta.supports_preferences:
                score += 15
            
            scores[name] = score
        
        return max(scores, key=scores.get)
```

---

### 3. GUI Architecture (`GUI_DIAGRAM.puml`)

#### Main Window Structure

```python
class MainWindow(QMainWindow):
    def __init__(self):
        self.setWindowTitle("SchedularV3")
        self.resize(1400, 900)
        
        # Main components
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Create tabs
        self.file_settings_tab = FileSettingsTab()
        self.course_browser_tab = CourseBrowserTab()
        self.course_selector_tab = CourseSelectorTab()
        self.schedule_viewer_tab = ScheduleViewerTab()
        self.academic_tab = AcademicTab()
        
        # Add tabs
        self.tab_widget.addTab(self.file_settings_tab, "📁 File & Settings")
        self.tab_widget.addTab(self.course_browser_tab, "📚 Course Browser")
        self.tab_widget.addTab(self.course_selector_tab, "✅ Course Selector")
        self.tab_widget.addTab(self.schedule_viewer_tab, "📊 Schedule Viewer")
        self.tab_widget.addTab(self.academic_tab, "🎓 Academic")
        
        # Setup signals
        self._setup_signals()
```

#### Tab Details

**1. File Settings Tab**
```python
class FileSettingsTab(QWidget):
    # Components
    - file_browser: QFileDialog
    - algorithm_selector: AlgorithmSelectorWidget
    - parameter_panel: QGroupBox
      - max_results: QSpinBox (1-100)
      - max_ects: QSpinBox (25-45)
      - allow_conflicts: QCheckBox
      - timeout: QSpinBox (30-300s)
    - preferences_panel: QGroupBox
      - free_days: QListWidget
      - time_slots: QListWidget
      - campus_pref: QComboBox
    - generate_btn: QPushButton
    - progress_bar: QProgressBar
    
    # Signals
    file_selected = pyqtSignal(str)
    algorithm_configured = pyqtSignal(dict)
    generation_started = pyqtSignal()
    generation_finished = pyqtSignal(list)
```

**2. Course Browser Tab**
```python
class CourseBrowserTab(QWidget):
    # Advanced filtering
    - faculty_filter: QComboBox
    - department_filter: QComboBox
    - campus_filter: QComboBox
    - type_filter: QComboBox
    - teacher_filter: QComboBox
    - search_box: QLineEdit (debounced 300ms)
    
    # Table view
    - course_table: QTableWidget
      Columns: Code | Name | ECTS | Type | Teacher | Schedule | Campus
    
    # Actions
    - delete_btn: QPushButton (with confirmation)
    - refresh_btn: QPushButton
    
    # Performance optimizations
    - Debouncing (300ms for search)
    - Batch updates (setUpdatesEnabled)
    - Smart group deletion
```

**3. Course Selector Tab**
```python
class CourseSelectorTab(QWidget):
    # Tri-state selection system
    - course_tree: QTreeWidget
      Group Level (main_code)
      └─ Course Level (code.section)
    
    # States
    MANDATORY = 0  # ✅ Green
    OPTIONAL = 1   # ❌ Orange
    EXCLUDED = 2   # ⬜ Gray
    
    # Click cycle
    def on_item_clicked(item, column):
        current_state = item.checkState(column)
        next_state = (current_state + 1) % 3
        item.setCheckState(column, next_state)
        update_color(item, next_state)
    
    # Real-time sync
    courses_updated = pyqtSignal(list)
```

**4. Schedule Viewer Tab**
```python
class ScheduleViewerTab(QWidget):
    # Program list
    - program_combo: QComboBox
    - conflict_label: QLabel
    - ects_label: QLabel
    
    # Weekly grid
    - schedule_grid: ScheduleGridWidget
      Days: Monday-Friday
      Periods: 1-14 (08:30-21:30)
    
    # Course details
    - details_panel: QTextEdit
      - Course info
      - Teacher
      - Schedule
      - Prerequisites
    
    # Export buttons
    - export_pdf_btn: QPushButton
    - export_excel_btn: QPushButton
    - export_jpeg_btn: QPushButton
```

**5. Academic Tab**
```python
class AcademicTab(QWidget):
    # Sub-tabs
    - prerequisites_viewer: PrerequisiteViewer
    - gpa_calculator: GPACalculatorWidget
    - graduation_planner: GraduationPlannerWidget
    - transcript_import: TranscriptImportWidget
```

#### Custom Widgets

**ScheduleGridWidget**
```python
class ScheduleGridWidget(QWidget):
    # Grid structure
    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    PERIODS = range(1, 15)  # 14 periods
    
    # Cell rendering
    def paint_course_cell(course: Course, time_slot: TimeSlot):
        color = SCHEDULE_COLORS[course_index % len(SCHEDULE_COLORS)]
        if has_conflict(course, time_slot):
            color = QColor(255, 100, 100)  # Red
        
        draw_cell(color, course.code, course.name)
    
    # Click handling
    def on_cell_clicked(day: str, period: int):
        courses = get_courses_at(day, period)
        emit course_details_requested(courses)
```

---

### 4. Data Flow (`DATA_FLOW_DIAGRAM.puml`)

#### Complete Flow Example

```
┌─────────────────────────────────────────────────────┐
│ 1. Course Data Loading                              │
├─────────────────────────────────────────────────────┤
│ User → MainWindow → FileSettingsTab                 │
│   → ExcelLoader.process_excel(file_path)            │
│   → Parse columns (Turkish/English support)         │
│   → Create Course objects                           │
│   → Database.save_courses(courses)                  │
│   → Signal: file_selected                           │
│   → Update status bar                               │
└─────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────┐
│ 2. Course Selection                                 │
├─────────────────────────────────────────────────────┤
│ User → CourseSelectorTab                            │
│   → Browse courses (grouped by main_code)           │
│   → Click to cycle states                           │
│     First: MANDATORY ✅                             │
│     Second: OPTIONAL ❌                             │
│     Third: EXCLUDED ⬜                              │
│   → Signal: selection_changed                       │
└─────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────┐
│ 3. Algorithm Configuration                          │
├─────────────────────────────────────────────────────┤
│ User → FileSettingsTab                              │
│   → Select algorithm (DFS, A*, GA, ...)             │
│   → Set parameters                                  │
│     - max_results: 50                               │
│     - max_ects: 30                                  │
│     - allow_conflicts: False                        │
│     - timeout: 120s                                 │
│   → Set preferences (optional)                      │
│     - Free days: [Saturday, Sunday]                 │
│     - Preferred times: Morning                      │
│   → Signal: algorithm_configured                    │
└─────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────┐
│ 4. Schedule Generation                              │
├─────────────────────────────────────────────────────┤
│ User → Click "Generate Schedules"                   │
│   → AlgorithmSelector.select_scheduler(requirements)│
│   → Score algorithms                                │
│   → Return best Scheduler class                     │
│   → Initialize scheduler                            │
│   → scheduler.generate_schedules(groups, mand, opt) │
│                                                     │
│   ┌─ Prepare Search Space                          │
│   │  - Build course groups                         │
│   │  - Identify mandatory/optional                 │
│   │  - Create valid selections                     │
│   │  - Apply smart filters                         │
│   └─                                                │
│                                                     │
│   ┌─ Run Algorithm                                 │
│   │  while not done and not timeout:               │
│   │    - Generate partial schedule                 │
│   │    - Validate ECTS limit                       │
│   │    - Check conflicts                           │
│   │    - Check prerequisites (if enabled)          │
│   │    - Prune invalid branches                    │
│   │    - Update progress bar                       │
│   └─                                                │
│                                                     │
│   ┌─ Finalize Results                              │
│   │  - Validate all schedules                      │
│   │  - Calculate preference scores                 │
│   │  - Sort by score (desc)                        │
│   │  - Limit to max_results                        │
│   └─                                                │
│                                                     │
│   → Signal: schedules_generated(List[Schedule])     │
│   → Auto-switch to ScheduleViewerTab                │
└─────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────┐
│ 5. View & Export                                    │
├─────────────────────────────────────────────────────┤
│ ScheduleViewerTab → Display schedules               │
│   → Populate program_combo                          │
│   → Render first schedule in grid                   │
│   → Highlight conflicts (red)                       │
│   → Show statistics                                 │
│                                                     │
│ User → Select export format                         │
│   PDF → PDFExporter.export(schedule)                │
│     - Add Işık logo (#0018A8)                       │
│     - Weekly grid table                             │
│     - Course list                                   │
│     - Statistics summary                            │
│                                                     │
│   Excel → ExcelExporter.export(schedule)            │
│     - Multi-sheet workbook                          │
│     - Formatted tables                              │
│     - Color-coded conflicts                         │
│                                                     │
│   JPEG → JPEGExporter.export(schedule)              │
│     - High-resolution image (300 DPI)               │
│     - Visual styling                                │
│     - Printable format                              │
└─────────────────────────────────────────────────────┘
```

---

### 5. Database Schema (`DATABASE_SCHEMA.puml`)

#### SQLite Tables

**courses table**
```sql
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,              -- COMP1111.1
    main_code TEXT NOT NULL,                -- COMP1111
    name TEXT NOT NULL,                     -- Programming Fundamentals
    ects INTEGER NOT NULL,                  -- 6
    course_type TEXT NOT NULL,              -- lecture/ps/lab
    schedule TEXT NOT NULL,                 -- JSON: [["Monday",1],["Monday",2]]
    teacher TEXT,                           -- Tuğba Erkoç
    has_lecture BOOLEAN NOT NULL DEFAULT 1,
    faculty TEXT,                           -- Engineering
    department TEXT,                        -- Computer Engineering
    campus TEXT,                            -- Şile/Maslak
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_courses_main_code ON courses(main_code);
CREATE INDEX idx_courses_code ON courses(code);
```

**schedules table**
```sql
CREATE TABLE schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    total_credits INTEGER NOT NULL,
    conflict_count INTEGER DEFAULT 0,
    courses TEXT NOT NULL,                  -- JSON: ["COMP1111.1", "MATH2201.1"]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**programs table**
```sql
CREATE TABLE programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    metadata TEXT,                          -- JSON: {"faculty": "Engineering"}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**program_schedules table (many-to-many)**
```sql
CREATE TABLE program_schedules (
    program_id INTEGER NOT NULL,
    schedule_id INTEGER NOT NULL,
    PRIMARY KEY (program_id, schedule_id),
    FOREIGN KEY (program_id) REFERENCES programs(id),
    FOREIGN KEY (schedule_id) REFERENCES schedules(id)
);
```

**transcripts table**
```sql
CREATE TABLE transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,        -- 23SOFT1040
    student_name TEXT NOT NULL,             -- YİĞİT OKUR
    program TEXT NOT NULL,                  -- Computer Engineering
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**grades table**
```sql
CREATE TABLE grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transcript_id INTEGER NOT NULL,
    course_code TEXT NOT NULL,              -- COMP1111
    course_name TEXT NOT NULL,
    ects INTEGER NOT NULL,
    letter_grade TEXT NOT NULL,             -- AA/BA/.../FF
    numeric_grade REAL NOT NULL,            -- 0.0-4.0
    semester TEXT NOT NULL,                 -- Fall-2023
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transcript_id) REFERENCES transcripts(id) ON DELETE CASCADE
);
```

---

## 🔍 Sequence Diagrams

### Schedule Generation Sequence (`SEQUENCE_GENERATE.puml`)

```
User → FileSettingsTab: Click "Generate Schedules"
FileSettingsTab → FileSettingsTab: Validate inputs
FileSettingsTab → AlgorithmSelector: select_scheduler(requirements)
AlgorithmSelector → AlgorithmSelector: Score all algorithms
AlgorithmSelector → FileSettingsTab: DFSScheduler class

FileSettingsTab → DFSScheduler: __init__(params)
FileSettingsTab → DFSScheduler: generate_schedules(groups, mandatory, optional)

DFSScheduler → DFSScheduler: _prepare_search_space()
DFSScheduler → ConstraintUtils: build_group_options(groups, mandatory)

loop For each group
    ConstraintUtils → ConstraintUtils: Get valid combinations
    ConstraintUtils → ConstraintUtils: Filter by constraints
end

ConstraintUtils → DFSScheduler: (valid_selections, group_options)
DFSScheduler → DFSScheduler: _run_algorithm(search)

loop DFS Recursion
    DFSScheduler → DFSScheduler: _dfs_recursive(depth, current, search)
    
    alt Reached max results
        DFSScheduler → DFSScheduler: Return
    else depth < len(groups)
        loop For each valid option
            DFSScheduler → DFSScheduler: Try adding course(s)
            DFSScheduler → DFSScheduler: _is_valid_partial_selection()
            
            DFSScheduler → Course: Calculate total ECTS
            Course → DFSScheduler: total_ects
            
            alt ECTS > max_ects
                DFSScheduler → DFSScheduler: Skip (prune branch)
            else allow_conflicts = False
                DFSScheduler → Schedule: Check conflicts
                Schedule → Course: conflicts_with()
                Course → Schedule: has_conflict
                Schedule → DFSScheduler: conflict_count
                
                alt Has conflicts
                    DFSScheduler → DFSScheduler: Skip
                else No conflicts
                    DFSScheduler → DFSScheduler: Recurse deeper
                end
            else allow_conflicts = True
                DFSScheduler → DFSScheduler: Recurse deeper
            end
        end
    else All mandatory included
        DFSScheduler → Schedule: Create Schedule
        Schedule → Schedule: Calculate total_credits
        Schedule → Schedule: Calculate conflict_count
        Schedule → DFSScheduler: schedule
        DFSScheduler → DFSScheduler: Add to results
    end
end

DFSScheduler → DFSScheduler: _finalize_results(raw_results)

loop For each result
    DFSScheduler → DFSScheduler: _is_valid_final_schedule()
    DFSScheduler → DFSScheduler: Score with preferences
end

DFSScheduler → DFSScheduler: Sort by score
DFSScheduler → DFSScheduler: Limit to max_results
DFSScheduler → FileSettingsTab: List[Schedule]

FileSettingsTab → ScheduleViewerTab: Display schedules
ScheduleViewerTab → ScheduleViewerTab: Clear previous results

loop For each schedule
    ScheduleViewerTab → ScheduleViewerTab: Add to program list
    ScheduleViewerTab → ScheduleViewerTab: Display conflict count
end

ScheduleViewerTab → User: Show schedules
```

---

## 🔄 State Diagram (`STATE_DIAGRAM.puml`)

### Application States

```
[*] → NotInitialized

NotInitialized → Initializing: Application Start
Initializing → Ready: Initialization Complete
Initializing → Error: Initialization Failed

state Ready {
    [*] → NoFileLoaded
    
    NoFileLoaded → FileLoading: User selects Excel file
    FileLoading → FileLoaded: Load successful
    FileLoading → NoFileLoaded: Load failed
    
    FileLoaded → CourseSelecting: User switches to Selector tab
    CourseSelecting → CourseSelected: User marks courses
    
    CourseSelected → AlgorithmConfiguring: User switches to File tab
    AlgorithmConfiguring → ReadyToGenerate: Configuration complete
    
    ReadyToGenerate → Generating: User clicks Generate
    Generating → SchedulesGenerated: Generation successful
    Generating → GenerationFailed: Generation failed
    Generating → Generating: Cancel & Retry
    
    SchedulesGenerated → ViewingSchedules: User switches to Viewer tab
    ViewingSchedules → Exporting: User clicks Export
    Exporting → ViewingSchedules: Export complete
    
    ViewingSchedules → CourseSelecting: User modifies selection
    CourseSelecting → ReadyToGenerate: Re-configure
}

Ready → Exiting: User closes application
Exiting → [*]

Error → [*]: Critical error
```

**State Actions:**

- **FileLoading:**
  - Read Excel file
  - Parse courses
  - Validate data
  - Save to database
  - Update UI

- **Generating:**
  - Prepare search space
  - Run algorithm
  - Validate results
  - Sort by preferences
  - Update progress bar
  - Can be cancelled by user

- **ViewingSchedules:**
  - View schedule grid
  - Check conflicts
  - View course details
  - Export to PDF/Excel/JPEG
  - Compare schedules

---

## 📦 Deployment (`DEPLOYMENT_DIAGRAM.puml`)

### Target Platforms
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 20.04+)

### Runtime Requirements
```
Python 3.11+
├── Standard Library
└── Third-party Packages
    ├── PyQt6 6.6.1+
    ├── pandas 2.1.0+
    ├── numpy 1.24.0+
    ├── openpyxl 3.1.0+
    ├── reportlab 4.0.0+
    ├── matplotlib 3.7.0+
    ├── Pillow 10.0.0+
    └── pytest 7.4.0+
```

### Application Structure
```
User Workstation
├── SchedularV3 Application
│   ├── PyQt6 GUI
│   ├── Business Logic
│   └── Algorithm Engine
├── SQLite Database
│   └── course_scheduler.db
├── File System
│   ├── Excel Files (.xlsx)
│   ├── CSV Files (.csv)
│   ├── PDF Exports
│   ├── JPEG Exports
│   └── Log Files
└── Python 3.11+ Runtime
    └── Virtual Environment (venv/)
```

**Key Features:**
- ✅ Standalone desktop application
- ✅ No internet required
- ✅ Fully offline
- ✅ Self-contained
- ✅ No external services
- ✅ No API calls

---

## 🎯 Use Cases (`USE_CASE_DIAGRAM.puml`)

### Actors

**1. Student (Primary User)**
- Load course data
- Browse and filter courses
- Select mandatory/optional courses
- Generate schedules
- View schedules & check conflicts
- Calculate GPA & simulate grades
- Check prerequisites
- Check graduation progress
- Export schedules

**2. Academic Advisor**
- All student features
- Benchmark algorithms
- Compare multiple schedules
- Provide recommendations

**3. Administrator**
- System configuration
- Data management (delete courses)
- View logs
- Algorithm benchmarking

### Main Use Cases

1. **Load Course Data**
   - Import Excel File
   - Import Transcript

2. **Browse Courses**
   - Filter Courses (Faculty, Department, Campus, Type)
   - Search Courses
   - Delete Courses (Admin only)

3. **Select Courses**
   - Select Mandatory Courses
   - Select Optional Courses
   - Exclude Courses

4. **Configure Algorithm**
   - Set Parameters (max_results, max_ects, timeout)
   - Set Preferences (free days, time slots)

5. **Generate Schedules**
   - Run algorithm
   - Validate results
   - Sort by preferences

6. **View Schedules**
   - Display weekly grid
   - Check Conflicts
   - Compare Schedules

7. **Academic Features**
   - Calculate GPA
   - Simulate Grades
   - Check Prerequisites
   - View Prerequisite Chain
   - Check Graduation Progress
   - View Timeline
   - Get Recommendations

8. **Export**
   - Export to PDF
   - Export to Excel
   - Export to JPEG

9. **Manage Transcripts**
   - Add Grades
   - Edit Grades
   - Delete Grades

---

## 📈 Activity Diagram (`ACTIVITY_DIAGRAM.puml`)

### Schedule Generation Activity Flow

1. **Start**
2. **Load Excel File**
   - If valid → Parse → Create Course objects → Save to DB
   - If invalid → Show error → Stop

3. **Select Courses**
   - Browse available courses
   - Repeat:
     - Select course
     - If first click → Mark as Mandatory ✅
     - If second click → Mark as Optional ❌
     - If third click → Mark as Excluded ⬜

4. **Configure Algorithm**
   - Select algorithm from dropdown
   - Set parameters:
     - max_results: 1-100
     - max_ects: 25-45
     - allow_conflicts: 0-10
     - timeout: 30-300s
   - Set preferences (optional):
     - Desired free days
     - Preferred time slots
     - Campus preference
     - Morning/Afternoon

5. **Generate Schedules**
   - Show progress dialog
   - Fork:
     - Prepare search space
     - Build course groups
     - Identify mandatory/optional
   - Fork:
     - Initialize algorithm
     - Set parameters
   - Run algorithm:
     - While not done AND not timeout:
       - Generate partial schedule
       - If ECTS limit exceeded → Prune branch
       - Else if has conflicts AND not allowed → Prune branch
       - Else if all mandatory included:
         - Validate schedule
         - If valid:
           - Calculate preference score
           - Add to results
           - If reached max results → Stop generation
       - Else → Continue recursion
       - Update progress bar
   - Sort results by score
   - Close progress dialog

6. **View Results**
   - If schedules found:
     - Display in Viewer tab
     - Display weekly grid
     - Highlight conflicts (red)
     - Show course details
     - If user wants to export:
       - Select format (PDF/Excel/JPEG)
       - Generate file
       - Save file
       - Show success message
   - Else:
     - Show "No schedules found"
     - Analyze failure reasons
     - Display suggestions

7. **Stop**

---

## 🏛️ Package Dependencies (`PACKAGE_DIAGRAM.puml`)

### Package Hierarchy

```
main.py
  ↓
config/
  settings.py
  
core/
  models.py
  database.py
  excel_loader.py
  academic.py
  transcript_parser.py
  isik_university_data.py
  prerequisite_data.py
  curriculum_data.py
  
algorithms/
  base_scheduler.py
  dfs_scheduler.py
  bfs_scheduler.py
  a_star_scheduler.py
  dijkstra_scheduler.py
  iddfs_scheduler.py
  greedy_scheduler.py
  genetic_algorithm.py
  simulated_annealing.py
  hill_climbing.py
  tabu_search.py
  particle_swarm.py
  hybrid_ga_sa.py
  constraint_programming.py
  algorithm_selector.py
  constraints.py
  evaluator.py
  heuristics.py
  
gui/
  main_window.py
  tabs/
    file_settings_tab.py
    course_browser_tab.py
    course_selector_tab.py
    schedule_viewer_tab.py
    academic_tab.py
    graduation_planner_widget.py
  widgets/
    algorithm_selector.py
    schedule_grid.py
    course_card.py
    progress_dialog.py
  dialogs/
    algorithm_comparison.py
    add_grade_dialog.py
    transcript_import_dialog.py
    
reporting/
  pdf.py
  excel.py
  jpeg.py
  charts.py
  
utils/
  error_handler.py
  performance.py
  schedule_metrics.py
  
tests/
  test_*.py
```

### Dependency Directions

```
main.py → config, gui, utils
gui → core, algorithms, reporting, utils
algorithms → core, utils
reporting → core, utils
core → config
tests → core, algorithms, gui
```

**Key Principles:**
- No circular dependencies
- Clear layer separation
- Core has minimal dependencies
- GUI depends on all layers
- Tests have access to everything

---

## 📊 Metrics & Statistics

### Code Metrics
- **Total Lines of Code:** ~8,000+
- **Python Files:** 60+
- **Test Files:** 10+
- **Test Coverage:** 65%
- **Test Success Rate:** 100% (33/33 passing)

### Component Counts
- **Data Models:** 8 (Course, Schedule, CourseGroup, Program, Grade, Transcript, GraduationRequirement, TimeSlot)
- **Schedulers:** 15+ algorithms
- **GUI Tabs:** 5 main tabs
- **Custom Widgets:** 5 (AlgorithmSelector, ScheduleGrid, CourseCard, ProgressDialog, GraduationPlanner)
- **Dialogs:** 3 (AlgorithmComparison, AddGrade, TranscriptImport)
- **Database Tables:** 6 (courses, schedules, programs, program_schedules, transcripts, grades)

### Performance Benchmarks
- **Small Problems (<20 courses):** <1 second (DFS, Greedy)
- **Medium Problems (20-50 courses):** 1-5 seconds (DFS, A*, BFS)
- **Large Problems (50-100 courses):** 5-60 seconds (GA, SA, Hybrid)
- **Very Large (100+ courses):** 60-300 seconds (CP-SAT, Hybrid GA-SA)

### Algorithm Comparison
| Algorithm | Speed | Optimality | Memory | Use Case |
|-----------|-------|------------|--------|----------|
| DFS | ⚡⚡⚡ Fast | ❌ No | 💾 Low | Quick results |
| BFS | ⚡⚡ Medium | ✅ Yes | 💾💾 Medium | Optimal small |
| A* | ⚡⚡ Medium | ✅ Yes* | 💾💾 Medium | Best general |
| Dijkstra | ⚡ Slow | ✅ Yes | 💾💾💾 High | Weighted |
| IDDFS | ⚡⚡ Medium | ✅ Yes | 💾 Low | Memory-limited |
| Greedy | ⚡⚡⚡ Fast | ❌ No | 💾 Low | Quick approx |
| Genetic | ⚡ Slow | ❌ No | 💾💾 Medium | Large search |
| Sim. Annealing | ⚡ Slow | ❌ No | 💾 Low | Avoid local |
| Hill Climbing | ⚡⚡ Medium | ❌ No | 💾 Low | Local opt |
| Tabu | ⚡ Slow | ❌ No | 💾💾 Medium | Escape local |
| Particle Swarm | ⚡ Slow | ❌ No | 💾💾 Medium | Swarm intel |
| Hybrid GA-SA | ⚡ Slow | ❌ No | 💾💾 Medium | Complex |
| CP-SAT | ⚡ Slow | ✅ Yes | 💾💾💾 High | Hard constraints |

*Optimal with admissible heuristic

---

## 🎨 Işık University Branding

### Official Colors
- **Primary Blue:** #0018A8 (Pantone Blue 072 C)
  - RGB: (0, 24, 168)
  - CMYK: (100, 95, 0, 3)

### Logo Usage
- **Download:** https://www.isikun.edu.tr/sites/default/files/2024-10/2458_1_IU-Logo.zip
- **Placement:** `resources/images/`
- **Guidelines:**
  - Use only in blue (#0018A8) or black
  - Do not modify logo form
  - Maintain clear space

### Schedule Colors
```python
SCHEDULE_COLORS = [
    "#0018A8",  # Işık Blue (priority 1)
    "#FFB6C1",  # Light pink
    "#FFD700",  # Gold
    "#90EE90",  # Light green
    "#87CEEB",  # Sky blue
    "#DDA0DD",  # Plum
    "#F0E68C",  # Khaki
    "#FFA07A",  # Light salmon
    "#20B2AA",  # Light sea green
    "#778899",  # Light slate gray
    "#FF69B4",  # Hot pink
    "#CD853F",  # Peru
]
```

### UI Theming
- **Light Theme:** Default (white background)
- **Dark Theme:** Optional (dark background with #0018A8 accents)

---

## 🔐 Data Security & Privacy

### Local Data Storage
- All data stored locally in SQLite database
- No cloud upload
- No external API calls
- Full user control

### Sensitive Data
- Student transcripts stored encrypted
- No personal data transmitted
- GDPR compliant (local-only)

---

## 🚀 Future Enhancements

### Phase 9: Advanced Reporting (Planned)
- [ ] Custom PDF templates
- [ ] Multi-language support (Turkish/English)
- [ ] Analytics dashboard
- [ ] Schedule heatmaps
- [ ] Prerequisite graphs (NetworkX)

### Phase 10: Machine Learning (Planned)
- [ ] Course recommendation system
- [ ] Success probability prediction
- [ ] Optimal schedule prediction
- [ ] Student behavior analysis

### Phase 11: Web Version (Future)
- [ ] Django/Flask backend
- [ ] React frontend
- [ ] REST API
- [ ] Multi-user support
- [ ] Cloud synchronization

---

## 📚 Documentation Index

### User Guides
- **USER_GUIDE.md** - Complete user manual
- **PHASE_7.5_USAGE_GUIDE.md** - Transcript import guide
- **QUICK_START.md** - Quick start tutorial

### Technical Documentation
- **ARCHITECTURE_INDEX.md** - This document (architecture overview)
- **PHASE_02_DATA_LAYER.md** - Data layer documentation
- **PHASE_07_ACADEMIC_SYSTEM.md** - Academic system documentation
- **ISIK_UNIVERSITY_DATA_INTEGRATION.md** - Işık University data

### PlantUML Diagrams
- **ARCHITECTURE.puml** - Overall architecture
- **CLASS_DIAGRAM.puml** - Core class structure
- **ALGORITHM_DIAGRAM.puml** - Algorithm architecture
- **GUI_DIAGRAM.puml** - GUI components
- **DATABASE_SCHEMA.puml** - Database schema
- **DATA_FLOW_DIAGRAM.puml** - Data flow
- **SEQUENCE_GENERATE.puml** - Schedule generation sequence
- **STATE_DIAGRAM.puml** - Application states
- **DEPLOYMENT_DIAGRAM.puml** - Deployment architecture
- **PACKAGE_DIAGRAM.puml** - Package dependencies
- **USE_CASE_DIAGRAM.puml** - Use cases
- **ACTIVITY_DIAGRAM.puml** - Activity flow

---

## 🎓 Academic Credits

**Developed for:** Işık University Students  
**Institution:** Işık Üniversitesi (Işık University)  
**Location:** İstanbul, Turkey  
**Project Type:** Open Source (MIT License)

---

## 📞 Support & Contact

**Issues:** GitHub Issues  
**Documentation:** `/docs` folder  
**Email:** schedularv3@example.com (placeholder)

---

**Report Generated:** 26 Kasım 2025  
**Report Version:** 1.0.0  
**Status:** Architecture Complete ✅  
**Next Phase:** Phase 9 (Advanced Reporting)
