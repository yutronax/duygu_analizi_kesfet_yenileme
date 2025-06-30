import sqlite3

class KullanıcıBilgileri:
    def __init__(self):
        self.sql = sqlite3.connect(r"DATABASE_YOLU\kullanicibilgileri.db")
        self.sql.execute("""
            CREATE TABLE IF NOT EXISTS kullanıcıbilgileri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isim TEXT NOT NULL,
                soyisim TEXT NOT NULL,
                sifre TEXT NOT NULL
            )
        """)
        self.sql.execute("""
            CREATE TABLE IF NOT EXISTS kullanıcıilgialanları (
                id INTEGER NOT NULL,
                ilgi_alanları TEXT NOT NULL,
                FOREIGN KEY (id) REFERENCES kullanıcıbilgileri(id)
            )
        """)
        self.calistir = self.sql.cursor()

    def kullanıcı_bilgilerini_ekle(self, isim, soyisim, sifre):
        self.calistir.execute("INSERT INTO kullanıcıbilgileri (isim, soyisim, sifre) VALUES (?, ?, ?)", (isim, soyisim, sifre))
        self.sql.commit()

    def kullanıcı_bilgilerini_getir(self, isim):
        self.calistir.execute("SELECT * FROM kullanıcıbilgileri WHERE isim = ?", (isim,))
        kullanıcı_bilgileri = self.calistir.fetchone()
        if kullanıcı_bilgileri:
            return {
                "id": kullanıcı_bilgileri[0],
                "isim": kullanıcı_bilgileri[1],
                "soyisim": kullanıcı_bilgileri[2],
                "sifre": kullanıcı_bilgileri[3]
            }
        else:
            return None
    def sifreler_getir(self):
        self.calistir.execute("SELECT sifre FROM kullanıcıbilgileri")
        sifreler = self.calistir.fetchall()
        return [sifre[0] for sifre in sifreler]

class KullanıcıIlgiAlani:
    def __init__(self):
        self.sql = sqlite3.connect(r"DATABASE_YOLU\kullanicibilgileri.db")
        self.calistir = self.sql.cursor()

    def kullanıcının_ilgi_alanları_ekle(self, kullanıcı_id, alan):
        self.calistir.execute("INSERT INTO kullanıcıilgialanları (id, ilgi_alanları) VALUES (?, ?)", (kullanıcı_id, alan))
        self.sql.commit()

    def kullanıcının_ilgi_alanları_getir(self, kullanıcı_id):
        self.calistir.execute("""
            SELECT k.isim, k.soyisim, i.ilgi_alanları 
            FROM kullanıcıbilgileri k 
            JOIN kullanıcıilgialanları i ON k.id = i.id 
            WHERE k.id = ?
        """, (kullanıcı_id,))
        sonuc = self.calistir.fetchone()

        if sonuc:
            isim, soyisim, ilgi_alanları = sonuc
            ilgi_listesi = ilgi_alanları.split(',')  # Eğer virgülle ayrılmışsa
            return isim, soyisim, ilgi_listesi
        else:
            return None, None, []
