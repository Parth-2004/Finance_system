from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator

from models.transaction import TransactionType


class TransactionCreate(BaseModel):
    amount: float
    type: TransactionType
    category: str
    date: date
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(v, 2)

    @field_validator("category")
    @classmethod
    def category_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Category must not be empty")
        return v.strip().lower()


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(v, 2) if v is not None else v


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    type: TransactionType
    category: str
    date: date
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[TransactionResponse]


# ── Analytics schemas ─────────────────────────────────────────────────────────

class CategoryBreakdown(BaseModel):
    category: str
    total: float
    count: int
    percentage: float


class MonthlyTotal(BaseModel):
    month: str          # "2024-01"
    income: float
    expense: float
    net: float


class SummaryResponse(BaseModel):
    total_income: float
    total_expenses: float
    current_balance: float
    total_transactions: int
    recent_transactions: List[TransactionResponse]
