from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from dependencies import require_analyst, require_viewer
from models.transaction import TransactionType
from models.user import User, UserRole
from schemas.transaction import CategoryBreakdown, MonthlyTotal, SummaryResponse
from services.analytics_service import get_category_breakdown, get_monthly_totals, get_summary

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=SummaryResponse)
def summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_viewer),
):
    """
    Financial summary: total income, expenses, balance, and 5 recent transactions.
    - Admins see system-wide summary.
    - Others see their own data.
    """
    user_id = None if current_user.role == UserRole.admin else current_user.id
    return get_summary(db, user_id=user_id)


@router.get("/category-breakdown", response_model=list[CategoryBreakdown])
def category_breakdown(
    type: Optional[TransactionType] = Query(None, description="Filter by income or expense"),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """
    Analyst+: Breakdown of spending or income by category with percentage.
    """
    user_id = None if current_user.role == UserRole.admin else current_user.id
    return get_category_breakdown(db, type=type, date_from=date_from, date_to=date_to, user_id=user_id)


@router.get("/monthly", response_model=list[MonthlyTotal])
def monthly_totals(
    year: Optional[int] = Query(None, description="Filter by year e.g. 2024"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """
    Analyst+: Monthly income vs expense breakdown with net balance per month.
    """
    user_id = None if current_user.role == UserRole.admin else current_user.id
    return get_monthly_totals(db, user_id=user_id, year=year)
