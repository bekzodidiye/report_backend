# 🚀 Fuqarolar Monitoring Platformasi - API Documentation

Frontend dasturchilar uchun backend integratsiyasi bo'yicha to'liq qo'llanma.

## 🔗 Asosiy Ma'lumotlar
*   **Base URL (Production):** `https://report-backend-ncxk.onrender.com/api/v1/`
*   **API Documentation (Swagger):** `https://report-backend-ncxk.onrender.com/api/docs/`
*   **API Documentation (Redoc):** `https://report-backend-ncxk.onrender.com/api/redoc/`

---

## 🔐 Authentication (JWT)

Loyihada **JWT (JSON Web Token)** ishlatiladi. Tokenlar `access` va `refresh` turlariga bo'linadi.

### 1. Login
*   **URL:** `POST /auth/login/`
*   **Request Body:**
    ```json
    {
      "email": "user@example.uz",
      "password": "yourpassword"
    }
    ```
*   **Response:**
    ```json
    {
      "access": "...",
      "refresh": "...",
      "user": {
        "id": 1,
        "email": "user@example.uz",
        "role": "citizen"
      }
    }
    ```

### 2. Tokenni ishlatish
Barcha himoyalangan (`IsAuthenticated`) so'rovlar uchun `Authorization` header'ini yuborish shart:
`Authorization: Bearer <your_access_token>`

### 3. Tokenni yangilash (Refresh)
*   **URL:** `POST /auth/refresh/`
*   **Body:** `{"refresh": "<refresh_token>"}`

---

## 🏛️ Institutions (Muassasalar)
*   **Ro'yxat:** `GET /institutions/` (Filterlar: `region`, `district`, `type`, `status`)
*   **Batafsil:** `GET /institutions/{id}/`
*   **Region/District list:** `GET /institutions/regions/`

---

## 📜 Promises (Va'dalar)
*   **Ro'yxat:** `GET /promises/` (Filterlar: `institution_id`, `category`)
*   **Batafsil:** `GET /promises/{id}/`

---

## 📝 Reports (Hisobotlar)
*   **Yuborish:** `POST /reports/` (Form-data: `promise`, `institution`, `comment`, `media`, `latitude`, `longitude`)
*   **Mening hisobotlarim:** `GET /reports/my-reports/`
*   **Tasdiqlash (User verification):** `POST /reports/{id}/verify/`

---

## 🏗️ Dashboard (Statistika)
*   **Umumiy stats:** `GET /dashboard/stats/`
*   **Xarita ma'lumotlari:** `GET /dashboard/map/`
*   **Top foydalanuvchilar:** `GET /dashboard/top-users/`

---

## 👮 Moderation (Admin uchun)
*   **Kutilayotgan hisobotlar:** `GET /moderation/reports/`
*   **Moderatsiyalash:** `PATCH /moderation/reports/{id}/` (Status: `verified` yoki `rejected`)

---

## ⚠️ Xatoliklar Formati
```json
{
  "success": false,
  "message": "Error details here",
  "errors": {
    "field_name": ["Specific error message"]
  }
}
```
---
**Savollar bo'lsa:** Backend dev
