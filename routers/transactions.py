from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_admin, require_analyst, require_viewer
from models.transaction import TransactionType
from models.user import User, UserRole
from schemas.transaction import (
    TransactionCreate,
    TransactionListResponse,
    TransactionResponse,
    TransactionUpdate,
)
from services.transaction_service import (
    create_transaction,
    delete_transaction,
    get_transaction_by_id,
    get_transactions,
    update_transaction,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    # Filters
    type: Optional[TransactionType] = Query(None, description="Filter by income or expense"),
    category: Optional[str] = Query(None, description="Filter by category"),
    date_from: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_viewer),
):
    """
    List transactions with optional filters and pagination.
    - Viewers and analysts see their own transactions.
    - Admins see all transactions.
    """
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from must be before or equal to date_to",
        )

    # Admins can see all; others only see their own
    filter_user_id = None if current_user.role == UserRole.admin else current_user.id

    skip = (page - 1) * page_size
    items, total = get_transactions(
        db,
        skip=skip,
        limit=page_size,
        type=type,
        category=category,
        date_from=date_from,
        date_to=date_to,
        user_id=filter_user_id,
    )

    return TransactionListResponse(total=total, page=page, page_size=page_size, items=items)


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def add_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Admin only: Create a new transaction."""
    tx = create_transaction(db, data, user_id=current_user.id)
    return tx


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_viewer),
):
    """Get a single transaction by ID."""
    tx = get_transaction_by_id(db, transaction_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    # Non-admins can only view their own transactions
    if current_user.role != UserRole.admin and tx.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return tx


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def edit_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Admin only: Partially update a transaction."""
    if not data.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )
    tx = update_transaction(db, transaction_id, data)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return tx


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Admin only: Delete a transaction."""
    success = delete_transaction(db, transaction_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
