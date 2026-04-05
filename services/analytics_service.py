from collections import defaultdict
from datetime import date
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.transaction import Transaction, TransactionType
from schemas.transaction import CategoryBreakdown, MonthlyTotal, SummaryResponse


def get_summary(db: Session, user_id: Optional[int] = None) -> SummaryResponse:
    query = db.query(Transaction)
    if user_id:
        query = query.filter(Transaction.user_id == user_id)

    all_transactions = query.all()

    total_income = sum(t.amount for t in all_transactions if t.type == TransactionType.income)
    total_expenses = sum(t.amount for t in all_transactions if t.type == TransactionType.expense)
    balance = round(total_income - total_expenses, 2)

    recent = (
        query.order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .limit(5)
        .all()
    )

    return SummaryResponse(
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        current_balance=balance,
        total_transactions=len(all_transactions),
        recent_transactions=recent,
    )


def get_category_breakdown(
    db: Session,
    type: Optional[TransactionType] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    user_id: Optional[int] = None,
) -> list[CategoryBreakdown]:
    query = db.query(Transaction)

    if user_id:
        query = query.filter(Transaction.user_id == user_id)
    if type:
        query = query.filter(Transaction.type == type)
    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)

    transactions = query.all()

    if not transactions:
        return []

    category_totals: dict[str, dict] = defaultdict(lambda: {"total": 0.0, "count": 0})
    grand_total = 0.0

    for t in transactions:
        category_totals[t.category]["total"] += t.amount
        category_totals[t.category]["count"] += 1
        grand_total += t.amount

    result = []
    for category, data in sorted(category_totals.items(), key=lambda x: x[1]["total"], reverse=True):
        pct = round((data["total"] / grand_total) * 100, 2) if grand_total > 0 else 0.0
        result.append(
            CategoryBreakdown(
                category=category,
                total=round(data["total"], 2),
                count=data["count"],
                percentage=pct,
            )
        )

    return result


def get_monthly_totals(
    db: Session,
    user_id: Optional[int] = None,
    year: Optional[int] = None,
) -> list[MonthlyTotal]:
    query = db.query(Transaction)

    if user_id:
        query = query.filter(Transaction.user_id == user_id)
    if year:
        query = query.filter(func.strftime("%Y", Transaction.date) == str(year))

    transactions = query.all()

    monthly: dict[str, dict] = defaultdict(lambda: {"income": 0.0, "expense": 0.0})

    for t in transactions:
        month_key = t.date.strftime("%Y-%m")
        if t.type == TransactionType.income:
            monthly[month_key]["income"] += t.amount
        else:
            monthly[month_key]["expense"] += t.amount

    result = []
    for month in sorted(monthly.keys()):
        data = monthly[month]
        income = round(data["income"], 2)
        expense = round(data["expense"], 2)
        result.append(
            MonthlyTotal(
                month=month,
                income=income,
                expense=expense,
                net=round(income - expense, 2),
            )
        )

    return result
