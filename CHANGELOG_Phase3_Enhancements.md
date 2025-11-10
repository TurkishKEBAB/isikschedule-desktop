# Phase 3 Enhancements - Changelog

## 🎯 Geliştirmeler

### 1. ✅ Ayarlanabilir Çakışma Toleransı
**Dosya:** `gui/widgets/algorithm_selector.py`

- **Önce:** "Allow conflicts" basit checkbox (evet/hayır)
- **Şimdi:** "Max Conflicts" sayısal değer (0-10 arası)
  - **Default değer:** 1 çakışma
  - **0 değeri:** Hiç çakışma kabul edilmez
  - **1+ değeri:** Belirtilen sayıda çakışmaya izin verilir
  
**Kullanım:**
```python
# Algoritmalar şu parametreyi alır:
{
    "allow_conflicts": True/False,  # max_conflicts > 0 ise True
    "max_conflicts": 1,             # Maksimum izin verilen çakışma sayısı
}
```

---

### 2. 🔴 Çakışan Dersler Kırmızı Gösterilir
**Dosya:** `gui/widgets/schedule_grid.py`

**Yeni Özellik:**
- Aynı zaman diliminde birden fazla ders varsa **kırmızı** renkle gösterilir
- Normal dersler renkli palet ile gösterilir
- Çakışma tespiti otomatik yapılır

**Teknik Detaylar:**
```python
def _find_conflict_slots(self) -> set:
    """Çakışan zaman dilimlerini tespit eder."""
    # Her zaman dilimindeki ders sayısını kontrol eder
    # 2+ ders varsa çakışma olarak işaretler
    # Kırmızı renk (#F44336) uygulanır
```

**Görsel:**
- ✅ **Normal ders:** Pastel renkler (mavi, yeşil, pembe...)
- 🔴 **Çakışan ders:** Kırmızı (#F44336)

---

### 3. 📚 Ders Detayları Gösterimi
**Dosya:** `gui/tabs/schedule_viewer_tab.py`

**Yeni Panel:**
Schedule Viewer sekmesine sağ tarafta **Course Details** paneli eklendi.

**Gösterilen Bilgiler:**
- 📚 **Ana Ders Kodu** (COMP1007)
- 📖 **Ders Adı**
- 🔖 **Tam Kod** (COMP1007.1)
- 🏷️ **Ders Tipi** (lecture, ps, lab)
- 🎓 **ECTS Kredisi**
- 👨‍🏫 **Öğretim Üyesi**
- 🏛️ **Fakülte**
- 🏢 **Bölüm**
- 🏫 **Kampüs**
- 📅 **Ders Saatleri** (Gün ve slot bilgisi)

**Kullanım:**
1. Schedule Viewer sekmesinde programa tıklayın
2. Haftalık takvimde herhangi bir **derse tıklayın**
3. Sağ panelde detaylı bilgiler görünür

**Örnek Görünüm:**
```
📚 COMP1007

Course Name:
Introduction to Programming

Course Code: COMP1007.1

Type: LECTURE

ECTS: 6

Instructor:
Dr. John Doe

Faculty:
Faculty of Engineering

Department:
Computer Science

Campus:
Main Campus

Schedule:
  Monday: Slot(s) 1, 2
  Wednesday: Slot(s) 3, 4
```

---

## 🐛 Kritik Hatalar Düzeltildi

### 1. Excel Zaman Dilimi Parse Hatası
**Sorun:** "Ders Saati(leri)" sütunu sadece sayı içeriyordu (2, 8, 3)
**Çözüm:** "Ders Saati" sütunu kullanılıyor (T1, T2, M1 formatı)
**Sonuç:** ✅ 920 ders hiç uyarı olmadan yükleniyor

### 2. Course Nesnesi Hashable Değildi
**Sorun:** `TypeError: unhashable type: 'Course'`
**Çözüm:** Course sınıfına `__hash__()` ve `__eq__()` metodları eklendi
**Sonuç:** ✅ Course artık dict key ve set member olabiliyor

### 3. QPainter Düzgün Sonlandırılmıyordu
**Sorun:** `QBackingStore::endPaint()` uyarıları
**Çözüm:** `painter.end()` try-finally bloğunda güvenli şekilde çağrılıyor
**Sonuç:** ✅ Hiç QPainter hatası kalmadı

### 4. Traceback Modül İsim Çakışması
**Sorun:** `AttributeError: 'traceback' object has no attribute 'format_exception'`
**Çözüm:** `import traceback as tb_module` aliası kullanılıyor
**Sonuç:** ✅ Exception handler düzgün çalışıyor

---

## 📊 Test Sonuçları

```bash
✅ Excel yükleme: 920 kurs - 0 uyarı
✅ GUI başlatma: Hatasız
✅ Çakışma tespiti: Çalışıyor
✅ Ders detayları: Çalışıyor
✅ Painter rendering: Hatasız
```

---

## 🚀 Nasıl Kullanılır?

### Max Conflicts Ayarlama:
1. **File Settings** sekmesine gidin
2. **Algorithm Parameters** bölümünde **"Max Conflicts"** değerini ayarlayın
3. **0:** Hiç çakışma olmasın
4. **1:** Maksimum 1 çakışmaya izin ver (default)
5. **2+:** Daha fazla çakışmaya izin ver

### Çakışan Dersleri Görme:
1. **Generate Schedules** butonuna basın
2. **Schedule Viewer** sekmesine geçin
3. **Kırmızı** renkli dersler çakışmalı derslerdir
4. Her iki ders de görüntülenir

### Ders Detaylarını Görme:
1. Schedule Viewer'da bir programa tıklayın
2. Takvimde **herhangi bir derse** tıklayın
3. Sağdaki panelde **tam detayları** görün

---

## 📁 Değiştirilen Dosyalar

1. `core/excel_loader.py` - Zaman dilimi sütunu düzeltildi
2. `core/models.py` - Course hashable yapıldı
3. `gui/widgets/algorithm_selector.py` - Max conflicts parametresi
4. `gui/widgets/schedule_grid.py` - Çakışma tespiti ve kırmızı gösterim
5. `gui/tabs/schedule_viewer_tab.py` - Ders detayları paneli
6. `main.py` - Traceback çakışması çözüldü

---

## ✨ Sonraki Adımlar (Phase 4+)

- [ ] Export fonksiyonları (PDF, JPEG, Excel)
- [ ] Algoritma karşılaştırma raporu
- [ ] Gelişmiş filtreleme seçenekleri
- [ ] Çakışma çözümleme önerileri

---

**Geliştirme Tarihi:** 10 Kasım 2025  
**Versiyon:** 3.0.0 - Phase 3 Complete
