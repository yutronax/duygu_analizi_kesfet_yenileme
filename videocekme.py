import os
import time
import threading
from tqdm import tqdm
import yt_dlp
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class VideoDownloader:
    """
    YouTube Shorts videolarını otomatik olarak bulup indiren sınıf.
    Sanki YouTube'da geziniyormuş gibi videoları tek tek bulup kaydediyor.
    """
    
    def __init__(self):
        """Her şeyi hazırlayıp, indirme için gerekli ayarları yapıyoruz"""
        self.videoyuklendimi = False
        self.video_list = []  # Bulduğumuz videoların linklerini burada saklayacağız
        
        # Videoları nereye kaydedeceğimizi belirliyoruz
        self.kayit_klasoru = r"C:\Users\MONSTER\3D Objects\yazprojeler\assemble\flask_proje\venv\static\videos"
        
        # İlerleme takibi için - kullanıcıya "ne kadar bitti" diye göstermek için
        self.progress = 0
        self.status_message = "Hazırlanıyor..."
        self.is_complete = False
        self.driver = None  # Web tarayıcısı kontrolcüsü

    def _prepare_directory(self):
        """Kayıt klasörünü temizleyip hazırlıyoruz - eski dosyalar varsa sil, yoksa oluştur"""
        import shutil
        if os.path.exists(self.kayit_klasoru):
            shutil.rmtree(self.kayit_klasoru, ignore_errors=True)  # Eskisini tamamen sil
        os.makedirs(self.kayit_klasoru, exist_ok=True)  # Yenisini oluştur

    def _setup_driver(self):
        """
        Chrome tarayıcısını robot gibi kullanmak için hazırlıyoruz.
        Görünmez modda çalışacak, sanki bir insan kullanıyormuş gibi görünecek.
        """
        self._prepare_directory()
        try:
            chrome_options = Options()
            # Tarayıcı görünmesin, arka planda çalışsın
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")  # Grafik kartını kullanma
            chrome_options.add_argument("--no-sandbox")  # Güvenlik sınırlarını gevşet
            chrome_options.add_argument("--window-size=1920,1080")  # Pencere boyutu
            chrome_options.add_argument("--disable-dev-shm-usage")  # Bellek ayarı
            
            # İnsan gibi görünmek için kullanıcı aracısı ekle
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # Chrome sürücüsünü başlat
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            return True
        except Exception as e:
            print(f"Tarayıcı başlatılamadı: {e}")
            self.status_message = f"Tarayıcı hatası: {e}"
            return False

    def collect_videos(self, count=5):
        """
        YouTube Shorts'a gidip, videoları tek tek gezinerek linklerini topluyoruz.
        Sanki birisi telefonda shorts izliyormuş gibi.
        
        Args:
            count: Kaç tane video toplayalım
        """
        if not self._setup_driver():
            return False
            
        try:
            self.status_message = "YouTube'a bağlanılıyor..."
            self.driver.get("https://www.youtube.com/shorts/")
            
            # Sayfa tamamen yüklenene kadar bekle
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "ytd-shorts"))
            )
            
            self.status_message = "Videolar toplanıyor..."
            
            # İstediğimiz kadar video topla
            for i in range(count):
                try:
                    # Şu anki videonun linkini al
                    current_url = self.driver.current_url
                    
                    # Gerçekten shorts videosu mu kontrol et
                    if "shorts" not in current_url:
                        print(f"Bu shorts değil, atlanıyor: {current_url}")
                        continue
                    
                    print(f"{i+1}. video bulundu: {current_url}")
                    self.video_list.append(current_url)
                    
                    # İlerleme çubuğunu güncelle (her video için %20)
                    self.progress = (i + 1) * 20
                    
                    # Son video değilse, bir sonrakine geç
                    if i < count - 1:
                        try:
                            # "Sonraki video" butonunu farklı yollarla bulmaya çalış
                            next_selectors = [
                                '//button[@aria-label="Sonraki video"]',
                                '//button[@aria-label="Next video"]',
                                '//button[contains(@class, "navigation-button")]//yt-icon[@class="style-scope ytd-button-renderer"]',
                                '.navigation-button[title*="next" i]'
                            ]
                            
                            next_button = None
                            for selector in next_selectors:
                                try:
                                    if selector.startswith('//'):  # XPath
                                        next_button = WebDriverWait(self.driver, 5).until(
                                            EC.element_to_be_clickable((By.XPATH, selector))
                                        )
                                    else:  # CSS selector
                                        next_button = WebDriverWait(self.driver, 5).until(
                                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                        )
                                    break  # Buldu, döngüden çık
                                except:
                                    continue  # Bu selector çalışmadı, bir sonrakini dene
                            
                            if next_button:
                                next_button.click()
                                time.sleep(3)  # Video değişsin diye bekle
                            else:
                                # Buton bulunamadı, klavye tuşu ile dene
                                print("Sonraki butonu bulunamadı, klavye ile deniyorum...")
                                from selenium.webdriver.common.keys import Keys
                                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ARROW_DOWN)
                                time.sleep(3)
                                
                        except Exception as e:
                            print(f"Sonraki videoya geçemedi: {e}")
                            # Son çare olarak klavye tuşu dene
                            try:
                                from selenium.webdriver.common.keys import Keys
                                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ARROW_DOWN)
                                time.sleep(3)
                            except:
                                pass  # Hiçbir şey olmadı, devam et
                    
                except Exception as e:
                    print(f"{i+1}. video toplanırken hata: {e}")
                    continue  # Bu videoyu atla, devam et
                    
            return len(self.video_list) > 0  # En az bir video bulduk mu?
            
        except Exception as e:
            print(f"Video toplama genel hatası: {e}")
            self.status_message = f"Video toplama hatası: {e}"
            return False
        finally:
            # Her durumda tarayıcıyı kapat
            if self.driver:
                self.driver.quit()

    def download_videos(self):
        """
        Topladığımız video linklerini tek tek indiriyoruz.
        Her videoyu güzel bir isimle bilgisayara kaydediyoruz.
        """
        if not self.video_list:
            self.status_message = "İndirilecek video bulunamadı!"
            return False
            
        total_videos = len(self.video_list)
        successful_downloads = 0  # Kaç tane başarıyla indirdik
        
        for index, url in enumerate(self.video_list, start=1):
            try:
                self.status_message = f"Video {index}/{total_videos} indiriliyor..."
                
                # Video indirme ayarları - yt-dlp'ye "böyle indir" diyoruz
                ydl_opts = {
                    'outtmpl': os.path.join(self.kayit_klasoru, f'video_{index}.%(ext)s'),  # Dosya adı
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # En iyi kalite
                    'quiet': True,  # Sessiz çalış, çok konuşma
                    'no_warnings': True,  # Uyarı verme
                    'writethumbnail': False,  # Küçük resim indirme (hız için)
                    'writeinfojson': False,   # Video bilgilerini dosyaya yazma
                    'extractaudio': False,  # Sadece ses çıkarma
                    'audioquality': 0,  # Ses kalitesi
                    'embed_subs': False,  # Altyazıları gömme
                    'writesubtitles': False,  # Altyazı dosyası oluşturma
                }

                # yt-dlp ile videoyu indir
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    
                successful_downloads += 1
                print(f" {index}. video başarıyla indirildi!")
                
                # İlerleme çubuğunu güncelle (toplama %50, indirme %50)
                download_progress = (index / total_videos) * 50
                self.progress = 50 + download_progress
                
            except Exception as e:
                print(f"{index}. video indirilemedi: {e}")
                continue  # Bu video olmadı, devam et
                
        return successful_downloads > 0  # En az bir video indirebildik mi?

    def get_progress(self):
        """
        İşlemin ne kadar ilerlediğini söylüyoruz.
        Web sayfasında progress bar göstermek için kullanılıyor.
        """
        return {
            'progress': min(self.progress, 100),  # %100'ü geçmesin
            'status': self.status_message,  # "Ne yapıyor şu an?"
            'is_complete': self.is_complete,  # "Bitti mi?"
            'video_count': len(self.video_list)  # "Kaç video buldu?"
        }

    def main(self, count=5):
        """
        Ana işlem - önce videoları topla, sonra indir.
        Bu fonksiyon her şeyi baştan sona hallediyor.
        
        Args:
            count: Kaç video indirmek istiyoruz
        """
        try:
            # Her şeyi sıfırla, temiz başlayalım
            self.videoyuklendimi = False
            self.is_complete = False
            self.progress = 0
            
            # 1. Adım: Videoları topla
            self.status_message = "Videolar toplanıyor..."
            if not self.collect_videos(count=count):
                self.status_message = "Video toplama başarısız!"
                self.is_complete = True
                return False
            
            # 2. Adım: Videoları indir
            self.status_message = "Videolar indiriliyor..."
            success = self.download_videos()
            
            # Sonuçları değerlendir
            if success:
                self.videoyuklendimi = True
                self.progress = 100
                self.status_message = f"{len(self.video_list)} video başarıyla indirildi!"
                print("🎉 Tüm işlemler tamamlandı!")
            else:
                self.status_message = " Video indirme başarısız!"
                
            self.is_complete = True
            return success
            
        except Exception as e:
            print(f"Ana işlem hatası: {e}")
            self.status_message = f"Hata: {e}"
            self.is_complete = True
            return False


# Web uygulaması için yardımcı fonksiyonlar

def video_downloader_thread(downloader, count=5):
    """
    Video indirme işlemini arka planda çalıştırmak için.
    Web sayfası donmasın diye ayrı thread'de çalışıyor.
    """
    try:
        downloader.main(count=count)
    except Exception as e:
        print(f"Arka plan işlemi hatası: {e}")
        downloader.status_message = f"İşlem hatası: {e}"
        downloader.is_complete = True


# Global değişken - şu anki indirme işlemini takip etmek için
current_downloader = None

def start_video_download(count=5):
    """
    Video indirme işlemini başlat.
    Web sayfasından çağrıldığında bu fonksiyon çalışıyor.
    """
    global current_downloader
    
    current_downloader = VideoDownloader()
    
    # Arka planda çalışacak thread oluştur
    thread = threading.Thread(
        target=video_downloader_thread, 
        args=(current_downloader, count),
        daemon=True  # Ana program kapanınca bu da kapansın
    )
    thread.start()
    return current_downloader

def get_download_status():
    """
    İndirme durumunu kontrol et.
    Web sayfası "ne kadar bitti?" diye sorduğunda bu çalışıyor.
    """
    global current_downloader
    if current_downloader:
        return current_downloader.get_progress()
    return {
        'progress': 0, 
        'status': 'Başlatılmadı', 
        'is_complete': False, 
        'video_count': 0
    }


# Programı direkt çalıştırdığımızda ne olacak
if __name__ == "__main__":
    import pandas as pd
    
    # Video indiriciyi oluştur
    downloader = VideoDownloader()
    
    # Bulunan videoları CSV dosyasına kaydet (isteğe bağlı)
    videolar = pd.DataFrame(columns=["video_url"], index=downloader.video_list)
    videolar.to_csv("video_list.csv", index=False)
    
    # 3 video indir
    success = downloader.main(count=3)
    print(f"İşlem {'başarılı' if success else 'başarısız'}!")
