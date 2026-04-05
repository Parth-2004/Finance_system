"""
Unit & integration tests for the Finance Tracking System.

Run:
    pip install pytest httpx
    pytest tests.py -v
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app
from models.user import UserRole
from models.transaction import TransactionType

# ── Test database (in-memory SQLite) ─────────────────────────────────────────

TEST_DATABASE_URL = "sqlite:///./test_finance.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    return TestClient(app)


# ── Helpers ───────────────────────────────────────────────────────────────────

def register_and_login(client, email, password, role="viewer", name="Test User"):
    client.post("/auth/register", json={"name": name, "email": email, "password": password, "role": role})
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ── Auth Tests ────────────────────────────────────────────────────────────────

class TestAuth:
    def test_register_success(self, client):
        resp = client.post("/auth/register", json={
            "name": "New User", "email": "newuser@test.com", "password": "pass123"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "newuser@test.com"
        assert data["role"] == "viewer"

    def test_register_duplicate_email(self, client):
        payload = {"name": "Dup", "email": "dup@test.com", "password": "pass123"}
        client.post("/auth/register", json=payload)
        resp = client.post("/auth/register", json=payload)
        assert resp.status_code == 409

    def test_register_short_password(self, client):
        resp = client.post("/auth/register", json={
            "name": "Bad", "email": "bad@test.com", "password": "12"
        })
        assert resp.status_code == 422

    def test_login_success(self, client):
        client.post("/auth/register", json={
            "name": "Login User", "email": "login@test.com", "password": "mypass123"
        })
        resp = client.post("/auth/login", json={"email": "login@test.com", "password": "mypass123"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client):
        resp = client.post("/auth/login", json={"email": "login@test.com", "password": "wrongpass"})
        assert resp.status_code == 401

    def test_get_me(self, client):
        token = register_and_login(client, "me@test.com", "pass123", name="Me User")
        resp = client.get("/auth/me", headers=auth_headers(token))
        assert resp.status_code == 200
        assert resp.json()["email"] == "me@test.com"

    def test_invalid_token(self, client):
        resp = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
        assert resp.status_code == 401


# ── Transaction Tests ─────────────────────────────────────────────────────────

class TestTransactions:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.admin_token = register_and_login(client, "txadmin@test.com", "admin123", "admin", "TX Admin")
        self.viewer_token = register_and_login(client, "txviewer@test.com", "viewer123", "viewer", "TX Viewer")
        self.analyst_token = register_and_login(client, "txanalyst@test.com", "analyst123", "analyst", "TX Analyst")

    def test_create_transaction_as_admin(self, client):
        resp = client.post("/transactions", headers=auth_headers(self.admin_token), json={
            "amount": 5000.0,
            "type": "income",
            "category": "salary",
            "date": "2024-03-01",
            "notes": "Test income",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["amount"] == 5000.0
        assert data["category"] == "salary"

    def test_create_transaction_as_viewer_forbidden(self, client):
        resp = client.post("/transactions", headers=auth_headers(self.viewer_token), json={
            "amount": 100.0, "type": "expense", "category": "food", "date": "2024-03-01"
        })
        assert resp.status_code == 403

    def test_create_negative_amount_fails(self, client):
        resp = client.post("/transactions", headers=auth_headers(self.admin_token), json={
            "amount": -500.0, "type": "expense", "category": "food", "date": "2024-03-01"
        })
        assert resp.status_code == 422

    def test_create_zero_amount_fails(self, client):
        resp = client.post("/transactions", headers=auth_headers(self.admin_token), json={
            "amount": 0, "type": "income", "category": "salary", "date": "2024-03-01"
        })
        assert resp.status_code == 422

    def test_list_transactions_viewer(self, client):
        resp = client.get("/transactions", headers=auth_headers(self.viewer_token))
        assert resp.status_code == 200
        assert "items" in resp.json()

    def test_list_transactions_filter_by_type(self, client):
        resp = client.get("/transactions?type=income", headers=auth_headers(self.admin_token))
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item["type"] == "income"

    def test_list_transactions_invalid_date_range(self, client):
        resp = client.get(
            "/transactions?date_from=2024-06-01&date_to=2024-01-01",
            headers=auth_headers(self.admin_token),
        )
        assert resp.status_code == 400

    def test_update_transaction_as_admin(self, client):
        # Create first
        create_resp = client.post("/transactions", headers=auth_headers(self.admin_token), json={
            "amount": 200.0, "type": "expense", "category": "food", "date": "2024-03-10"
        })
        tx_id = create_resp.json()["id"]

        resp = client.patch(f"/transactions/{tx_id}", headers=auth_headers(self.admin_token), json={
            "amount": 250.0, "notes": "Updated note"
        })
        assert resp.status_code == 200
        assert resp.json()["amount"] == 250.0

    def test_update_nonexistent_transaction(self, client):
        resp = client.patch("/transactions/99999", headers=auth_headers(self.admin_token), json={
            "amount": 100.0
        })
        assert resp.status_code == 404

    def test_delete_transaction_as_admin(self, client):
        create_resp = client.post("/transactions", headers=auth_headers(self.admin_token), json={
            "amount": 100.0, "type": "expense", "category": "transport", "date": "2024-03-05"
        })
        tx_id = create_resp.json()["id"]
        del_resp = client.delete(f"/transactions/{tx_id}", headers=auth_headers(self.admin_token))
        assert del_resp.status_code == 204

    def test_delete_as_viewer_forbidden(self, client):
        resp = client.delete("/transactions/1", headers=auth_headers(self.viewer_token))
        assert resp.status_code == 403

    def test_pagination(self, client):
        resp = client.get("/transactions?page=1&page_size=2", headers=auth_headers(self.admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["items"]) <= 2


# ── Analytics Tests ───────────────────────────────────────────────────────────

class TestAnalytics:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.admin_token = register_and_login(client, "anadmin@test.com", "admin123", "admin", "Ana Admin")
        self.analyst_token = register_and_login(client, "anaanalyst@test.com", "analyst123", "analyst", "Ana Analyst")
        self.viewer_token = register_and_login(client, "anaviewer@test.com", "viewer123", "viewer", "Ana Viewer")

        # Seed some transactions
        for _ in range(3):
            client.post("/transactions", headers=auth_headers(self.admin_token), json={
                "amount": 10000.0, "type": "income", "category": "salary", "date": "2024-02-01"
            })
            client.post("/transactions", headers=auth_headers(self.admin_token), json={
                "amount": 2000.0, "type": "expense", "category": "food", "date": "2024-02-15"
            })

    def test_summary_returns_correct_fields(self, client):
        resp = client.get("/analytics/summary", headers=auth_headers(self.admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert "total_income" in data
        assert "total_expenses" in data
        assert "current_balance" in data
        assert "total_transactions" in data
        assert "recent_transactions" in data

    def test_summary_balance_is_correct(self, client):
        resp = client.get("/analytics/summary", headers=auth_headers(self.admin_token))
        data = resp.json()
        expected_balance = round(data["total_income"] - data["total_expenses"], 2)
        assert data["current_balance"] == expected_balance

    def test_category_breakdown_analyst_access(self, client):
        resp = client.get("/analytics/category-breakdown", headers=auth_headers(self.analyst_token))
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_category_breakdown_viewer_forbidden(self, client):
        resp = client.get("/analytics/category-breakdown", headers=auth_headers(self.viewer_token))
        assert resp.status_code == 403

    def test_monthly_totals_analyst_access(self, client):
        resp = client.get("/analytics/monthly", headers=auth_headers(self.analyst_token))
        assert resp.status_code == 200
        for item in resp.json():
            assert "month" in item
            assert "income" in item
            assert "expense" in item
            assert "net" in item

    def test_monthly_totals_viewer_forbidden(self, client):
        resp = client.get("/analytics/monthly", headers=auth_headers(self.viewer_token))
        assert resp.status_code == 403

    def test_category_breakdown_filter_by_type(self, client):
        resp = client.get(
            "/analytics/category-breakdown?type=expense",
            headers=auth_headers(self.analyst_token),
        )
        assert resp.status_code == 200

    def test_monthly_filter_by_year(self, client):
        resp = client.get("/analytics/monthly?year=2024", headers=auth_headers(self.analyst_token))
        assert resp.status_code == 200
        for item in resp.json():
            assert item["month"].startswith("2024")
