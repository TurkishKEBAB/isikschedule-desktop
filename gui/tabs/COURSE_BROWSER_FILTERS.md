# 📚 Course Browser - Advanced Filters Guide

## 🎯 Özet

Course Browser artık **920+ dersi** kolayca filtreleyebileceğiniz gelişmiş bir filtreleme sistemine sahip!

## 🔍 Filtre Kategorileri

### 1. **Hızlı Arama & Sıralama** (Her zaman görünür)
- **🔍 Arama Çubuğu**: Ders kodu, ismi veya eğitmen ismi ile arama
- **🔽 Show/Hide Filters**: Gelişmiş filtreleri göster/gizle
- **📊 Sıralama Seçenekleri**:
  - Code (A-Z / Z-A)
  - Name (A-Z / Z-A)
  - ECTS (Low-High / High-Low)
  - Capacity (Most Available)

---

### 2. **Temel Filtreler** 🏢

#### Kampüs Filtresi
- ☑️ Şile
- ☑️ Online
- ☑️ All (ikisini de göster)

#### Fakülte Filtresi
Dropdown'dan seçim:
- Mühendislik ve Doğa Bilimleri Fakültesi
- İktisadi, İdari ve Sosyal Bilimler Fakültesi
- Sanat, Tasarım ve Mimarlık Fakültesi

#### Ders Kodu Prefix Filtresi
- COMP, ARCH, BUSI, CIVL, BMED vb.
- Yazarak da arama yapabilirsiniz

#### Eğitmen Filtresi
- Tüm eğitmenlerin listesi
- Yazarak arama yapabilirsiniz

---

### 3. **Akademik Filtreler** 💳

#### AKTS Kredisi (Slider)
- **Min-Max**: 0-12 arası
- Örnek: Sadece 5-8 AKTS arası dersler

#### Sınıf Düzeyi
- ☑️ 1xxx (Freshman)
- ☑️ 2xxx (Sophomore)
- ☑️ 3xxx (Junior)
- ☑️ 4xxx (Senior)

---

### 4. **Zaman Filtreleri** ⏰

#### Gün Seçici
- ☑️ Mon, Tue, Wed, Thu, Fri, Sat, Sun
- Sadece belirli günlerde olan dersleri göster

#### Zaman Aralığı
- ☑️ **Morning (1-4)**: 08:00-12:00 arası
- ☑️ **Afternoon (5-8)**: 13:00-17:00 arası
- ☑️ **Evening (9+)**: 17:00+ akşam dersleri

#### Ders Tipi
- ☑️ **Lecture**: Teorik dersler
- ☑️ **Lab**: Laboratuvar dersleri
- ☑️ **Problem Session**: Problem çözüm saatleri

---

### 5. **Özel Filtreler** 🎯

#### Live Section (Online/Fiziksel)
- ☑️ **Online Only**: Sadece online dersler
- ☑️ **Physical Only**: Sadece fiziksel dersler (Şile)
- ☑️ **Both**: Her ikisi de

#### Çakışma Kontrolü
- ☑️ **Hide courses conflicting with selected**
  - Course Selector'da seçtiğiniz derslerle çakışan dersleri gizler
  - Zaman充돌u önler!

#### Favoriler
- ☑️ **Show only favorites**
  - Sadece favori işaretlediğiniz dersleri gösterir
  - ⭐ butonuyla ders favorilere eklenir

---

## 🗑️ Ders Silme

Her dersin sağında **🗑️ Delete** butonu var:
- Tıklayarak dersi listeden **kalıcı olarak** silebilirsiniz
- Silinen dersler Course Selector'a da geçmez
- **Dikkat**: Geri alınamaz! Excel'i tekrar yüklerseniz dersler geri gelir.

---

## ⭐ Favori Sistemi

Her dersin solunda **⭐/☆** butonu var:
- **☆**: Favorilere ekle
- **⭐**: Favorilerden çıkar
- Favori dersler "Show only favorites" filtresiyle gösterilebilir

---

## 📊 Bilgi Paneli

Alt kısımda gösterilen bilgiler:
```
📊 Showing 87 of 920 courses (9.5%)
```
- **87**: Filtrelerden geçen dersler
- **920**: Toplam ders sayısı
- **9.5%**: Gösterilen yüzde

---

## 💡 Kullanım Örnekleri

### Örnek 1: Sadece Online COMP Dersleri
1. "Show Filters" tıkla
2. Campus → Sadece "Online" işaretle
3. Prefix → "COMP" seç
4. Apply Filters

### Örnek 2: Pazartesi Sabahı Olan Dersler
1. Days → Sadece "Mon" işaretle
2. Time → Sadece "Morning (1-4)" işaretle
3. Diğer günleri kapat

### Örnek 3: Yüksek AKTS Dersler
1. ECTS slider → Min: 6, Max: 12
2. Sort → "ECTS (High-Low)"

### Örnek 4: Seçtiklerimle Çakışmayan Dersler
1. Course Selector'da birkaç ders seç
2. Course Browser'a dön
3. "Hide courses conflicting with selected" işaretle
4. Artık sadece çakışmayan dersler görünür!

---

## 🔄 Filtreleri Temizleme

**Clear All Filters** butonu:
- Tüm filtreleri varsayılan değerlere döndürür
- Arama çubuğunu temizler
- Sıralamayı sıfırlar

---

## 🎨 Renk Kodları

Tabloda:
- **Mavi kod**: Ders kodu (tıklanabilir)
- **Yeşil type**: Lecture
- **Mavi type**: Lab
- **Kırmızı type**: Problem Session
- **⭐ Sarı yıldız**: Favorilerde
- **☆ Beyaz yıldız**: Favorilerde değil

---

## 🚀 Performans İpuçları

920 ders varken:
1. Önce **temel filtreleri** kullanın (kampüs, fakülte)
2. Sonra **zaman filtrelerini** ekleyin
3. Arama için **tam ders kodunu** yazın (hızlıdır)
4. Gereksiz dersleri **silin** (performans artar)

---

## 🐛 Bilinen Limitler

- **Kapasite filtresi**: Şu anda Course model'de kota bilgisi yok
- **Elective/Core filtresi**: Course model'e eklenebilir
- **Prerequisite filtresi**: Academic tab'de mevcut

---

## 📝 Gelecek Geliştirmeler

- [ ] Kota/Kapasite bilgisi ekle
- [ ] Filtre preset'leri kaydetme
- [ ] Toplu ders silme
- [ ] Excel export (sadece filtrelenenler)
- [ ] Çakışma görselleştirmesi

---

**Yazar**: GitHub Copilot  
**Tarih**: 10 Kasım 2025  
**Versiyon**: SchedularV3 Phase 8
