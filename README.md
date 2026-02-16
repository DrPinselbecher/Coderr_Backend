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
| Database                | SQLite (default)      |
| Development Environment | VS Code recommended   |


---

## ⚙️ Installation & Setup

### ✅ 1. Clone the FRONTEND repository

```bash
git clone https://github.com/DrPinselbecher/Coderr_Frontend
cd Coderr_Frontend
```

### ✅ 2. Clone the BACKEND repository

```bash
git clone https://github.com/DrPinselbecher/Coderr_Backend
cd Coderr_Backend
```

### ✅ 3. Create & activate virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### ✅ 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Start Project

### 👉 1. Run database migrations

```bash
python manage.py migrate
```

### 👉 2. Create admin user (optional)

```bash
python manage.py createsuperuser
```

### 👉 3. Start the server

```bash
python manage.py runserver
```

Backend runs at:
👉 http://127.0.0.1:8000/

---

## 🔐 Authentication

Authentication is handled via **DRF Token Authentication**.

### Register

```bash
POST /api/registration/
```

### Login

```bash
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

```
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

The backend includes a full DRF test suite covering:

- Endpoints
- Permissions
- Serializers
- Search & Filters
- Redirect logic

Run tests:

```bash
python manage.py test
```

---

## 📄 Example Requirements (requirements.txt)

```bash
Django==5.x
djangorestframework==3.x
django-filter
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
