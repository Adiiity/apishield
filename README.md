# 🛡️ API Shield

Secure, scalable, and production-ready API authentication and authorization system built with **FastAPI**, **PostgreSQL**, and **JWT** — deployed on **AWS EC2** with full database integration via **Amazon RDS**.

---

## 🚀 Features

- ✅ JWT-based Authentication (Login & Register)
- ✅ Role-Based Access Control (RBAC) — `admin` vs `user`
- ✅ PostgreSQL integration with SQLAlchemy ORM
- ✅ Rate Limiting with SlowAPI (optional Redis support)
- ✅ Swagger UI with Bearer Token Auth
- ✅ RESTful `/transactions` API per user
- ✅ AWS EC2 hosted backend
- ✅ OpenAPI 3.0 Documentation
- ✅ Environment config using `.env`

---

## 🧱 Tech Stack

| Layer        | Stack                        |
|--------------|------------------------------|
| Language     | Python 3.8+                  |
| Framework    | FastAPI                      |
| Auth         | JWT (via python-jose)        |
| DB           | PostgreSQL (AWS RDS)         |
| ORM          | SQLAlchemy                   |
| API Docs     | Swagger UI / OpenAPI         |
| Hosting      | AWS EC2                      |
| Rate Limiting| SlowAPI                      |

---

## 📁 Project Structure

```
apishield/
├── main.py            # Entry point for FastAPI app
├── auth.py            # Auth logic (JWT, login, password hashing)
├── database.py        # SQLAlchemy models and DB connection
├── .env               # Environment variables
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```
---

## ⚙️ Setup Instructions

### 🔹 1. Clone the repo & install dependencies

```bash
git clone https://github.com/Adiiity/apishield.git
cd apishield
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### 🔹 2. Configure `.env`

```env
POSTGRES_USER=<user>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=<secureapi>
POSTGRES_HOST=<Will be updated soon, AWS EC2 instance>
POSTGRES_PORT=5432
SECRET_KEY=<secret_key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

### 🔹 3. Initialize the Database

```bash
python database.py  # This will create tables on AWS RDS
```

---

### 🔹 4. Run the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Visit `http://<ec2-ip>:8000/docs` for Swagger UI.

---

## 🔐 API Endpoints Overview

| Method | Route                 | Auth     | Description                      |
|--------|-----------------------|----------|----------------------------------|
| POST   | `/auth/register`      | ❌        | Register new user                |
| POST   | `/auth/login`         | ❌        | Get JWT token                    |
| GET    | `/users/me`           | ✅        | Protected route for any user     |
| GET    | `/admin/users`        | ✅ Admin  | List all users                   |
| GET    | `/transactions`       | ✅        | Get user's transactions          |
| POST   | `/transactions`       | ✅        | Create a transaction             |

Use `Bearer <JWT>` token in Swagger or headers.

---

## 💡 Example JWT Header (Swagger)

```http
Authorization: Bearer eyJhbGciOi...
```
---

## 🧑‍💻 Author

**Aditi Thakkar**  
🚀 Built for production-readiness and security-first APIs.
