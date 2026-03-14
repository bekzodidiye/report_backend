# 📘 Fuqarolar Monitoring Platformasi - To'liq API Spetsifikatsiyasi

Ushbu spetsifikatsiya har bir API endpointi uchun qanday ma'lumot yuborish (Request) va qanday natija kutish (Response) kerakligini batafsil tushuntiradi.

---

## 🔑 1. Authentication (Autentifikatsiya)

### 📝 Ro'yxatdan o'tish (Register)
*   **Endpoint:** `POST /api/v1/auth/register/`
*   **Request Body (JSON):**
    ```json
    {
      "email": "user@example.uz",
      "password": "strongpassword123",
      "phone": "+998901234567"
    }
    ```
*   **Response (201 Created):**
    ```json
    {
      "id": 12,
      "email": "user@example.uz",
      "phone": "+998901234567"
    }
    ```

### 🔓 Kirish (Login)
*   **Endpoint:** `POST /api/v1/auth/login/`
*   **Request Body (JSON):**
    ```json
    {
      "email": "user@example.uz",
      "password": "strongpassword123"
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "access": "eyJhbGciOiJIUzI1...",
      "refresh": "eyJhbGciOiJIUzI1...",
      "user": {
        "id": 12,
        "email": "user@example.uz",
        "role": "citizen"
      }
    }
    ```

### 👤 Mening profilim (Me)
*   **Endpoint:** `GET /api/v1/auth/me/`
*   **Header:** `Authorization: Bearer <access_token>`
*   **Response (200 OK):**
    ```json
    {
      "id": 12,
      "email": "user@example.uz",
      "phone": "+998901234567",
      "avatar": null,
      "role": "citizen",
      "score": 150,
      "level": "active_inspector"
    }
    ```

---

## 🏛️ 2. Institutions (Muassasalar)

### 📁 Muassasalar ro'yxati
*   **Endpoint:** `GET /api/v1/institutions/`
*   **Query Parametrlari:** `region`, `district`, `type` (school/kindergarten), `search`
*   **Response (200 OK):**
    ```json
    {
      "count": 120,
      "next": "...",
      "previous": null,
      "results": [
        {
          "id": 1,
          "name": "12-sonli umumta'lim maktabi",
          "type": "school",
          "region": "Toshkent shahri",
          "district": "Yunusobod tumani",
          "status": "active"
        }
      ]
    }
    ```

### 🔍 Muassasa batafsil (Detail)
*   **Endpoint:** `GET /api/v1/institutions/{id}/`
*   **Response (200 OK):**
    ```json
    {
      "id": 1,
      "name": "12-sonli maktab",
      "promises": [
        { "id": 5, "title": "Sport zalini ta'mirlash", "status": "pending" }
      ],
      "recent_problems": []
    }
    ```

---

## 📝 3. Reports (Hisobotlar)

### 📸 Hisobot yuborish (Create Report)
*   **Endpoint:** `POST /api/v1/reports/`
*   **Header:** `Authorization: Bearer <access_token>`
*   **Request Body (multipart/form-data):**
    *   `promise`: `5` (Va'da ID-si)
    *   `institution`: `1` (Muassasa ID-si)
    *   `comment`: "Ta'mirlash boshlangan, tom qismi yopilmoqda."
    *   `photo`: (File object)
    *   `promise_status`: `in_progress` (pending, in_progress, completed)
*   **Response (201 Created):**
    ```json
    {
      "id": 45,
      "status": "pending",
      "author_email": "user@example.uz"
    }
    ```

### 🤝 Hisobotni tasdiqlash (Verify Report)
*   **Endpoint:** `POST /api/v1/reports/{id}/verify/`
*   **Vazifasi:** Boshqa foydalanuvchi yuborgan hisobot to'g'riligini tasdiqlash uchun (Social Proof).
*   **Response (200 OK):**
    ```json
    { "success": true, "message": "Verification recorded" }
    ```

---

## 🏗️ 4. Dashboard (Statistika)

### 📊 Umumiy Statistika
*   **Endpoint:** `GET /api/v1/dashboard/stats/`
*   **Response:**
    ```json
    {
      "total_institutions": 1200,
      "total_reports": 450,
      "verified_reports": 380,
      "total_problems": 120,
      "total_users": 3500
    }
    ```

### 📍 Xarita ma'lumotlari
*   **Endpoint:** `GET /api/v1/dashboard/map/`
*   **Response:**
    ```json
    [
      {
        "id": 1,
        "name": "12-maktab",
        "latitude": 41.3111,
        "longitude": 69.2797,
        "status": "active"
      }
    ]
    ```

---

## 👮 5. Moderation (Moderatorlar uchun)

### 📥 Moderatsiya kutilayotgan hisobotlar
*   **Endpoint:** `GET /api/v1/moderation/reports/`
*   **Response:** `pending` holatdagi barcha hisobotlar ro'yxati.

---

## ⚠️ Xatoliklar qaytishi
Agar biror narsa xato bo'lsa, backend doimo quyidagi formatda javob beradi:

```json
{
  "success": false,
  "message": "Xatolik haqida qisqacha ma'lumot",
  "errors": {
    "field_name": ["Xatolik tafsiloti"]
  }
}
```
---
**Hujjat muddati:** 2026-yil, Mart
**Format:** v1.0.0
