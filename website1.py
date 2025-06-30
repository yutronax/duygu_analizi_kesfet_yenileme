import math
from flask import Flask, flash, redirect, render_template, request, url_for, session
import kullanıcıbilgileri, os, videocekme, duyguanalizi , pandas as pd, threading, etiketolusturma

app = Flask(__name__)

duygu_analizi = duyguanalizi.Duygu()   
video_data = pd.DataFrame(columns=["video_name", "emotion","video_url"])
video_list = []
current_index = 0
duygu_analizleri = []
video_adi = []
video_yuklendimi=True
video_indirme = videocekme.VideoDownloader()
etiket_indirme=etiketolusturma.EtiketOlusturma()
app.secret_key = 'your-secret-key-here'  
def videoları_içeri_aktar():
    VIDEO_FOLDER = r"C:\Users\MONSTER\3D Objects\yazprojeler\assemble\flask_proje\venv\static\videos"
    VALID_EXTENSIONS = (".mp4", ".webm", ".mkv", ".m4v", ".mov", ".ogg")
    try:
        return sorted([f for f in os.listdir(VIDEO_FOLDER)
                       if f.lower().endswith(VALID_EXTENSIONS)])
    except FileNotFoundError:
        return []

video_list = videoları_içeri_aktar()

@app.route('/')
def index():
   
    return redirect(url_for('anasayfa'))

@app.route('/anasayfa', methods=['GET', 'POST'])
def anasayfa():
    kullanici_bilgileri = kullanıcıbilgileri.KullanıcıBilgileri()
    
    if request.method == 'POST':
        # Giriş formu işlemi
        if 'giris' in request.form:
            isim = request.form.get('isim')
            soyisim = request.form.get('soyisim') 
            sifre = request.form.get('sifre')
            
            bilgiler = kullanici_bilgileri.kullanıcı_bilgilerini_getir(isim)
            
            if bilgiler and bilgiler['sifre'] == sifre:
                # Session'a kullanıcı bilgilerini kaydet
                session['user_id'] = bilgiler['id']
                session['user_name'] = bilgiler['isim']
                session['user_surname'] = bilgiler['soyisim']
                
                flash(f"Merhaba {bilgiler['isim']} {bilgiler['soyisim']}! Giriş başarılı.", 'success')
                return redirect(url_for('dashboard'))  
            else:
                flash("Kullanıcı adı veya şifre yanlış. Lütfen tekrar deneyin.", 'error')
                return render_template('anasayfa.html')
        
        # Kayıt ol butonuna basıldığında
        elif 'kayit_ol' in request.form:
            return redirect(url_for('kayit_ol'))
    
    # GET isteği için ana sayfayı göster
    return render_template('anasayfa.html')

@app.route('/kayit_ol', methods=['GET', 'POST'])
def kayit_ol():
    if request.method == 'POST':
        isim = request.form.get('isim')
        soyisim = request.form.get('soyisim')
        sifre = request.form.get('sifre')
        
        # Boş alan kontrolü
        if not isim or not soyisim or not sifre:
            flash("Lütfen tüm alanları doldurun.", 'error')
            return render_template('kayit_ol.html')
        
        kullanici_bilgileri = kullanıcıbilgileri.KullanıcıBilgileri()
        
        # Kullanıcı adı kontrolü
        mevcut_kullanici = kullanici_bilgileri.kullanıcı_bilgilerini_getir(isim)
        if mevcut_kullanici:
            flash("Bu kullanıcı adı zaten kullanılıyor. Lütfen farklı bir kullanıcı adı seçin.", 'error')
            return render_template('kayit_ol.html')
        
        # Şifre kontrolü - aynı şifre var mı?
        sifre_kullaniliyormu = False
        for sifre_kontrol in kullanici_bilgileri.sifreler_getir():
            if sifre == sifre_kontrol:
                sifre_kullaniliyormu = True
                break
        
        if sifre_kullaniliyormu:
            flash("Bu şifre zaten kullanılıyor. Lütfen farklı bir şifre girin.", 'error')
            return render_template('kayit_ol.html')
        else:
            # Kullanıcı bilgilerini ekle
            kullanici_bilgileri.kullanıcı_bilgilerini_ekle(isim, soyisim, sifre)
            flash(f"Merhaba {isim} {soyisim}! Kullanıcı bilgileri başarıyla eklendi.", 'success')
            return redirect(url_for('anasayfa'))
    
    return render_template('kayıt_ol.html')

@app.route('/dashboard')
def dashboard():
    """Giriş yapmış kullanıcılar için dashboard"""
    if 'user_id' not in session:
        flash("Lütfen önce giriş yapın.", 'error')
        return redirect(url_for('anasayfa'))
    
    return render_template('dashboard.html', 
                         user_name=session.get('user_name'),
                         user_surname=session.get('user_surname'))

@app.route('/cikis')
def cikis():
    """Kullanıcı çıkışı"""
    session.clear()
    flash("Başarıyla çıkış yaptınız.", 'success')
    return redirect(url_for('anasayfa'))

@app.route('/kullanici_bilgileri', methods=['GET'])
def kullanici_bilgileri_goruntule():
    if 'user_id' not in session:
        return redirect(url_for('anasayfa'))
    
    isim = request.args.get('isim')
    kullanici_bilgileri = kullanıcıbilgileri.KullanıcıBilgileri()
    bilgiler = kullanici_bilgileri.kullanıcı_bilgilerini_getir(isim)
    
    if bilgiler:
        return f"ID: {bilgiler['id']}, İsim: {bilgiler['isim']}, Soyisim: {bilgiler['soyisim']}"
    else:
        return "Kullanıcı bulunamadı."

@app.route('/video', methods=['GET', 'POST'])
def video_izle():
    if 'user_id' not in session:
        flash("Video izlemek için lütfen giriş yapın.", 'error')
        return redirect(url_for('anasayfa'))

    global current_index, duygu_analizleri, video_adi, video_list,video_yuklendimi

    # Video listesi boşsa güncelle
    if not video_list:
        video_list = videoları_içeri_aktar()
        if not video_list:
            flash("Henüz video bulunmamaktadır.", 'error')
            return redirect(url_for('dashboard'))

   
    if request.is_json:
        data = request.get_json()
        durum = data.get("durum")

        if durum == "play" and duygu_analizi.model_yuklendi:
            duygu_analizi.play()
        elif durum == "pause":
            duygu_analizi.pause()
        elif durum == "bitti":
            duygu_analizi.pause()
        return ('', 204)

    
    if request.method == "POST":
        action = request.form.get("action")

        if action == "next":
            # Mevcut analiz kaydediliyor
            dominant = duygu_analizi.get_dominant_emotion()
            duygu_analizleri.append(dominant)
            video_adi.append(f"videos/{video_list[current_index]}")

            duygu_analizi.pause()
           

            if current_index < len(video_list) - 1:
                current_index += 1
                duygu_analizi.emotion = {k: 0 for k in duygu_analizi.emotion}
                duygu_analizi.play()
            else:
                flash("Tüm videolar izlendi. Lütfen duygu analizini kaydedin.", 'info')

        elif action == "prev":
            # Mevcut analiz kaydediliyor
            dominant = duygu_analizi.get_dominant_emotion()
            duygu_analizleri.append(dominant)
            video_adi.append(f"videos/{video_list[current_index]}")

            duygu_analizi.pause()
           

            if current_index > 0:
                current_index -= 1
                duygu_analizi.emotion = {k: 0 for k in duygu_analizi.emotion}
                duygu_analizi.play()
            else:
                flash("Zaten ilk videodasınız.", "warning")

        elif action == "refresh":
            duygu_analizi.pause()
            threading.Thread(target=video_indirme.main, daemon=True).start()
            flash("Videolar yenileniyor...", 'info')
            
            return redirect(url_for('videolar_yuklenıyor'))

        elif action == "save":
            duygu_analizi.pause()
            if duygu_analizleri and video_adi:
                # Tüm listelerin uzunluğunu eşitle
                min_len = min(len(video_adi), len(duygu_analizleri))
                df = pd.DataFrame({
                    "video_name": video_adi[:min_len],
                    "emotion": duygu_analizleri[:min_len],
                   
                })
                df.to_csv("video_data.csv", index=False)
                threading.Thread(target=etiket_indirme.main, daemon=True).start()
                flash("Duygu analizi kaydedildi. Öneriler hazırlanıyor...", 'success')
                return redirect(url_for('etiketler_yukleniyor'))
            else:
                flash("Henüz analiz edilmiş video bulunmamaktadır.", 'warning')

    if 0 <= current_index < len(video_list):
        video_file = url_for('static', filename=f"videos/{video_list[current_index]}")
        video_name = video_list[current_index]
        return render_template("video.html",
                               video_file=video_file,
                               video_name=video_name,
                               current_index=current_index + 1,
                               total_videos=len(video_list))
    else:
        flash("Video bulunamadı veya geçersiz indeks.", 'error')
        return redirect(url_for('dashboard'))



@app.route('/video_yukle', methods=['GET', 'POST'])
def videolar_yuklenıyor():
    global video_indirme

    if video_indirme.videoyuklendimi:
         video_indirme.videoyuklendimi= False  
         return redirect(url_for('video_izle'))

    return render_template("videoyukle.html")


@app.route('/etiketler_yukleniyor')
def etiketler_yukleniyor():
    """Etiketlerin yüklendiği sayfa"""
    if not etiket_indirme.tumvideloryuklendimi:
        flash("Henüz tüm videolar yüklenmedi. Lütfen bekleyin.", 'info')
        return render_template("videoyukle.html")
    
    
    
    
    flash("Etiketler hazırlanıyor...", 'success')
    return redirect(url_for('onerilen_videolar'))




@app.route('/onerilen_videolar')
def onerilen_videolar():
   
    if 'user_id' not in session:
        flash("Önerilen videoları görmek için lütfen giriş yapın.", 'error')
        return redirect(url_for('anasayfa'))
    
    video_folder = r"C:\Users\MONSTER\3D Objects\yazprojeler\assemble\flask_proje\venv\static\downloaded_videos"
    
    try:
        video_files = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.webm', '.mkv'))]
        video_files = sorted(video_files)
    except FileNotFoundError:
        video_files = []
        flash("Henüz önerilen video bulunmamaktadır.", 'info')

    # Sayfalama
    page = int(request.args.get('page', 1))
    per_page = 4
    total_pages = math.ceil(len(video_files) / per_page) if video_files else 1
    start = (page - 1) * per_page
    end = start + per_page
    current_videos = video_files[start:end]

    return render_template(
        "onerilen_videolar.html",
        video_files=current_videos,
        page=page,
        total_pages=total_pages,
        has_videos=len(video_files) > 0
    )

@app.route('/video_oynat/<video_name>')
def video_oynat(video_name):
    """Önerilen videoları oynatmak için"""
    if 'user_id' not in session:
        return redirect(url_for('anasayfa'))
    
    video_file = url_for('static', filename=f"downloaded_videos/{video_name}")
    return render_template("video_oynat.html", video_file=video_file, video_name=video_name)

@app.errorhandler(404)
def sayfa_bulunamadi(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def sunucu_hatasi(error):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(debug=True)
