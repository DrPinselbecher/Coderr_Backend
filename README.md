**---------------------------------- EN -----------------------------------------------**

# ✅ CODERR – Backend (Django REST API)

**CODERR** is a service marketplace platform where **business users** can create offers and **customer users** can place orders and leave reviews.

This repository contains the **Django REST Framework backend API** powering the Coderr platform.

Frontend Repository:
👉 https://github.com/DrPinselbecher/Coderr_Frontend

---

## 🚀 Features

- User registration & login (Token Authentication)
- Business & Customer user roles
- Profile management
- Create offers with 3 pricing tiers (basic / standard / premium)
- Offer filtering, searching & ordering
- Orders created from offer details
- Business-side order status management
- Customer reviews (1–5 rating validation)
- Aggregated platform statistics endpoint
- Fully tested REST API

---

## 📦 Technologies & Requirements

| Technology              | Version / Info        |
|-------------------------|-----------------------|
| Python                  | 3.13.2                |
| Django                  | 5.2.x (LTS)           |
| Django REST Framework   | 3.16.1                |
| django-filter           | 25.2                  |
| django-cors-headers     | 4.x                   |
| python-dotenv           | 1.x                   |
| Database                | SQLite (default)      |
| Development Environment | VS Code recommended   |

---

## ⚙️ Installation & Setup

### ✅ 1. Clone BOTH repositories (same parent folder)

```bash
git clone https://github.com/DrPinselbecher/Coderr_Frontend
git clone https://github.com/DrPinselbecher/Coderr_Backend
```

Expected folder structure:

```text
your-folder/
├── Coderr_Frontend/
└── Coderr_Backend/
```

---

## 🖥 Backend Setup (Django)

### ✅ 2. Go into the backend folder

```bash
cd Coderr_Backend
```

### ✅ 3. Create & activate virtual environment

```bash
python -m venv env
source env/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### ✅ 4. Install dependencies

```bash
pip install -r requirements.txt
```

### ✅ 5. Create your local `.env` file

Create a file named **.env** in the same directory as **manage.py**.

Example `.env`:

```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
```

Generate a secure secret key (recommended):

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the generated value into `DJANGO_SECRET_KEY`.

### ✅ 6. Run database migrations

```bash
python manage.py migrate
```

### ✅ 7. Create admin user (optional)

```bash
python manage.py createsuperuser
```

### ✅ 8. Start the backend server

```bash
python manage.py runserver
```

Backend runs at:
👉 http://127.0.0.1:8000/

---

## 🌐 Frontend Setup

### ✅ 9. Go into the frontend folder (new terminal)

```bash
cd ../Coderr_Frontend
```

Start the frontend (depending on your setup):

```bash
npm install
npm start
```

If using VS Code Live Server (port 5500):
- Origin: http://127.0.0.1:5500
- CORS is already configured in backend via `.env`

---

## 🔐 Authentication

Authentication is handled via **DRF Token Authentication**.

### Register

```text
POST /api/registration/
```

### Login

```text
POST /api/login/
```

Both endpoints return:

```json
{
  "token": "your_token_here",
  "username": "your_username",
  "email": "your_email",
  "user_id": 1
}
```

Use token in request headers:

```text
Authorization: Token your_token_here
```

---

## 📦 Core API Modules

### 👤 Profiles
- Business & Customer profile types
- Profile update (owner only)
- Business profile list endpoint
- Customer profile list endpoint

### 💼 Offers
- Business users can create offers
- Exactly 3 pricing tiers required:
  - basic
  - standard
  - premium
- Filtering:
  - creator_id
  - min_price
  - max_delivery_time
- Search:
  - title
  - description
- Ordering:
  - updated_at
  - min_price
- Pagination enabled

Response structure (paginated):

```json
{
  "count": 10,
  "next": "...",
  "previous": null,
  "results": [...]
}
```

### 📦 Orders
- Customers can create orders from offer details
- Business users can update order status
- Admin-only delete
- Order count endpoints:
  - In-progress
  - Completed

### ⭐ Reviews
- Only customers can create reviews
- One review per business/customer combination
- Rating validation (1–5)
- Filter by:
  - business_user_id
  - reviewer_id

### 📊 Base Info Endpoint
Aggregated statistics endpoint returning:

- review_count
- average_rating
- business_profile_count
- offer_count

---

## 🧪 Testing

Run all tests:

```bash
python manage.py test
```

---

## 📄 Requirements

Use the versions defined in `requirements.txt`.

Example (may vary depending on repo state):

```text
asgiref==3.11.0
Django==5.2.x
django-filter==25.2
djangorestframework==3.16.1
pillow==12.1.0
sqlparse==0.5.5
tzdata==2025.3
python-dotenv==1.x
django-cors-headers==4.x
```

---

## 👤 Author

Project: CODERR  
Developer: René Theis  
GitHub: https://github.com/DrPinselbecher  

---

## 📌 Notes

This backend is part of a full-stack portfolio project.

Frontend Repository:
👉 https://github.com/DrPinselbecher/Coderr_Frontend
```