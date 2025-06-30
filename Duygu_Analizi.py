import time
import cv2
from deepface import DeepFace
import threading
import numpy as np

class Duygu:
    def __init__(self):
        self.video_source = 0
        self.exit = False
        self.gec = True
        self.model_yuklendi = False
        self.emotion = {
            "angry": 0, "disgust": 0, "fear": 0,
            "happy": 0, "sad": 0, "surprise": 0, "neutral": 0
        }
        
        # Yüz tespiti için Haar Cascade yükle
        print(" Yüz tespit modeli yükleniyor...")
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Emotion modeli yükle
        print(" Emotion modeli yükleniyor...")
        self.emotion_model = DeepFace.build_model("Emotion")
        print(" Modeller yüklendi.")
        self.model_yuklendi = True
        
        # Kamera başlat
        self.cap = cv2.VideoCapture(self.video_source)
        if not self.cap.isOpened():
            raise RuntimeError(" Kameraya bağlanılamadı!")
        
        # Kamera ayarları
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("🔄 Duygu analiz thread'i başlatıldı.")
    
    def _detect_faces(self, frame):
        """Yüz tespiti yap"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        return faces
    
    def _analyze_emotion_on_face(self, frame, face_coords):
        """Tespit edilen yüz üzerinde duygu analizi yap"""
        x, y, w, h = face_coords
        
        # Yüz bölgesini kırp
        face_roi = frame[y:y+h, x:x+w]
        
        # Minimum boyut kontrolü
        if face_roi.shape[0] < 48 or face_roi.shape[1] < 48:
            return None, 0
        
        try:
            # Sadece kırpılmış yüz bölgesi üzerinde duygu analizi
            result = DeepFace.analyze(
                face_roi,
                actions=['emotion'],
                enforce_detection=False,  # Zaten yüz tespit ettik
                silent=True
            )
            
            dominant_emotion = result[0]['dominant_emotion'].lower()
            score = result[0]['emotion'][dominant_emotion] / 100.0  # Yüzde olarak normalize et
            
            return dominant_emotion, score
            
        except Exception as e:
            print(f" Duygu analizi hatası: {e}")
            return None, 0
    
    def _run(self):
        frame_count = 0
        last_analysis_time = 0
        analysis_interval = 0.5  # 500ms'de bir analiz yap
        
        while True:
            if self.exit:
                break
            
            if self.gec or not self.model_yuklendi:
                time.sleep(0.1)
                continue
            
            ret, frame = self.cap.read()
            if not ret:
                print("Kameradan veri alınamadı, tekrar deniyor...")
                time.sleep(0.1)
                continue
            
            current_time = time.time()
            
            # Belirli aralıklarla analiz yap (performans için)
            if current_time - last_analysis_time >= analysis_interval:
                # 1. Önce yüz tespiti yap
                faces = self._detect_faces(frame)
                
                if len(faces) > 0:
                    print(f"👤 {len(faces)} yüz tespit edildi.")
                    
                    # En büyük yüz üzerinde analiz yap
                    largest_face = max(faces, key=lambda face: face[2] * face[3])
                    
                    # 2. Tespit edilen yüz üzerinde duygu analizi yap
                    emotion, score = self._analyze_emotion_on_face(frame, largest_face)
                    
                    if emotion and score > 0.6:  # Güvenilir sonuçlar için threshold
                        self.emotion[emotion] += 1
                        print(f"🙂 Algılanan Duygu: {emotion} ({round(score * 100, 1)}%)")
                    elif emotion:
                        print(f"🤔 Belirsiz duygu: {emotion} ({round(score * 100, 1)}%)")
                else:
                    print("👻 Yüz tespit edilemedi.")
                
                last_analysis_time = current_time
            
            frame_count += 1
            time.sleep(0.03)  # ~30 FPS için
        
        self.cap.release()
        print("🎬 Kamera kapatıldı ve analiz thread'i durdu.")
    
    def play(self):
        """Duygu analizini "oynat" (frame almaya başla)"""
        self.gec = False
        print("▶️ Duygu analizi başlatıldı.")
    
    def pause(self):
        """Duygu analizini "durdur" (frame okumayı bekle)"""
        self.gec = True
        print("⏸️ Duygu analizi duraklatıldı.")
    
    def stop(self):
        """Duygu analizini tamamen sonlandır (kamera serbest bırak)"""
        self.gec = True
        self.exit = True
        print("⏹️ Duygu analizi sonlandırılıyor...")
        
        # Thread'in bitmesini bekle
        if self.thread.is_alive():
            self.thread.join(timeout=2)
    
    def get_dominant_emotion(self):
        """En baskın duyguyu döndür"""
        if not any(self.emotion.values()):
            return None
        return max(self.emotion, key=self.emotion.get)
    
    def get_emotion_stats(self):
        """Tüm duygu istatistiklerini döndür"""
        total = sum(self.emotion.values())
        if total == 0:
            return {}
        
        return {emotion: round((count / total) * 100, 1) 
                for emotion, count in self.emotion.items()}
    
    def reset_stats(self):
        """Duygu istatistiklerini sıfırla"""
        self.emotion = {
            "angry": 0, "disgust": 0, "fear": 0,
            "happy": 0, "sad": 0, "surprise": 0, "neutral": 0
        }
        print("📊 Duygu istatistikleri sıfırlandı.")

# Kullanım örneği
if __name__ == "__main__":
    try:
        # Duygu analizi nesnesini oluştur
        duygu_analizi = Duygu()
        
        # Analizi başlat
        duygu_analizi.play()
        
        # 30 saniye analiz yap
        print(" 30 saniye boyunca duygu analizi yapılacak...")
        time.sleep(30)
        
        # Sonuçları göster
        print("\nDuygu Analizi Sonuçları:")
        stats = duygu_analizi.get_emotion_stats()
        for emotion, percentage in stats.items():
            print(f"  {emotion}: %{percentage}")
        
        print(f"\n En baskın duygu: {duygu_analizi.get_dominant_emotion()}")
        
        # Analizi durdur
        duygu_analizi.stop()
        
    except KeyboardInterrupt:
        print("\nKullanıcı tarafından durduruldu.")
        duygu_analizi.stop()
    except Exception as e:
        print(f" Hata: {e}")
        if 'duygu_analizi' in locals():
            duygu_analizi.stop()
