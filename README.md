# 🏛️ "Fuqarolar Monitoring Platformasi" - Backend

O'zbekistondagi maktab va bog'chalarda hukumat tomonidan berilgan va'dalarni fuqarolik nazorati (civic monitoring) platformasi backend tizimi.

---

## 🚀 Tezkir Ishga Tushirish (Quick Start)

### 1. Omborni klonlash (Clone)
```bash
git clone https://github.com/bekzodidiye/report_backend.git
cd report_backend
```

### 2. Sozlamalar (Environment)
`.env.example` faylini `.env` deb nusxalang va kerakli parollarni o'rnating.

### 3. Docker orqali ishga tushirish
```bash
docker-compose up --build
```

### 4. API Manzillari
*   **Base URL:** `http://localhost:8000/api/v1/`
*   **Swagger API Docs:** `http://localhost:8000/api/docs/`
*   **Admin Panel:** `http://localhost:8000/admin/`

---

## 📚 Batafsil Hujjatlar (Full Docs)

Sizga qulay bo'lishi uchun loyiha ikki turdagi batafsil hujjatlar bilan ta'minlangan:

1.  **[Backend System Guide](BACKEND_STRICT_GUIDE.md)**: Arxiv, texnologik stek, har bir ilova (`apps/`) vazifasi va server sozlamalari haqida.
2.  **[Frontend API Guide](API_GUIDE.md)**: Frontend dasturchilar uchun barcha endpointlar, JWT login va integratsiya qo'llanmasi.

---

## 🛠️ Muhim Buyruqlar

*   **Migratsiya yuborish:** `docker-compose exec web python manage.py migrate`
*   **Superuser yaratish:** `docker-compose exec web python manage.py createsuperuser`
*   **Testlarni ishga tushirish:** `docker-compose exec web pytest`
*   **GeoASR Synx:** `docker-compose exec web python manage.py shell -c "from integrations.geoasr.sync import GeoASRSyncService; GeoASRSyncService.sync_all()"`

---
**Civic Platform - 2026**
Backend: Django 4.2 + DRF
