# 💰 Finance Tracking System

A clean, well-structured **Python + FastAPI** backend for managing personal financial records with role-based access control, analytics, full CRUD operations, and a **premium frontend dashboard**.

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
| Frontend     | Vanilla HTML + CSS + JavaScript    |

---

## Project Structure

```
finance_system/
├── main.py                     # App entry point, router registration, frontend serving
├── config.py                   # App settings (secret key, DB URL, etc.)
├── database.py                 # SQLAlchemy engine, session, Base
├── dependencies.py             # Auth dependencies & role guards
├── seed.py                     # Demo data seeder
├── tests.py                    # Unit + integration tests
├── requirements.txt
├── .gitignore
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
├── services/
│   ├── auth_service.py         # Auth logic: hashing, token, user CRUD
│   ├── transaction_service.py  # Transaction CRUD + filtering
│   └── analytics_service.py    # Summary, category breakdown, monthly totals
│
└── static/
    └── index.html              # Full-featured frontend dashboard (single-page app)
```

---

## Frontend Dashboard

The project includes a **premium single-page frontend application** served directly by FastAPI at the root URL (`/`). The frontend is built with vanilla HTML, CSS, and JavaScript — no build tools required.

### Frontend Features

- **Login & Registration** — Animated login card with demo credentials for quick testing
- **Dashboard Overview** — Summary stat cards showing total income, expenses, net balance, and transaction count
- **Transaction Management** — Full table view with pagination, inline editing, and creation modals (Admin only)
- **Advanced Filtering** — Filter transactions by type, category, and date range
- **Analytics Page** — Category breakdown with animated progress bars and monthly income vs. expense comparison
- **User Management** — Admin panel to view, update roles, and delete users
- **Role-Based UI** — Navigation items and actions are dynamically shown/hidden based on the logged-in user's role
- **Toast Notifications** — Success, error, and info feedback messages
- **Responsive Design** — Sidebar navigation, monospace typography (DM Mono), and warm color palette

### Design Details

| Aspect         | Details                                          |
|----------------|--------------------------------------------------|
| Typography     | Syne (headings), DM Mono (body), Lora (accents)  |
| Color Palette  | Warm paper/cream background, gold accents, ink-dark sidebar |
| Interactions   | Hover effects, slide-up animations, modal overlays with blur |
| Layout         | Fixed sidebar + scrollable main content area      |

---

## How to Download & Run This Project

### 1. Clone the repository

```bash
git clone https://github.com/Parth-2004/Finance_system.git
cd Finance_system
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

#### Activate it:

- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\activate
  ```
- **Windows (CMD):**
  ```cmd
  venv\Scripts\activate
  ```
- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note (Windows):** If you encounter a bcrypt-related error, run:
> ```bash
> pip install "bcrypt<4.0.0"
> ```

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

> **Note (Windows):** If you see a Unicode/emoji error, run:
> ```powershell
> $env:PYTHONIOENCODING="utf-8"; python seed.py
> ```

### 6. Run the server

```bash
uvicorn main:app --reload
```

### 7. Open in your browser

| URL                              | Description                    |
|----------------------------------|--------------------------------|
| http://localhost:8000            | Frontend Dashboard (login UI)  |
| http://localhost:8000/docs       | Swagger API Documentation      |
| http://localhost:8000/health     | Health check endpoint          |

---

## Demo Accounts (after seeding)

| Role     | Name   | Email                   | Password    |
|----------|--------|-------------------------|-------------|
| Admin    | Parth  | admin@finance.com       | admin123    |
| Analyst  | Ansh   | analyst@finance.com     | analyst123  |
| Viewer   | Ram    | viewer@finance.com      | viewer123   |

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

8. **Frontend is a single HTML file** — no build step, no npm, no frameworks. It communicates with the backend via `fetch()` calls to the API endpoints.

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

---

## Deployment

To deploy this project (e.g., on [Render](https://render.com)):

1. Push the code to a GitHub repository.
2. On Render, create a **New Web Service** and connect to the repo.
3. Set these configurations:
   - **Build Command:** `pip install -r requirements.txt && python seed.py`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
4. Once live, access `https://your-app-url.onrender.com/docs` for Swagger docs, or `/` for the frontend dashboard.

---

## License

This project is open-source and available for educational and personal use.
