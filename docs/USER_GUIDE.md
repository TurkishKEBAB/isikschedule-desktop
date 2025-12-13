# 📖 SchedularV3 - Kullanıcı Kılavuzu

> **Modern Ders Çizelgeleme Sistemi**  
> Sürüm 3.0 | 10 Kasım 2025

---

## 🚀 Hızlı Başlangıç

### 1. Excel Dosyası Yükleme

1. **File & Settings** sekmesine gidin
2. **Browse** butonuna tıklayın
3. Işık Üniversitesi ders Excel dosyanızı seçin
4. Dosya otomatik olarak yüklenecektir

**Desteklenen Format:**
- Excel (.xlsx) formatı
- Gerekli sütunlar: Ders Kodu, Ders Adı, ECTS, Ders Saati, vb.

---

### 2. Algoritma Seçimi

**File & Settings** sekmesinde algoritmayı seçin:

#### 🚀 Hızlı Algoritmalar
- **DFS (Depth-First Search)** - Orta boyut problemler için
- **Greedy** - En hızlı sonuç
- **BFS** - Optimal garanti

#### 🎯 Kaliteli Algoritmalar
- **A\*** - En iyi genel amaçlı
- **Simulated Annealing** - Karmaşık problemler
- **Genetic Algorithm** - Büyük arama uzayı

#### ⚙️ Parametreler
- **Max Results:** Kaç program üretilecek (1-100)
- **Max ECTS:** Maksimum kredi limiti (0-60)
- **Allow Conflicts:** Çakışmalara izin ver
- **Max Conflicts:** Maksimum çakışma sayısı (0-10)
- **Timeout:** Maksimum süre (saniye)

---

### 3. Ders Seçimi

**Course Selector** sekmesinde:

1. **Mandatory (Zorunlu):** ✅ işaretleyin
2. **Optional (Seçmeli):** 🔲 boş bırakın
3. **Exclude (Hariç tut):** ❌ işaretleyin

**Filtreleme:**
- Ders koduna göre ara
- Fakülte/bölüm bazlı filtrele
- ECTS kredi filtresi

---

### 4. Program Üretme

1. **Generate Schedules** butonuna tıklayın
2. Algoritma çalışacak ve programlar üretilecek
3. **Schedule Viewer** sekmesine otomatik geçiş yapılacak

---

### 5. Sonuçları İnceleme

**Schedule Viewer** sekmesinde:

#### 📅 Haftalık Program Grid
- Renkli ders kutuları
- Çakışan dersler **kırmızı** renkte
- Ders üzerine tıklayarak detay görün

#### 📊 İstatistikler
- Toplam ders sayısı
- Toplam ECTS kredisi
- Çakışma sayısı
- Ders listesi

#### ⚖️ Algoritma Karşılaştırması
- **Compare Algorithms** butonuna tıklayın
- Yan yana performans karşılaştırması
- En iyi programı seçin

---

## 💾 Dışa Aktarma

### PDF Export
1. **Export PDF** butonuna tıklayın
2. Kayıt konumunu seçin
3. Profesyonel PDF raporu oluşturulacak

**İçerik:**
- Haftalık çizelge tablosu
- Detaylı ders listesi
- İstatistik özeti

---

### JPEG Export
1. **Export JPEG** butonuna tıklayın
2. Klasör seçin
3. Her program için bir görsel

**Özellikler:**
- Yüksek kalite (95% JPEG)
- Yazdırmaya hazır
- Paylaşım için ideal

---

### Excel Export
1. **Export Excel** butonuna tıklayın
2. Kayıt konumunu seçin
3. Multi-sheet Excel oluşturulacak

**Sheets:**
- Summary: Genel özet
- Schedule_1, Schedule_2, ...: Her program

---

## 🎨 Tema Değiştirme

**View → Dark Theme** menüsünden:
- ☀️ **Light Theme:** Aydınlık tema
- 🌙 **Dark Theme:** Karanlık tema

---

## 🔧 Gelişmiş Özellikler

### Scheduler Preferences

**Algorithm Settings** bölümünde:

- **Prioritize Less Conflicts:** Çakışma az olanları tercih et
- **Prioritize More ECTS:** ECTS yüksek olanları tercih et
- **Prefer Morning:** Sabah derslerini tercih et
- **Prefer Compact:** Kompakt programları tercih et

---

### Conflict Tolerance

**Max Conflicts** parametresi:
- `0`: Hiç çakışma yok
- `1-2`: Kabul edilebilir seviye
- `3+`: Yüksek tolerans

**Not:** Conflict count yükseldikçe daha fazla program bulunur.

---

## 🏛️ Sistem Mimarisi

### Genel Bakış

SchedularV3, katmanlı (layered) mimari kullanır:

1. **Presentation Layer:** PyQt6 GUI (5 sekme)
2. **Business Logic:** 15+ algoritma + Academic system
3. **Data Layer:** SQLite + Excel I/O
4. **Reporting:** PDF/Excel/JPEG export

**Detaylı Bilgi:** Bkz. `docs/ARCHITECTURE_COMPLETE_REPORT.md`

### Algoritma Mimarisi

15+ farklı scheduling algoritması:
- **Search:** DFS, BFS, A*, Dijkstra, IDDFS
- **Optimization:** GA, SA, HC, Tabu, PSO, Hybrid
- **Greedy:** Fast approximation
- **CP-SAT:** Constraint programming

**Algoritma Seçimi:** Sistem otomatik olarak en uygun algoritmayı seçer.

**Diagram:** `docs/ALGORITHM_DIAGRAM.puml`

### Veri Akışı
```

---

## ❓ Sık Sorulan Sorular

### Q: Program bulunamadı, ne yapmalıyım?

**A:** Şunları deneyin:
1. Max ECTS limitini artırın
2. Allow Conflicts'i aktif edin
3. Zorunlu ders sayısını azaltın
4. Farklı bir algoritma deneyin
5. Timeout süresini artırın

---

### Q: Hangi algoritmayı seçmeliyim?

**A:** Kullanım senaryonuza göre:
- **Hızlı sonuç:** Greedy veya DFS
- **En iyi kalite:** A* veya Simulated Annealing
- **Dengeli:** DFS veya IDDFS

---

### Q: Çakışmalar neden oluşuyor?

**A:** Çakışma sebepleri:
1. Aynı saatte iki ders
2. Max ECTS limiti düşük
3. Zorunlu ders sayısı fazla
4. Seçilen derslerin saatleri uyumsuz

**Çözüm:**
- Max Conflicts parametresini ayarlayın
- Bazı dersleri seçmeli yapın
- Farklı grup/şube deneyin

---

### Q: Excel dosyam yüklenmiyor?

**A:** Kontrol edin:
1. Dosya .xlsx formatında mı?
2. Gerekli sütunlar var mı?
3. Dosya bozuk değil mi?
4. Başka bir program dosyayı kullanmıyor mu?

---

## 🆘 Destek

**Sorun mu yaşıyorsunuz?**

1. **Log Dosyası:** `logs/` klasöründe
2. **GitHub Issues:** Bug bildirin
3. **Documentation:** `docs/` klasöründe daha fazla bilgi

---

## 🎯 İpuçları

1. **İlk defa kullanıyorsanız:** DFS algoritması ile başlayın
2. **Çok sayıda program istiyorsanız:** Max Results'ı artırın
3. **Hızlı sonuç istiyorsanız:** Greedy algoritması kullanın
4. **En iyi program istiyorsanız:** A* veya Simulated Annealing
5. **Karşılaştırma yapmak için:** Compare Algorithms özelliğini kullanın

---

**Son Güncelleme:** 10 Kasım 2025  
**Versiyon:** 3.0.0
