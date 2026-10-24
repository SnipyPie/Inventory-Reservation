from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import engine
from app.models.wallet import Wallet
from decimal import Decimal

from app.models.wallet_transaction import WalletTransaction

def get_wallet_balance(user_id: int):
    with Session(engine) as session:
        wallet = session.scalar(
            select(Wallet).where(Wallet.user_id == user_id)
        )

        if wallet is None:
            return None

        return wallet.balance

def deposit_to_wallet(user_id: int, amount: Decimal):
    if not amount.is_finite() or amount <= 0:
        raise ValueError("Deposit amount must be greater than zero.")

    if amount != amount.quantize(Decimal("0.01")):
        raise ValueError("Deposit amount can have at most two decimal places.")

    with Session(engine) as session:
        wallet = session.scalar(
            select(Wallet)
            .where(Wallet.user_id == user_id)
            .with_for_update()
        )

        if wallet is None:
            raise ValueError("No wallet was found for this user.")

        wallet.balance += amount

        transaction = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type="deposit",
            amount=amount,
        )
        session.add(transaction)
        session.commit()
        session.refresh(wallet)

        return wallet.balance