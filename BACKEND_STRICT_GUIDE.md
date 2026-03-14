# 🏛️ "Fuqarolar Monitoring Platformasi" - Backend System Documentation

Ushbu hujjat loyihaning arxitekturasi, strukturasi, ishlash mexanizmi va barcha texnik jihatlari haqida to'liq ma'lumot beradi.

---

## 🛠️ 1. Texnologik Stek (Tech Stack)
*   **Framework:** Django 4.2 + Django REST Framework 3.14
*   **Ma'lumotlar bazasi:** PostgreSQL 15
*   **Kesh va Navbat (Queue):** Redis 7
*   **Fon vazifalari:** Celery + Celery Beat (Periodic Tasks)
*   **Monitoring:** Sentry + Django Prometheus
*   **Konteynerizatsiya:** Docker + Docker Compose
*   **Deploy:** Render (Web Service + Managed Postgres)

---

## 📂 2. Loyiha Strukturasi (App Overview)

Loyiha modulli arxitektura asosida qurilgan. Har bir ilovaning (`apps/`) o'z vazifasi bor:

### 🔹 1. `apps.users` (Foydalanuvchilar)
*   **Vazifasi:** Ro'yxatdan o'tish, Login (JWT), Profil boshqaruvi.
*   **Reputation System:** Foydalanuvchilarning "Score" (bal) va "Level" (daraja) tizimi.
*   **Xususiyati:** Custom User model (`AbstractUser`) ishlatilgan.

### 🔹 2. `apps.institutions` (Ta'lim muassasalari)
*   **Vazifasi:** Maktablar va bog'chalar ro'yxatini saqlash.
*   **GeoData:** Muassasalarning geografik koordinatalari (lat, long).
*   **Integratsiya:** GeoASR (davlat reyestri) dan ma'lumotlarni sinxronizatsiya qilish.

### 🔹 3. `apps.promises` (Vada berilgan ishlar)
*   **Vazifasi:** Har bir maktab uchun hukumat tomonidan berilgan "va'dalar" (masalan: "Tom qismini ta'mirlash", "Yangi kompyuterlar").
*   **Bog'lanish:** Har bir va'da bitta `Institution`ga tegishli.

### 🔹 4. `apps.reports` (Hisobotlar va Tasdiqlash)
*   **Vazifasi:** Fuqarolar va'daning bajarilganligini rasm/video orqali isbotlashadi.
*   **Verification:** Bir foydalanuvchi yuborgan hisobotni boshqa bir necha foydalanuvchi tasdiqlashi kerak (Social Proof).
*   **Media:** S3 (AWS/R2) yoki FileSystem bilan ishlaydi.

### 🔹 5. `apps.problems` (Muammolar)
*   **Vazifasi:** Va'dadan tashqari yangi muammolarni rasm bilan ko'rsatish (masalan: "Oshxonada sharoit yomon").

### 🔹 6. `apps.dashboard` (Statistika)
*   **Vazifasi:** Landing page uchun umumiy hisob-kitoblar, xarita ma'lumotlari va top-foydalanuvchilar.
*   **Kesh:** Ma'lumotlar Redisda keshlanadi (tezlik uchun).

### 🔹 7. `apps.moderation` (Moderatsiya)
*   **Vazifasi:** Admin/Moderatorlar uchun kutilayotgan hisobotlarni ko'rish va ularni tasdiqlash/rad etish.

---

## ⚙️ 3. Core Componentlar (Markaziy tizim)
Loyiha markazida `core/` moduli joylashgan:
*   `core.responses`: Barcha API'lar uchun standart JSON format.
*   `core.exceptions`: Xatoliklarni chiroyli ko'rsatish uchun custom handler.
*   `core.pagination`: Ma'lumotlarni sahifalarga bo'lib yuborish.
*   `core.permissions`: Rolga asoslangan kirish huquqlari (`IsCitizen`, `IsModerator`).

---

## 🚀 4. Ishga tushirish (Local Development)

### Docker orqali (Tavsiya etiladi):
```bash
docker-compose up --build
```
Bu buyruq Postgres, Redis, Celery va Django-ni bir vaqtda ishga tushiradi.

### Qo'lda (VirtualEnv):
1. `python -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements/development.txt`
4. Postgre va Redis xizmatlarini ishga tushiring.
5. `python manage.py migrate`
6. `python manage.py runserver`

---

## ☁️ 5. Deploy va Server Sozlamalari (Render)

### Dockerfile
Loyihada production uchun maxsus `Dockerfile` ishlatilgan. U quyidagi ketma-ketlikda ishlaydi:
1. `entrypoint.sh` bajariladi.
2. `migrate` (bazani yangilash).
3. `setup_admin` (admin yaratish).
4. `collectstatic` (static fayllarni yig'ish).
5. `gunicorn` (serverni ASGI rejimida ishga tushirish).

### Muhim Environment Variables (.env)
*   `DATABASE_URL`: Postgres manzili.
*   `REDIS_URL`: Redis manzili.
*   `SECRET_KEY`: Django xavfsizlik kaliti.
*   `ALLOWED_HOSTS`: `.onrender.com`.
*   `DJANGO_SUPERUSER_PASSWORD`: Admin paroli.

---

## 🔐 6. Admin Panel
*   **Manzil:** `https://your-app.onrender.com/admin/`
*   **Login (Default):** `admin@example.uz`
*   **Parol:** `admin123` (yoki `.env`dagi qiymat)

---

## 📝 7. API Dokumentatsiya
Loyiha o'zidan o'zi hujjatlashadi:
*   **Swagger:** `/api/docs/`
*   **Redoc:** `/api/redoc/`

---
**Civic Monitoring Platform - 2026**
Backend Engineer: Senior Django Dev
