from decimal import Decimal

from tests.test_support import ServiceTestCase

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction
from app.services import wallet_service


class WalletServiceTests(ServiceTestCase):
    def test_balance_and_deposit_create_ledger_entry(self):
        user_id, _wallet_id = self.create_user_with_wallet()

        self.assertEqual(wallet_service.get_wallet_balance(user_id), Decimal("0.00"))
        new_balance = wallet_service.deposit_to_wallet(
            user_id,
            Decimal("25.50"),
        )
        self.assertEqual(new_balance, Decimal("25.50"))

        with Session(self.engine) as session:
            transaction = session.scalar(select(WalletTransaction))
            self.assertEqual(transaction.transaction_type, "deposit")
            self.assertEqual(transaction.amount, Decimal("25.50"))

    def test_missing_wallet_balance_and_deposit(self):
        self.assertIsNone(wallet_service.get_wallet_balance(9999))
        with self.assertRaisesRegex(ValueError, "No wallet"):
            wallet_service.deposit_to_wallet(9999, Decimal("1.00"))

    def test_deposit_rejects_nonpositive_nonfinite_and_excess_precision(self):
        user_id, _wallet_id = self.create_user_with_wallet()

        for amount in (
            Decimal("0.00"),
            Decimal("-1.00"),
            Decimal("NaN"),
            Decimal("1.001"),
        ):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                wallet_service.deposit_to_wallet(user_id, amount)

        self.assertEqual(wallet_service.get_wallet_balance(user_id), Decimal("0.00"))

    def test_transaction_history_is_user_scoped_and_newest_first(self):
        user_id, _ = self.create_user_with_wallet(email="one@example.com")
        other_user_id, _ = self.create_user_with_wallet(email="two@example.com")
        wallet_service.deposit_to_wallet(user_id, Decimal("5.00"))
        wallet_service.deposit_to_wallet(user_id, Decimal("7.00"))
        wallet_service.deposit_to_wallet(other_user_id, Decimal("99.00"))

        rows = wallet_service.get_wallet_transactions(user_id)

        self.assertEqual([row.amount for row in rows], [Decimal("7.00"), Decimal("5.00")])
        self.assertTrue(all(row.transaction_type == "deposit" for row in rows))

    def test_no_transactions_returns_empty_list(self):
        user_id, _ = self.create_user_with_wallet()
        self.assertEqual(wallet_service.get_wallet_transactions(user_id), [])
