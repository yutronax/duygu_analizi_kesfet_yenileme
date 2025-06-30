import os
import time
from google import genai
from google.genai import types
import pandas as pd

from googleapiclient.discovery import build
import yt_dlp

class EtiketOlusturma:


    def __init__(self):
        
       
        self.youtube_api = "SENİN_YOUTUBE_APİ_ANAHTARI"
        self.tumvideloryuklendimi = False
        self.api_key = "SENİN_GEMİNİ_APİ_ANAHTARI"
        self.client = genai.Client(api_key=self.api_key)
        

    def etiket_olustur(self, etiket_aciklamasi):
        try:
            system_instruction1 = """You are a video tag generator. Extract relevant English tags from video descriptions.

Rules:
- Return ONLY tags separated by commas
- No explanations, no sentences, no additional text
- Maximum 6 tags
- Focus on content type, genre, platform, mood
- Examples: comedy,entertainment,tiktok,funny,viral,tutorial"""
    
            response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=str(system_instruction1),  # config içinde!
                temperature=0.3,
                max_output_tokens=50,
                top_p=0.8,
                top_k=40,
            ),
            contents=[f"Video description: {etiket_aciklamasi}"]
            )
            return response.text
        
        except Exception as e:
            print(f"Hata oluştu: {e}")
            return None

    def video_sum(self, video_url):
        try:
            yol = r"VİDEO_YOLU\static"
            video_path = os.path.join(yol, video_url)
            
            # Check if file exists
            if not os.path.exists(video_path):
                print(f"Video dosyası bulunamadı: {video_path}")
                return None
            
            print(f"Video yükleniyor: {video_path}")
            
            # Upload the file
            myfile = self.client.files.upload(file=video_path)
            print(f"Dosya yüklendi. File ID: {myfile.name}")
            
            # Wait for file to be processed
            print("Dosya işlenmesi bekleniyor...")
            max_wait_time = 300  # 5 minutes maximum wait time
            wait_time = 0
            check_interval = 5  # Check every 5 seconds
            
            while wait_time < max_wait_time:
                try:
                    # Get file info to check status
                    file_info = self.client.files.get(name=myfile.name)
                    print(f"Dosya durumu: {file_info.state}")
                    
                    if file_info.state == "ACTIVE":
                        print("Dosya hazır, içerik oluşturuluyor...")
                        break
                    elif file_info.state == "FAILED":
                        print("Dosya işleme başarısız oldu")
                        return None
                    
                    time.sleep(check_interval)
                    wait_time += check_interval
                    
                except Exception as e:
                    print(f"Dosya durumu kontrol edilirken hata: {e}")
                    time.sleep(check_interval)
                    wait_time += check_interval
            
            if wait_time >= max_wait_time:
                print("Dosya işleme zaman aşımına uğradı")
                return None
            
            # Generate content
            response = self.client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=[myfile, "Summarize this video. It should consist of 3-4 sentences"]
               
            )
            print(response.text.strip())
            # Clean up: delete the uploaded file
            try:
                self.client.files.delete(name=myfile.name)
                print("Yüklenen dosya temizlendi")
            except Exception as e:
                print(f"Dosya temizlenirken hata: {e}")
            
            return response.text.strip()
            
        except Exception as e:
            print(f"Video özet oluşturulurken hata: {e}")
            import traceback
            traceback.print_exc()
            return None

    def youtube_video_ara(self, etiketler):
        max_results = 5
        api_key = self.youtube_api
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        query = " ".join(etiketler)
        
        request = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=max_results,
            type="video"
        )
        response = request.execute()
        
        videolar = []
        print("YouTube araması yapılıyor...")
        for item in response['items']:
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            description = item['snippet']['description']
            print(f"Video ID: {video_id}, Başlık: {title}")
            videolar.append({
                'video_id': video_id,
                'title': title,
                'description': description
            })
        
        return videolar

    def videolari_indir(self, video_list, kayit_klasoru):
        for video in video_list:
            if isinstance(video, dict) and 'video_id' in video:
                url = f"https://www.youtube.com/watch?v={video['video_id']}"
            elif isinstance(video, str):
                url = video
            else:
                continue

            print(f"İndiriliyor: {url}")

            ydl_opts = {
                'outtmpl': os.path.join(kayit_klasoru, '%(id)s.%(ext)s'),
                'format': 'best',
                'merge_output_format': 'mp4',
                'noplaylist': True,
                'quiet': False,
                'ignoreerrors': False
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                print(f"Başarıyla indirildi: {url}")
            except Exception as e:
                print(f"Video indirilemedi: {url}")
                import traceback
                traceback.print_exc()
            self.tumvideloryuklendimi = True


    def main(self):
       
       
        
        try:
            videolar = pd.read_csv(r"video_data.csv")
            alinacak_videolar = videolar[videolar['emotion'] == 'happy']['video_name'].tolist()
        except Exception as e:
            print(f"CSV dosyası okunamadı: {e}")
            return
        
        toplam_etiketler = []
        
        for video in alinacak_videolar:
            print(f"\nİşleniyor: {video}")
            
            açıklama = self.video_sum(video)
            if not açıklama:
                print(f"Video için açıklama alınamadı: {video}")
                continue
                
            etiket = self.etiket_olustur(açıklama)
            if etiket:
                print(f"Oluşturulan Etiket: {etiket}")
                toplam_etiketler.append(etiket)
            else:
                print("Etiket oluşturulamadı.")
        
        if not toplam_etiketler:
            print("Hiç etiket oluşturulamadı!")
            return
        
        # Etiketleri birleştir ve temizle
        etiketler = []
        for etiket in toplam_etiketler:
            etiketler.extend([e.strip() for e in etiket.split(",")])
        etiketler = list(set(etiketler))  # Tekrarları kaldır

        print(f"\nToplam Etiketler ({len(etiketler)}): {etiketler}")
        
        # YouTube'da ara
        sonuclar = self.youtube_video_ara(etiketler)
        print(f"\nToplam {len(sonuclar)} video bulundu.")

        # Sonuçları göster
        for i, v in enumerate(sonuclar, 1):
            print(f"\n{i}. Video:")
            print(f"Video ID: {v['video_id']}")
            print(f"Başlık: {v['title']}")
            print(f"Açıklama: {v['description'][:100]}...")  # İlk 100 karakter
            print(f"Link: https://www.youtube.com/watch?v={v['video_id']}")
            print("-" * 40)
        
        # İndirme klasörünü oluştur ve videoları indir
        kayit_klasoru = r"C:\Users\MONSTER\3D Objects\yazprojeler\assemble\flask_proje\venv\static\downloaded_videos"
        os.makedirs(kayit_klasoru, exist_ok=True)
        
        print(f"\nVideolar {kayit_klasoru} klasörüne indiriliyor...")
        self.videolari_indir(sonuclar, kayit_klasoru)
        print("İşlem tamamlandı!")



