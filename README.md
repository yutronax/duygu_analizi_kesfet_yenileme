# Duygu Analizi ile Video Keşfet

Bu proje, kullanıcıların yüz ifadelerini analiz ederek kişiselleştirilmiş video önerileri sunan bir Flask web uygulamasıdır. Kameradan alınan görüntülerde duygu tespiti yapılarak kullanıcının beğenebileceği videolar önerilir.

## Özellikler

- **Gerçek Zamanlı Duygu Analizi**: Kamera üzerinden yüz ifadelerini analiz eder
- **Kullanıcı Yönetimi**: Kayıt olma ve giriş yapma sistemi
- **Video İzleme**: YouTube Shorts tarzı video izleme deneyimi
- **Akıllı Öneriler**: Duygu analizine dayalı kişiselleştirilmiş video önerileri
- **Otomatik Video İndirme**: YouTube'dan benzer içerikleri otomatik indirir
- **Modern Web Arayüzü**: Responsive tasarım ve kullanıcı dostu interface

## Ekran Görüntüleri

Proje modern ve kullanıcı dostu bir web arayüzüne sahiptir:
- Gradient arkaplan tasarımı
- Kart tabanlı layout
- Responsive tasarım
- Video oynatıcı ile entegre duygu analizi
- Temiz ve anlaşılır navigasyon

## Kurulum

### Gereksinimler

Python 3.8+ ve aşağıdaki kütüphaneler gereklidir:

```bash
pip install flask opencv-python deepface pandas google-generativeai yt-dlp selenium webdriver-manager
```

### Chrome Driver

Selenium için Chrome WebDriver gereklidir. `webdriver-manager` otomatik olarak indirecektir.

### API Anahtarları

`etiketolusturma.py` dosyasında Google AI API anahtarlarını kendi anahtarlarınızla değiştirin:

```python
self.youtube_api = "YOUR_YOUTUBE_API_KEY"
self.api_key = "YOUR_GOOGLE_AI_API_KEY"
```

## Kullanım

### Uygulamayı Başlatma

```bash
python website1.py
```

Uygulama `http://localhost:5000` adresinde çalışacaktır.

### Kullanım Adımları

1. **Kayıt Ol**: Ana sayfadan yeni hesap oluşturun
2. **Giriş Yap**: Kullanıcı bilgilerinizle giriş yapın
3. **Video İzle**: Dashboard'dan "Video İzle" seçeneğini seçin
4. **Duygu Analizi**: Videolar izlenirken kamera duygu analizini otomatik yapar
5. **Kaydet**: İzleme tamamlandığında analizi kaydedin
6. **Öneriler**: Size özel video önerileri görüntüleyin

## Dosya Yapısı

```
├── website1.py              # Ana Flask uygulaması
├── duyguanalizi.py          # Duygu analizi modülü
├── videocekme.py            # Video indirme modülü
├── etiketolusturma.py       # Video etiketleme ve öneri sistemi
├── kullanıcıbilgileri.py    # Kullanıcı veritabanı yönetimi
├── templates/               # HTML şablonları
├── static/                  # CSS, JS ve medya dosyaları
│   ├── videos/             # İzlenecek videolar
│   └── downloaded_videos/   # Önerilen videolar
└── video_data.csv          # Duygu analizi sonuçları
```

## Teknik Detaylar

### Duygu Analizi
- **DeepFace** kütüphanesi kullanılarak gerçek zamanlı yüz ifade analizi
- OpenCV ile yüz tespiti
- 7 farklı duygu kategorisi: mutlu, üzgün, kızgın, şaşkın, korkmuş, iğrenmiş, nötr

### Video Öneri Sistemi
- Google AI ile video içerik analizi
- Duygu durumuna göre etiket oluşturma
- YouTube API ile benzer içerik arama
- Otomatik video indirme

### Veritabanı
- SQLite veritabanı kullanılarak kullanıcı bilgileri saklanır
- Şifre tekrarı kontrolü
- Kullanıcı oturumu yönetimi

## Güvenlik Notları

- API anahtarlarınızı public repository'lerde paylaşmayın
- Gerçek kullanımda şifreleri hash'leyerek saklayın
- Dosya yollarını sistem durumunuza göre ayarlayın

## Katkıda Bulunma

1. Projeyi fork edin
2. Özellik branch'i oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## İletişim

Proje Linki: [https://github.com/yutronax/duygu_analizi_kesfet_yenileme](https://github.com/yutronax/duygu_analizi_kesfet_yenileme)

## Sorun Giderme

### Yaygın Sorunlar

- **Kamera erişim hatası**: Kamera izinlerini kontrol edin
- **Model yükleme hatası**: İnternet bağlantınızı kontrol edin
- **Video indirme hatası**: YouTube API limitlerini kontrol edin
- **Chrome driver hatası**: Chrome tarayıcınızın güncel olduğundan emin olun
