import time
import cv2
from deepface import DeepFace
import threading
import numpy as np


class Duygu:
    """
    Bu sınıf kameradan gelen görüntülerde yüzleri bulup, o yüzlerdeki duyguları anlamaya çalışıyor.
    Sanki bir arkadaşın yüzüne bakıp "mutlu musun yoksa üzgün mü?" diye sorması gibi.
    """
    
    def __init__(self):
        """Her şeyi hazırlayıp, sistemi çalışmaya hazır hale getiriyoruz"""
        # Temel ayarlar - kameranın nereden geldiği vs.
        self.video_source = 0
        self.exit = False
        self.gec = True
        self.model_yuklendi = False
        
        # Her duyguyu kaç kez gördüğümüzü sayacağız
        self.emotion = {
            "angry": 0, 
            "disgust": 0, 
            "fear": 0,
            "happy": 0, 
            "sad": 0, 
            "surprise": 0, 
            "neutral": 0
        }
        
        # Önce yüz tanıma, sonra kamera, en son analiz başlatma
        self._load_models()
        self._setup_camera()
        self._start_analysis_thread()
    
    def _load_models(self):
        """Yapay zeka modellerini yüklüyoruz - yüz bulma ve duygu anlama için"""
        # Yüz bulmak için önceden eğitilmiş bir model kullanıyoruz
        print("📦 Yüz tespit modeli yükleniyor...")
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Duyguları anlamak için DeepFace'in modelini kullanıyoruz
        print("📦 Emotion modeli yükleniyor...")
        self.emotion_model = DeepFace.build_model("Emotion")
        print("✅ Modeller yüklendi.")
        self.model_yuklendi = True
    
    def _setup_camera(self):
        """Kamerayı açıp, kaliteli görüntü alabilmesi için ayarlıyoruz"""
        self.cap = cv2.VideoCapture(self.video_source)
        
        if not self.cap.isOpened():
            raise RuntimeError("⚠️ Kameraya bağlanılamadı!")
        
        # Görüntü kalitesi için çözünürlüğü ayarlıyoruz
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    def _start_analysis_thread(self):
        """Analizi arka planda sürekli çalıştırmak için ayrı bir thread başlatıyoruz"""
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print(" Duygu analiz thread'i başlatıldı.")
    
    def _detect_faces(self, frame):
        """
        Görüntüde yüz var mı yok mu bakıyoruz. Varsa nerede olduğunu buluyoruz.
        
        Args:
            frame: Bakacağımız görüntü
            
        Returns:
            list: Bulduğumuz yüzlerin konumları [(x, y, genişlik, yükseklik), ...]
        """
        # Önce görüntüyü siyah-beyaz yapıyoruz (yüz bulma daha kolay)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Yüzleri buluyoruz
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,      # Görüntüyü ne kadar küçültüp büyütürsek
            minNeighbors=5,       # Bir yüz için en az kaç komşu piksel olsun
            minSize=(30, 30)      # En küçük yüz boyutu
        )
        
        return faces
    
    def _analyze_emotion_on_face(self, frame, face_coords):
        """
        Bulduğumuz yüze bakıp "bu kişi mutlu mu, üzgün mü?" diye anlamaya çalışıyoruz
        
        Args:
            frame: Tam görüntü
            face_coords: Yüzün nerede olduğu (x, y, genişlik, yükseklik)
            
        Returns:
            tuple: (hangi_duygu, ne_kadar_emin)
        """
        x, y, w, h = face_coords
        
        # Sadece yüz kısmını kesip alıyoruz
        face_roi = frame[y:y+h, x:x+w]
        
        # Yüz çok küçükse analiz edemeyiz
        if face_roi.shape[0] < 48 or face_roi.shape[1] < 48:
            return None, 0
        
        try:
            # DeepFace'e "bu yüzdeki duygu ne?" diye soruyoruz
            result = DeepFace.analyze(
                face_roi,
                actions=['emotion'],
                enforce_detection=False,  # Zaten yüzü bulduk, tekrar arama
                silent=True
            )
            
            # En güçlü duyguyu bulup, ne kadar emin olduğunu öğreniyoruz
            dominant_emotion = result[0]['dominant_emotion'].lower()
            confidence_score = result[0]['emotion'][dominant_emotion] / 100.0
            
            return dominant_emotion, confidence_score
            
        except Exception as e:
            print(f"Duygu analizi hatası: {e}")
            return None, 0
    
    def _process_frame(self, frame):
        """
        Bir fotoğrafı alıp tüm işlemi yapıyoruz: yüz bul, duygu anla
        
        Args:
            frame: İnceleyeceğimiz fotoğraf
        """
        # Önce yüz arayalım
        faces = self._detect_faces(frame)
        
        if len(faces) == 0:
            print("👻 Yüz tespit edilemedi.")
            return
        
        print(f" {len(faces)} yüz tespit edildi.")
        
        # En büyük yüzü seçiyoruz (muhtemelen en önemlisi o)
        largest_face = max(faces, key=lambda face: face[2] * face[3])
        
        # O yüzdeki duyguyu anlamaya çalışalım
        emotion, confidence = self._analyze_emotion_on_face(frame, largest_face)
        
        # Sonucu değerlendirip kaydedelim
        self._evaluate_emotion_result(emotion, confidence)
    
    def _evaluate_emotion_result(self, emotion, confidence):
        """
        Bulduğumuz duygu sonucuna "güvenebilir miyiz?" diye bakıyoruz
        
        Args:
            emotion: Bulduğumuz duygu
            confidence: Ne kadar emin olduğumuz (0-1 arası)
        """
        if not emotion:
            return
        
        confidence_threshold = 0.6  # %60'dan fazla eminse kabul edelim
        
        if confidence > confidence_threshold:
            # Yeterince eminiz - sayacımızı artıralım
            self.emotion[emotion] += 1
            print(f"🙂 Algılanan Duygu: {emotion} ({round(confidence * 100, 1)}%)")
        else:
            # Pek emin değiliz - sadece bilgi verelim
            print(f"🤔 Belirsiz duygu: {emotion} ({round(confidence * 100, 1)}%)")
    
    def _run(self):
        """
        Ana çalışma döngüsü - sürekli kameradan görüntü alıp analiz ediyoruz
        Bu fonksiyon arka planda çalışır durur
