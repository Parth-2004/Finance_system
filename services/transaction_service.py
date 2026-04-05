from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from models.transaction import Transaction, TransactionType
from schemas.transaction import TransactionCreate, TransactionUpdate


def create_transaction(db: Session, data: TransactionCreate, user_id: int) -> Transaction:
    tx = Transaction(
        user_id=user_id,
        amount=data.amount,
        type=data.type,
        category=data.category,
        date=data.date,
        notes=data.notes,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def get_transaction_by_id(db: Session, transaction_id: int) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


def get_transactions(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    type: Optional[TransactionType] = None,
    category: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    user_id: Optional[int] = None,
) -> tuple[list[Transaction], int]:
    query = db.query(Transaction)

    if user_id is not None:
        query = query.filter(Transaction.user_id == user_id)
    if type is not None:
        query = query.filter(Transaction.type == type)
    if category is not None:
        query = query.filter(Transaction.category == category.lower())
    if date_from is not None:
        query = query.filter(Transaction.date >= date_from)
    if date_to is not None:
        query = query.filter(Transaction.date <= date_to)

    total = query.count()
    items = query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()
    return items, total


def update_transaction(
    db: Session, transaction_id: int, data: TransactionUpdate
) -> Optional[Transaction]:
    tx = get_transaction_by_id(db, transaction_id)
    if not tx:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tx, field, value)

    db.commit()
    db.refresh(tx)
    return tx


def delete_transaction(db: Session, transaction_id: int) -> bool:
    tx = get_transaction_by_id(db, transaction_id)
    if not tx:
        return False
    db.delete(tx)
    db.commit()
    return True
