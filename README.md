# 💰 Finance Tracking System

A clean, well-structured **Python + FastAPI** backend for managing personal financial records with role-based access control, analytics, and full CRUD operations.

---

## Tech Stack

| Layer        | Technology                         |
|--------------|------------------------------------|
| Framework    | FastAPI                            |
| Database     | SQLite (via SQLAlchemy ORM)        |
| Validation   | Pydantic v2                        |
| Auth         | JWT (python-jose) + bcrypt         |
| Testing      | Pytest + HTTPX (TestClient)        |
| API Docs     | Swagger UI (auto-generated)        |

---

## Project Structure

```
finance_system/
├── main.py                     # App entry point, router registration
├── config.py                   # App settings (secret key, DB URL, etc.)
├── database.py                 # SQLAlchemy engine, session, Base
├── dependencies.py             # Auth dependencies & role guards
├── seed.py                     # Demo data seeder
├── tests.py                    # Unit + integration tests
├── requirements.txt
│
├── models/
│   ├── user.py                 # User model + UserRole enum
│   └── transaction.py          # Transaction model + TransactionType enum
│
├── schemas/
│   ├── user.py                 # Pydantic schemas for users
│   └── transaction.py          # Pydantic schemas for transactions + analytics
│
├── routers/
│   ├── auth.py                 # /auth/* endpoints
│   ├── transactions.py         # /transactions/* endpoints
│   └── analytics.py            # /analytics/* endpoints
│
└── services/
    ├── auth_service.py         # Auth logic: hashing, token, user CRUD
    ├── transaction_service.py  # Transaction CRUD + filtering
    └── analytics_service.py    # Summary, category breakdown, monthly totals
```

---

## Setup & Installation

### 1. Clone and enter the project

```bash
git clone <your-repo-url>
cd finance_system
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure environment

Create a `.env` file to override defaults:

```env
SECRET_KEY=your-super-secret-key
DATABASE_URL=sqlite:///./finance.db
```

### 5. Seed demo data

```bash
python seed.py
```

This creates 3 users and 25 sample transactions.

### 6. Run the server

```bash
uvicorn main:app --reload
```

Server runs at: **http://localhost:8000**
Interactive API docs: **http://localhost:8000/docs**

---

## Demo Accounts (after seeding)

| Role     | Email                   | Password    |
|----------|-------------------------|-------------|
| Admin    | admin@finance.com       | admin123    |
| Analyst  | analyst@finance.com     | analyst123  |
| Viewer   | viewer@finance.com      | viewer123   |

---

## API Endpoints

### Authentication

| Method | Endpoint              | Access  | Description              |
|--------|-----------------------|---------|--------------------------|
| POST   | `/auth/register`      | Public  | Register a new user      |
| POST   | `/auth/login`         | Public  | Login and get JWT token  |
| GET    | `/auth/me`            | All     | Get your own profile     |
| GET    | `/auth/users`         | Admin   | List all users           |
| PATCH  | `/auth/users/{id}`    | Admin   | Update user name/role    |
| DELETE | `/auth/users/{id}`    | Admin   | Delete a user            |

### Transactions

| Method | Endpoint                    | Access           | Description                  |
|--------|-----------------------------|------------------|------------------------------|
| GET    | `/transactions`             | All              | List transactions (paginated)|
| POST   | `/transactions`             | Admin            | Create a transaction         |
| GET    | `/transactions/{id}`        | All (own data)   | Get single transaction       |
| PATCH  | `/transactions/{id}`        | Admin            | Update a transaction         |
| DELETE | `/transactions/{id}`        | Admin            | Delete a transaction         |

**Query filters for `GET /transactions`:**

| Param       | Example              | Description             |
|-------------|----------------------|-------------------------|
| `type`      | `?type=income`       | Filter by income/expense|
| `category`  | `?category=food`     | Filter by category      |
| `date_from` | `?date_from=2024-01-01` | Start date filter    |
| `date_to`   | `?date_to=2024-03-31`   | End date filter      |
| `page`      | `?page=2`            | Page number (default 1) |
| `page_size` | `?page_size=10`      | Items per page (max 100)|

### Analytics

| Method | Endpoint                       | Access   | Description                         |
|--------|--------------------------------|----------|-------------------------------------|
| GET    | `/analytics/summary`           | All      | Total income, expenses, balance     |
| GET    | `/analytics/category-breakdown`| Analyst+ | Spending by category with %         |
| GET    | `/analytics/monthly`           | Analyst+ | Monthly income vs expense totals    |

---

## Role-Based Access Control

```
Viewer   →  view own transactions + summary
Analyst  →  Viewer permissions + category/monthly analytics + filters
Admin    →  Full access: create, update, delete transactions and manage users
```

Role is enforced via JWT token claims + dependency injection on every route.

---

## Running Tests

```bash
pip install pytest httpx
pytest tests.py -v
```

Tests cover:
- User registration and login (including edge cases)
- Role-based access control (403 assertions)
- Transaction CRUD operations
- Input validation (negative amounts, duplicate emails, short passwords)
- Analytics endpoint accuracy
- Pagination behavior
- Date range validation

---

## Design Decisions & Assumptions

1. **SQLite** was chosen for simplicity and zero-setup. Switching to PostgreSQL only requires changing `DATABASE_URL` in `.env`.

2. **Admins create transactions** on behalf of the system. In a real app, analysts/viewers might have their own transaction entry.

3. **JWT tokens** expire after 24 hours. This can be adjusted in `config.py`.

4. **Category** values are stored lowercase and trimmed to ensure consistent filtering.

5. **Amounts** are always positive floats. Transaction type (`income` / `expense`) determines the direction.

6. **Admins see all data** in analytics and transaction lists. Other roles see only their own records.

7. A user **cannot delete themselves** even as an admin.

---

## Example Usage (curl)

**Register:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "email": "john@example.com", "password": "john1234"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@finance.com", "password": "admin123"}'
```

**Create Transaction (Admin):**
```bash
curl -X POST http://localhost:8000/transactions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"amount": 5000, "type": "income", "category": "salary", "date": "2024-03-01"}'
```

**Get Summary:**
```bash
curl http://localhost:8000/analytics/summary \
  -H "Authorization: Bearer <token>"
```

**Filter Transactions:**
```bash
curl "http://localhost:8000/transactions?type=expense&category=food&date_from=2024-01-01" \
  -H "Authorization: Bearer <token>"
```
