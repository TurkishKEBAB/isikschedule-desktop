# Phase 7.5: Transcript Import System

## 📥 Kullanım Kılavuzu

### Transcript Import Özellikleri

Phase 7.5 ile eklenen **Transcript Import** sistemi, öğrencilerin transkriptlerini sisteme aktarmasını ve akademik verilerini yönetmesini sağlar.

### ✨ Özellikler

1. **Excel Import**
   - Türkçe/İngilizce kolon isimleri otomatik algılama
   - Öğrenci bilgilerini otomatik çıkarma
   - Not verilerini otomatik parse etme
   
2. **Manuel Not Girişi**
   - Ders kodu, adı, ECTS girişi
   - Harf notu seçimi (AA-FF, P, W, I, NA)
   - Otomatik sayısal not hesaplama (4.0-0.0)
   
3. **Transcript Yönetimi**
   - Not tablosu (düzenleme/silme)
   - Gerçek zamanlı GPA hesaplama
   - ECTS toplamı görüntüleme
   - Renk kodlu GPA gösterimi (Yeşil: ≥3.0, Turuncu: ≥2.0, Kırmızı: <2.0)

4. **Veritabanı Entegrasyonu**
   - SQLite'a kaydetme/yükleme
   - Otomatik transcript güncelleme
   - Cascade silme desteği

5. **Excel Export**
   - Transcript'i Excel'e aktarma
   - Özet satırı (GPA, ECTS, öğrenci bilgileri)
   - UTF-8 kodlama desteği

### 📂 Dosya Formatı

**Excel Transcript Formatı:**

```
Satır 1-3: Öğrenci Bilgileri (opsiyonel)
  Student ID    23SOFT1040
  Student Name  YİĞİT OKUR
  Program       Computer Science Engineering

Satır 5+: Not Verileri (zorunlu)
  Course Code | Course Name                    | ECTS | Letter Grade | Semester
  ------------|--------------------------------|------|--------------|----------------
  COMP1007    | INTRO TO COMPUTER ENGINEERING  | 1    | DD           | Fall-2023
  CORE0101    | HISTORY OF TURKISH REPUBLIC I  | 2    | BA           | Fall-2023
  ...
```

**Desteklenen Kolon İsimleri:**

- **Ders Kodu**: `Ders Kodu`, `Kodu`, `Course Code`, `Code`, `KODU`
- **Ders Adı**: `Ders Adı`, `Ders`, `Course Name`, `Name`, `Ders ADI`
- **ECTS**: `AKTS`, `ECTS`, `Kredi`, `Credits`, `Credit`, `KREDİ`
- **Harf Notu**: `Harf Notu`, `Harf`, `Letter Grade`, `Grade`, `NOT`
- **Sayısal Not**: `Sayısal Not`, `Sayısal`, `Numeric Grade`, `Numeric`, `SAYISAL`
- **Dönem**: `Dönem`, `Yarıyıl`, `Semester`, `Term`, `DÖNEM`

### 🎯 Kullanım Adımları

#### 1. Excel'den Import

1. **Academic** tab'ına git
2. **📥 Import** alt-sekmesine tıkla
3. **📁 Import from Excel** butonuna tıkla
4. Excel dosyasını seç (`.xlsx` veya `.xls`)
5. Sistem otomatik olarak:
   - Öğrenci bilgilerini algılar
   - Notları parse eder
   - GPA'yı hesaplar
   - Tabloyu doldurur

#### 2. Manuel Not Ekleme

1. **✏️ Add Grade Manually** butonuna tıkla
2. Formu doldur:
   - Ders Kodu (ör: `COMP1007`)
   - Ders Adı (ör: `Introduction to Programming`)
   - ECTS (1-30 arası)
   - Harf Notu (AA, BA, BB, CB, CC, DC, DD, FD, FF)
   - Dönem (ör: `Fall-2023`)
3. **💾 Save** butonuna tıkla

#### 3. Not Düzenleme/Silme

- **Düzenleme**: Tablodaki ✏️ butonuna tıkla
- **Silme**: Tablodaki 🗑️ butonuna tıkla

#### 4. Veritabanına Kaydetme

1. Tüm bilgileri gir (Student ID, Name, Program zorunlu)
2. **💾 Save to Database** butonuna tıkla
3. Başarılı mesajı görüntülenir
4. GPA Calculator ve Graduation Planner otomatik güncellenir

#### 5. Excel'e Export

1. **📤 Export to Excel** butonuna tıkla
2. Dosya adı gir (varsayılan: `transcript_[STUDENT_ID].xlsx`)
3. Kaydet
4. Excel dosyası şunları içerir:
   - Tüm notlar
   - Özet satırı (öğrenci bilgileri, GPA, ECTS)

### 📊 Harf Notu - Sayısal Not Dönüşümü

| Harf Notu | Sayısal Not | Açıklama           |
|-----------|-------------|--------------------|
| AA        | 4.0         | Mükemmel           |
| BA        | 3.5         | Pekiyi             |
| BB        | 3.0         | İyi                |
| CB        | 2.5         | Orta Seviye        |
| CC        | 2.0         | Geçer (Minimum)    |
| DC        | 1.5         | Koşullu Geçer      |
| DD        | 1.0         | Şartlı Geçer       |
| FD        | 0.5         | Başarısız (Düşük)  |
| FF        | 0.0         | Başarısız          |
| P         | 0.0         | Geçti (GPA'de yok) |
| F         | 0.0         | Kaldı              |
| W         | 0.0         | Çekildi            |
| I         | 0.0         | Tamamlanmamış      |
| NA        | 0.0         | Uygulanamaz        |

### 🧮 GPA Hesaplama

```
GPA = (Σ(ECTS × Sayısal Not)) / Σ(ECTS)
```

**Örnek:**
- COMP1007: 1 ECTS × 1.0 (DD) = 1.0
- CORE0101: 2 ECTS × 3.5 (BA) = 7.0
- COMP1111: 6 ECTS × 2.5 (CB) = 15.0
- **Toplam:** (1.0 + 7.0 + 15.0) / (1 + 2 + 6) = **23.0 / 9 = 2.56**

### 📈 ECTS Limiti

GPA'ya göre dönemlik ECTS limiti:
- **GPA ≥ 3.0**: 42 ECTS
- **2.5 ≤ GPA < 3.0**: 37 ECTS
- **GPA < 2.5**: 31 ECTS

### 🗄️ Veritabanı Yapısı

**transcripts tablosu:**
```sql
CREATE TABLE transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    student_name TEXT NOT NULL,
    program TEXT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

**grades tablosu:**
```sql
CREATE TABLE grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transcript_id INTEGER NOT NULL,
    course_code TEXT NOT NULL,
    course_name TEXT NOT NULL,
    ects INTEGER NOT NULL,
    letter_grade TEXT NOT NULL,
    numeric_grade REAL NOT NULL,
    semester TEXT NOT NULL,
    created_at TIMESTAMP,
    FOREIGN KEY (transcript_id) REFERENCES transcripts (id) ON DELETE CASCADE
)
```

### 🧪 Test Dosyası

Sistemle birlikte gelen `sample_transcript_yigit_okur.xlsx` dosyası:
- **Öğrenci:** YİĞİT OKUR (23SOFT1040)
- **Program:** Computer Science Engineering
- **ECTS:** 91 kredi
- **Ders Sayısı:** 24
- **GPA:** ~2.29

**Test için:**
1. Academic → Import sekmesine git
2. "Import from Excel" butonuna tıkla
3. `sample_transcript_yigit_okur.xlsx` dosyasını seç
4. Verilerin otomatik yüklendiğini gör

### 🔄 Entegrasyon

Transcript import edildikten sonra:

1. **GPA Calculator** otomatik güncellenir
   - Mevcut GPA görüntülenir
   - ECTS bilgisi gösterilir
   - "What-If" simülasyonu yapılabilir

2. **Graduation Planner** otomatik güncellenir
   - Tamamlanan dersler listelenir
   - Eksik dersler hesaplanır
   - Mezuniyet ilerleme çubuğu güncellenir

3. **Prerequisite Checker** kullanılabilir
   - Tamamlanan dersler otomatik algılanır
   - Alınabilecek dersler gösterilir

### 📝 Notlar

- Retake dersleri: Sadece son notu ekleyin
- Transfer dersleri: Normal ders olarak eklenebilir
- F notları: Eğer retake edilmişse eklemeyin
- Dönem formatı: Serbest (ör: `Fall-2023`, `2023-2024 Güz`, `Güz 2023`)

### 🐛 Sorun Giderme

**"Required column not found" hatası:**
- Excel'deki kolon isimlerini kontrol edin
- Desteklenen kolon isimlerinden birini kullanın
- İlk satırda başlık olduğundan emin olun

**"No grades found" hatası:**
- Öğrenci bilgilerinden sonra boş satır bırakın
- Not verilerinin doğru satırda olduğundan emin olun

**GPA eşleşmiyor:**
- Tüm notların doğru girildiğini kontrol edin
- F notlarının retake edilmişlerse eklenmediğinden emin olun
- ECTS değerlerini kontrol edin

### 🎓 İleri Özellikler (Phase 7.5 Day 2)

Gelecek güncellemeler:
- [ ] Otomatik transcript yükleme (program başlangıcında)
- [ ] Gelişmiş validasyon
- [ ] Transcript karşılaştırma
- [ ] Semester-wise GPA breakdown
- [ ] Grade trend visualization

---

**Phase 7.5 Durum:** Day 1 Complete (50%) ✅  
**Toplam Kod:** ~1320 satır  
**Dosyalar:** 4 yeni modül (transcript_import_dialog.py, add_grade_dialog.py, transcript_parser.py, database.py extensions)
