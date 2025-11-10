# 📋 Phase 8: Kalan Görevler

**Durum:** 🟡 85% Complete (15% kaldı)  
**Hedef Tarih:** 12 Kasım 2025  
**Öncelik:** HIGH

---

## ✅ Tamamlanan Özellikler (85%)

### Course Browser Tab ✅
- ✅ Advanced filtering system (Faculty, Department, Campus, Type, Teacher)
- ✅ Quick filters (Search bar, Sort dropdown)
- ✅ Collapsible filter panel (Show/Hide Filters)
- ✅ Performance optimization (Debouncing 300ms)
- ✅ Performance optimization (Manual apply for advanced filters)
- ✅ Performance optimization (Table batch updates)
- ✅ Smart group deletion (Lecture+Lab/PS confirmation)
- ✅ Course deletion with confirmation dialog
- ✅ Cross-tab synchronization (Browser → Selector)
- ✅ Course count badges (Lecture/Lab/PS)
- ✅ Multi-column table view
- ✅ Delete button functionality

### Course Selector Tab ✅
- ✅ Tri-state visual indicators (✅ mandatory, ❌ optional, plain excluded)
- ✅ Color-coded styling (green bold, orange, gray)
- ✅ Dynamic text updates
- ✅ Cross-tab synchronization (Browser deletions update selector)

### Main Window ✅
- ✅ Signal-slot connections for cross-tab communication
- ✅ Status bar updates with course counts

---

## 🔴 Kalan Görevler (15%)

### 1. Export Fonksiyonları (5%) 🔴

#### 1.1 CSV Export Ekle
**Dosya:** `gui/tabs/course_browser_tab.py`
**Görev:**
- Course Browser'a "Export to CSV" butonu ekle
- Filtered results'u CSV'ye export et
- CSV format: Tüm sütunlar dahil (Code, Name, Teacher, Faculty, etc.)
- Save dialog ile dosya adı seçimi

**Beklenen Kod:**
```python
def _export_to_csv(self):
    """Export filtered courses to CSV."""
    if not self._filtered_courses:
        QMessageBox.warning(self, "No Data", "No courses to export!")
        return
    
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Export to CSV", "", "CSV Files (*.csv)"
    )
    if file_path:
        # Use pandas to export
        df = pd.DataFrame([{
            'Code': c.code,
            'Name': c.name,
            'Type': c.course_type,
            'ECTS': c.ects,
            'Teacher': c.teacher,
            'Faculty': c.faculty,
            # ... other fields
        } for c in self._filtered_courses])
        df.to_csv(file_path, index=False)
        QMessageBox.information(self, "Success", f"Exported {len(self._filtered_courses)} courses!")
```

**UI Değişikliği:**
- Browser tab'ın üst kısmına "Export CSV" butonu ekle
- Delete butonunun yanına yerleştir

**Tahmini Süre:** 30 dakika

---

#### 1.2 Filtered Results Export
**Görev:**
- Mevcut filtreleri koruyarak export yap
- Export başlığına filter bilgisi ekle
- Export dialog'da filter summary göster

**Örnek:**
```
Exporting 45 courses
Filters applied:
- Faculty: Engineering
- Type: Lecture
- Campus: Main Campus
```

**Tahmini Süre:** 20 dakika

---

### 2. Batch Operations (5%) 🔴

#### 2.1 Multi-Select Functionality
**Dosya:** `gui/tabs/course_browser_tab.py`
**Görev:**
- Table'da multi-select enable et: `setSelectionMode(QTableWidget.SelectionMode.MultiSelection)`
- Ctrl+Click ile multiple selection
- Shift+Click ile range selection
- Select All / Deselect All butonları ekle

**UI Değişikliği:**
```python
# Table selection mode
self.course_table.setSelectionMode(
    QTableWidget.SelectionMode.ExtendedSelection  # Multi-select
)

# Selection buttons
select_all_btn = QPushButton("Select All")
select_all_btn.clicked.connect(self.course_table.selectAll)

deselect_btn = QPushButton("Deselect All")
deselect_btn.clicked.connect(self.course_table.clearSelection)
```

**Tahmini Süre:** 30 dakika

---

#### 2.2 Bulk Delete
**Görev:**
- Seçili tüm kursları sil
- Confirmation dialog'da count göster
- Progress bar ile silme işlemi (10+ course ise)

**Beklenen Kod:**
```python
def _delete_selected_courses(self):
    """Delete all selected courses."""
    selected_rows = set(item.row() for item in self.course_table.selectedItems())
    if not selected_rows:
        QMessageBox.warning(self, "No Selection", "Please select courses to delete!")
        return
    
    count = len(selected_rows)
    reply = QMessageBox.question(
        self, "Confirm Deletion",
        f"Delete {count} selected courses?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    
    if reply == QMessageBox.StandardButton.Yes:
        # Delete courses
        courses_to_delete = [self._filtered_courses[row] for row in sorted(selected_rows, reverse=True)]
        for course in courses_to_delete:
            self._courses.remove(course)
        
        # Emit signal and refresh
        self.courses_updated.emit(self._courses.copy())
        self._apply_filters()
```

**UI Değişikliği:**
- "Delete" butonunu "Delete Selected" olarak değiştir
- Seçim yoksa butonu disable et

**Tahmini Süre:** 45 dakika

---

#### 2.3 Bulk Export
**Görev:**
- Seçili kursları export et (CSV)
- "Export Selected" butonu ekle

**Tahmini Süre:** 20 dakika

---

### 3. UI Polish & Enhancements (5%) 🔴

#### 3.1 Filter Presets
**Dosya:** `gui/tabs/course_browser_tab.py`
**Görev:**
- Favorite filter combinations'ı kaydet
- "Save Current Filters" butonu
- "Load Filters" dropdown
- JSON file ile persistence

**Örnek Preset:**
```json
{
  "Engineering Lectures": {
    "faculty": "Faculty of Engineering",
    "course_type": "lecture",
    "campus": "Main Campus"
  },
  "CS Courses": {
    "faculty": "Faculty of Engineering",
    "department": "Computer Science"
  }
}
```

**UI:**
- "Save Filters As..." butonu
- "Load Preset" dropdown
- "Delete Preset" butonu

**Tahmini Süre:** 1 saat

---

#### 3.2 Keyboard Shortcuts
**Görev:**
- Ctrl+F: Focus search box
- Ctrl+A: Select all
- Delete: Delete selected
- Ctrl+E: Export CSV
- F5: Refresh/reload

**Beklenen Kod:**
```python
def keyPressEvent(self, event):
    """Handle keyboard shortcuts."""
    if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
        if event.key() == Qt.Key.Key_F:
            self.search_edit.setFocus()
        elif event.key() == Qt.Key.Key_A:
            self.course_table.selectAll()
        elif event.key() == Qt.Key.Key_E:
            self._export_to_csv()
    elif event.key() == Qt.Key.Key_Delete:
        self._delete_selected_courses()
    elif event.key() == Qt.Key.Key_F5:
        self._apply_filters()
    else:
        super().keyPressEvent(event)
```

**Tahmini Süre:** 30 dakika

---

#### 3.3 Column Persistence
**Görev:**
- Kullanıcının column width ayarlarını kaydet
- QSettings ile persistence
- Uygulama açıldığında restore et

**Beklenen Kod:**
```python
def _save_column_widths(self):
    """Save column widths to settings."""
    settings = QSettings("SchedularV3", "CourseBrowser")
    widths = [self.course_table.columnWidth(i) for i in range(self.course_table.columnCount())]
    settings.setValue("column_widths", widths)

def _restore_column_widths(self):
    """Restore column widths from settings."""
    settings = QSettings("SchedularV3", "CourseBrowser")
    widths = settings.value("column_widths", None)
    if widths:
        for i, width in enumerate(widths):
            self.course_table.setColumnWidth(i, width)
```

**Tahmini Süre:** 30 dakika

---

## 📊 Görev Öncelik Sıralaması

### Yüksek Öncelik (Must Have)
1. **CSV Export** - Export fonksiyonalitesi temel feature
2. **Multi-Select** - Kullanıcı deneyimi için kritik
3. **Bulk Delete** - Multi-select'in tamamlayıcısı

### Orta Öncelik (Should Have)
4. **Keyboard Shortcuts** - Power users için önemli
5. **Bulk Export** - CSV ile birlikte güzel olur

### Düşük Öncelik (Nice to Have)
6. **Filter Presets** - İleri seviye feature, sonra eklenebilir
7. **Column Persistence** - QOL improvement, zorunlu değil

---

## 🎯 Tamamlanma Planı

### Senaryo 1: Hızlı Tamamlama (3-4 saat)
**Sadece yüksek öncelikli görevler**
1. CSV Export (30 min)
2. Multi-Select (30 min)
3. Bulk Delete (45 min)
4. Keyboard Shortcuts (30 min)
5. Testing + Bug fixes (1 saat)

**Sonuç:** Phase 8 → 95% complete

---

### Senaryo 2: Tam Tamamlama (6-7 saat)
**Tüm görevler**
1. CSV Export (30 min)
2. Filtered Export (20 min)
3. Multi-Select (30 min)
4. Bulk Delete (45 min)
5. Bulk Export (20 min)
6. Keyboard Shortcuts (30 min)
7. Column Persistence (30 min)
8. Filter Presets (1 saat)
9. Testing + Bug fixes (2 saat)

**Sonuç:** Phase 8 → 100% complete ✅

---

### Senaryo 3: Minimal (Phase 9'a geç)
**Sadece export fonksiyonları**
1. CSV Export (30 min)
2. Testing (30 min)

**Sonuç:** Phase 8 → 90% complete → Phase 9'a geç

---

## 💡 Öneri

**Senaryo 1'i öneriyorum:**
- CSV export kritik feature
- Multi-select + bulk operations kullanıcı deneyimini çok artırır
- Keyboard shortcuts power users için değerli
- Filter presets ve column persistence Phase 10'da eklenebilir

**Phase 8'i 95%'te bırakıp Phase 9'a geçelim:**
- Export fonksiyonları (PDF, Excel, JPEG) daha kritik
- Analytics dashboard daha fazla değer katar
- Filter presets "polish" feature, MVP için gerekli değil

---

## 🚀 Şimdi Ne Yapalım?

### Seçenek A: Phase 8'i bitirelim (3-4 saat)
✅ CSV Export  
✅ Multi-Select  
✅ Bulk Operations  
✅ Keyboard Shortcuts  
→ Phase 8 complete %95+  
→ Phase 9'a geçelim

### Seçenek B: Phase 9'a geçelim (hemen)
- Phase 8 %85'te kalsın
- Export özelliklerini Phase 9'da çözeriz
- Reporting daha önemli şu anda

### Seçenek C: Minimal update (30 min)
- Sadece CSV export ekle
- Phase 8 → %90
- Phase 9'a geç

---

**Senin kararın! Ne yapmak istersin?** 🤔

1. **"A"** - Phase 8'i bitirelim (3-4 saat, %95+ complete)
2. **"B"** - Phase 9'a geçelim (reporting/export daha önemli)
3. **"C"** - Sadece CSV export ekle (30 min), Phase 9'a geç

Hangisini tercih edersin?

