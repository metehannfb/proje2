import sys
import mysql.connector
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem
)


def veritabani_baglan():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="espor"
    )

# Veritabanı ve tablo oluşturma
def veritabani_ve_tablo_olustur():
    try:
        db = mysql.connector.connect(host="localhost", user="root", password="1234")
        cursor = db.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS espor")
        cursor.close()
        db.close()
    except Exception as e:
        print("Veritabanı oluşturulamadı:", e)

    try:
        db = veritabani_baglan()
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS oyuncular (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ad VARCHAR(50),
                soyad VARCHAR(50),
                `takim` VARCHAR(50),
                oynadigi_oyun VARCHAR(100)
            )
        """)
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        print("Tablo oluşturulamadı:", e)

class LoginEkrani(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("E-spor Yönetim Giriş")
        self.setGeometry(300, 200, 300, 150)

        widget = QWidget()
        layout = QVBoxLayout()

        self.kullanici_input = QLineEdit()
        self.kullanici_input.setText("admin")
        self.sifre_input = QLineEdit()
        self.sifre_input.setText("1234")
        self.sifre_input.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(QLabel("Kullanıcı Adı:"))
        layout.addWidget(self.kullanici_input)
        layout.addWidget(QLabel("Şifre:"))
        layout.addWidget(self.sifre_input)

        btn = QPushButton("Giriş Yap")
        btn.clicked.connect(self.giris_kontrol)
        layout.addWidget(btn)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def giris_kontrol(self):
        if self.kullanici_input.text() == "admin" and self.sifre_input.text() == "1234":
            self.menu = AnaMenu()
            self.menu.show()
            self.close()
        else:
            QMessageBox.warning(self, "Hatalı Giriş", "Kullanıcı adı veya şifre hatalı")

# Ana Menü
class AnaMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("E-spor Yönetim Sistemi")
        self.setGeometry(200, 100, 400, 200)

        widget = QWidget()
        layout = QVBoxLayout()

        btn_oyuncu_ekle = QPushButton("Oyuncu Ekle")
        btn_oyuncu_ekle.clicked.connect(self.oyuncu_ekle_ac)
        layout.addWidget(btn_oyuncu_ekle)

        btn_oyuncu_liste = QPushButton("Oyuncu Listesi / Sil")
        btn_oyuncu_liste.clicked.connect(self.oyuncu_liste_ac)
        layout.addWidget(btn_oyuncu_liste)

        btn_cikis = QPushButton("Çıkış")
        btn_cikis.clicked.connect(self.close)
        layout.addWidget(btn_cikis)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def oyuncu_ekle_ac(self):
        self.ekle_pencere = OyuncuEkle()
        self.ekle_pencere.show()

    def oyuncu_liste_ac(self):
        self.liste_pencere = OyuncuListele()
        self.liste_pencere.show()

# Oyuncu Ekleme Penceresi
class OyuncuEkle(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Oyuncu Ekle")
        self.setFixedSize(300, 250)

        layout = QVBoxLayout()
        self.ad_input = QLineEdit()
        self.soyad_input = QLineEdit()
        self.takim_input = QLineEdit()
        self.oynadigi_oyun_input = QLineEdit()

        layout.addWidget(QLabel("Ad:"))
        layout.addWidget(self.ad_input)
        layout.addWidget(QLabel("Soyad:"))
        layout.addWidget(self.soyad_input)
        layout.addWidget(QLabel("Takım:"))
        layout.addWidget(self.takim_input)
        layout.addWidget(QLabel("Oynadığı Oyun:"))
        layout.addWidget(self.oynadigi_oyun_input)

        kaydet_btn = QPushButton("Kaydet")
        kaydet_btn.clicked.connect(self.kaydet)
        layout.addWidget(kaydet_btn)

        self.setLayout(layout)

    def kaydet(self):
        ad = self.ad_input.text().strip()
        soyad = self.soyad_input.text().strip()
        takim = self.takim_input.text().strip()
        oynadigi_oyun = self.oynadigi_oyun_input.text().strip()

        if ad == "" or soyad == "":
            QMessageBox.warning(self, "Hata", "Ad ve soyad boş olamaz.")
            return

        try:
            db = veritabani_baglan()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO oyuncular (ad, soyad, takim, oynadigi_oyun) VALUES (%s, %s, %s, %s)",
                (ad, soyad, takim, oynadigi_oyun)
            )
            db.commit()
            cursor.close()
            db.close()
            QMessageBox.information(self, "Başarılı", "Oyuncu eklendi.")
            self.close()
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Veritabanı hatası: {e}")

# Oyuncu Listeleme ve Silme Penceresi
class OyuncuListele(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Oyuncular")
        self.setGeometry(100, 100, 650, 300)

        self.layout = QVBoxLayout()
        self.tablo = QTableWidget()
        self.layout.addWidget(self.tablo)

        sil_btn = QPushButton("Seçili Oyuncuyu Sil")
        sil_btn.clicked.connect(self.oyuncu_sil)
        self.layout.addWidget(sil_btn)

        self.setLayout(self.layout)
        self.listele()

    def listele(self):
        try:
            db = veritabani_baglan()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM oyuncular")
            kayitlar = cursor.fetchall()
            cursor.close()
            db.close()

            self.tablo.setRowCount(len(kayitlar))
            self.tablo.setColumnCount(5)
            self.tablo.setHorizontalHeaderLabels(["ID", "Ad", "Soyad", "Takım", "Oynadığı Oyun"])
            for i, row in enumerate(kayitlar):
                for j, cell in enumerate(row):
                    self.tablo.setItem(i, j, QTableWidgetItem(str(cell)))
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Veritabanı hatası: {e}")

    def oyuncu_sil(self):
        secilen = self.tablo.currentRow()
        if secilen < 0:
            QMessageBox.warning(self, "Hata", "Lütfen bir oyuncu seçin.")
            return

        oyuncu_id = self.tablo.item(secilen, 0).text()
        try:
            db = veritabani_baglan()
            cursor = db.cursor()
            cursor.execute("DELETE FROM oyuncular WHERE id = %s", (oyuncu_id,))
            db.commit()
            cursor.close()
            db.close()
            QMessageBox.information(self, "Silindi", "Oyuncu başarıyla silindi.")
            self.listele()
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Veritabanı hatası: {e}")

if __name__ == "__main__":
    veritabani_ve_tablo_olustur()
    app = QApplication(sys.argv)
    giris = LoginEkrani()
    giris.show()
    sys.exit(app.exec())
