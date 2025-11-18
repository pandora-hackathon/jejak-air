# Jejak Air 

## 🧑‍🧑‍🧒‍🧒 Anggota
- Nisrina Alya Nabilah
- Saffana Firsta Aqila
- Nadia Aisyah Fazila
- Keisha Vania Laurent
- Alya Nabilla Khamil

## 🔗 Link repository 
https://github.com/pandora-hackathon/jejak-air

## ⚙️ Petunjuk Untuk Menjalankan Aplikasi
- **Clone repository**
    - `git clone https://github.com/username/https://github.com/pandora-hackathon/jejak-air.git`
- **Buat virtual environment**
    - `python3 -m venv env`
    - MacOS / Linux -> `source env/bin/activate  `  
    - Windows -> `env\Scripts\activate`       
- **Install dependencies**
    - `pip install -r requirements.txt`
- **Setup environment**
    - Buat file .env pada root project kemudian isi dengan 
    - `PRODUCTION=False`
- **Lakukan migrasi database**
    - `python manage.py migrate`
- **Import data**
    - `python manage.py import_data`
- **Buat superuser untuk mengakses Django Admin (Opsional)**
    - `python manage.py createsuperuser`
- **Jalankan server lokal**
    - `python manage.py runserver`
- **Akses di Browser**
    - Aplikasi utama -> http://localhost:8000/
    - Django admin -> http://localhost:8000/admin/
