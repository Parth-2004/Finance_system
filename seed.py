"""
Seed script — populates the database with demo users and transactions.

Run:
    python seed.py

Seeded accounts:
    admin@finance.com   / admin123    (role: admin)
    analyst@finance.com / analyst123  (role: analyst)
    viewer@finance.com  / viewer123   (role: viewer)
"""

from datetime import date, timedelta
import random
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, engine, Base
from models import User, UserRole, Transaction, TransactionType

Base.metadata.create_all(bind=engine)

USERS = [
    {"name": "Parth", "email": "admin@finance.com", "password": "admin123", "role": UserRole.admin},
    {"name": "Ansh", "email": "analyst@finance.com", "password": "analyst123", "role": UserRole.analyst},
    {"name": "Ram", "email": "viewer@finance.com", "password": "viewer123", "role": UserRole.viewer},
]

INCOME_CATEGORIES = ["salary", "freelance", "investments", "rental", "bonus"]
EXPENSE_CATEGORIES = ["food", "transport", "utilities", "entertainment", "health", "shopping", "rent"]

SAMPLE_TRANSACTIONS = [
    # Income entries
    {"amount": 75000.00, "type": TransactionType.income, "category": "salary",      "notes": "Monthly salary - January"},
    {"amount": 75000.00, "type": TransactionType.income, "category": "salary",      "notes": "Monthly salary - February"},
    {"amount": 75000.00, "type": TransactionType.income, "category": "salary",      "notes": "Monthly salary - March"},
    {"amount": 15000.00, "type": TransactionType.income, "category": "freelance",   "notes": "Web design project"},
    {"amount": 8500.00,  "type": TransactionType.income, "category": "freelance",   "notes": "API development contract"},
    {"amount": 5200.00,  "type": TransactionType.income, "category": "investments", "notes": "Dividend payout Q1"},
    {"amount": 3000.00,  "type": TransactionType.income, "category": "rental",      "notes": "Property rental income"},
    {"amount": 10000.00, "type": TransactionType.income, "category": "bonus",       "notes": "Annual performance bonus"},
    {"amount": 2500.00,  "type": TransactionType.income, "category": "investments", "notes": "Mutual fund returns"},
    {"amount": 3000.00,  "type": TransactionType.income, "category": "rental",      "notes": "Property rental income Feb"},
    # Expense entries
    {"amount": 12000.00, "type": TransactionType.expense, "category": "rent",          "notes": "Monthly house rent"},
    {"amount": 12000.00, "type": TransactionType.expense, "category": "rent",          "notes": "Monthly house rent Feb"},
    {"amount": 12000.00, "type": TransactionType.expense, "category": "rent",          "notes": "Monthly house rent Mar"},
    {"amount": 4500.00,  "type": TransactionType.expense, "category": "food",          "notes": "Groceries and dining"},
    {"amount": 3200.00,  "type": TransactionType.expense, "category": "food",          "notes": "Groceries Feb"},
    {"amount": 2800.00,  "type": TransactionType.expense, "category": "transport",     "notes": "Cab and metro monthly"},
    {"amount": 1500.00,  "type": TransactionType.expense, "category": "utilities",     "notes": "Electricity, water, internet"},
    {"amount": 1800.00,  "type": TransactionType.expense, "category": "utilities",     "notes": "Utilities Feb"},
    {"amount": 3500.00,  "type": TransactionType.expense, "category": "entertainment", "notes": "OTT, outings, events"},
    {"amount": 6000.00,  "type": TransactionType.expense, "category": "shopping",      "notes": "Clothes and electronics"},
    {"amount": 2200.00,  "type": TransactionType.expense, "category": "health",        "notes": "Gym, medicine, checkup"},
    {"amount": 900.00,   "type": TransactionType.expense, "category": "transport",     "notes": "Fuel expenses"},
    {"amount": 1200.00,  "type": TransactionType.expense, "category": "entertainment", "notes": "Streaming subscriptions"},
    {"amount": 4100.00,  "type": TransactionType.expense, "category": "food",          "notes": "Groceries Mar"},
    {"amount": 800.00,   "type": TransactionType.expense, "category": "health",        "notes": "Pharmacy"},
]


def random_date_in_last_3_months() -> date:
    today = date.today()
    start = today - timedelta(days=90)
    delta = (today - start).days
    return start + timedelta(days=random.randint(0, delta))


def seed():
    db = SessionLocal()

    try:
        # Clear existing data
        db.query(Transaction).delete()
        db.query(User).delete()
        db.commit()
        print("🗑  Cleared existing data.")

        # Create users
        from services.auth_service import hash_password

        created_users = []
        for u in USERS:
            user = User(
                name=u["name"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
            )
            db.add(user)
            db.flush()
            created_users.append(user)
            print(f"✅ Created user: {u['email']} ({u['role'].value})")

        db.commit()

        # Assign transactions to admin user (id of Alice Admin)
        admin_user = created_users[0]

        for i, tx_data in enumerate(SAMPLE_TRANSACTIONS):
            tx = Transaction(
                user_id=admin_user.id,
                amount=tx_data["amount"],
                type=tx_data["type"],
                category=tx_data["category"],
                date=random_date_in_last_3_months(),
                notes=tx_data.get("notes"),
            )
            db.add(tx)

        db.commit()
        print(f"✅ Created {len(SAMPLE_TRANSACTIONS)} transactions for {admin_user.email}")

        print("\n" + "=" * 50)
        print("🌱 Seed complete! Use these credentials to test:")
        print("=" * 50)
        for u in USERS:
            print(f"  {u['role'].value:8s} → {u['email']}  /  {u['password']}")
        print("=" * 50)
        print("📖 API docs: http://localhost:8000/docs")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
